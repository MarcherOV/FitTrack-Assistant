import json
import asyncio
from sqlalchemy.exc import IntegrityError

from src.db.database import async_session
from src.repositories.exercises import ExerciseRepository
from src.schemas.exercises import ExercisePOST 

async def seed_exercises():
    try:
        with open("exercises.json", "r", encoding="utf-8") as file:
            raw_exercises = json.load(file)
    except FileNotFoundError:
        print("❌ The file “exercises.json” was not found!")
        return

    print(f"⏳ Let's start the import {len(raw_exercises)} exercises...")

    async with async_session() as session:
        added_count = 0
        skipped_count = 0

        for item in raw_exercises:
            exercise_data = ExercisePOST(
                name=item["name"],
                category_id=item["category_id"],
                type_id=item["type_id"]
            )

            try:
                await ExerciseRepository.create_exercise(session, exercise_data)
                added_count += 1
                
            except IntegrityError:
                skipped_count += 1
                
        print(f"✅ Import completed!")
        print(f"➕ Added new: {added_count}")
        print(f"⏭ Skipped (duplicates/errors): {skipped_count}")

if __name__ == "__main__":
    asyncio.run(seed_exercises())