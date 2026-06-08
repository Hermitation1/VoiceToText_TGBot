import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.session.aiohttp import AiohttpSession
from faster_whisper import WhisperModel

from config import settings

logger = logging.getLogger(__name__)

session = AiohttpSession(proxy=settings.proxy_url)  # IF YOU USE PROXY

bot = Bot(token=settings.bot_token, session=session)
# bot = Bot(token=settings.bot_token) # without proxy
router = Router()
dp = Dispatcher()
dp.include_router(router)


def create_model() -> WhisperModel:
    logger.info("Loading model...")
    # model = WhisperModel("small", device="cpu", compute_type="int8") # based on cpu - SLOW mode  # noqa: E501
    model = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
    logger.info("Model loaded")
    return model
