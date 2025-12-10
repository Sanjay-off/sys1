
# ===========================================
# admin_bot/main.py
# ===========================================
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import Config
from database.connection import Database
from admin_bot.middlewares.auth import AdminAuthMiddleware
from admin_bot.keyboards.menu import get_admin_commands

# Import handlers
from admin_bot.handlers import start
from admin_bot.handlers import generate_link
from admin_bot.handlers import regenerate_post
from admin_bot.handlers import broadcast
from admin_bot.handlers import force_sub
from admin_bot.handlers import user_management
from admin_bot.handlers import settings
from admin_bot.handlers import batch

logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize bot and dispatcher
    bot = Bot(
        token=Config.ADMIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Connect to database
    await Database.connect()
    
    # Register middlewares
    dp.message.middleware(AdminAuthMiddleware())
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(generate_link.router)
    dp.include_router(regenerate_post.router)
    dp.include_router(broadcast.router)
    dp.include_router(force_sub.router)
    dp.include_router(user_management.router)
    dp.include_router(settings.router)
    dp.include_router(batch.router)
    
    # Set bot commands
    await bot.set_my_commands(get_admin_commands())
    
    print("🤖 Admin Bot started!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await Database.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())