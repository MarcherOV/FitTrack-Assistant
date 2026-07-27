import json
import logging
from datetime import datetime, timedelta
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.services.set_collector import handle_process_universal_field_input
from src.bot.keyboards.start_kb import start_kb
from src.bot.keyboards.training_kb import (CategoryCallback, ExerciseCallback, training_kb, set_kb,
                                            continue_set_adding_kb, create_categories_kb, create_exercises_kb)

from src.bot.services.exercise_type_config import EXERCISE_TYPE_CONFIG, FIELD_PROMPTS


class WorkoutFSM(StatesGroup):
    active_training = State()
    waiting_for_field_value = State()


router = Router()

logger = logging.getLogger(__name__)

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
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await message.answer("⚠️ Something went wrong while saving the data to the server. Please try again later.")


@router.callback_query(F.data == "add_exercise")
async def add_exercise(callback: CallbackQuery, api_client: APIClient, db_user: dict):
    try:
        categories = await api_client.get(endpoint="/categories/")
        if not categories:
            return await callback.message.answer("Sorry, there is no category")
        categories_kb = create_categories_kb(categories)
        
        return await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await callback.message.answer("⚠️ Something went wrong while saving the data to the server. Please try again later.")



@router.callback_query(CategoryCallback.filter(), WorkoutFSM.active_training)
async def select_category(callback: CallbackQuery, callback_data: CategoryCallback, api_client: APIClient):
    category_id = callback_data.id
    try:
        exercises = await api_client.get(f"/categories/{category_id}/exercises")
        if not exercises:
            return await callback.message.answer("Sorry, there is no exercise for this category")
        
        exercises_kb = create_exercises_kb(exercises)
        await callback.message.edit_text(text="Choose the exercise:", reply_markup=exercises_kb)
        await callback.answer()
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await callback.message.answer("⚠️ Something went wrong while saving the data to the server. Please try again later.")



@router.callback_query(ExerciseCallback.filter(), WorkoutFSM.active_training)
async def select_exercise(callback: CallbackQuery, callback_data: ExerciseCallback, api_client, state: FSMContext):
    exercise_id = callback_data.id
    type_id = callback_data.type_id
    await state.update_data(exercise_id=exercise_id, type_id=type_id)
    await callback.message.edit_text(text=callback_data.name, reply_markup=set_kb)
    await callback.answer()


@router.callback_query(F.data == "add_set", WorkoutFSM.active_training)
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
        await state.update_data(training_exercise_id=data.get("id"),
        remaining_fields=fields_to_fill,
        current_set_payload={},
        current_set_number=1
        )
        await callback.answer()
        await ask_next_field(callback.message, state, api_client)
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await callback.message.answer("⚠️ Something went wrong while saving the data to the server. Please try again later.")


async def ask_next_field(message: Message, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    remaining_fields: list = data.get("remaining_fields", [])
    
    if remaining_fields:
        next_field = remaining_fields[0]
        await state.update_data(current_field=next_field)
        await state.set_state(WorkoutFSM.waiting_for_field_value)

        prompt = FIELD_PROMPTS.get(next_field, f"Enter the value for {next_field}:")
        return await message.answer(prompt)

    training_exercise_id = data.get("training_exercise_id")
    collected_payload = data.get("current_set_payload", {})
    
    set_number = data.get("current_set_number", 1)
    collected_payload["set_number"] = set_number

    try:
        data_res = await api_client.post(
            f"/training-exercises/{training_exercise_id}/sets", 
            json_data=collected_payload
        )
        set_id = data_res.get("id")
        
        await state.update_data(current_set_number=set_number + 1)
        await state.set_state(WorkoutFSM.active_training)

        return await message.answer(
            f"✅ Set #{set_number} (ID: {set_id}) has been successfully added!\n"
            "Would you like to add another set?",
            reply_markup=continue_set_adding_kb
        )
    except HTTPStatusError as e:
        logger.error(f"API Error during set saving: {e.response.status_code} - {e.response.text}")
        await state.set_state(WorkoutFSM.active_training)
        return await message.answer(
            "⚠️ Failed to save the set to the server. Please try adding it again.",
            reply_markup=continue_set_adding_kb
        )


@router.message(WorkoutFSM.waiting_for_field_value)
async def process_universal_field_input(message: Message, state: FSMContext, api_client: APIClient):
    await handle_process_universal_field_input(message, state, api_client)
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
    try:
        categories = await api_client.get(endpoint="/categories/")
        categories_kb = create_categories_kb(categories)
        await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)
        await callback.answer()
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await callback.message.answer("⚠️ Something went wrong while loading categories. Please try again.")


@router.callback_query(F.data == "back_to_training")
async def back_to_training(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    training_id = data.get("training_id", "unknown")
    await callback.message.edit_text(f"Ok! The training has id {training_id}", reply_markup=training_kb)
    await callback.answer()


@router.callback_query(F.data == "end_training")
async def back_to_start_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("What would you like to do next?")
    await callback.answer()