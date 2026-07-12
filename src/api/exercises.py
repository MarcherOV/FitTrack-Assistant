from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.schemas.exercises import *
from src.repositories.exercises import *

router_exercise = APIRouter(prefix="/exercises", tags=["Exercises"])

@router_exercise.get("/{exercise_id}", response_model=ExerciseGET, status_code=status.HTTP_200_OK)
async def get_exercise(exercise_id: int, session: AsyncSession = Depends(get_session)):
    exercise = await ExerciseRepository.get_exercise(session, exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The exercise does not exist")
    return exercise

@router_exercise.get("/", response_model=list[ExerciseGET], status_code=status.HTTP_200_OK)
async def get_all_exercises(session: AsyncSession = Depends(get_session)):
    exercises = await ExerciseRepository.get_all_exercises(session)
    return exercises

@router_exercise.post("/", response_model=ExerciseGET, status_code=status.HTTP_201_CREATED)
async def create_exercise(exercise_data: ExercisePOST, session: AsyncSession = Depends(get_session)):
    category = await CategoryRepository.get_category(session, exercise_data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Category with id {exercise_data.category_id} does not exist"
        )
    type_ = await TypeRepository.get_type(session, exercise_data.type_id)
    if not type_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Type with id {exercise_data.type_id} does not exist"
        )
    try:
        exercise = await ExerciseRepository.create_exercise(session, exercise_data)
        return exercise
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exercise with name '{exercise_data.name}' already exists.")

@router_exercise.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_id: int, session: AsyncSession = Depends(get_session)):
    exercise_deleted = await ExerciseRepository.delete_exercise(session, exercise_id)
    if not exercise_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The exercise does not exist")
    return None


router_category = APIRouter(prefix="/categories", tags=["Categories"])

@router_category.get("/{category_id}", response_model=CategoryGET, status_code=status.HTTP_200_OK)
async def get_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category = await CategoryRepository.get_category(session, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The category does not exist")
    return category

@router_category.get("/", response_model=list[CategoryGET], status_code=status.HTTP_200_OK)
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    categories = await CategoryRepository.get_all_categories(session)
    return categories

@router_category.get("/{category_id}/exercises", response_model=list[ExerciseGET], status_code=status.HTTP_200_OK)
async def get_category_with_exercises(category_id: int, session: AsyncSession = Depends(get_session)):
    category_with_exercises = await CategoryRepository.get_category_with_exercises(session, category_id)
    if not category_with_exercises:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The category does not exist")
    return category_with_exercises.exercises

@router_category.post("/", response_model=CategoryGET, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryPOST, session: AsyncSession = Depends(get_session)):
    category = await CategoryRepository.create_category(session, category_data)
    return category

@router_category.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category_deleted = await CategoryRepository.delete_category(session, category_id)
    if not category_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The category does not exist")
    return None


router_type = APIRouter(prefix="/types", tags=["Types"])

@router_type.get("/{type_id}", response_model=TypeGET, status_code=status.HTTP_200_OK)
async def get_type(type_id: int, session: AsyncSession = Depends(get_session)):
    type_ = await TypeRepository.get_type(session, type_id)
    if not type_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The type does not exist")
    return type_

@router_type.get("/", response_model=list[TypeGET], status_code=status.HTTP_200_OK)
async def get_all_types(session: AsyncSession = Depends(get_session)):
    types = await TypeRepository.get_all_types(session)
    return types

@router_type.get("/{type_id}/exercises", response_model=list[ExerciseGET], status_code=status.HTTP_200_OK)
async def get_type_with_exercises(type_id: int, session: AsyncSession = Depends(get_session)):
    type_with_exercises = await TypeRepository.get_type_with_exercises(session, type_id)
    if not type_with_exercises:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The type does not exist")
    return type_with_exercises.exercises

@router_type.post("/", response_model=TypeGET, status_code=status.HTTP_201_CREATED)
async def create_type(type_data: TypePOST, session: AsyncSession = Depends(get_session)):
    type_ = await TypeRepository.create_type(session, type_data)
    return type_

@router_type.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_type(type_id: int, session: AsyncSession = Depends(get_session)):
    type_deleted = await TypeRepository.delete_type(session, type_id)
    if not type_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The type does not exist")
    return None