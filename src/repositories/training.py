from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Sequence
from src.models.training import Training, TrainingExercise, SetsExercise
from src.schemas.training import TrainingPOST, TrainingUPDATE, TrainingExercisePOST, TrainingExerciseUPDATE, SetsExercisePOST, SetsExerciseUPDATE


class TrainingRepository:

    @staticmethod
    async def get_training(session: AsyncSession, training_id: int) -> Training | None:
        query = select(Training).where(Training.id == training_id).options(
            selectinload(Training.exercises).selectinload(TrainingExercise.sets)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_training_by_user_id(session: AsyncSession, user_id: int) -> Sequence[Training]:
        query = select(Training).where(Training.user_id == user_id).options(
            selectinload(Training.exercises).selectinload(TrainingExercise.sets)
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_training(session: AsyncSession, training_data: TrainingPOST) -> Training:
        training = Training(
            user_id = training_data.user_id,
            date = training_data.date,
            duration_time = training_data.duration_time
        )

        for exercise_data in training_data.exercises:
            training_exercise = TrainingExercise(
                exercise_id = exercise_data.exercise_id
            )
            for set_data in exercise_data.sets:
                set_exercise = SetsExercise(
                    set_number = set_data.set_number,
                    repetitions = set_data.repetitions,
                    weight = set_data.weight,
                    distance = set_data.distance,
                    processing_time = set_data.processing_time,
                    calories_burned = set_data.calories_burned
                )
                training_exercise.sets.append(set_exercise)
            training.exercises.append(training_exercise)
        
        session.add(training)
        await session.commit()
        return await TrainingRepository.get_training(session, training.id)
    
    @staticmethod
    async def delete_training(session: AsyncSession, training_id: int) -> bool:
        training = await TrainingRepository.get_training(session, training_id)
        if training:
            await session.delete(training)
            await session.commit()
            return True
        return False
    
    @staticmethod
    async def update_training(session: AsyncSession, training_id: int, training_data: TrainingUPDATE) -> Training | None:
        training = await TrainingRepository.get_training(session, training_id)
        if not training:
            return None
        update_dict = training_data.model_dump(exclude_unset=True, exclude={"exercises"})
        for key, value in update_dict.items():
            setattr(training, key, value)
        
        await session.commit()
        await session.refresh(training)
        return training

class TrainingExerciseRepository:

    @staticmethod
    async def get_training_exercise(session: AsyncSession, training_exercise_id: int) -> TrainingExercise | None:
        query = select(TrainingExercise).where(TrainingExercise.id == training_exercise_id).options(selectinload(TrainingExercise.sets))

        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_training_exercises(session: AsyncSession, training_id: int) -> Sequence[TrainingExercise]:
        query = select(TrainingExercise).where(TrainingExercise.training_id == training_id).options(selectinload(TrainingExercise.sets))
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_training_exercise(session: AsyncSession, training_id: int, exercise_data: TrainingExercisePOST):
        training_exercise = TrainingExercise(
            training_id = training_id,
            exercise_id = exercise_data.exercise_id
        )

        for set_data in exercise_data.sets:
            set_exercise = SetsExercise(
                set_number = set_data.set_number,
                repetitions = set_data.repetitions,
                weight = set_data.weight,
                distance = set_data.distance,
                processing_time = set_data.processing_time,
                calories_burned = set_data.calories_burned
            )
            training_exercise.sets.append(set_exercise)
        
        session.add(training_exercise)
        await session.commit()
        return await TrainingExerciseRepository.get_training_exercise(session, training_exercise.id)
    
    @staticmethod
    async def update_training_exercise(session: AsyncSession, training_exercise_id: int, exercise_data: TrainingExerciseUPDATE) -> TrainingExercise | None:
        training_exercise = await TrainingExerciseRepository.get_training_exercise(session, training_exercise_id)
        if not training_exercise:
            return None
        update_dict = exercise_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(training_exercise, key, value)
        
        await session.commit()
        await session.refresh(training_exercise)
        return training_exercise
    
    @staticmethod
    async def delete_training_exercise(session: AsyncSession, training_exercise_id: int) -> bool:
        training_exercise = await session.get(TrainingExercise, training_exercise_id)
        if not training_exercise:
            return False
        await session.delete(training_exercise)
        await session.commit()
        return True
    
class SetsExerciseRepository:

    @staticmethod
    async def get_set_exercise(session: AsyncSession, set_exercise_id: int) -> SetsExercise | None:
        return await session.get(SetsExercise, set_exercise_id)
    
    @staticmethod
    async def get_all_sets_to_exercise(session: AsyncSession, training_exercise_id: int) -> Sequence[SetsExercise]:
        query = select(SetsExercise).where(SetsExercise.training_exercise_id == training_exercise_id).order_by(SetsExercise.set_number)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_set_exercise(session: AsyncSession, training_exercise_id: int, set_data: SetsExercisePOST):
        set_exercise = SetsExercise(
            training_exercise_id = training_exercise_id,
            set_number = set_data.set_number,
            repetitions = set_data.repetitions,
            weight = set_data.weight,
            distance = set_data.distance,
            processing_time = set_data.processing_time,
            calories_burned = set_data.calories_burned
        )
        session.add(set_exercise)
        await session.commit()
        await session.refresh(set_exercise)
        return set_exercise
    
    @staticmethod
    async def update_set_exercise(session: AsyncSession, set_exercise_id: int, set_data: SetsExerciseUPDATE) -> SetsExercise | None:
        set_exercise = await SetsExerciseRepository.get_set_exercise(session, set_exercise_id)
        if not set_exercise:
            return None
        update_dict = set_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(set_exercise, key, value)
        
        await session.commit()
        await session.refresh(set_exercise)
        return set_exercise
    
    @staticmethod
    async def delete_set_exercise(session: AsyncSession, set_exercise_id: int) -> bool:
        set_exercise = await SetsExerciseRepository.get_set_exercise(session, set_exercise_id)
        if not set_exercise:
            return False
        await session.delete(set_exercise)
        await session.commit()
        return True
    
