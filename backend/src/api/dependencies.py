from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import SECRET_KEY, ALGORITHM
from src.db.database import get_session
from src.repositories.users import UserRepository
from src.models.users import User
from src.core.config import TELEGRAM_TOKEN

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/telegram", auto_error=False)
api_key_header = APIKeyHeader(name="X-Bot-Token", auto_error=False)

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    bot_token: str = Depends(api_key_header),
    session: AsyncSession = Depends(get_session)
) -> User:
    
    if bot_token:
        if bot_token != TELEGRAM_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid bot token"
            )
            
        telegram_id_str = request.headers.get("X-Telegram-Id")
        if not telegram_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Telegram-Id header is required for bot requests"
            )
            
        user = await UserRepository.get_user_by_telegram_id(session, int(telegram_id_str))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise ValueError("No sub in token")
            user_id = int(user_id_str)
            
        except (jwt.ExpiredSignatureError, jwt.PyJWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await UserRepository.get_user(session=session, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide Bearer token or Bot API Key.",
    )