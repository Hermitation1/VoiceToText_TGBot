import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot
from aiogram.types import Message

from middleware import ProcessingMiddleware, UserAccess
from tests.conftest import make_event


class TestUserAccess:
    @pytest.mark.asyncio
    async def test_allows_start_command(self):
        handler = AsyncMock()
        middleware = UserAccess()
        event = make_event(text="/start")

        await middleware(handler, event, {})

        handler.assert_called_once_with(event, {})

    @pytest.mark.asyncio
    async def test_allows_help_command(self):
        handler = AsyncMock()
        middleware = UserAccess()
        event = make_event(text="/help")

        await middleware(handler, event, {})

        handler.assert_called_once_with(event, {})

    @pytest.mark.asyncio
    async def test_allows_allowed_users(self, monkeypatch):
        monkeypatch.setattr("middleware.allowed_users", {"123456789": "alice"})
        handler = AsyncMock()
        middleware = UserAccess()
        event = make_event()

        await middleware(handler, event, {})

        handler.assert_called_once_with(event, {})

    @patch.object(Message, "answer", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_blocks_unauthorized_user(self, mock_answer, monkeypatch):
        monkeypatch.setattr("middleware.allowed_users", {})
        handler = AsyncMock()
        middleware = UserAccess()
        event = make_event()

        await middleware(handler, event, {})

        handler.assert_not_called()
        mock_answer.assert_called_once_with("У вас нет прав\nYou don't have access")


class TestProcessingMiddleware:
    @patch.object(Bot, "send_message", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_first_file_start_processing(self, mock_send_message):
        handler = AsyncMock()
        middleware = ProcessingMiddleware()
        event = make_event()

        await middleware(handler, event, {})
        await asyncio.sleep(0)

        handler.assert_called_once_with(event, {})
        mock_send_message.assert_not_called()
        assert event.from_user.id not in middleware._queues

    @patch.object(Bot, "send_message", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_second_file_in_queue(self, mock_send_message):
        handler = AsyncMock()
        middleware = ProcessingMiddleware()
        event = make_event()
        user_id = event.from_user.id
        middleware._queues[user_id] = asyncio.PriorityQueue()
        middleware._position[user_id] = 0

        await middleware(handler, event, {})

        handler.assert_not_called()
        mock_send_message.assert_called_once_with(
            user_id, "В очереди (1)\nIn queue (1)"
        )
        assert user_id in middleware._queues

    @pytest.mark.asyncio
    async def test_files_processing_by_id_and_after_user_removed_from_queue(self):
        handler = AsyncMock()
        middleware = ProcessingMiddleware()
        event_1 = make_event()
        event_2 = make_event(message_id=2)
        user_id = event_1.from_user.id
        middleware._queues[user_id] = asyncio.PriorityQueue()
        middleware._position[user_id] = 0
        middleware._queues[user_id].put_nowait(
            (event_1.message_id, handler, event_1, {})
        )
        middleware._queues[user_id].put_nowait(
            (event_2.message_id, handler, event_2, {})
        )

        await middleware._process_queue(user_id)

        assert handler.mock_calls[0].args[0] is event_1
        assert handler.mock_calls[1].args[0] is event_2
        assert user_id not in middleware._queues
        assert user_id not in middleware._position
