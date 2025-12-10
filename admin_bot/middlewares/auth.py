
# ===========================================
# admin_bot/middlewares/auth.py
# ===========================================
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from config.settings import Config

class AdminAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            
            # Check if user is admin
            if user_id not in Config.ADMIN_IDS:
                await event.answer(
                    "❌ Not Authorized",
                    message_effect_id=Config.UNAUTHORIZED_EFFECT_ID
                )
                return
        
        return await handler(event, data)
