from pydantic import BaseModel
from typing import Optional

class UserPOST(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class UserGET(UserPOST):
    id: int

    class Config:
        from_attributes = True
