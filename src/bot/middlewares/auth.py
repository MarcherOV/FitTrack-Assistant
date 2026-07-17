import logging
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from httpx import HTTPStatusError
from src.bot.services.api_client import APIClient

class UserAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        tg_user = data.get("event_from_user")

        if not tg_user:
            return await handler(event, data)
        
        api_client: APIClient = data.get("api_client")
        if not api_client:
            logging.error(
                "APIClient was not found in the dictionary! Check the order in which the middleware was registered."
            )
            return await handler(event, data)
        
        try:
            user_data = await api_client.get(f"/users/{tg_user.id}")

        except HTTPStatusError as e:
            if e.response.status_code == 404:
                logging.info(
                    f"New User Registration: {tg_user.id}"
                )

                payload = {
                    "telegram_id": tg_user.id,
                    "username": tg_user.username
                }
                user_data = await api_client.post("/users/", json_data=payload)
            else:
                logging.error(
                    f"User authorization error: {e}"
                )
                return
            
        data["db_user"] = user_data
        return await handler(event, data)