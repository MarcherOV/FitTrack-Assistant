from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from src.bot.services.exercise_type_config import *

class CategoryCallback(CallbackData, prefix="cat"):
    id: int


class ExerciseCallback(CallbackData, prefix="ex"):
    id: int
    name: str
    type_id: int


class TrainingExerciseCallback(CallbackData, prefix = "training_ex"):
    id: int
    exercise_name: str
    type_id: int


class SetsExerciseCallback(CallbackData, prefix = "sets_exercise"):
    id: int
    exercise_type_id: int


class TrainingActionCallback(CallbackData, prefix="training"):
    action: str #edit or delete
    id: int


training_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add exercise", callback_data="add_exercise"), InlineKeyboardButton(text="End a training!", callback_data="end_training")]])


set_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add set", callback_data="add_set"), InlineKeyboardButton(text="Back to exercises", callback_data="back_to_exercises")]
])


set_edit_training_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add set", callback_data="add_set_in_edit_mode"), InlineKeyboardButton(text="Back to exercises", callback_data="back_to_see_all_trainings")]
])


continue_set_adding_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data="add_set_in_edit_mode"), InlineKeyboardButton(text="No", callback_data="back_to_categories")]
])


continue_set_adding_edit_mode_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data="add_set_in_edit_mode"), InlineKeyboardButton(text="No", callback_data="back_to_see_all_trainings")]
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


def create_training_action_kb(training_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text = "✏️ Edit", callback_data=TrainingActionCallback(action = "edit", id = training_id).pack()))
    keyboard.add(InlineKeyboardButton(text = "🗑 Delete", callback_data=TrainingActionCallback(action = "delete", id = training_id).pack()))
    return keyboard.adjust(2).as_markup()


def create_edit_training_choice_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⏱ Change the duration", callback_data="tr_edit_duration"))
    keyboard.add(InlineKeyboardButton(text="🏋️ Edit exercises/sets", callback_data="tr_edit_sets"))
    keyboard.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_tr_edit"))
    return keyboard.adjust(1).as_markup()


def create_edit_training_choise_exercise_kb(training_exercises):
    keyboard = InlineKeyboardBuilder()
    for training_exercise in training_exercises:
        training_ex_id = training_exercise.get("id")
        exercise = training_exercise.get("exercise")
        if exercise:
            exercise_name = str(exercise.get("name"))
            type_id = exercise.get("type_id")
        keyboard.add(InlineKeyboardButton(text=exercise_name.capitalize(), callback_data=TrainingExerciseCallback(id=training_ex_id, exercise_name=exercise_name, type_id=type_id).pack()))

    keyboard.row(InlineKeyboardButton(text="Add new exercise", callback_data="add_new_exercise", style="primary"),)
    keyboard.row(InlineKeyboardButton(text="Back to edit options", callback_data="back_to_edit_options", style="danger"),)
    return keyboard.as_markup()



def create_edit_training_choise_set_kb(sets_exercise, exercise_type_id):
    keyboard = InlineKeyboardBuilder()
    text_inf = INFO_TEXT_ABOUT_SET.get(exercise_type_id)
    for set in sets_exercise:
        set_id = set.get("id")
        set_number = set.get("set_number", 0)
        if exercise_type_id == 1:
            set_weight = set.get("weight", 0)
            set_reps = set.get("repetitions", 0)
            keyboard.add(InlineKeyboardButton(text = text_inf.format(set_number = set_number, set_weight = set_weight, set_reps = set_reps), callback_data=SetsExerciseCallback(id = set_id, exercise_type_id = exercise_type_id).pack()))
        elif exercise_type_id == 2:
            set_distance = set.get("distance", 0)
            set_processing_time = set.get("processing_time", 0)
            set_calories_burned = set.get("calories_burned", 0)
            keyboard.add(InlineKeyboardButton(text = text_inf.format(set_number = set_number, set_distance = set_distance, set_processing_time = set_processing_time, set_calories_burned = set_calories_burned), callback_data=SetsExerciseCallback(id = set_id, exercise_type_id = exercise_type_id).pack()))
        elif exercise_type_id == 3:
            set_reps = set.get("repetitions", 0)
            set_weight = set.get("weight", 0)
            keyboard.add(InlineKeyboardButton(text = text_inf.format(set_number = set_number, set_reps = set_reps, set_weight = set_weight), callback_data=SetsExerciseCallback(id = set_id, exercise_type_id = exercise_type_id).pack()))
        elif exercise_type_id == 4:
            processing_time = set.get("processing_time", 0)
            set_weight = set.get("weight", 0)
            keyboard.add(InlineKeyboardButton(text = text_inf.format(set_number = set_number, processing_time = processing_time, set_weight = set_weight), callback_data=SetsExerciseCallback(id = set_id, exercise_type_id = exercise_type_id).pack()))

    keyboard.row(InlineKeyboardButton(text="Add new set", callback_data="add_set_to_exercise", style="primary"),)
    keyboard.row(InlineKeyboardButton(text="Back to exercise options", callback_data="back_to_ex_options", style="danger"),)
    return keyboard.as_markup() 