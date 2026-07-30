import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError

from src.bot.services.api_client import APIClient
from src.bot.keyboards.start_kb import start_kb
from src.bot.keyboards.training_kb import (
    TrainingActionCallback, TrainingExerciseCallback, SetsExerciseCallback,
    CategoryCallback, ExerciseCallback, TrainingPagCallback, set_edit_training_kb,
    create_training_action_kb, create_edit_training_choice_kb,
    create_edit_training_choise_exercise_kb, create_edit_training_choice_set_kb,
    create_categories_kb, create_exercises_kb, continue_set_adding_edit_mode_kb,
    create_paginated_training_kb
)
from src.bot.services.exercise_type_config import EXERCISE_TYPE_CONFIG
from src.bot.services.set_collector import handle_ask_next_field, handle_process_universal_field_input
from src.exceptions.future_error import FutureDateError

logger = logging.getLogger(__name__)

router = Router()

class EditTrainingFSM(StatesGroup):
    choose_what_to_edit = State()
    waiting_for_duration = State()
    waiting_for_date = State()
    choosing_exercise_to_edit = State()
    choosing_set_to_edit = State()
    add_new_exercise = State()
    active_training = State()
    waiting_for_field_value = State()


def format_trainings_page(items: list[dict], page: int, total_pages: int) -> str:
    if not items:
        return "🤷‍♂️ There are no entries on this page."

    lines = [f"🗓 **Your Workout History (Page {page} of {total_pages}):**\n"]

    for t in items:
        date_str = datetime.fromisoformat(t["date"]).strftime("%d.%m.%Y %H:%M")
        lines.append(f"🏋️ **Workout #{t['id']} of {date_str}**")

        exercises = t.get("exercises", [])
        if not exercises:
            lines.append("  _(empty workout)_")
        else:
            for ex in exercises:
                ex_name = ex.get("exercise", {}).get("name", "Exercise")
                sets_count = len(ex.get("sets", []))
                lines.append(f"  🔹 **{ex_name}**: {sets_count} sets")
        lines.append("")

    return "\n".join(lines)

@router.message(F.text == "See all my trainings")
async def see_all_trainings(message: Message, api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    try:
        data = await api_client.get(f"/users/{user_id}/trainings/?page=1&page_size=3")
        items = data.get("items", [])
        if not items:
            return await message.answer("🤷‍♂️ You don't have any saved workouts yet.")

        text = format_trainings_page(items, page=data["page"], total_pages=data["total_pages"])
        kb = create_paginated_training_kb(
            items=items, page = data["page"],
            total_pages=data["total_pages"],
            has_prev=data["has_previous"],
            has_next=data["has_next"],
        )
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    except HTTPStatusError as e:
        logger.exception(f"Error fetching trainings: {e}")
        await message.answer("❌ An error occurred while loading your workout history.")

@router.callback_query(TrainingPagCallback.filter())
async def process_training_pagination(
    callback: CallbackQuery, callback_data: TrainingPagCallback,
    api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    target_page = callback_data.page
    try:
        data = await api_client.get(f"/users/{user_id}/trainings/?page={target_page}&page_size=3")
        items = data.get("items", [])
        text = format_trainings_page(items=items, page=data["page"], total_pages=data["total_pages"])
        kb = create_paginated_training_kb(
            items=items, page=data["page"],
            total_pages=data["total_pages"],
            has_prev=data["has_previous"],
            has_next=data["has_next"]
        )
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await callback.answer()
    except HTTPStatusError as e:
        logger.exception("Error fetching trainings page %s: %s", target_page, e)
        await callback.answer("❌ Failed to load page.", show_alert=True)

@router.callback_query(F.data == "pag_noop")
async def ignore_noop_callback(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(TrainingActionCallback.filter(F.action == "delete"))
async def delete_training(callback: CallbackQuery, callback_data: TrainingActionCallback, api_client: APIClient):
    try:
        await api_client.delete(f"/trainings/{callback_data.id}")
        await callback.message.delete()
        await callback.answer("✅ Record successfully deleted!", show_alert=False)
    except HTTPStatusError:
        await callback.answer("❌ Failed to delete record from database.", show_alert=True)


@router.callback_query(TrainingActionCallback.filter(F.action == "edit"))
async def start_editing_training(callback: CallbackQuery, callback_data: TrainingActionCallback, state: FSMContext, api_client: APIClient):
    try:
        training_data = await api_client.get(f"/trainings/{callback_data.id}")
    except HTTPStatusError:
        return await callback.answer("❌ The workout could not be loaded.", show_alert=True)

    await state.update_data(editing_training_id=callback_data.id, editing_training_data=training_data)
    await state.set_state(EditTrainingFSM.choose_what_to_edit)
    await callback.message.answer(
        "🛠 **Editing a Workout**\nWhat exactly do you want to change?",
        reply_markup=create_edit_training_choice_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "tr_edit_date", EditTrainingFSM.choose_what_to_edit)
async def ask_new_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTrainingFSM.waiting_for_date)
    await callback.message.edit_text("📅 Enter a new workout date in the format `DD.MM.YYYY` (for example, `28.07.2026`):")

@router.message(EditTrainingFSM.waiting_for_date)
async def process_new_date(message: Message, state: FSMContext, api_client: APIClient):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        now = datetime.now()
        if dt <= now:
            dt = dt.replace(hour=now.hour, minute=now.minute, second=0)
            data = await state.get_data()
            training_id = data.get("editing_training_id")
            payload = {"date": dt.isoformat()}
            await api_client.patch(f"/trainings/{training_id}", json_data=payload)
            await state.clear()
            await message.answer(
                        f"✅ **Success!** The workout date has been changed to **{dt}**.\nClick *See all my trainings* to view the updated list.",
                        reply_markup=start_kb
                    )
        else:
            raise FutureDateError
            
    except ValueError:
        await message.answer("⚠️ Incorrect format! Enter the date as `DD.MM.YYYY` (for example, 28.07.2026) or click the button.")
    except FutureDateError:
        await message.answer("⚠️ Please enter a date that is no later than today's date")
    except HTTPStatusError as e:
        logger.exception(f"Error patching duration: {e}")
        await message.answer("❌ Error updating the workout on the server.")

@router.callback_query(F.data == "tr_edit_duration", EditTrainingFSM.choose_what_to_edit)
async def ask_new_duration(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTrainingFSM.waiting_for_duration)
    await callback.message.edit_text("⏱ **Enter a new workout duration in minutes** (for example: *60* or *45*):", parse_mode="Markdown")


@router.message(EditTrainingFSM.waiting_for_duration)
async def process_new_duration(message: Message, state: FSMContext, api_client: APIClient):
    try:
        minutes = int(message.text.strip())
        if minutes <= 0: raise ValueError
    except ValueError:
        return await message.answer("⚠️ Please enter a positive integer (minutes, for example: 60).")

    data = await state.get_data()
    training_id = data.get("editing_training_id")
    payload = {"duration_time": int(timedelta(minutes=minutes).total_seconds())}

    try:
        await api_client.patch(f"/trainings/{training_id}", json_data=payload)
        await state.clear()
        await message.answer(
            f"✅ **Success!** The workout duration has been changed to **{minutes} min**.\nClick *See all my trainings* to view the updated list.",
            reply_markup=start_kb
        )
    except HTTPStatusError as e:
        logger.exception(f"Error patching duration: {e}")
        await message.answer("❌ Error updating the workout on the server.")


@router.callback_query(F.data == "tr_edit_sets")
async def ask_to_choose_exercise_to_edit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    training_exercises_data = data.get("editing_training_data", {}).get("exercises", [])
    await state.set_state(EditTrainingFSM.choosing_exercise_to_edit)
    await callback.message.edit_text(
        "Choose which exercises to edit:",
        reply_markup=create_edit_training_choise_exercise_kb(training_exercises_data),
        parse_mode="Markdown"
    )


@router.callback_query(TrainingExerciseCallback.filter())
async def ask_to_choose_set_to_edit(callback: CallbackQuery, callback_data: TrainingExerciseCallback, state: FSMContext, api_client: APIClient):
    try:
        set_data = await api_client.get(f"/training-exercises/{callback_data.id}/sets")
        await state.update_data(
            exercise_name=callback_data.exercise_name,
            training_exercise_id=callback_data.id,
            type_id=callback_data.type_id
        )
        await callback.message.edit_text(
            f"Choose which set to edit for {callback_data.exercise_name}",
            reply_markup=create_edit_training_choice_set_kb(set_data, callback_data.type_id),
            parse_mode="Markdown"
        )
    except HTTPStatusError as e:
        logger.exception(f"Error fetching sets: {e}")
        await callback.answer("❌ An error occurred while loading your sets.")


async def ask_next_field(message: Message, state: FSMContext, api_client: APIClient):
    """Delegates to the shared set collector service."""
    await handle_ask_next_field(message, state, api_client, EditTrainingFSM.waiting_for_field_value, EditTrainingFSM.active_training, continue_set_adding_edit_mode_kb)


@router.message(EditTrainingFSM.waiting_for_field_value)
async def process_universal_field_input(message: Message, state: FSMContext, api_client: APIClient):
    is_valid = await handle_process_universal_field_input(message, state, api_client)
    if is_valid:
        await ask_next_field(message, state, api_client)


@router.callback_query(SetsExerciseCallback.filter())
async def start_editing_existing_set(callback: CallbackQuery, callback_data: SetsExerciseCallback, api_client: APIClient, state: FSMContext):
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(callback_data.exercise_type_id, ["weight", "repetitions"]).copy()
    await state.update_data(set_id=callback_data.id, remaining_fields=fields_to_fill, action="edit", current_set_payload={})
    await state.set_state(EditTrainingFSM.active_training)
    await callback.answer()
    await ask_next_field(callback.message, state, api_client)


@router.callback_query(F.data == "add_set_to_exercise")
async def start_adding_new_set_to_existing_ex(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    data = await state.get_data()
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(data.get("type_id"), ["weight", "repetitions"]).copy()
    await state.update_data(remaining_fields=fields_to_fill, action="add", current_set_payload={}, current_set_number = None)
    await callback.answer()
    await ask_next_field(callback.message, state, api_client)


@router.callback_query(F.data == "add_first_set_in_edit_mode")
async def start_adding_exercise_and_first_set(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    """Triggered after picking a NEW exercise to add to an existing workout."""
    data = await state.get_data()
    training_id = data["editing_training_id"]
    exercise_id = data["exercise_id"]
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(data.get("type_id"), ["weight", "repetitions"]).copy()

    try:
        res = await api_client.post(f"/trainings/{training_id}/exercises", json_data={"exercise_id": exercise_id, "sets": []})
        await state.update_data(training_exercise_id=res.get("id"), remaining_fields=fields_to_fill, action="add", current_set_payload={}, current_set_number=1)
        await callback.answer()
        await ask_next_field(callback.message, state, api_client)
    except HTTPStatusError as e:
        logger.exception(f"Error creating training exercise: {e}")
        await callback.answer("❌ Failed to add exercise. Try again.", show_alert=True)


@router.callback_query(F.data == "add_another_set_in_edit_mode")
async def start_adding_subsequent_set(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    """Triggered when user clicks 'Yes' to add another set to the newly added exercise."""
    data = await state.get_data()
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(data.get("type_id"), ["weight", "repetitions"]).copy()
    await state.update_data(remaining_fields=fields_to_fill, action="add", current_set_payload={})
    await callback.answer()
    await ask_next_field(callback.message, state, api_client)


@router.callback_query(F.data == "add_new_exercise")
async def add_exercise_edit_mode(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    try:
        categories = await api_client.get(endpoint="/categories/")
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await callback.answer("⚠️ Something went wrong while loading categories. Please try again.", show_alert=True)
        return
    if not categories:
        return await callback.message.answer("Sorry, there are no categories available.")
    await state.set_state(EditTrainingFSM.add_new_exercise)
    await callback.message.edit_text("Choose the category of exercise:", reply_markup=create_categories_kb(categories))


@router.callback_query(CategoryCallback.filter(), EditTrainingFSM.add_new_exercise)
async def select_category(callback: CallbackQuery, callback_data: CategoryCallback, api_client: APIClient):
    try:
        exercises = await api_client.get(f"/categories/{callback_data.id}/exercises")
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        await callback.answer("⚠️ Something went wrong while loading exercises. Please try again.", show_alert=True)
        return
    if not exercises:
        return await callback.message.answer("Sorry, there are no exercises for this category.")
    await callback.message.edit_text("Choose the exercise:", reply_markup=create_exercises_kb(exercises))
    await callback.answer()


@router.callback_query(ExerciseCallback.filter(), EditTrainingFSM.add_new_exercise)
async def select_exercise(callback: CallbackQuery, callback_data: ExerciseCallback, state: FSMContext):
    await state.update_data(exercise_id=callback_data.id, type_id=callback_data.type_id)
    await callback.message.edit_text(text=callback_data.name, reply_markup=set_edit_training_kb)
    await callback.answer()


@router.callback_query(F.data == "back_to_ex_options")
async def back_to_exercise_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await ask_to_choose_exercise_to_edit(callback, state)


@router.callback_query(F.data == "back_to_edit_options")
async def back_to_training_edit_menu(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    await start_editing_training(callback, TrainingActionCallback(action="edit", id=data.get("editing_training_id")), state, api_client)


@router.callback_query(F.data == "cancel_tr_edit")
async def cancel_training_editing(callback: CallbackQuery, state: FSMContext, api_client: APIClient, db_user: dict):
    await state.clear()
    await callback.answer()
    await see_all_trainings(callback.message, api_client, db_user)


@router.callback_query(F.data == "back_to_see_all_trainings")
async def back_to_see_all_trainings(callback: CallbackQuery, state: FSMContext, api_client: APIClient, db_user: dict):
    await state.clear()
    await callback.answer()
    await see_all_trainings(callback.message, api_client, db_user)