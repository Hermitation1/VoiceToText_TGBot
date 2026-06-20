import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiogram import Bot
from aiogram.types import CallbackQuery, Message

from services import (
    delete_user,
    load_users,
    request_access,
    save_users,
    set_user_access,
)
from tests.conftest import make_callback, make_event


def make_users_file(path: Path, data: dict[str, str]) -> None:
    """Записать тестовый JSON в файл."""
    path.write_text(json.dumps(data), encoding="utf-8")


class TestLoadUsers:
    def test_returns_empty_dict_when_file_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "nonexistent.json"
        monkeypatch.setattr("services.USERS_FILE", fake)
        assert load_users() == {}

    def test_reads_existing_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "users.json"
        make_users_file(fake, {"123": "alice", "456": "bob"})
        monkeypatch.setattr("services.USERS_FILE", fake)
        assert load_users() == {"123": "alice", "456": "bob"}


class TestSaveUsers:
    def test_writes_and_reads_back(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "users.json"
        monkeypatch.setattr("services.USERS_FILE", fake)

        save_users({"789": "charlie"})

        assert load_users() == {"789": "charlie"}

    def test_overwrites_existing_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "users.json"
        make_users_file(fake, {"111": "old"})
        monkeypatch.setattr("services.USERS_FILE", fake)

        save_users({"222": "new"})

        assert load_users() == {"222": "new"}


class TestRequestAccess:
    @patch.object(Message, "answer", new_callable=AsyncMock)
    @patch.object(Bot, "send_message", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_request_access_notifies_owner_and_user(
        self, mock_send_message, mock_answer, monkeypatch
    ):
        event = make_event(text="/start")
        monkeypatch.setattr("config.settings.owner_id", "333444555")

        await request_access(event)

        # проверяем сообщение владельцу — текст и клавиатура
        assert mock_send_message.call_args.args[0] == "333444555"
        assert "Запрос доступа от @alice" in mock_send_message.call_args.args[1]
        assert "reply_markup" in mock_send_message.call_args.kwargs

        # проверяем ответ пользователю
        mock_answer.assert_called_once_with(
            "Запрос отправлен, ожидайте\nRequest sent, please wait"
        )


class TestSetUserAccess:
    @patch.object(Message, "edit_reply_markup", new_callable=AsyncMock)
    @patch.object(Bot, "send_message", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_approve_grants_access_and_removes_keyboard(
        self, mock_send_message, mock_edit_message, monkeypatch
    ):
        callback = make_callback("approve_123456789|@alice")
        monkeypatch.setattr("services.save_users", Mock())

        await set_user_access(callback)

        mock_send_message.assert_called_once_with(
            "123456789",
            (
                "Доступ выдан! Можете пользоваться ботом.\n"
                "Access granted! You can now use the bot."
            ),
        )
        mock_edit_message.assert_called_once_with(reply_markup=None)

    @patch.object(Message, "edit_reply_markup", new_callable=AsyncMock)
    @patch.object(Bot, "send_message", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_deny_notifies_and_removes_keyboard(
        self, mock_send_message, mock_edit, monkeypatch
    ):
        callback = make_callback("deny_123456789|@alice")
        monkeypatch.setattr("services.save_users", Mock())

        await set_user_access(callback)

        mock_send_message.assert_called_once_with(
            "123456789",
            "В доступе отказано.\nAccess denied.",
        )
        mock_edit.assert_called_once_with(reply_markup=None)


class TestDeleteUser:
    @patch.object(Message, "edit_reply_markup", new_callable=AsyncMock)
    @patch.object(CallbackQuery, "answer", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_delete_user(self, mock_answer, mock_edit, monkeypatch):
        callback = make_callback("delete_123456789|@alice")
        monkeypatch.setattr("services.save_users", Mock())
        monkeypatch.setattr("services.allowed_users", {"123456789": "@alice"})

        await delete_user(callback)

        mock_answer.assert_called_once_with(
            "Пользователь @alice удален! / User @alice deleted!"
        )
        mock_edit.assert_called_once_with(reply_markup=None)
