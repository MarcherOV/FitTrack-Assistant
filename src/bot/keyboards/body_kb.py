from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class BodyPartCallback(CallbackData, prefix="bpart"):
    part_key: str
    part_name: str

class BodyInfoActionCallback(CallbackData, prefix="body_info"):
    action: str #edit or delete
    id: int
    measurement_id: Optional[int] = None

skip_weight_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➡️ Skip (no weight)", callback_data="skip_weight")]
])

after_weight_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📏 Add body measurements (cm)", callback_data="go_to_measurements")],
    [InlineKeyboardButton(text="🏁 Let's wrap it up here", callback_data="finish_body_info")]
])

BODY_PARTS = {
    "chest": "Chest",
    "waist": "Waist",
    "hips": "Hips",
    "biceps": "Biceps",
    "thigh": "Thigh",
    "calf": "Calf"
}

def create_measurements_kb(current_measurements: dict):
    keyboard = InlineKeyboardBuilder()

    for key, name in BODY_PARTS.items():
        if key in current_measurements:
            btn_text = f"{name}: {current_measurements[key]} cm"
        else:
            btn_text = f"+ {name}"

        keyboard.add(InlineKeyboardButton(
            text=btn_text,
            callback_data=BodyPartCallback(part_key=key, part_name=name).pack()
        ))

    keyboard.adjust(2)

    keyboard.row(InlineKeyboardButton(
        text = "💾 Save measurements to the database",
        callback_data= "save_measurements_json",
    ))
    return keyboard.as_markup()

def create_measurements_to_edit_kb(current_measurements: dict):
    keyboard = InlineKeyboardBuilder()

    for key, name in BODY_PARTS.items():
        if key in current_measurements:
            btn_text = f"{name}: {current_measurements[key]} cm"
        else:
            btn_text = f"+ {name}"

        keyboard.add(InlineKeyboardButton(
            text=btn_text,
            callback_data=BodyPartCallback(part_key=key, part_name=name).pack()
        ))

    keyboard.adjust(2)

    keyboard.row(InlineKeyboardButton(
        text = "💾 Save edited measurements to the database",
        callback_data= "save_edited_measurements_json",
    ))
    return keyboard.as_markup()

def create_body_info_action_kb(body_info_id: int, measurement_id: int | None):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text = "✏️ Edit", callback_data=BodyInfoActionCallback(action = "edit", id = body_info_id, measurement_id = measurement_id).pack()))
    keyboard.add(InlineKeyboardButton(text = "🗑 Delete", callback_data=BodyInfoActionCallback(action = "delete", id = body_info_id).pack()))
    
    return keyboard.adjust(2).as_markup()

def create_edit_body_choice_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⚖️ Edit Weight", callback_data="edit_body_weight"))
    keyboard.add(InlineKeyboardButton(text="📏 Edit Measurements", callback_data="edit_body_measures"))
    keyboard.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_edit"))
    return keyboard.adjust(1).as_markup()

