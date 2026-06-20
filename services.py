import asyncio
import json
import logging
import os
from pathlib import Path

import ffmpeg
from aiogram.types import (
    Audio,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Video,
    VideoNote,
    Voice,
)
from faster_whisper import WhisperModel

from config import settings
from core import bot

MediaFile = Voice | Video | VideoNote | Audio

_model: WhisperModel | None = None
_model_lock = asyncio.Lock()


def init_model(model: WhisperModel) -> None:
    global _model
    _model = model


USERS_FILE = Path("allowed_users.json")

logger = logging.getLogger(__name__)


def load_users() -> dict[str, str]:
    if USERS_FILE.exists():
        return dict(json.loads(USERS_FILE.read_text()))
    return dict()


def save_users(users: dict[str, str]) -> None:
    USERS_FILE.write_text(json.dumps(dict(users)))


allowed_users = load_users()


async def request_access(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Разрешить/Approve",
                    callback_data=f"approve_{user_id}|@{username}",
                ),
                InlineKeyboardButton(
                    text="❌ Запретить/Deny",
                    callback_data=f"deny_{user_id}|@{username}",
                ),
            ]
        ]
    )

    await bot.send_message(
        settings.owner_id,
        f"Запрос доступа от @{message.from_user.username}\n"
        f"Access request from @{message.from_user.username}\n"
        f"ID:{user_id}\n",
        reply_markup=keyboard,
    )
    await message.answer("Запрос отправлен, ожидайте\nRequest sent, please wait")


async def set_user_access(callback: CallbackQuery):
    user = callback.data.split("_")[1]
    user_id, username = user.split("|")
    if callback.data.startswith("approve_"):
        allowed_users[str(user_id)] = username
        save_users(allowed_users)
        await bot.send_message(
            user_id,
            "Доступ выдан! Можете пользоваться ботом.\n"
            "Access granted! You can now use the bot.",
        )
    elif callback.data.startswith("deny_"):
        await bot.send_message(user_id, "В доступе отказано.\nAccess denied.")
    await callback.message.edit_reply_markup(reply_markup=None)


async def get_users_with_delete_buttons(message: Message):
    users = ""
    buttons = []
    for user_id, username in allowed_users.items():
        users += f"\n{username}"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"❌ {username}", callback_data=f"delete_{user_id}|{username}"
                ),
            ],
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(f"Список пользователей / Users:{users}", reply_markup=keyboard)


async def delete_user(callback: CallbackQuery):
    user = callback.data.split("_")[1]
    user_id, username = user.split("|")
    del allowed_users[user_id]
    save_users(allowed_users)
    await callback.answer(f"Пользователь {username} удален! / User {username} deleted!")
    await callback.message.edit_reply_markup(reply_markup=None)


async def handle_audio_or_video_file(
    message: Message,
    file_format: str,
):
    file_obj: MediaFile = getattr(message, message.content_type)
    file_id = file_obj.file_id

    file_name = f"voice_files/{file_id}.{file_format}"
    ogg_name = f"voice_files/{file_id}.ogg"

    try:
        file = await bot.get_file(file_id)
        # data = await bot.download_file(file.file_path)
        data = await download_with_retry(file.file_path)

        msg = await message.answer("Downloading...")

        with open(file_name, "wb") as f:
            f.write(data.read())

        if not file_name.endswith(".ogg"):
            await msg.edit_text("Converting...")
            await asyncio.to_thread(convert_to_ogg_audio, file_name, ogg_name)
        await msg.edit_text("Transcribing...")
        await transcribe_audio(msg, ogg_name)

    except Exception as e:
        await message.answer("Something went wrong, please try again later")
        logger.exception(f"Ошибка: {e}")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
        if os.path.exists(ogg_name):
            os.remove(ogg_name)


async def transcribe_audio(msg, audio_path: str):
    async with _model_lock:
        segments, _info = await asyncio.to_thread(
            _model.transcribe,
            audio_path,
            no_repeat_ngram_size=3,
            no_speech_threshold=0.6,
            repetition_penalty=1.03,
        )  # language="ru"

    text = ""  # ' '.join(line.text for line in segments)

    for segment in segments:
        text += segment.text
        await msg.edit_text(text)


async def download_with_retry(file_path: str, retries: int = 3):
    last_err = None
    for _attempt in range(retries):
        try:
            return await bot.download_file(file_path)
        except Exception as e:
            last_err = e
            await asyncio.sleep(0.5)
    raise last_err


def convert_to_ogg_audio(input_path: str, output_path: str):
    ffmpeg.input(input_path).output(output_path, threads=8, vn=None).run(quiet=True)


async def keepalive_task():
    while True:
        await asyncio.sleep(60)
        try:
            await bot.get_me()
        except Exception as e:
            logger.warning(f"Keepalive ping failed: {e}")
