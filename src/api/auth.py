from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserPOST
from src.schemas.auth import TelegramAuthRequest, TokenResponse
from src.core.security import verify_telegram_web_app_data, create_access_token
from src.core import config
from src.db.database import get_session
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.repositories.users import UserRepository
from datetime import timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/telegram", response_model=TokenResponse)
async def authenticate_via_telegram(
    auth_data: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session)
):
    telegram_user = verify_telegram_web_app_data(auth_data.initData, config.TELEGRAM_TOKEN)
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Telegram data",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    telegram_id = telegram_user.get("id")
    
    db_user = await UserRepository.get_user_by_telegram_id(session=session, telegram_id=telegram_id)
    
    if not db_user:
        user_data = UserPOST(telegram_id=telegram_id, username=telegram_user.get("username", None)) 
        db_user = await UserRepository.create_user(
            session=session,
            user_data=user_data
        )
    
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token, user_id=db_user.id)