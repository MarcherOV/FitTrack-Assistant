from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.schemas.body import *
from src.repositories.body import *

router_body = APIRouter(prefix="/body-info", tags=["Body"])

@router_body.get("/users/{user_id}/", response_model=list[BodyInfoGET], status_code=status.HTTP_200_OK)
async def get_body_info_of_user(user_id: int, session: AsyncSession = Depends(get_session)):
    body_info = await BodyInfoRepository.get_all_body_info_by_user_id(session, user_id)
    if not body_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The body info does not exist")
    return body_info
    
@router_body.get("/{body_info_id}", response_model=BodyInfoGET, status_code=status.HTTP_200_OK)
async def get_body_info(body_info_id: int, session: AsyncSession = Depends(get_session)):
    body_info = await BodyInfoRepository.get_body_info(session, body_info_id)
    if not body_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The body info does not exist")
    return body_info

@router_body.get("/{body_info_id}/measurements", response_model=list[BodyMeasurementGET], status_code=status.HTTP_200_OK)
async def get_body_info_with_measurements(body_info_id: int, session: AsyncSession = Depends(get_session)):
    body_info = await BodyInfoRepository.get_body_info_with_body_measurements(session, body_info_id)
    if not body_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The body info does not exist")
    return body_info.measurements

@router_body.post("/", response_model=BodyInfoGET, status_code=status.HTTP_201_CREATED)
async def create_body_info(body_info_data: BodyInfoPOST, session: AsyncSession = Depends(get_session)):
    try:
        body_info = await BodyInfoRepository.create_body_info(session, body_info_data)
        return body_info
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user does not exist")
    
@router_body.patch("/{body_info_id}", response_model=BodyInfoGET, status_code=status.HTTP_200_OK)
async def update_body_info(body_info_id: int, body_info_data: BodyInfoUPDATE, session: AsyncSession = Depends(get_session)):
    try:
        body_info = await BodyInfoRepository.update_body_info(session, body_info_id, body_info_data)
        return body_info
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user does not exist")
    
@router_body.delete("/{body_info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_body_info(body_info_id: int, session: AsyncSession = Depends(get_session)):
    body_info_deleted = await BodyInfoRepository.delete_body_info(session, body_info_id)
    if not body_info_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The body info does not exist")
    return None


router_body_measurements = APIRouter(prefix="/body-measurements", tags=["Body"])

@router_body_measurements.get("/{body_measurement_id}", response_model=BodyMeasurementGET, status_code=status.HTTP_200_OK)
async def get_body_measurement(body_measurement_id: int, session: AsyncSession = Depends(get_session)):
    body_measurement = await BodyMeasurementRepository.get_body_measurement(session, body_measurement_id)
    if not body_measurement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The body info does not exist")
    return body_measurement
    
@router_body_measurements.post("/", response_model=BodyMeasurementGET, status_code=status.HTTP_201_CREATED)
async def create_body_measurement(body_measurement_data: BodyMeasurementPOST, session: AsyncSession = Depends(get_session)):
    try:
        body_measurement = await BodyMeasurementRepository.create_body_measurements(session, body_measurement_data)
        return body_measurement
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The body measurement does not exist")
    
@router_body_measurements.patch("/{body_measurement_id}", response_model=BodyMeasurementGET, status_code=status.HTTP_200_OK)
async def update_body_measurement(body_measurement_id: int, body_measurement_data: BodyMeasurementUPDATE, session: AsyncSession = Depends(get_session)):
    body_measurement_updated = await BodyMeasurementRepository.update_body_measurements(session, body_measurement_id, body_measurement_data)
    if not body_measurement_updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The body measurement does not exist")
    return body_measurement_updated

@router_body_measurements.delete("/{body_measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_body_measurement(body_measurement_id: int, session: AsyncSession = Depends(get_session)):
    body_measurement_deleted = await BodyMeasurementRepository.delete_body_measurements(session, body_measurement_id)
    if not body_measurement_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The body measurement does not exist")
    return None