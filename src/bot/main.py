import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
import os
from src.bot.handlers.start import router as start_router
from src.bot.handlers.training import router as training_router
from src.bot.handlers.body import router as body_router
from src.bot.handlers.all_trainings import router as all_trainings_router
from src.bot.middlewares.api import *
from src.bot.middlewares.auth import *
from src.bot.services.api_client import *
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def main():
    bot = Bot(TELEGRAM_TOKEN)
    db = Dispatcher()

    api_client = APIClient(base_url="http://127.0.0.1:8000/", secret_token="")

    db.update.outer_middleware(APIClientMiddleware(api_client))
    db.update.outer_middleware(UserAuthMiddleware())

    db.include_router(start_router)
    db.include_router(training_router)
    db.include_router(body_router)
    db.include_router(all_trainings_router)
    await db.start_polling(bot)

if __name__ == "__main__":
    try:
        print("Bot is started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is closed")