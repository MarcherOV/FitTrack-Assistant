from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class BodyPartCallback(CallbackData, prefix="bpart"):
    part_key: str
    part_name: str

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