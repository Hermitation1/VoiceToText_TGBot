from datetime import datetime

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User
from faster_whisper import WhisperModel


def make_event(message_id=1, text: str | None = None) -> Message:
    return Message(
        message_id=message_id,
        from_user=User(
            id=123456789, is_bot=False, first_name="Alice", username="alice"
        ),
        chat=Chat(id=123456789, type="private"),
        date=datetime.now(),
        text=text,
    )


def make_callback(data: str) -> CallbackQuery:
    message = make_event(text="/start")
    return CallbackQuery(
        id="1",
        from_user=message.from_user,
        message=message,
        chat_instance="x",
        data=data,
    )


@pytest.fixture(scope="session")
def tiny_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")
