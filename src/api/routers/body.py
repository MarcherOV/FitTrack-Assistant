from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.schemas.body import *
from src.repositories.body import *
from src.repositories.users import UserRepository
from src.pagination.pagination import PaginatedResponse
from src.api.dependencies import get_current_user
from src.models.users import User
from math import ceil

router_body = APIRouter(prefix="/body-info", tags=["Body"])

@router_body.get("/users/{user_id}/", response_model=list[BodyInfoGET], status_code=status.HTTP_200_OK)
async def get_body_info_of_user(user_id: int, session: AsyncSession = Depends(get_session),
                                current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these trainings"
        )
    body_info = await BodyInfoRepository.get_all_body_info_by_user_id(session, user_id)
    if not body_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The body info does not exist")
    return body_info
    
@router_body.get("/{body_info_id}", response_model=BodyInfoGET, status_code=status.HTTP_200_OK)
async def get_body_info(body_info_id: int, session: AsyncSession = Depends(get_session),):
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

@router_body.get("/users/{user_id}/measurements/", response_model=PaginatedResponse[BodyInfoWithMeasurementsGET], status_code=status.HTTP_200_OK)
async def get_all_user_body_info_with_measurements(user_id: int, session: AsyncSession = Depends(get_session), 
                                                   page: int = Query(1, ge=1, description="Page number"),
                                                   page_size: int = Query(5, ge=1, le=50, description="Number of entries on the page"),
                                                   current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these trainings"
        )
    user_body_info, total = (await BodyInfoRepository.get_all_user_body_info_with_body_measurements(session=session, user_id=current_user.id, page=page, page_size=page_size))
    total_pages = ceil(total / page_size) if total > 0 else 0
    has_next = page < total_pages
    has_previous = page > 1 and page <= total_pages + 1
    return PaginatedResponse(
        items=user_body_info,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )

@router_body.get("/", response_model=list[BodyInfoWithMeasurementsGET], status_code=status.HTTP_200_OK)
async def get_all_body_info(session: AsyncSession = Depends(get_session)):
    all_body_info = await BodyInfoRepository.get_all_body_info(session)
    return all_body_info

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