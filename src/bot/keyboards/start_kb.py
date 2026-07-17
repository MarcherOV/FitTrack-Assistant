from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Add training"), KeyboardButton(text="See all my trainings")],
    [KeyboardButton(text="Add body info"), KeyboardButton(text="See all my body info")],
    [KeyboardButton(text="See my stats")]
])