#


# ===========================================
# user_bot/handlers/start.py
# ===========================================
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from datetime import datetime

from config.settings import Config
from database.operations import UserOperations
from database.models import UserModel

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Check if user exists in database
    user = await UserOperations.get_user(user_id)
    
    if not user:
        # Create new user
        user_data = UserModel.create(
            user_id=user_id,
            username=username,
            first_name=first_name
        )
        await UserOperations.create_user(user_data)
    else:
        # Update last active
        await UserOperations.update_user(user_id, {"last_active": datetime.utcnow()})
    
    # Send welcome message
    welcome_text = f"""⚡️ Hᴇʏ, {first_name or username or 'User'} ~

I ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ.
use the link in the public group to access the media"""
    
    await message.answer(
        welcome_text,
        message_effect_id=Config.FIRE_EFFECT_ID
    )