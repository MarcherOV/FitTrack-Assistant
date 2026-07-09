from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BaseORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BodyInfoPOST(BaseModel):
    user_id: int
    date: datetime
    weight: float | None = None

class BodyInfoGET(BodyInfoPOST, BaseORMModel):
    id: int

class BodyInfoUPDATE(BaseModel):
    date: datetime | None = None
    weight: float | None = None

class BodyMeasurementPOST(BaseModel):
    body_info_id: int
    measurements: dict

class BodyMeasurementGET(BodyMeasurementPOST, BaseORMModel):
    id: int

class BodyMeasurementUPDATE(BaseModel):
    measurements: dict | None = None

class BodyInfoWithMeasurementsGET(BodyInfoGET):
    measurements: list[BodyMeasurementGET] = []