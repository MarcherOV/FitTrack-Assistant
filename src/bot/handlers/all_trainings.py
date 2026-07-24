from datetime import datetime, timedelta
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.keyboards.start_kb import *
from src.bot.keyboards.training_kb import *

router = Router()

class EditTrainingFSM(StatesGroup):
    choose_what_to_edit = State()
    waiting_for_duration = State()

    choosing_exercise_to_edit = State()
    choosing_set_to_edit = State()

    add_new_exercise = State()
    active_training = State()

    waiting_for_field_value = State()


@router.message(F.text == "See all my trainings")
async def see_all_trainings(message: Message, api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    try:
        trainings = await api_client.get(f"/users/{user_id}/trainings/")
        if not trainings:
            return await message.answer("🤷‍♂️ You don't have any saved workouts yet.")

        last_trainings = trainings[-5:]
        await message.answer("🗓 **Your most recent workouts:**")

        for t in last_trainings:
            training_id = t["id"]

            date_obj = datetime.fromisoformat(t["date"])
            date_str = date_obj.strftime("%d.%m.%Y %H:%M")

            text = f"🏋️ **Workout by {date_str}**\n"
           
            if not t.get("exercises"):
                text += "  _(empty workout)_\n\n"
            else:
                for ex in t["exercises"]:
                    ex_name = ex.get("exercise", {}).get("name", f"Exercise #{ex['exercise_id']}")
                    text += f"  🔹 **{ex_name}**\n"

                    for s in ex.get("sets", []):
                        set_details = []
                        if s.get("weight"): set_details.append(f"{s['weight']} kg")
                        if s.get("repetitions"): set_details.append(f"{s['repetitions']} reps")
                        if s.get("processing_time"): set_details.append(f"{s['processing_time']} sec")
                        if s.get("distance"): set_details.append(f"{s['distance']} km")
                        details_str = ", ".join(set_details) if set_details else "no data available"
                        text += f"    Set {s['set_number']}: {details_str}\n"

            kb = create_training_action_kb(training_id = training_id)
            await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    except HTTPStatusError as e:
        await message.answer("❌ An error occurred while loading your workout history.")
        print(f"Error fetching trainings: {e}")


@router.callback_query(TrainingActionCallback.filter(F.action == "delete"))
async def delete_training(callback: CallbackQuery, callback_data: TrainingActionCallback,
                          api_client: APIClient):

    training_id = callback_data.id
    try:
        await api_client.delete(f"/trainings/{training_id}")
        await callback.message.delete()
        await callback.answer("✅ Record successfully deleted!", show_alert=False)
    except HTTPStatusError as e:
        await callback.answer("❌ Failed to delete record from database.", show_alert=True)



@router.callback_query(TrainingActionCallback.filter(F.action == "edit"))
async def start_editing_training(callback: CallbackQuery, callback_data: TrainingActionCallback,
                                 state: FSMContext, api_client: APIClient):
    if callback_data:
        training_id = callback_data.id
    else:
        pass

    try:
        training_data = await api_client.get(f"/trainings/{training_id}")
    except HTTPStatusError:
        return await callback.answer("❌ The workout could not be loaded.", show_alert=True)

    await state.update_data(editing_training_id = training_id,
                            editing_training_data = training_data)

    await state.set_state(EditTrainingFSM.choose_what_to_edit)
    await callback.message.answer(
        "🛠 **Editing a Workout**\nWhat exactly do you want to change?",
        reply_markup=create_edit_training_choice_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "tr_edit_duration", EditTrainingFSM.choose_what_to_edit)
async def ask_new_duration(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditTrainingFSM.waiting_for_duration)
    await callback.message.edit_text(
        "⏱ **Enter a new workout duration in minutes** (for example: *60* or *45*):",
        parse_mode="Markdown"
    )


@router.message(EditTrainingFSM.waiting_for_duration)
async def process_new_duration(message: Message, state: FSMContext, api_client: APIClient):
    try:
        minutes = int(message.text.strip())
        if minutes <=0: raise ValueError
    except ValueError:
        return await message.answer("⚠️ Please enter a positive integer (minutes, for example: 60).")

    data = await state.get_data()
    training_id = data.get("editing_training_id")

    duration_seconds = int(timedelta(minutes=minutes).total_seconds())

    payload ={
        "duration_time": duration_seconds
    }

    try:
        await api_client.patch(f"/trainings/{training_id}", json_data = payload)
        await state.clear()

        await message.answer(
            f"✅ **Success!** The workout duration has been changed to **{minutes} min**.\n"
            "Click *See all my trainings* to view the updated list.",
            reply_markup=start_kb
        )
    except HTTPStatusError as e:
        await message.answer(
            "❌ Error updating the workout on the server."
        )
        print(f"Error patching duration {e}")


@router.callback_query(F.data == "tr_edit_sets")
async def ask_to_choose_exercise_to_edit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    training_data = data.get("editing_training_data")
    training_exercises_data = training_data.get("exercises")
    await state.set_state(EditTrainingFSM.choosing_exercise_to_edit)
    await callback.message.edit_text("Choose which exercises to edit:",
                                     reply_markup=create_edit_training_choise_exercise_kb(training_exercises_data),
                                     parse_mode="Markdown")


@router.callback_query(TrainingExerciseCallback.filter())
async def ask_to_choose_set_to_edit(callback: CallbackQuery, callback_data: TrainingExerciseCallback, state: FSMContext, api_client: APIClient):
    training_exercise_id = callback_data.id
    exercise_type_id = callback_data.type_id
    exercise_name = callback_data.exercise_name
    try:
        set_data = await api_client.get(f"/training-exercises/{training_exercise_id}/sets")
        await state.update_data(exercise_name = exercise_name,
                                training_exercise_id = training_exercise_id,
                                type_id = exercise_type_id)
        await callback.message.edit_text(
            f"Choose which set to edit for {exercise_name}",
            reply_markup=create_edit_training_choise_set_kb(set_data, exercise_type_id),
            parse_mode="Markdown"
        )

    except HTTPStatusError as e:
        await callback.answer("❌ An error occurred while loading your set exercise.")
        print(f"Error fetching set: {e}")


@router.callback_query(SetsExerciseCallback.filter())
async def start_adding_set(callback: CallbackQuery, callback_data: SetsExerciseCallback, api_client: APIClient, state: FSMContext):
    set_id = callback_data.id
    type_id = callback_data.exercise_type_id
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(type_id, ["weight", "repetitions"]).copy()
    await state.update_data(
    set_id = set_id,
    remaining_fields=fields_to_fill,
    action="edit",
    current_set_payload={}
    )
    await state.set_state(EditTrainingFSM.active_training)
    await callback.answer()
    await ask_next_field(callback.message, state, api_client)


async def ask_next_field(message: Message, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    remaining_fields: list = data.get("remaining_fields", [])
    if remaining_fields:
        next_field = remaining_fields[0]
        await state.update_data(current_field = next_field)
        await state.set_state(EditTrainingFSM.waiting_for_field_value)
        promt = FIELD_PROMPTS.get(next_field, f"Enter the value for {next_field}:")
        return await message.answer(promt)

    set_id = data.get("set_id")
    collected_payload = data.get("current_set_payload", {})
    action = data.get("action")
    if action == "edit":
        data_res = await api_client.patch(f"/sets/{set_id}", json_data=collected_payload)

    exercise_name = data.get("exercise_name")
    training_exercise_id = data.get("training_exercise_id")
    if action == "add":
        sets_ex = await api_client.get(f"/training-exercises/{training_exercise_id}/sets")
        set_number = len(sets_ex) + 1 if sets_ex else 1

        collected_payload["set_number"] = set_number
        data_res =  await api_client.post(f"/training-exercises/{training_exercise_id}/sets", json_data=collected_payload)

    type_id = data.get("type_id")
    try:
        set_data = await api_client.get(f"/training-exercises/{training_exercise_id}/sets")
        return await message.answer(
            f"✅ Set has been successfully added!\nWould you like to edit another set for {exercise_name}?",
            reply_markup=create_edit_training_choise_set_kb(set_data, type_id),
        )
    except HTTPStatusError as e:
        await message.answer("❌ An error occurred while loading your set exercise.")
        print(f"Error fetching set: {e}")


@router.message(EditTrainingFSM.waiting_for_field_value)
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


@router.callback_query(F.data == "add_set_to_exercise")
async def start_adding_set(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    data_workout = await state.get_data()
    type_id = data_workout.get("type_id")
    fields_to_fill = EXERCISE_TYPE_CONFIG.get(type_id, ["weight", "repetitions"]).copy()
    await state.update_data(
    remaining_fields=fields_to_fill,
    action="add",
    current_set_payload={}
    )

    await callback.answer()
    await ask_next_field(callback.message, state, api_client)


@router.callback_query(F.data == "back_to_ex_options")
async def back_to_ex_options(callback: CallbackQuery, state: FSMContext):
    await ask_to_choose_exercise_to_edit(callback, state)


@router.callback_query(F.data == "back_to_edit_options")
async def back_to_ex_options(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    training_id = data.get("editing_training_id")
    callback_data = TrainingActionCallback(action="edit", id=training_id)
    await start_editing_training(callback = callback, state =state, callback_data = callback_data, api_client = api_client)


@router.callback_query(F.data == "cancel_tr_edit")
async def back_to_ex_options(callback: CallbackQuery, api_client: APIClient, db_user: dict):
    await see_all_trainings(callback.message, api_client, db_user)


@router.callback_query(F.data == "add_new_exercise")
async def add_exercise(callback: CallbackQuery, api_client: APIClient, state: FSMContext, db_user: dict):
    categories = await api_client.get(endpoint="/categories/")
    if not categories:
        return await callback.message.answer("Sorry, there is no category")

    print(categories)
    categories_kb = create_categories_kb(categories)
    await state.set_state(EditTrainingFSM.add_new_exercise)
    return await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)


@router.callback_query(CategoryCallback.filter(), EditTrainingFSM.add_new_exercise)
async def select_category(callback: CallbackQuery, callback_data: CategoryCallback, api_client: APIClient):
    category_id = callback_data.id
    exercises = await api_client.get(f"/categories/{category_id}/exercises")
    if not exercises:
        return await callback.message.answer("Sorry, there is no exercise for this category")

    print(exercises)
    exercises_kb = create_exercises_kb(exercises)
    await callback.message.edit_text(text="Choose the exercise:", reply_markup=exercises_kb)
    await callback.answer()


@router.callback_query(ExerciseCallback.filter(), EditTrainingFSM.add_new_exercise)
async def select_exercise(callback: CallbackQuery, callback_data: ExerciseCallback, api_client, state: FSMContext):
    exercise_id = callback_data.id
    type_id = callback_data.type_id
    await state.update_data(exercise_id=exercise_id)
    await state.update_data(type_id=type_id)
    await callback.message.edit_text(text=callback_data.name, reply_markup=set_edit_training_kb)
    await callback.answer()


@router.callback_query(F.data == "add_set_in_edit_mode")
async def start_adding_set(callback: CallbackQuery, api_client: APIClient, state: FSMContext):
    data_workout = await state.get_data()
    training_id = data_workout["editing_training_id"]
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
        await state.set_state(EditTrainingFSM.waiting_for_field_value)
        promt = FIELD_PROMPTS.get(next_field, f"Enter the value for {next_field}:")

        return await message.answer(promt)

    training_exercise_id = data.get("training_exercise_id")
    collected_payload = data.get("current_set_payload", {})

    sets_ex = await api_client.get(f"/training-exercises/{training_exercise_id}/sets")
    set_number = len(sets_ex) + 1 if sets_ex else 1

    collected_payload["set_number"] = set_number
    data_res = await api_client.post(f"/training-exercises/{training_exercise_id}/sets", json_data=collected_payload)

    set_id = data_res.get("id")

    await state.set_state(EditTrainingFSM.active_training)
    return await message.answer(
        f"✅ Set #{set_number} (ID: {set_id}) has been successfully added!\nWould you like to add another set?",
        reply_markup=continue_set_adding_edit_mode_kb
    )


@router.message(EditTrainingFSM.waiting_for_field_value)
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


@router.callback_query(F.data == "add_set_in_edit_mode")
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


@router.callback_query(F.data == "back_to_see_all_trainings")
async def back_to_see_all_trainings(callback: CallbackQuery, api_client: APIClient, db_user: dict):
    await see_all_trainings(message = callback.message, api_client = api_client, db_user = db_user)