from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.users import User
from src.models.training import Training
from src.db.database import get_session
from src.api.dependencies import get_current_user
from src.schemas.training import TrainingGET ,TrainingPOST, TrainingUPDATE, TrainingExerciseGET, TrainingExercisePOST, TrainingExerciseUPDATE, SetsExerciseGET, SetsExercisePOST, SetsExerciseUPDATE
from src.repositories.training import TrainingRepository, TrainingExerciseRepository, SetsExerciseRepository

def _check_owner(trainig: Training, current_user: User):
    if trainig.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this training"
        )

router_training = APIRouter(prefix="/trainings", tags=["Trainings"])

@router_training.get("/{training_id}", response_model=TrainingGET, status_code=status.HTTP_200_OK)
async def get_training(training_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training = await TrainingRepository.get_training(session, training_id)
    if not training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    _check_owner(training, current_user)
    return training

@router_training.get("/{training_id}/exercises", response_model=list[TrainingExerciseGET], status_code=status.HTTP_200_OK)
async def get_training_exercises(training_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training = await TrainingRepository.get_training(session, training_id)
    if not training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    _check_owner(training, current_user)
    return await TrainingExerciseRepository.get_all_training_exercises(session, training_id)

@router_training.post("/{training_id}/exercises", response_model=TrainingExerciseGET, status_code=status.HTTP_201_CREATED)
async def create_training_exercise(training_id: int, training_exercise_data: TrainingExercisePOST, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training = await TrainingRepository.get_training(session, training_id)
    if not training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    _check_owner(training, current_user)
    try:
        training_exercise = await TrainingExerciseRepository.create_training_exercise(session, training_id, training_exercise_data)
        return training_exercise
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID or Exercise ID does not exist.")

@router_training.post("/", response_model=TrainingGET, status_code=status.HTTP_201_CREATED)
async def create_training(training_data: TrainingPOST, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training_data.user_id = current_user.id
    return await TrainingRepository.create_training(session, training_data)

@router_training.patch("/{training_id}", response_model=TrainingGET, status_code=status.HTTP_200_OK)
async def update_training(training_id: int, training_data: TrainingUPDATE, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training = await TrainingRepository.get_training(session, training_id)
    if not training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    _check_owner(training, current_user)
    return await TrainingRepository.update_training(session, training_id, training_data)

@router_training.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training(training_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training = await TrainingRepository.get_training(session, training_id)
    if not training:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training does not exist")
    _check_owner(training, current_user)
    await TrainingRepository.delete_training(session, training_id)
    return None

router_training_exercises = APIRouter(prefix="/training-exercises", tags=["Training Exercises"])

@router_training_exercises.get("/{training_exercise_id}", response_model=TrainingExerciseGET, status_code=status.HTTP_200_OK)
async def get_training_exercise(training_exercise_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training_exercise = await TrainingExerciseRepository.get_training_exercise_with_owner(session, training_exercise_id)
    if not training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    _check_owner(training_exercise.training, current_user)
    return training_exercise

@router_training_exercises.get("/{training_exercise_id}/sets", response_model=list[SetsExerciseGET], status_code=status.HTTP_200_OK)
async def get_sets_exercise(training_exercise_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training_exercise = await TrainingExerciseRepository.get_training_exercise_with_owner(session, training_exercise_id)
    if not training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    _check_owner(training_exercise.training, current_user)
    return await SetsExerciseRepository.get_all_sets_to_exercise(session, training_exercise_id)

@router_training_exercises.post("/{training_exercise_id}/sets", response_model=SetsExerciseGET, status_code=status.HTTP_201_CREATED)
async def create_set_exercise(training_exercise_id: int, set_data: SetsExercisePOST, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training_exercise = await TrainingExerciseRepository.get_training_exercise_with_owner(session, training_exercise_id)
    if not training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    _check_owner(training_exercise.training, current_user)
    return await SetsExerciseRepository.create_set_exercise(session, training_exercise_id, set_data)

@router_training_exercises.patch("/{training_exercise_id}", response_model=TrainingExerciseGET, status_code=status.HTTP_200_OK)
async def update_training_exercise(training_exercise_id: int, training_exercise_data: TrainingExerciseUPDATE,session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training_exercise = await TrainingExerciseRepository.get_training_exercise_with_owner(session, training_exercise_id)
    if not training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    _check_owner(training_exercise.training, current_user)
    return await TrainingExerciseRepository.update_training_exercise(session, training_exercise_id, training_exercise_data)

@router_training_exercises.delete("/{training_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_exercise(training_exercise_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    training_exercise = await TrainingExerciseRepository.get_training_exercise_with_owner(session, training_exercise_id)
    if not training_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The training exercise does not exist")
    _check_owner(training_exercise.training, current_user)
    await TrainingExerciseRepository.delete_training_exercise(session, training_exercise_id)
    return None

router_sets = APIRouter(prefix="/sets", tags=["Sets"])

@router_sets.get("/{set_exercise_id}", response_model=SetsExerciseGET, status_code=status.HTTP_200_OK)
async def get_set(set_exercise_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    set_exercise = await SetsExerciseRepository.get_set_exercise_with_owner(session, set_exercise_id)
    if not set_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The set to exercise does not exist")
    _check_owner(set_exercise.training_exercise.training, current_user)
    return set_exercise

@router_sets.patch("/{set_exercise_id}", response_model=SetsExerciseGET, status_code=status.HTTP_200_OK)
async def update_set(set_exercise_id: int, set_data: SetsExerciseUPDATE, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    set_exercise = await SetsExerciseRepository.get_set_exercise_with_owner(session, set_exercise_id)
    if not set_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The set to exercise does not exist")
    _check_owner(set_exercise.training_exercise.training, current_user)
    return await SetsExerciseRepository.update_set_exercise(session, set_exercise_id, set_data)

@router_sets.delete("/{set_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(set_exercise_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    set_exercise = await SetsExerciseRepository.get_set_exercise_with_owner(session, set_exercise_id)
    if not set_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The set to exercise does not exist")
    _check_owner(set_exercise.training_exercise.training, current_user)
    await SetsExerciseRepository.delete_set_exercise(session, set_exercise_id)
    return None