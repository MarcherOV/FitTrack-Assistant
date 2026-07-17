from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.bot.services.api_client import APIClient

class APIClientMiddleware(BaseMiddleware):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["api_client"] = self.api_client
        return await handler(event, data)