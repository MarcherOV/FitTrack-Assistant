from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from schemas.users import UserGET, UserPOST

class UserRepository:

    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserPOST) -> User:
        user = User(
            telegram_id = user_data.telegram_id,
            username = user_data.username
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(session: AsyncSession, telegram_id: int) -> bool:
        user = await UserRepository.get_user_by_telegram_id(session, telegram_id)
        if user:
            await session.delete(user)
            await session.commit()
            return True
        return False
    