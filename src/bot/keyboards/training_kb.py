from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class CategoryCallback(CallbackData, prefix="cat"):
    id: int

class ExerciseCallback(CallbackData, prefix="ex"):
    id: int
    name: str
    type_id: int

training_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add exercise", callback_data="add_exercise"), InlineKeyboardButton(text="End a training!", callback_data="end_training")]])

set_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add set", callback_data="add_set"), InlineKeyboardButton(text="Back to exercises", callback_data="back_to_exercises")]
])

continue_set_adding_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data="add_set_to_existing_ex"), InlineKeyboardButton(text="No", callback_data="back_to_categories")]
])

def create_categories_kb(categories: list):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        name = str(category.get("name"))
        cat_id = int(category.get("id"))
        keyboard.add(InlineKeyboardButton(text = name, callback_data=CategoryCallback(id=cat_id).pack(), style="primary"))
    keyboard.adjust(3)
    keyboard.row(InlineKeyboardButton(text="Back to training", callback_data="back_to_training", style="danger"))
    return keyboard.as_markup()

def create_exercises_kb(exercises: list):
    keyboard = InlineKeyboardBuilder()
    for exercise in exercises:
        ex_name = str(exercise.get("name"))
        ex_id = int(exercise.get("id"))
        type_id = int(exercise.get("type_id"))
        keyboard.add(InlineKeyboardButton(text = ex_name, callback_data=ExerciseCallback(id=ex_id, name=ex_name, type_id=type_id).pack(), style="primary"))
    keyboard.adjust(3)
    keyboard.row(InlineKeyboardButton(text="Back to categories", callback_data="back_to_categories", style="danger"),)
    return keyboard.as_markup()