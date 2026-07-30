import logging
from datetime import datetime
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.keyboards.body_kb import (
    BodyPartCallback, BodyInfoActionCallback, BodyInfoPagCallback, skip_weight_kb, after_weight_kb, 
    create_measurements_kb, BODY_PARTS, create_body_info_action_kb, BodyInfoActionCallback,
    create_edit_body_choice_kb, create_measurements_to_edit_kb,
    create_paginated_body_kb)
from src.bot.keyboards.start_kb import start_kb
from src.exceptions.future_error import FutureDateError

router = Router()

logger = logging.getLogger(__name__)

class EditBodyInfoFSM(StatesGroup):
    choose_what_to_edit = State()
    waiting_for_new_weight = State()
    waiting_for_date = State()
    menu_measurements_to_edit = State()
    waiting_for_part_value_to_edit = State()

def format_body_page(items: list[dict], page: int, total_pages: int) -> str:
    if not items:
        return "🤷‍♂️ There are no entries on this page."

    lines = [f"🗓 **Your Body Info History (Page {page} of {total_pages}):**\n"]

    for t in items:
        date_str = datetime.fromisoformat(t["date"]).strftime("%d.%m.%Y %H:%M")
        lines.append(f"🏋️ **Body Info #{t['id']} of {date_str}**")
        weight = t["weight"]
        if weight:
            lines.append(f"Weight: {weight}")
        else:
            lines.append("No info about weight")
        measurements = t.get("measurements", [])
        if not measurements:
            lines.append("  _(empty body measurements)_")
        else:
            lines.append(f"Measurements:")
            for ms in measurements:
                ms_name = ms.get("measurements", {})
                for key, name in BODY_PARTS.items():
                    if key in ms_name:
                        btn_text = f"{name}: {ms_name[key]} cm"
                    else:
                        btn_text = f"+ {name}"
                    lines.append(btn_text)
        lines.append("")

    return "\n".join(lines)


@router.message(F.text == "See all my body info")
async def see_all_body_info(message: Message, api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    try:
        data = await api_client.get(f"/body-info/users/{user_id}/measurements/?page=1&page_size=3")  
        items = data.get("items", [])
        if not items:
            return await message.answer("🤷‍♂️ You don't have any saved body measurements yet.")
        text = format_body_page(items=items, page=data["page"], total_pages=data["total_pages"])
        kb = create_paginated_body_kb(
            items=items, page=data["page"],
            total_pages=data["total_pages"],
            has_prev=data["has_previous"],
            has_next=data["has_next"]
        )
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    except HTTPStatusError as e:
        logger.exception("Error fetching body info: {e}")
        await message.answer("❌ An error occurred while loading the history.")

@router.callback_query(BodyInfoPagCallback.filter())
async def process_training_pagination(
    callback: CallbackQuery, callback_data: BodyInfoPagCallback,
    api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    target_page = callback_data.page
    try:
        data = await api_client.get(f"/body-info/users/{user_id}/measurements/?page={target_page}&page_size=3")
        items = data.get("items", [])
        text = format_body_page(items=items, page=data["page"], total_pages=data["total_pages"])
        kb = create_paginated_body_kb(
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

@router.callback_query(BodyInfoActionCallback.filter(F.action == "delete"))
async def delete_body_info(callback: CallbackQuery, callback_data: BodyInfoActionCallback,
                          api_client: APIClient):
    body_info_id = callback_data.id
    try:
        await api_client.delete(f"/body-info/{body_info_id}")

        await callback.message.delete()

        await callback.answer("✅ Record successfully deleted!", show_alert=False)

    except HTTPStatusError as e:
        await callback.answer("❌ Failed to delete record from database.", show_alert=True)


@router.callback_query(BodyInfoActionCallback.filter(F.action == "edit"))
async def start_editing_body_info(callback: CallbackQuery, callback_data: BodyInfoActionCallback, api_client: APIClient, state: FSMContext):
    target_id = callback_data.id
    measurement_id = callback_data.measurement_id
    current_measurements = {}
    if measurement_id:
        try:
            res = await api_client.get(f"/body-measurements/{measurement_id}")
            current_measurements = res.get("measurements", {})
        except HTTPStatusError:
            logger.warning(f"Failed to load measurements for body info ID {target_id}")
    await state.update_data(editing_body_info_id = target_id)
    await state.update_data(editing_body_info_measurements = current_measurements)
    await state.update_data(editing_body_info_measurement_id = measurement_id)
    await state.set_state(EditBodyInfoFSM.choose_what_to_edit)

    await callback.message.answer(
        text="🛠 **Edit mode**\nWhat exactly would you like to update in this record?",
        reply_markup=create_edit_body_choice_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "edit_body_date")
async def ask_new_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditBodyInfoFSM.waiting_for_date)
    await callback.message.edit_text("📅 Enter a new body info date in the format `DD.MM.YYYY` (for example, `28.07.2026`):")

@router.message(EditBodyInfoFSM.waiting_for_date)
async def process_new_date(message: Message, state: FSMContext, api_client: APIClient):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        now = datetime.now()
        if dt <= now:
            dt = dt.replace(hour=now.hour, minute=now.minute, second=0)
            data = await state.get_data()
            body_info_id = data.get("editing_body_info_id")
            payload = {"date": dt.isoformat()}
            await api_client.patch(f"/body-info/{body_info_id}", json_data=payload)
            await state.clear()
            await message.answer(
                        f"✅ **Success!** The body info date has been changed to **{dt}**.\nClick *See all my trainings* to view the updated list.",
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

@router.callback_query(F.data == "edit_body_weight")
async def ask_for_new_weight(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditBodyInfoFSM.waiting_for_new_weight)

    await callback.message.edit_text(
        "✍️ **Enter the new weight in kg** (e.g., *74.5*):",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(EditBodyInfoFSM.waiting_for_new_weight)
async def process_new_weight(message: Message, state: FSMContext, api_client: APIClient):
    try:
        new_weight = float(message.text.strip().replace(",", "."))
        if not (20 <= new_weight <=350):
            raise ValueError
    except ValueError:
        return await message.answer("⚠️ Please enter a valid number (e.g., 70 or 70.5).")
    
    data = await state.get_data()
    target_id = data.get("editing_body_info_id")
    payload = {
        "weight": new_weight
    }

    try:
        await api_client.patch(f"/body-info/{target_id}", json_data= payload)
        await state.clear()

        await message.answer(
            f"✅ **Success!** Weight has been updated to **{new_weight} kg**.\n"
            "Click *See all my body info* to check the updated list.",
            reply_markup=start_kb,
            parse_mode="Markdown"
        )
    except HTTPStatusError as e:
        await message.answer("❌ Failed to update the record on the server.")
        logger.exception(f"Patch error: {e}")

@router.callback_query(F.data == "edit_body_measures")
async def show_measurements_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kb = create_measurements_to_edit_kb(data.get("editing_body_info_measurements", {}))

    await state.set_state(EditBodyInfoFSM.menu_measurements_to_edit)

    await callback.message.edit_text(
        "📏 **Select a body part** to enter the measurement in centimeters:\n"
        "*(You can fill in only the required fields and then click “Save”)*",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(BodyPartCallback.filter(), EditBodyInfoFSM.menu_measurements_to_edit)
async def select_body_part_to_edit(callback: CallbackQuery, callback_data: BodyPartCallback, state: FSMContext):
    await state.update_data(active_part_key = callback_data.part_key, active_part_name=callback_data.part_name)
    await state.set_state(EditBodyInfoFSM.waiting_for_part_value_to_edit)

    await callback.message.edit_text(
        f"✍️ Enter the volume for **{callback_data.part_name}** in centimeters (for example: *95.5*):"
    )
    await callback.answer()


@router.message(EditBodyInfoFSM.waiting_for_part_value_to_edit)
async def process_measurements_value_to_edit(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip().replace(",", "."))
        if not(10 <= val <= 250):
            raise ValueError
    except ValueError:
        return await message.answer("⚠️ Enter a valid number (for example: 80 or 80.5).")
    
    data = await state.get_data()
    measurements: dict = data.get("editing_body_info_measurements", {})
    part_key = data.get("active_part_key")

    measurements[part_key] = val
    await state.update_data(editing_body_info_measurements=measurements)
    await state.set_state(EditBodyInfoFSM.menu_measurements_to_edit)

    kb = create_measurements_to_edit_kb(measurements) 
    await message.answer(
        f"👍 **{data.get('active_part_name')}**: {val} cm is saved\n\nSelect the next zone or save:",
        reply_markup=kb
    )

@router.callback_query(F.data == "save_edited_measurements_json", EditBodyInfoFSM.menu_measurements_to_edit)
async def save_edited_measurements_json(callback: CallbackQuery, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    measurements_dict = data.get("editing_body_info_measurements", {})
    body_measurements_id = data.get("editing_body_info_measurement_id")

    if not measurements_dict:
        return await callback.answer("⚠️ You haven't entered any measurements!", show_alert=True)
    payload = {
        "measurements": measurements_dict
    }
    await callback.answer()
    try:
        if body_measurements_id:
            await api_client.patch(f"/body-measurements/{body_measurements_id}", json_data={"measurements": measurements_dict})
        else:
            body_info_id = data.get("editing_body_info_id")
            await api_client.post("/body-measurements/", json_data={
                "body_info_id": body_info_id,
                "measurements": measurements_dict
            })
        await state.clear()

        report_lines = [f"• **{BODY_PARTS[k]}**: {v} cm" for k, v in measurements_dict.items()]
        report = "\n".join(report_lines)

        await callback.message.edit_text(
            f"🎉 **All edited data has been successfully saved to the history!**\n\n{report}"
        )
        await callback.message.answer("What would you like to do next?", reply_markup=start_kb)
    except HTTPStatusError as e:
        logger.exception("Error saving edited body measurements")
        await callback.message.answer("❌ An error occurred while saving the measurements on the backend.")

@router.callback_query(F.data == "cancel_edit")
async def cancel_edit_mode(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("Edit cancelled", show_alert=False)
    await callback.message.answer("What would you like to do next?", reply_markup=start_kb)