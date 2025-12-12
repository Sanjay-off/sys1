import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config.settings import Config
from database.connection import Database

# Import middlewares
from user_bot.middlewares.force_sub import ForceSubscriptionMiddleware
from user_bot.middlewares.verification_check import VerificationMiddleware

# Import handlers
from user_bot.handlers import start
from user_bot.handlers import help as help_handler
from user_bot.handlers import verification
from user_bot.handlers import resource_delivery
from user_bot.handlers import join_request
from user_bot.handlers import create_token

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
    
    # Register routers (CRITICAL ORDER!)
    # 1. Verification handlers MUST be first (verify_ and newToken)
    dp.include_router(verification.router)
    
    # 2. Then resource delivery (all other /start with args)
    dp.include_router(resource_delivery.router)
    
    # 3. Then general commands (no args /start, /help, etc.)
    dp.include_router(start.router)
    dp.include_router(help_handler.router)
    dp.include_router(create_token.router)
    
    # 4. Finally join request handler
    dp.include_router(join_request.router)
    
    # Set bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help message"),
        BotCommand(command="create_token", description="Generate verification token"),
    ])
    
    print("🤖 User Bot started!")
    print("📋 Handler registration order:")
    print("   1. Verification handlers (verify_*, newToken)")
    print("   2. Resource delivery handlers (unique_id, batch_*)")
    print("   3. General commands (/start, /help, /create_token)")
    print("   4. Join request handler")
    
    try:
        await dp.start_polling(bot)
    finally:
        await Database.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())