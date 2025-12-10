


# ===========================================
# user_bot/main.py
# ===========================================
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import Config
from database.connection import Database

# Import middlewares
from user_bot.middlewares.force_sub import ForceSubscriptionMiddleware
from user_bot.middlewares.verification_check import VerificationMiddleware

# Import handlers
from user_bot.handlers import start
from user_bot.handlers import help as help_handler
from user_bot.handlers import resource_delivery
from user_bot.handlers import verification
from user_bot.handlers import join_request

logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize bot and dispatcher
    bot = Bot(
        token=Config.USER_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Connect to database
    await Database.connect()
    
    # Register middlewares (order matters!)
    # 1. First check force subscription
    dp.message.middleware(ForceSubscriptionMiddleware())
    # 2. Then check verification
    dp.message.middleware(VerificationMiddleware())
    
    # Register routers
    dp.include_router(verification.router)  # Must be first for verify_ payloads
    dp.include_router(resource_delivery.router)  # Then resource delivery
    dp.include_router(start.router)
    dp.include_router(help_handler.router)
    dp.include_router(join_request.router)  # Join request handler
    
    print("🤖 User Bot started!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await Database.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())