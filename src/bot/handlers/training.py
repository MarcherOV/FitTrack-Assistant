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
                                            continue_set_adding_kb, create_categories_kb, create_exercises_kb,
                                            date_choice_kb, duration_choice_kb, types_kb)

from src.bot.services.exercise_type_config import EXERCISE_TYPE_CONFIG, FIELD_PROMPTS


class WorkoutFSM(StatesGroup):
    waiting_for_date = State()
    waiting_for_duration = State()
    active_training = State()
    waiting_for_field_value = State()
    waiting_for_final_duration = State()

    waiting_for_new_exercise_name = State()
    waiting_for_new_exercise_type = State()


router = Router()

logger = logging.getLogger(__name__)

@router.message(F.text == "💪 Add training")
async def start_add_training(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(WorkoutFSM.waiting_for_date)
    await message.answer(
        "📅 *When did the practice take place?*\n\n"
        "Click the button below if you're working out today, or enter a date in the format `DD.MM.YYYY` (for example, `28.07.2026`):",
        reply_markup=date_choice_kb,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "date_now", WorkoutFSM.waiting_for_date)
async def process_date_now(callback: CallbackQuery, state: FSMContext):
    await state.update_data(workout_date=datetime.now().isoformat())
    await ask_for_duration(callback.message, state, is_callback=True)
    await callback.answer()

@router.message(WorkoutFSM.waiting_for_date)
async def process_date_custom(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        now = datetime.now()
        dt = dt.replace(hour=now.hour, minute=now.minute, second=0)
        
        await state.update_data(workout_date=dt.isoformat())
        await ask_for_duration(message, state, is_callback=False)
    except ValueError:
        await message.answer("⚠️ Incorrect format! Enter the date as `DD.MM.YYYY` (for example, 28.07.2026) or click the button.")

async def ask_for_duration(message: Message, state: FSMContext, is_callback: bool = False):
    await state.set_state(WorkoutFSM.waiting_for_duration)
    text = (
        "⏱ *How many minutes did the workout last?*\n\n"
        "Enter a number (for example, `60` or `45`), or click the button below to record the time after you finish your exercises:"
    )
    if is_callback:
        await message.edit_text(text, reply_markup=duration_choice_kb, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=duration_choice_kb, parse_mode="Markdown")

@router.callback_query(F.data == "duration_skip", WorkoutFSM.waiting_for_duration)
async def process_duration_skip(callback: CallbackQuery, state: FSMContext, api_client: APIClient, db_user: dict):
    await create_training_record(callback, state, api_client, db_user.get("id"), duration_minutes=0)
    await callback.answer()

@router.message(WorkoutFSM.waiting_for_duration)
async def process_duration_custom(message: Message, state: FSMContext, api_client: APIClient, db_user: dict):
    try:
        minutes = int(message.text.strip())
        if minutes < 0: raise ValueError
        await create_training_record(message, state, api_client, db_user.get("id"), duration_minutes=minutes)
    except ValueError:
        await message.answer("⚠️ Enter a positive integer (for example, 60):")

async def create_training_record(event, state: FSMContext, api_client: APIClient, user_id: int, duration_minutes: int):
    data = await state.get_data()
    date_str = data.get("workout_date", datetime.now().isoformat())
    duration_seconds = int(timedelta(minutes=duration_minutes).total_seconds())
    
    payload = {
        "user_id": user_id,
        "date": date_str,
        "duration_time": duration_seconds,
        "exercises": []
    }
    
    try:
        res = await api_client.post("/trainings/", json_data=payload)
        training_id = res.get("id")
        
        await state.update_data(training_id=training_id, duration_minutes=duration_minutes)
        await state.set_state(WorkoutFSM.active_training)
        
        date_display = datetime.fromisoformat(date_str).strftime("%d.%m.%Y")
        text = (
            f"✅ *Workout #{training_id} successfully created!*\n"
            f"📅 Date: `{date_display}` | ⏱ Duration: `{duration_minutes} min`\n\n"
            "Now add the first exercise:"
        )
        
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text, reply_markup=training_kb, parse_mode="Markdown")
        else:
            await event.answer(text, reply_markup=training_kb, parse_mode="Markdown")
            
    except HTTPStatusError as e:
        logger.exception("Error creating training: %s", e)
        msg = "⚠️ An error occurred while saving the workout to the server."
        if isinstance(event, CallbackQuery): await event.message.answer(msg)
        else: await event.answer(msg)

@router.callback_query(F.data == "add_exercise")
async def add_exercise(callback: CallbackQuery, api_client: APIClient, db_user: dict):
    telegram_id = callback.from_user.id
    request_headers = {"X-Telegram-Id": str(telegram_id)}
    try:
        categories = await api_client.get(endpoint="/categories/", headers=request_headers)
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
    telegram_id = callback.from_user.id
    request_headers = {"X-Telegram-Id": str(telegram_id)}
    try:
        exercises = await api_client.get(f"/categories/{category_id}/exercises", headers=request_headers)
        
        exercises = exercises or [] 
        
        exercises_kb = create_exercises_kb(exercises, category_id)
        await callback.message.edit_text(text="Choose the exercise or create a new one:", reply_markup=exercises_kb)
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

@router.callback_query(F.data.startswith("create_ex_"), WorkoutFSM.active_training)
async def process_create_custom_exercise(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(new_ex_category_id=category_id)
    
    await state.set_state(WorkoutFSM.waiting_for_new_exercise_name)
    await callback.message.edit_text("📝 *Enter the name of your new exercise:*", parse_mode="Markdown")
    await callback.answer()


@router.message(WorkoutFSM.waiting_for_new_exercise_name)
async def get_custom_exercise_name(message: Message, state: FSMContext):
    await state.update_data(new_ex_name=message.text.strip())
    await state.set_state(WorkoutFSM.waiting_for_new_exercise_type)
    await message.answer("⚙️ *Select the type of your exercise:*", reply_markup=types_kb, parse_mode="Markdown")


@router.callback_query(F.data.startswith("new_ex_type_"), WorkoutFSM.waiting_for_new_exercise_type)
async def create_and_select_custom_exercise(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    type_id = int(callback.data.split("_")[3])
    data = await state.get_data()
    
    category_id = data.get("new_ex_category_id")
    name = data.get("new_ex_name")

    telegram_id = callback.from_user.id
    request_headers = {"X-Telegram-Id": str(telegram_id)}

    payload = {
        "name": name,
        "category_id": category_id,
        "type_id": type_id
    }
    
    try:
        res = await api_client.post("/exercises/", json_data=payload, headers=request_headers)
        exercise_id = res.get("id")
        
        await state.update_data(exercise_id=exercise_id, type_id=type_id)
        await state.set_state(WorkoutFSM.active_training)
        
        await callback.message.edit_text(
            f"✅ Exercise *{name}* successfully created and selected! You can now add sets.", 
            reply_markup=set_kb, 
            parse_mode="Markdown"
        )
        await callback.answer()
    except HTTPStatusError as e:
        logger.error(f"API Error creating exercise: {e}")
        await state.set_state(WorkoutFSM.active_training)
        await callback.message.answer("⚠️ Failed to create the exercise. Please try again.")

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
    telegram_id = callback.from_user.id
    request_headers = {"X-Telegram-Id": str(telegram_id)}
    try:
        categories = await api_client.get(endpoint="/categories/", headers=request_headers)
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
async def back_to_start_menu(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    duration = data.get("duration_minutes", 0)
    training_id = data.get("training_id")

    if duration > 0 or not training_id:
        await state.clear()
        await callback.message.edit_text("🎉 *The training session was a success!*\nWhat do we do next?", parse_mode="Markdown")
        await callback.message.answer("Select an action from the menu:", reply_markup=start_kb)
        await callback.answer()
        return

    await state.set_state(WorkoutFSM.waiting_for_final_duration)
    await callback.message.edit_text(
        "🏁 *The workout is over!*\n\n⏱ How many minutes did it last in total? (Enter a number, for example, `55`):",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(WorkoutFSM.waiting_for_final_duration)
async def process_final_duration(message: Message, state: FSMContext, api_client: APIClient):
    try:
        minutes = int(message.text.strip())
        if minutes <= 0: raise ValueError
    except ValueError:
        return await message.answer("⚠️ Enter the correct number of minutes (a positive integer):")
        
    data = await state.get_data()
    training_id = data.get("training_id")
    payload = {"duration_time": int(timedelta(minutes=minutes).total_seconds())}
    
    try:
        await api_client.patch(f"/trainings/{training_id}", json_data=payload)
        await state.clear()
        await message.answer(f"🎉 *Recorded: {minutes} min!* The workout has been saved in your history.", reply_markup=start_kb)
    except HTTPStatusError:
        logger.exception("Failed to patch final duration")
        await state.clear()
        await message.answer("⚠️ The workout is complete, but the time could not be updated on the server.", reply_markup=start_kb)