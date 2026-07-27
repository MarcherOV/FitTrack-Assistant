import logging
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.services.exercise_type_config import FIELD_PROMPTS

logger = logging.getLogger(__name__)

async def handle_ask_next_field(
    message: Message, 
    state: FSMContext, 
    api_client: APIClient, 
    next_state,
    idle_state,
    success_keyboard
):
    data = await state.get_data()
    remaining_fields: list = data.get("remaining_fields", [])
    
    if remaining_fields:
        next_field = remaining_fields[0]
        await state.update_data(current_field=next_field)
        await state.set_state(next_state)
        
        prompt = FIELD_PROMPTS.get(next_field, f"Enter the value for {next_field}:")
        return await message.answer(prompt)

    training_exercise_id = data.get("training_exercise_id")
    collected_payload = data.get("current_set_payload", {})
    action = data.get("action", "add") # "add" or "edit"

    try:
        if action == "edit":
            set_id = data.get("set_id")
            await api_client.patch(f"/sets/{set_id}", json_data=collected_payload)
            await state.set_state(idle_state)
            return await message.answer("✅ Set successfully updated!", reply_markup=success_keyboard)
            
        elif action == "add":
            if "current_set_number" in data:
                set_number = data["current_set_number"]
            else:
                sets_ex = await api_client.get(f"/training-exercises/{training_exercise_id}/sets")
                set_number = len(sets_ex) + 1 if sets_ex else 1
            collected_payload["set_number"] = set_number
            
            data_res = await api_client.post(f"/training-exercises/{training_exercise_id}/sets", json_data=collected_payload)
            await state.update_data(current_set_number=set_number + 1)
            await state.set_state(idle_state)
            set_id = data_res.get("id")
            
            return await message.answer(
                f"✅ Set #{set_number} (ID: {set_id}) has been successfully added!\nWould you like to add another set?",
                reply_markup=success_keyboard
            )
    except HTTPStatusError as e:
        logger.exception("Error saving set data")
        await message.answer("❌ Server error occurred while saving the set.")


async def handle_process_universal_field_input(message: Message, state: FSMContext, api_client: APIClient):
    data = await state.get_data()
    current_field = data.get("current_field")
    remaining_fields: list = data.get("remaining_fields", [])
    collected_payload: dict = data.get("current_set_payload", {})

    text = message.text.strip().replace(",", ".")
        
    try:
        if current_field in ["repetitions", "calories_burned"]:
            value = int(text)
            if value <= 0:
                raise ValueError("Value must be greater than 0")
        elif current_field in ["weight", "distance", "processing_time"]:
            value = float(text)
            if value < 0:
                raise ValueError("Value cannot be negative")
        else:
            value = text
    except ValueError:
        await message.answer(f"⚠️ Please enter a valid positive number for “{current_field}”.")
        return False
    
    collected_payload[current_field] = value
    if current_field in remaining_fields:
        remaining_fields.remove(current_field)
    
    await state.update_data(
        remaining_fields=remaining_fields,
        current_set_payload=collected_payload
    )
    return True
    
        