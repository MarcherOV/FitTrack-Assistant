from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.schemas.users import UserGET, UserPOST
from src.repositories.users import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserPOST, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserPOST, session: AsyncSession = Depends(get_session)):
    existing_user = await UserRepository.get_user_by_telegram_id(session, user_data.telegram_id)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already exists")
    new_user = await UserRepository.create_user(session, user_data)
    return new_user

@router.get("/{telegram_id}", response_model=UserGET, status_code=status.HTTP_200_OK)
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session)):
    user = await UserRepository.get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user