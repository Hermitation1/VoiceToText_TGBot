import asyncio
import logging
import os

from aiogram import F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message,
)

from config import settings
from core import bot, create_model, dp, router
from messages import HELP_MESSAGE
from middleware import ProcessingMiddleware, UserAccess
from services import (
    allowed_users,
    delete_user,
    get_users_with_delete_buttons,
    handle_audio_or_video_file,
    init_model,
    keepalive_task,
    request_access,
    set_user_access,
)

router.message.middleware(UserAccess())
# router.message.middleware(RateLimitMiddleware())
router.message.middleware(ProcessingMiddleware())


@router.message(Command("start"))
async def start_bot(message: Message):
    if str(message.from_user.id) in allowed_users:
        await message.answer("У вас уже есть доступ\nYou already have access")
    else:
        await request_access(message=message)


@router.message(Command("help"))
async def send_help_message(message: Message):
    await message.answer(HELP_MESSAGE)


@router.message(Command("get_users"), F.from_user.id == settings.owner_id)
async def get_users(message: Message):
    await get_users_with_delete_buttons(message=message)


@router.callback_query(F.data.startswith("delete_"))
async def delete_user_callback(callback: CallbackQuery):
    await delete_user(callback=callback)


@router.callback_query(F.data.startswith("approve_") | F.data.startswith("deny_"))
async def handle_user_access(callback: CallbackQuery):
    await set_user_access(callback=callback)


@router.message(F.voice)
async def handle_voice(message: Message):
    await handle_audio_or_video_file(
        message=message,
        file_format="ogg",
    )


@router.message(F.audio)
async def handle_audio(message: Message):
    await handle_audio_or_video_file(
        message=message,
        file_format=message.audio.mime_type.split("/")[1],
    )


@router.message(F.video_note | F.video)
async def handle_video_note(message: Message):
    await handle_audio_or_video_file(
        message=message,
        file_format="mp4",
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    init_model(create_model())
    os.makedirs("voice_files", exist_ok=True)
    asyncio.create_task(keepalive_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
