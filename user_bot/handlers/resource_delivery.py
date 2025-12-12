# ===========================================
# user_bot/handlers/resource_delivery.py - COMPLETELY FIXED
# ===========================================
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from database.operations import FileOperations, UserOperations, AdminConfigOperations
from config.settings import Config
from utils.helpers import is_zip_file, format_duration
from utils.deletion_scheduler import deletion_scheduler

router = Router()

@router.message(CommandStart(deep_link=True, magic=F.args.regexp(r'^[^v][^e][^r].*')))
async def handle_resource_request(message: Message):
    """Handle resource delivery via deeplink (NOT starting with 'ver')"""
    # Extract arguments from /start command
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
    if not args:
        return
    
    user_id = message.from_user.id
    bot = message.bot
    
    # Skip verification payloads (they're handled in verification.py)
    if args.startswith('verify_') or args == 'newToken':
        return
    
    # Check if user is banned
    user = await UserOperations.get_user(user_id)
    if user and user.get("is_banned", False):
        await message.answer("❌ You are banned from using this bot.")
        return
    
    # Handle batch vs single resource
    if args.startswith("batch_"):
        unique_id = args.replace("batch_", "")
        await deliver_batch_resource(message, bot, unique_id, user_id)
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
    
    # Get user data to check access count
    user = await UserOperations.get_user(user_id)
    current_access = user.get("user_access_count", 0) if user else 0
    
    if current_access <= 0:
        await message.answer("❌ You don't have enough media access. Please verify first.")
        return
    
    # Decrement user access count
    await UserOperations.decrement_access_count(user_id)
    
    # Fetch and send resource from private channel
    try:
        channel_msg_id = file_data["channel_message_id"]
        message_ids = []  # Track all message IDs for deletion
        
        if file_data["file_type"] == "text":
            # Send text content
            resource_msg = await message.answer(file_data["text_content"])
            message_ids.append(resource_msg.message_id)
        else:
            # Copy message from private channel
            resource_msg = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.PRIVATE_CHANNEL_ID,
                message_id=channel_msg_id
            )
            message_ids.append(resource_msg.message_id)
            
            # If it's a document (potentially zip), add password caption
            if file_data["file_type"] == "document":
                password = await AdminConfigOperations.get_setting("zip_password")
                if not password:
                    password = Config.DEFAULT_ZIP_PASSWORD
                
                pwd_msg = await message.answer(f"🔐 Password: `{password}`", parse_mode="Markdown")
                message_ids.append(pwd_msg.message_id)
        
        # Get deletion time
        deletion_time = await AdminConfigOperations.get_setting("deletion_time")
        if not deletion_time:
            deletion_time = Config.DEFAULT_DELETION_TIME
        
        # Send warning message
        warning_text = f"""⚠️ Tᴇʟᴇɢʀᴀᴍ Mғ Dᴏɴᴛ Lɪᴋᴇ Iᴛ Sᴏ....
Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {format_duration(deletion_time)}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."""
        
        warning_msg = await message.answer(warning_text)
        message_ids.append(warning_msg.message_id)
        
        # Get user bot info for deeplink
        bot_info = await bot.get_me()
        deeplink = f"https://t.me/{bot_info.username}?start={unique_id}"
        
        # Schedule deletion
        await deletion_scheduler.schedule_deletion(
            bot=bot,
            chat_id=message.chat.id,
            message_ids=message_ids,
            delay_minutes=deletion_time,
            deeplink=deeplink,
            unique_id=unique_id
        )
        
        print(f"✅ Resource delivered to user {user_id}, access count: {current_access - 1}")
        
    except Exception as e:
        print(f"Error delivering resource: {e}")
        await message.answer(f"❌ Error delivering resource: {str(e)}")

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
    
    # Get user data to check access count
    user = await UserOperations.get_user(user_id)
    current_access = user.get("user_access_count", 0) if user else 0
    
    if current_access <= 0:
        await message.answer("❌ You don't have enough media access. Please verify first.")
        return
    
    # Decrement user access count
    await UserOperations.decrement_access_count(user_id)
    
    # Send all batch files
    batch_file_ids = file_data.get("batch_file_ids", [])
    message_ids = []
    
    for file_info in batch_file_ids:
        try:
            copied_msg = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.PRIVATE_CHANNEL_ID,
                message_id=file_info["channel_message_id"]
            )
            message_ids.append(copied_msg.message_id)
        except Exception as e:
            print(f"Error sending batch file: {e}")
    
    # Get deletion time
    deletion_time = await AdminConfigOperations.get_setting("deletion_time")
    if not deletion_time:
        deletion_time = Config.DEFAULT_DELETION_TIME
    
    # Send warning message
    warning_text = f"""⚠️ Tᴇʟᴇɢʀᴀᴍ Mғ Dᴏɴᴛ Lɪᴋᴇ Iᴛ Sᴏ....
Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {format_duration(deletion_time)}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."""
    
    warning_msg = await message.answer(warning_text)
    message_ids.append(warning_msg.message_id)
    
    # Get user bot info for deeplink
    bot_info = await bot.get_me()
    deeplink = f"https://t.me/{bot_info.username}?start=batch_{unique_id}"
    
    # Schedule deletion
    await deletion_scheduler.schedule_deletion(
        bot=bot,
        chat_id=message.chat.id,
        message_ids=message_ids,
        delay_minutes=deletion_time,
        deeplink=deeplink,
        unique_id=unique_id
    )
    
    print(f"✅ Batch resource delivered to user {user_id}, files: {len(batch_file_ids)}, access count: {current_access - 1}")