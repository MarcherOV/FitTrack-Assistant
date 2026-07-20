import json
from datetime import datetime, timedelta
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient

from src.bot.keyboards.training_kb import (CategoryCallback, ExerciseCallback, training_kb, set_kb,
                                            continue_set_adding_kb, create_categories_kb, create_exercises_kb,)
from src.bot.services.exercise_type_config import EXERCISE_TYPE_CONFIG, FIELD_PROMPTS

class WorkoutFSM(StatesGroup):
    active_training = State()
    waiting_for_field_value = State()

router = Router()

@router.message(F.text == "Add training")
async def add_training(message: Message, api_client: APIClient, db_user: dict, state: FSMContext):
    user_id = db_user.get("id")
    date = datetime.now().isoformat()
    payload = {"user_id": user_id,
               "date": date,
               "duration_time": int(timedelta().total_seconds()),
               "exercises": []}
    try:
        data = await api_client.post("/trainings/", json_data=payload)
        await state.update_data(training_id=data.get("id"))
        await state.set_state(WorkoutFSM.active_training)
        training_id = data.get("id")
        return await message.answer(f"Ok! The training has id {training_id}", reply_markup=training_kb)
    except HTTPStatusError as e:
        print(f"Error: {e}")

@router.callback_query(F.data == "add_exercise")
async def add_exercise(callback: CallbackQuery, api_client: APIClient, db_user: dict):
    categories = await api_client.get(endpoint="/categories/")
    if not categories:
        return await callback.message.answer("Sorry, there is no category")
    print(categories)
    categories_kb = create_categories_kb(categories)
    return await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)

@router.callback_query(CategoryCallback.filter())
async def select_category(callback: CallbackQuery, callback_data: CategoryCallback, api_client: APIClient):
    category_id = callback_data.id
    exercises = await api_client.get(f"/categories/{category_id}/exercises")
    if not exercises:
        return await callback.message.answer("Sorry, there is no exercise for this category")
    print(exercises)
    exercises_kb = create_exercises_kb(exercises)
    await callback.message.edit_text(text="Choose the exercise:", reply_markup=exercises_kb)
    await callback.answer()

@router.callback_query(ExerciseCallback.filter())
async def select_exercise(callback: CallbackQuery, callback_data: ExerciseCallback, api_client, state: FSMContext):
    exercise_id = callback_data.id
    type_id = callback_data.type_id
    await state.update_data(exercise_id=exercise_id)
    await state.update_data(type_id=type_id)
    await callback.message.edit_text(text=callback_data.name, reply_markup=set_kb)
    await callback.answer()

@router.callback_query(F.data == "add_set")
async def start_adding_set(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    data_workout = await state.get_data()
    training_id = data_workout["training_id"]
    exercise_id = data_workout["exercise_id"]
    type_id = data_workout.get("type_id")
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(type_id, ["weight", "repetitions"]).copy()
    payload = {
        "exercise_id": exercise_id,
        "sets": []
    }
    try:
        data = await api_client.post(f"/trainings/{training_id}/exercises", json_data=payload)
        await state.update_data(training_exercise_id=data.get("id"))
        await state.update_data(
        remaining_fields=fields_to_fill,
        current_set_payload={}
        )
        await callback.answer()
        await ask_next_field(callback.message, state, api_client)
    except HTTPStatusError as e:
        print(f"Error: {e}")

async def ask_next_field(message: Message, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    remaining_fields: list = data.get("remaining_fields", [])
    if remaining_fields:
        next_field = remaining_fields[0]
        await state.update_data(current_field = next_field)
        await state.set_state(WorkoutFSM.waiting_for_field_value)

        promt = FIELD_PROMPTS.get(next_field, f"Enter the value for {next_field}:")
        return await message.answer(promt)
    
    training_exercise_id = data.get("training_exercise_id")
    collected_payload = data.get("current_set_payload", {})

    sets_ex = await api_client.get(f"/training-exercises/{training_exercise_id}/sets")
    set_number = len(sets_ex) + 1 if sets_ex else 1

    collected_payload["set_number"] = set_number

    data_res = await api_client.post(f"/training-exercises/{training_exercise_id}/sets", json_data=collected_payload)

    set_id = data_res.get("id")

    await state.set_state(WorkoutFSM.active_training)

    return await message.answer(
        f"✅ Set #{set_number} (ID: {set_id}) has been successfully added!\nWould you like to add another set?",
        reply_markup=continue_set_adding_kb
    )

@router.message(WorkoutFSM.waiting_for_field_value)
async def process_universal_field_input(message: Message, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    current_field = data.get("current_field")
    remaining_fields: list = data.get("remaining_fields", [])
    collected_payload: dict = data.get("current_set_payload", {})

    text = message.text.strip().replace(",", ".")

    try:
        if current_field in ["repetitions", "calories_burned"]:
            value = int(text)
        elif current_field in ["weight", "distance", "processing_time"]:
            value = float(text)
        else:
            value = text
    except ValueError:
        return await message.answer(f"⚠️ Please enter a valid number for the “{current_field}” field.")
    
    collected_payload[current_field] = value

    if current_field in remaining_fields:
        remaining_fields.remove(current_field)

    await state.update_data(
        remaining_fields=remaining_fields,
        current_set_payload = collected_payload
    )

    await ask_next_field(message, state, api_client)

@router.callback_query(F.data == "add_set_to_existing_ex")
async def add_set(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    data_workout = await state.get_data()
    type_id = data_workout.get("type_id")
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(type_id, ["weight", "repetitions"]).copy()
    await state.update_data(
        remaining_fields=fields_to_fill,
        current_set_payload={}
    )

    await callback.answer()
    await ask_next_field(callback.message, state, api_client)

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, api_client: APIClient):
    categories = await api_client.get(endpoint="/categories/")
    categories_kb = create_categories_kb(categories)
    await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)
    await callback.answer()

@router.callback_query(F.data == "back_to_training")
async def back_to_training(callback: CallbackQuery, api_client: APIClient):
    await callback.message.edit_text("Ok! The training has id", reply_markup=training_kb)
    await callback.answer()
