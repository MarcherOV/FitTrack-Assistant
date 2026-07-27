import logging
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.keyboards.body_kb import (
    BodyPartCallback, skip_weight_kb, after_weight_kb, 
    create_measurements_kb, BODY_PARTS)
from src.bot.keyboards.start_kb import start_kb

router = Router()

logger = logging.getLogger(__name__)

class BodyInfoFSM(StatesGroup):
    waiting_for_weight = State()
    menu_measurements = State()
    waiting_for_part_value = State()

@router.message(F.text == "Add body info")
async def start_body_info(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BodyInfoFSM.waiting_for_weight)
    await message.answer("⚖️ **Enter your current weight in kg** (for example: *75.5*):\n\n"
                         "Or click the button below if you want to record only your body measurements.",
                         reply_markup=skip_weight_kb)
    
async def _create_base_body_info(api_client: APIClient, user_id: int, weight: float | None) -> int:
    payload = {
        "user_id": user_id,
        "weight": weight,
        "date": datetime.now().isoformat()
    }
    res = await api_client.post("/body-info/", json_data=payload)
    return res.get("id")

@router.message(BodyInfoFSM.waiting_for_weight)
async def process_weight_input(message: Message, state: FSMContext, api_client: APIClient, db_user: dict):
    try:
        weight = float(message.text.strip().replace(",", "."))
        if not(20 <= weight <=350):
            raise ValueError
    except ValueError:
        return await message.answer("⚠️ Please enter a valid number (for example: 70 or 70.5).")
    
    try:
        body_info_id = await _create_base_body_info(api_client, db_user.get("id"), weight)
        await state.update_data(body_info_id = body_info_id, measurements = {})
        await state.set_state(BodyInfoFSM.menu_measurements)

        await message.answer(f"✅ Your weight of **{weight} kg** has been successfully saved!\n\nWould you like to add your body measurements (circumferences in cm)?",
                             reply_markup=after_weight_kb)
    except HTTPStatusError as e:
        await message.answer("❌ Server save error.")


@router.callback_query(F.data == "skip_weight", BodyInfoFSM.waiting_for_weight)
async def process_skip_weight(callback: CallbackQuery, state: FSMContext, api_client: APIClient, db_user: dict):
    await callback.answer()
    try:
        body_info_id = await _create_base_body_info(api_client, db_user.get("id"), weight=None)
        await state.update_data(body_info_id = body_info_id, measurements = {})
        await state.set_state(BodyInfoFSM.menu_measurements)

        await callback.message.edit_text(
            "⏩ Weight is missing.\n\nWould you like to add your body measurements (circumferences in cm)?",
            reply_markup=after_weight_kb
        )
    except HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        return await callback.message.answer("⚠️ Something went wrong while saving the data to the server. Please try again later.")


@router.callback_query(F.data == "go_to_measurements")
async def show_measurements_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kb = create_measurements_kb(data.get("measurements", {}))

    await state.set_state(BodyInfoFSM.menu_measurements)

    await callback.message.edit_text(
        "📏 **Select a body part** to enter the measurement in centimeters:\n"
        "*(You can fill in only the required fields and then click “Save”)*",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(BodyPartCallback.filter(), BodyInfoFSM.menu_measurements)
async def select_body_part_to_measure(callback: CallbackQuery, callback_data: BodyPartCallback, state: FSMContext):
    await state.update_data(active_part_key = callback_data.part_key, active_part_name=callback_data.part_name)
    await state.set_state(BodyInfoFSM.waiting_for_part_value)

    await callback.message.edit_text(
        f"✍️ Enter the volume for **{callback_data.part_name}** in centimeters (for example: *95.5*):"
    )
    await callback.answer()


@router.message(BodyInfoFSM.waiting_for_part_value)
async def process_measurements_value(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip().replace(",", "."))
        if not(10 <= val <= 250):
            raise ValueError
    except ValueError:
        return await message.answer("⚠️ Enter a valid number (for example: 80 or 80.5).")
    
    data = await state.get_data()
    measurements: dict = data.get("measurements", {})
    part_key = data.get("active_part_key")

    measurements[part_key] = val
    await state.update_data(measurements=measurements)
    await state.set_state(BodyInfoFSM.menu_measurements)

    kb = create_measurements_kb(measurements)
    await message.answer(
        f"👍 **{data.get('active_part_name')}**: {val} cm is saved\n\nSelect the next zone or save:",
        reply_markup=kb
    )


@router.callback_query(F.data == "save_measurements_json", BodyInfoFSM.menu_measurements)
async def save_measurements_json(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    measurements_dict = data.get("measurements", {})
    body_info_id = data.get("body_info_id")

    if not measurements_dict:
        return await callback.answer("⚠️ You haven't entered any measurements!", show_alert=True)
    payload = {
        "body_info_id": body_info_id,
        "measurements": measurements_dict
    }
    await callback.answer()
    try:
        await api_client.post("/body-measurements/", json_data= payload)
        await state.clear()

        report_lines = [f"• **{BODY_PARTS[k]}**: {v} cm" for k, v in measurements_dict.items()]
        report = "\n".join(report_lines)

        await callback.message.edit_text(
            f"🎉 **All data has been successfully saved to the history!**\n\n{report}"
        )
        await callback.message.answer("What would you like to do next?", reply_markup=start_kb)
    except HTTPStatusError as e:
        await callback.message.answer("❌ An error occurred while saving the measurements on the backend.")


@router.callback_query(F.data == "finish_body_info")
async def finish_without_measurements(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👌 Your weight has been saved without any additional measurements.")
    await callback.message.answer("What would you like to do next?", reply_markup=start_kb)
    await callback.answer()