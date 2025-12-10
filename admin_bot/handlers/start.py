# ===========================================
# admin_bot/handlers/start.py
# ===========================================
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    admin_name = message.from_user.first_name or "Admin"
    
    await message.answer(
        f"👋 Welcome back, {admin_name}!\n\n"
        f"🤖 Admin Bot is ready to use.\n\n"
        f"📋 Use the menu button or type /help to see available commands."
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = """
🔧 **Admin Bot Commands:**

📝 **Resource Management:**
/generate_link - Generate resource link
/regenerate_post - Regenerate post template
/generate_batch - Generate batch resource link

📢 **Broadcasting:**
/broadcast - Broadcast message to all users

👥 **User Management:**
/ban_user - Ban a user
/unban_user - Unban a user
/set_verified - Verify a user manually
/unset_verified - Unverify a user
/set_user_media_count - Set paid media count for user
/verification_stats - View verification statistics

📺 **Channel Management:**
/add_force_sub - Add force sub channel
/remove_force_sub - Remove force sub channel
/list_force_sub - List force sub channels

⚙️ **Settings:**
/set_media_count - Set free media access count
/set_password - Set zip file password
/set_deletion_time - Set resource deletion time
/set_verify_link - Set how to verify link

❌ **Other:**
/cancel - Cancel current operation
    """
    await message.answer(help_text)
