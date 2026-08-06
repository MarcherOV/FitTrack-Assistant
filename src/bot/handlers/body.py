import logging
from datetime import datetime
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.keyboards.body_kb import (
    BodyPartCallback, skip_weight_kb, after_weight_kb,
    body_date_choice_kb, 
    create_measurements_kb, BODY_PARTS)
from src.bot.keyboards.start_kb import start_kb

router = Router()

logger = logging.getLogger(__name__)

class BodyInfoFSM(StatesGroup):
    waiting_for_date = State()
    waiting_for_weight = State()
    menu_measurements = State()
    waiting_for_part_value = State()

@router.message(F.text == "⚖️ Add body info")
async def start_body_info(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BodyInfoFSM.waiting_for_date)
    await message.answer(
        "📅 *When were these measurements taken?*\n\n"
        "Click below for today, or enter a custom date in `DD.MM.YYYY` format (for example: `28.07.2026`):",
        reply_markup=body_date_choice_kb,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "body_date_now", BodyInfoFSM.waiting_for_date)
async def process_body_date_now(callback: CallbackQuery, state: FSMContext):
    await state.update_data(body_date=datetime.now().isoformat())
    await ask_for_weight(callback.message, state, is_callback=True)
    await callback.answer()

@router.message(BodyInfoFSM.waiting_for_date)
async def process_body_date_custom(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        now = datetime.now()
        dt = dt.replace(hour=now.hour, minute=now.minute, second=0)
        
        await state.update_data(body_date=dt.isoformat())
        await ask_for_weight(message, state, is_callback=False)
    except ValueError:
        await message.answer("⚠️ Invalid format! Please enter the date as `DD.MM.YYYY` (e.g., 28.07.2026) or click the button.")

async def ask_for_weight(message: Message, state: FSMContext, is_callback: bool = False):
    await state.set_state(BodyInfoFSM.waiting_for_weight)
    text = (
        "⚖️ *Enter your weight in kg* (for example: *75.5*):\n\n"
        "Or click the button below if you want to record only your body measurements."
    )
    if is_callback:
        await message.edit_text(text, reply_markup=skip_weight_kb, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=skip_weight_kb, parse_mode="Markdown")

async def _create_base_body_info(api_client: APIClient, user_id: int, weight: float | None, date_str: str) -> int:
    payload = {
        "user_id": user_id,
        "weight": weight,
        "date": date_str
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
        data = await state.get_data()
        date_str = data.get("body_date", datetime.now().isoformat())
        body_info_id = await _create_base_body_info(api_client, db_user.get("id"), weight, date_str)
        await state.update_data(body_info_id = body_info_id, measurements = {})
        await state.set_state(BodyInfoFSM.menu_measurements)

        date_display = datetime.fromisoformat(date_str).strftime("%d.%m.%Y")
        await message.answer(
            f"✅ Weight of *{weight} kg* saved for `{date_display}`!\n\n"
            "Would you like to add your body measurements (circumferences in cm)?",
            reply_markup=after_weight_kb,
            parse_mode="Markdown"
        )
    except HTTPStatusError as e:
        await message.answer("❌ Server save error.")


@router.callback_query(F.data == "skip_weight", BodyInfoFSM.waiting_for_weight)
async def process_skip_weight(callback: CallbackQuery, state: FSMContext, api_client: APIClient, db_user: dict):
    await callback.answer()
    try:
        data = await state.get_data()
        date_str = data.get("body_date", datetime.now().isoformat())
        
        body_info_id = await _create_base_body_info(api_client, db_user.get("id"), weight=None, date_str=date_str)
        await state.update_data(body_info_id=body_info_id, measurements={})
        await state.set_state(BodyInfoFSM.menu_measurements)

        date_display = datetime.fromisoformat(date_str).strftime("%d.%m.%Y")
        await callback.message.edit_text(
            f"⏩ Weight skipped for `{date_display}`.\n\n"
            "Would you like to add your body measurements (circumferences in cm)?",
            reply_markup=after_weight_kb,
            parse_mode="Markdown"
        )
    except HTTPStatusError as e:
        logger.exception("API Error: %s", e)
        await callback.message.edit_text("⚠️ Something went wrong while saving the data to the server. Please try again later.")


@router.callback_query(F.data == "go_to_measurements")
async def show_measurements_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kb = create_measurements_kb(data.get("measurements", {}))

    await state.set_state(BodyInfoFSM.menu_measurements)

    await callback.message.edit_text(
        "📏 *Select a body part* to enter the measurement in centimeters:\n"
        "*(You can fill in only the required fields and then click “Save”)*",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(BodyPartCallback.filter(), BodyInfoFSM.menu_measurements)
async def select_body_part_to_measure(callback: CallbackQuery, callback_data: BodyPartCallback, state: FSMContext):
    await state.update_data(active_part_key = callback_data.part_key, active_part_name=callback_data.part_name)
    await state.set_state(BodyInfoFSM.waiting_for_part_value)

    await callback.message.edit_text(
        f"✍️ Enter the volume for *{callback_data.part_name}* in centimeters (for example: *95.5*):"
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
        f"👍 *{data.get('active_part_name')}*: {val} cm is saved\n\nSelect the next zone or save:",
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

        report_lines = [f"• *{BODY_PARTS[k]}*: {v} cm" for k, v in measurements_dict.items()]
        report = "\n".join(report_lines)

        await callback.message.edit_text(
            f"🎉 *All data has been successfully saved to the history!*\n\n{report}"
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