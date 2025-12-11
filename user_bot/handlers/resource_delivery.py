

# ===========================================
# user_bot/handlers/resource_delivery.py
# ===========================================
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart ,CommandObject
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from database.operations import FileOperations, UserOperations
from config.settings import Config
from utils.helpers import is_zip_file

router = Router()

@router.message(CommandStart(deep_link=True))
async def handle_resource_request(message: Message, bot: Bot):
    """Handle resource delivery via deeplink"""
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    print("args"+args)
    if not args:
        return
    
    # Check if user is banned
    user = await UserOperations.get_user(user_id)
    if user and user.get("is_banned", False):
        await message.answer("❌ You are banned from using this bot.")
        return
    
    # Handle different payload types
    if args.startswith("verify_"):
        # Will be handled in verification handler (Phase 2)
        pass
    elif args.startswith("batch_"):
        # Will be handled in batch handler (Phase 4)
        unique_id = args.replace("batch_", "")
        await deliver_batch_resource(message, bot, unique_id, user_id)
    elif args == "newToken":
        # Will be handled in verification handler (Phase 2)
        pass
    else:
        # Single resource delivery
        unique_id = args
        await deliver_single_resource(message, bot, unique_id, user_id)

async def deliver_single_resource(message: Message, bot: Bot, unique_id: str, user_id: int):
    """Deliver a single resource to user"""
    # Get file from database
    file_data = await FileOperations.get_file_by_unique_id(unique_id)
    
    if not file_data:
        await message.answer("❌ Resource not found or has been removed.")
        return
    
    # Decrement user access count (middleware already checked > 0)
    await UserOperations.decrement_access_count(user_id)
    
    # Fetch and send resource from private channel
    try:
        channel_msg_id = file_data["channel_message_id"]
        
        if file_data["file_type"] == "text":
            # Send text content
            resource_msg = await message.answer(file_data["text_content"])
        else:
            # Copy message from private channel
            resource_msg = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.PRIVATE_CHANNEL_ID,
                message_id=channel_msg_id
            )
            
            # If it's a zip file, add password caption
            if file_data["file_type"] == "document":
                from database.operations import AdminConfigOperations
                password = await AdminConfigOperations.get_setting("zip_password")
                if not password:
                    password = Config.DEFAULT_ZIP_PASSWORD
                
                await message.answer(f"🔐 Password: `{password}`")
        
        # Send warning message about deletion
        from database.operations import AdminConfigOperations
        deletion_time = await AdminConfigOperations.get_setting("deletion_time")
        if not deletion_time:
            deletion_time = Config.DEFAULT_DELETION_TIME
        
        from utils.helpers import format_duration
        warning_text = f"""⚠️ Tᴇʟᴇɢʀᴀᴍ Mғ Dᴏɴᴛ Lɪᴋᴇ Iᴛ Sᴏ....
Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {format_duration(deletion_time)}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."""
        
        warning_msg = await message.answer(warning_text)
        
        # TODO: Implement auto-deletion in Phase 4
        
    except Exception as e:
        await message.answer(f"❌ Error delivering resource: {e}")

@router.callback_query(F.data == "close_message")
async def handle_close_button(callback: CallbackQuery):
    """Handle close button press"""
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")
    await callback.answer()

async def deliver_batch_resource(message: Message, bot: Bot, unique_id: str, user_id: int):
    """Deliver batch resources to user"""
    # Get file from database
    file_data = await FileOperations.get_file_by_unique_id(unique_id)
    
    if not file_data or not file_data.get("is_batch", False):
        await message.answer("❌ Batch resource not found or has been removed.")
        return
    
    # TODO: Add middleware checks in Phase 2
    
    # Send all batch files
    batch_file_ids = file_data.get("batch_file_ids", [])
    
    for file_info in batch_file_ids:
        try:
            await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.PRIVATE_CHANNEL_ID,
                message_id=file_info["channel_message_id"]
            )
        except Exception as e:
            print(f"Error sending batch file: {e}")
    
    # Send warning message
    # Similar to single resource delivery
