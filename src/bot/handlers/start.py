from aiogram.filters import CommandStart
from aiogram.types import Message, User
from aiogram import Router

from src.bot.keyboards.start_kb import start_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, db_user: dict):
    username = db_user.get("username")
    id_ = db_user.get("id")
    print(username, id_)
    print(message.from_user.id)
    await message.reply(f"Hi {message.from_user.username}!",
                        reply_markup=start_kb)