import asyncio
import logging

from aiogram import BaseMiddleware
from aiogram.types import Message

from core import bot
from services import allowed_users

logger = logging.getLogger(__name__)


class UserAccess(BaseMiddleware):
    def __init__(self):
        self.allowed_users = allowed_users

    async def __call__(self, handler, event: Message, data):
        user_id = str(event.from_user.id)
        general_commands = ["/start", "/help"]
        if event.text in general_commands or user_id in allowed_users:
            return await handler(event, data)
        else:
            await event.answer("У вас нет прав\nYou don't have access")
            return None


class ProcessingMiddleware(BaseMiddleware):
    def __init__(self):
        self._queues: dict[int, asyncio.Queue[tuple]] = {}  # user_id: messages_queue

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id

        if user_id not in self._queues:
            self._queues[user_id] = asyncio.Queue(maxsize=10)
            self._queues[user_id].put_nowait((handler, event, data))
            asyncio.create_task(self._process_queue(user_id=user_id))
            return None
        else:
            self._queues[user_id].put_nowait((handler, event, data))
            await bot.send_message(
                user_id,
                f"В очереди ({self._queues[user_id].qsize()})\n"
                f"In queue ({self._queues[user_id].qsize()})",
            )
            return None

    async def _process_queue(self, user_id):
        while not self._queues[user_id].empty():
            handler, event, data = await self._queues[user_id].get()
            try:
                await handler(event, data)
            except Exception as e:
                logger.exception(f"Queue worker error for user {user_id}\nError: {e}")
            finally:
                self._queues[user_id].task_done()

        del self._queues[user_id]
