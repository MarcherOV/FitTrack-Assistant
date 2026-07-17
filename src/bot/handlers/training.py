import json
from datetime import datetime, timedelta
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient

from src.bot.keyboards.training_kb import CategoryCallback, training_kb, create_categories_kb, create_exercises_kb

router = Router()

training_id = None

@router.message(F.text == "Add training")
async def add_training(message: Message, api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    date = datetime.now().isoformat()
    payload = {"user_id": user_id,
               "date": date,
               "duration_time": int(timedelta().total_seconds()),
               "exercises": []}
    try:
        data = await api_client.post("/trainings/", json_data=payload)
        training_id = data.get("id")
        return await message.answer(f"Ok! The training has id {training_id}", reply_markup=training_kb)
    except HTTPStatusError as e:
        print(f"Error: {e}")

@router.callback_query(F.data == "add_exercise")
async def add_exercise(callback: CallbackQuery, api_client: APIClient, db_user: dict):
    categories = await api_client.get(endpoint="/categories/")
    if not categories:
        return await callback.message.answer("Sorry, there is no category")
    print(categories)
    categories_kb = create_categories_kb(categories)
    return await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)

@router.callback_query(CategoryCallback.filter())
async def select_category(callback: CallbackQuery, callback_data: CategoryCallback, api_client: APIClient):
    category_id = callback_data.id
    exercises = await api_client.get(f"/categories/{category_id}/exercises")
    if not exercises:
        return await callback.message.answer("Sorry, there is no exercise for this category")
    print(exercises)
    exercises_kb = create_exercises_kb(exercises)
    await callback.message.edit_text(text="Choose the exercise:", reply_markup=exercises_kb)
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, api_client: APIClient):
    categories = await api_client.get(endpoint="/categories/")
    categories_kb = create_categories_kb(categories)
    await callback.message.edit_text("Choose the category of exercise:", reply_markup=categories_kb)
    await callback.answer()

@router.callback_query(F.data == "back_to_training")
async def back_to_training(callback: CallbackQuery, api_client: APIClient):
    await callback.message.edit_text("Ok! The training has id", reply_markup=training_kb)
    await callback.answer()