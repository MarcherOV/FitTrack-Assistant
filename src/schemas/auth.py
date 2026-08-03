from pydantic import BaseModel

class TelegramAuthRequest(BaseModel):
    initData: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int


class TelegramAuthWidgetRequest(BaseModel):
    data: dict