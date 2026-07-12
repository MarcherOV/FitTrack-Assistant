from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.exercises import Exercise, Category, Type
from src.schemas.exercises import ExercisePOST, ExerciseUPDATE, ExerciseGET, CategoryPOST, CategoryUPDATE, CategoryGET, TypePOST, TypeUPDATE, TypeGET

class ExerciseRepository:

    @staticmethod
    async def get_all_exercises(session: AsyncSession) -> list[Exercise]:
        query = select(Exercise)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_exercise(session: AsyncSession, exercise_id: int) -> Exercise | None:
        query = select(Exercise).where(Exercise.id == exercise_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_exercise(session: AsyncSession, exercise_data: ExercisePOST) -> Exercise:
        exercise = Exercise(
            name = exercise_data.name,
            category_id = exercise_data.category_id,
            type_id = exercise_data.type_id
        )
        session.add(exercise)
        try:
            await session.commit()
            await session.refresh(exercise)
            return exercise
        except IntegrityError as e:
            await session.rollback()
            raise e
    
    @staticmethod
    async def delete_exercise(session: AsyncSession, exercise_id: int) -> bool:
        exercise = await ExerciseRepository.get_exercise(session, exercise_id)
        if exercise:
            await session.delete(exercise)
            await session.commit()
            return True
        return False
    
class CategoryRepository:

    @staticmethod
    async def get_all_categories(session: AsyncSession) -> list[Category]:
        query = select(Category)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_category(session: AsyncSession, category_id: int) -> Category | None:
        query = select(Category).where(Category.id == category_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_category_with_exercises(session: AsyncSession, category_id: int) -> Category | None:
        query = select(Category).where(Category.id == category_id).options(selectinload(Category.exercises))
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_category(session: AsyncSession, category_data: CategoryPOST) -> Category:
        category = Category(
            name = category_data.name
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category
    
    @staticmethod
    async def delete_category(session: AsyncSession, category_id: int) -> bool:
        category = await CategoryRepository.get_category(session, category_id)
        if category:
            await session.delete(category)
            await session.commit()
            return True
        return False
    
class TypeRepository:

    @staticmethod
    async def get_all_types(session: AsyncSession) -> list[Type]:
        query = select(Type)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_type(session: AsyncSession, type_id: int) -> Type | None:
        query = select(Type).where(Type.id == type_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_type_with_exercises(session: AsyncSession, type_id: int) -> Type | None:
        query = select(Type).where(Type.id == type_id).options(selectinload(Type.exercises))
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_type(session: AsyncSession, type_data: TypePOST) -> Type:
        type_ = Type(
            name = type_data.name
        )
        session.add(type_)
        await session.commit()
        await session.refresh(type_)
        return type_
    
    @staticmethod
    async def delete_type(session: AsyncSession, type_id: int) -> bool:
        type_ = await TypeRepository.get_type(session, type_id)
        if type_:
            await session.delete(type_)
            await session.commit()
            return True
        return False