from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.schemas.training import TrainingGET ,TrainingPOST, TrainingUPDATE, TrainingExerciseGET, TrainingExercisePOST, TrainingExerciseUPDATE, SetsExerciseGET, SetsExercisePOST, SetsExerciseUPDATE
from src.repositories.training import TrainingRepository, TrainingExerciseRepository, SetsExerciseRepository

router_training = APIRouter(prefix="/trainings", tags=["Trainings"])

@router_training.get("/{training_id}", response_model=TrainingGET, status_code=status.HTTP_200_OK)
async def get_training(training_id: int, session: AsyncSession = Depends(get_session)):
    training = await TrainingRepository.get_training(session, training_id)
    if not training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    return training

@router_training.get("/{training_id}/exercises", response_model=list[TrainingExerciseGET], status_code=status.HTTP_200_OK)
async def get_training_exercises(training_id: int, session: AsyncSession = Depends(get_session)):
    exercises = await TrainingExerciseRepository.get_all_training_exercises(session, training_id)
    return exercises

@router_training.post("/{training_id}/exercises", response_model=TrainingExerciseGET, status_code=status.HTTP_201_CREATED)
async def create_training_exercise(training_id: int, training_exercise_data: TrainingExercisePOST, session: AsyncSession = Depends(get_session)):
    try:
        training_exercise = await TrainingExerciseRepository.create_training_exercise(session, training_id, training_exercise_data)
        return training_exercise
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID or Exercise ID does not exist.")

@router_training.post("/", response_model=TrainingGET, status_code=status.HTTP_201_CREATED)
async def create_training(training_data: TrainingPOST, session: AsyncSession = Depends(get_session)):
    training = await TrainingRepository.create_training(session, training_data)
    return training

@router_training.patch("/{training_id}", response_model=TrainingGET, status_code=status.HTTP_200_OK)
async def update_training(training_id: int, training_data: TrainingUPDATE, session: AsyncSession = Depends(get_session)):
    updated_training = await TrainingRepository.update_training(session, training_id, training_data)
    if not updated_training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    return updated_training

@router_training.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training(training_id: int, session: AsyncSession = Depends(get_session)):
    training_deleted = await TrainingRepository.delete_training(session, training_id)
    if not training_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    return None

router_training_exercises = APIRouter(prefix="/training-exercises", tags=["Training Exercises"])

@router_training_exercises.get("/{training_exercise_id}", response_model=TrainingExerciseGET, status_code=status.HTTP_200_OK)
async def get_training_exercise(training_exercise_id: int, session: AsyncSession = Depends(get_session)):
    training_exercise = await TrainingExerciseRepository.get_training_exercise(session, training_exercise_id)
    if not training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    return training_exercise

@router_training_exercises.get("/{training_exercise_id}/sets", response_model=list[SetsExerciseGET], status_code=status.HTTP_200_OK)
async def get_sets_exercise(training_exercise_id: int, session: AsyncSession = Depends(get_session)):
    sets_exercise = await SetsExerciseRepository.get_all_sets_to_exercise(session, training_exercise_id)
    return sets_exercise

@router_training_exercises.post("/{training_exercise_id}/sets", response_model=SetsExerciseGET, status_code=status.HTTP_201_CREATED)
async def create_set_exercise(training_exercise_id: int, set_data: SetsExercisePOST, session: AsyncSession = Depends(get_session)):
    set_exercise = await SetsExerciseRepository.create_set_exercise(session, training_exercise_id, set_data)
    return set_exercise

@router_training_exercises.patch("/{training_exercise_id}", response_model=TrainingExerciseGET, status_code=status.HTTP_200_OK)
async def update_training_exercise(training_exercise_id: int, training_exercise_data: TrainingExerciseUPDATE,session: AsyncSession = Depends(get_session)):
    updated_training_exercise = await TrainingExerciseRepository.update_training_exercise(session, training_exercise_id, training_exercise_data)
    if not updated_training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    return updated_training_exercise

@router_training_exercises.delete("/{training_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_exercise(training_exercise_id: int, session: AsyncSession = Depends(get_session)):
    training_exercise_deleted = await TrainingExerciseRepository.delete_training_exercise(session, training_exercise_id)
    if not training_exercise_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    return None

router_sets = APIRouter(prefix="/sets", tags=["Sets"])

@router_sets.get("/{set_exercise_id}", response_model=SetsExerciseGET, status_code=status.HTTP_200_OK)
async def get_set(set_exercise_id: int, session: AsyncSession = Depends(get_session)):
    set_exercise = await SetsExerciseRepository.get_set_exercise(session, set_exercise_id)
    if not set_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The set to exercise does not exist")
    return set_exercise

@router_sets.patch("/{set_exercise_id}", response_model=SetsExerciseGET, status_code=status.HTTP_200_OK)
async def update_set(set_exercise_id: int, set_data: SetsExerciseUPDATE, session: AsyncSession = Depends(get_session)):
    updated_set_exercise = await SetsExerciseRepository.update_set_exercise(session, set_exercise_id, set_data)
    if not updated_set_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The set to exercise does not exist") 
    return updated_set_exercise

@router_sets.delete("/{set_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(set_exercise_id: int, session: AsyncSession = Depends(get_session)):
    set_exercise_deleted = await SetsExerciseRepository.delete_set_exercise(session, set_exercise_id)
    if not set_exercise_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The set to exercise does not exist")
    return None