import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
import os
from handlers.start import router as start_router
from handlers.training import router as training_router
from handlers.body import router as body_router
from handlers.all_trainings import router as all_trainings_router
from handlers.all_body_info import router as all_body_info_router
from middlewares.api import *
from middlewares.auth import *
from services.api_client import *
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def main():
    bot = Bot(TELEGRAM_TOKEN)
    storage = RedisStorage.from_url("redis://redis:6379/0")
    db = Dispatcher(storage=storage, bot=bot)

    api_client = APIClient(base_url="http://api:8000/", secret_token=TELEGRAM_TOKEN)

    db.update.outer_middleware(APIClientMiddleware(api_client))
    db.update.outer_middleware(UserAuthMiddleware())

    db.include_router(start_router)
    db.include_router(training_router)
    db.include_router(body_router)
    db.include_router(all_trainings_router)
    db.include_router(all_body_info_router)
    await db.start_polling(bot)

if __name__ == "__main__":
    try:
        print("Bot is started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is closed")