from datetime import datetime, timedelta
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient
from src.bot.keyboards.start_kb import *

router = Router()

@router.message(F.text == "See all my trainings")
async def see_all_trainings(message: Message, api_client: APIClient, db_user: dict):
    user_id = db_user.get("id")
    try:
        trainings = await api_client.get(f"/users/{user_id}/trainings/")
        if not trainings:
            return await message.answer("🤷‍♂️ You don't have any saved workouts yet.")
        
        last_trainings = trainings[-5:]
        response_text = "🗓 **Your most recent workouts:**\n\n"
        
        for t in last_trainings:
            date_obj = datetime.fromisoformat(t["date"])
            date_str = date_obj.strftime("%d.%m.%Y %H:%M")
            
            response_text += f"🏋️ **Workout by {date_str}**\n"
            
            if not t.get("exercises"):
                response_text += "  _(empty workout)_\n\n"
                continue
                
            for ex in t["exercises"]:
                ex_name = ex.get("exercise", {}).get("name", f"Exercise #{ex['exercise_id']}")
                response_text += f"  🔹 **{ex_name}**\n"
                
                for s in ex.get("sets", []):
                    set_details = []
                    if s.get("weight"): set_details.append(f"{s['weight']} kg")
                    if s.get("repetitions"): set_details.append(f"{s['repetitions']} reps")
                    if s.get("processing_time"): set_details.append(f"{s['processing_time']} sec")
                    if s.get("distance"): set_details.append(f"{s['distance']} km")
                    
                    details_str = ", ".join(set_details) if set_details else "no data available"
                    response_text += f"    Set {s['set_number']}: {details_str}\n"
            
            response_text += "\n"
            
        await message.answer(response_text, parse_mode="Markdown")

    except HTTPStatusError as e:
        await message.answer("❌ An error occurred while loading your workout history.")
        print(f"Error fetching trainings: {e}")
