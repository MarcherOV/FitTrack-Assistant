from datetime import datetime, timedelta
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.keyboards.body_kb import *
from src.bot.keyboards.start_kb import *

router = Router()

class EditBodyInfoFSM(StatesGroup):
    choose_what_to_edit = State()
    waiting_for_new_weight = State()
    menu_measurements_to_edit = State()
    waiting_for_part_value_to_edit = State()

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
    body_info_id = await _create_base_body_info(api_client, db_user.get("id"), weight=None)
    await state.update_data(body_info_id = body_info_id, measurements = {})
    await state.set_state(BodyInfoFSM.menu_measurements)

    await callback.message.edit_text(
        "⏩ Weight is missing.\n\nWould you like to add your body measurements (circumferences in cm)?",
        reply_markup=after_weight_kb
    )
    await callback.answer()


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
    await callback.answer()


@router.callback_query(F.data == "finish_body_info")
async def finish_without_measurements(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👌 Your weight has been saved without any additional measurements.")
    await callback.message.answer("What would you like to do next?", reply_markup=start_kb)
    await callback.answer()


@router.message(F.text == "See all my body info")
async def see_all_body_info(message: Message, api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    
    try:
        records = await api_client.get(f"/body-info/users/{user_id}/measurements")
        
        if not records:
            return await message.answer("🤷‍♂️ You don't have any saved body measurements yet.")
        
        last_records = records[-5:]
        
        await message.answer("📊 **Your body measurement history:**")
        for rec in last_records:
            rec_id = rec["id"]
            date_obj = datetime.fromisoformat(rec["date"])
            date_str = date_obj.strftime("%d.%m.%Y %H:%M")
            weight = rec.get("weight")
            
            text = f"📅 **Post from {date_str}**\n"
            
            if weight is not None:
                text += f"  ⚖️ **Weight:** {weight} kg\n"
            else:
                text += "  ⚖️ **Weight:** _(not specified)_\n"
                
            measurements_list = rec.get("measurements", [])
            measurement_id = None
            if measurements_list:
                for m_item in measurements_list:
                    m_dict = m_item.get("measurements", {})
                    if m_dict:
                        text += "  📏 **Volumes:**\n"
                        for part_key, part_val in m_dict.items():
                            part_name = BODY_PARTS.get(part_key, part_key.capitalize())
                            text += f"    • {part_name}: {part_val} cm\n"
                    m_id = m_item.get("id")
                    if m_id:
                        measurement_id = m_id
            else:
                if weight is None:
                    text += "  _(empty entry)_\n"
            kb = create_body_info_action_kb(body_info_id=rec_id, measurement_id=measurement_id)
            await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    except HTTPStatusError as e:
        await message.answer("❌ An error occurred while loading the history.")
        print(f"Error fetching body info: {e}")


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
            pass
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
        print(f"Patch error: {e}")

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

    try:
        await api_client.patch(f"/body-measurements/{body_measurements_id}", json_data= payload)
        await state.clear()

        report_lines = [f"• **{BODY_PARTS[k]}**: {v} cm" for k, v in measurements_dict.items()]
        report = "\n".join(report_lines)

        await callback.message.edit_text(
            f"🎉 **All edited data has been successfully saved to the history!**\n\n{report}"
        )
        await callback.message.answer("What would you like to do next?", reply_markup=start_kb)
        await state.clear()
    except HTTPStatusError as e:
        await callback.message.answer("❌ An error occurred while saving the measurements on the backend.")
    await callback.answer()

@router.callback_query(F.data == "cancel_edit")
async def cancel_edit_mode(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("Edit cancelled", show_alert=False)
    await callback.message.answer("What would you like to do next?", reply_markup=start_kb)