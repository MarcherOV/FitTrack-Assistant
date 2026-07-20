from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.body import BodyInfo, BodyMeasurement
from src.schemas.body import BodyInfoGET, BodyInfoPOST, BodyInfoUPDATE, BodyMeasurementGET, BodyMeasurementPOST, BodyMeasurementUPDATE, BodyInfoWithMeasurementsGET

class BodyInfoRepository:

    @staticmethod
    async def get_body_info(session: AsyncSession, body_info_id: int) -> BodyInfo:
        query = select(BodyInfo).where(BodyInfo.id == body_info_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_body_info_with_body_measurements(session: AsyncSession, body_info_id: int) -> BodyInfo | None:
        query = select(BodyInfo).where(BodyInfo.id == body_info_id).options(selectinload(BodyInfo.measurements))
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_user_body_info_with_body_measurements(session: AsyncSession, user_id: int) -> list[BodyInfo]:
        query = select(BodyInfo).where(BodyInfo.user_id == user_id).options(selectinload(BodyInfo.measurements))
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_all_body_info_by_user_id(session: AsyncSession, user_id: int) -> list[BodyInfo]:
        query = (
            select(BodyInfo)
            .where(BodyInfo.user_id == user_id)
            .options(selectinload(BodyInfo.measurements))
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_all_body_info(session: AsyncSession) -> list[BodyInfo]:
        query = select(BodyInfo).options(selectinload(BodyInfo.measurements))
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_body_info(session: AsyncSession, body_info_data: BodyInfoPOST) -> BodyInfo:
        body_info = BodyInfo(
            user_id = body_info_data.user_id,
            date = body_info_data.date,
            weight = body_info_data.weight
        )
        session.add(body_info)
        await session.commit()
        await session.refresh(body_info)
        return body_info
    
    @staticmethod
    async def update_body_info(session: AsyncSession, body_info_id: int ,body_info_data: BodyInfoUPDATE) -> BodyInfo | None:
        body_info = await BodyInfoRepository.get_body_info(session, body_info_id)
        if not body_info:
            return None
        update_dict = body_info_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(body_info, key, value)
        
        await session.commit()
        await session.refresh(body_info)
        return body_info
    
    @staticmethod
    async def delete_body_info(session: AsyncSession, body_info_id: int) -> bool:
        body_info = await BodyInfoRepository.get_body_info(session, body_info_id)
        if body_info:
            await session.delete(body_info)
            await session.commit()
            return True
        return False
    
class BodyMeasurementRepository:
    
    @staticmethod
    async def get_body_measurement(session: AsyncSession, body_measurement_id: int) -> BodyMeasurement:
        query = select(BodyMeasurement).where(BodyMeasurement.id == body_measurement_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_body_measurement_by_body_info_id(session: AsyncSession, body_info_id: int) -> list[BodyMeasurement]:
        query = select(BodyMeasurement).where(BodyMeasurement.body_info_id == body_info_id)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_body_measurements(session: AsyncSession, body_measurements_data: BodyMeasurementPOST) -> BodyMeasurement:
        body_measurements = BodyMeasurement(
            body_info_id = body_measurements_data.body_info_id,
            measurements = body_measurements_data.measurements
        )
        session.add(body_measurements)
        await session.commit()
        await session.refresh(body_measurements)
        return body_measurements
    
    @staticmethod
    async def update_body_measurements(session: AsyncSession, body_measurements_id: int, body_measurements_data: BodyMeasurementUPDATE) -> BodyMeasurement | None:
        body_measurements = await BodyMeasurementRepository.get_body_measurement(session, body_measurements_id)
        if not body_measurements:
            return None
        update_dict = body_measurements_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(body_measurements, key, value)

        await session.commit()
        await session.refresh(body_measurements)
        return body_measurements
    
    @staticmethod
    async def delete_body_measurements(session: AsyncSession, body_measurements_id: int) -> bool:
        body_measurements = await BodyMeasurementRepository.get_body_measurement(session, body_measurements_id)
        if body_measurements:
            await session.delete(body_measurements)
            await session.commit()
            return True
        return False
