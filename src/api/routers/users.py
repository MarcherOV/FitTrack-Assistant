from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.schemas.users import UserGET, UserPOST
from src.schemas.training import TrainingGET
from src.repositories.users import UserRepository
from src.repositories.training import TrainingRepository
from src.pagination.pagination import PaginatedResponse
from src.api.dependencies import get_current_user
from src.models.users import User
from math import ceil
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserPOST, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserPOST, session: AsyncSession = Depends(get_session)):
    existing_user = await UserRepository.get_user_by_telegram_id(session, user_data.telegram_id)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already exists")
    new_user = await UserRepository.create_user(session, user_data)
    return new_user

@router.get("/{telegram_id}", response_model=UserGET, status_code=status.HTTP_200_OK)
async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession = Depends(get_session)):
    user = await UserRepository.get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/{user_id}/trainings/", response_model=PaginatedResponse[TrainingGET], status_code=status.HTTP_200_OK)
async def get_all_user_trainings(user_id: int, session: AsyncSession = Depends(get_session),
                                 page: int = Query(1, ge=1, description="Page number"),
                                 page_size: int = Query(5, ge=1, le=50, description="Number of entries on the page"),
                                 current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these trainings"
        )
    trainings, total = (await TrainingRepository.get_training_by_user_id(session=session, user_id=current_user.id, page=page, page_size=page_size))
    total_pages = ceil(total / page_size) if total > 0 else 0
    has_next = page < total_pages
    has_previous = page > 1 and page <= total_pages + 1
    return PaginatedResponse(
        items=trainings,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )