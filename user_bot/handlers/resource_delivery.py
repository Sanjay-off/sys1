

# ===========================================
# user_bot/handlers/resource_delivery.py - UPDATED
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

@router.message(CommandStart(deep_link=True))
async def handle_resource_request(message: Message, bot: Bot):
    """Handle resource delivery via deeplink"""
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
    if not args:
        return
    
    # Skip verification payloads
    if args.startswith('verify_') or args == 'newToken':
        return
    
    # Check if user is banned
    user = await UserOperations.get_user(user_id)
    if user and user.get("is_banned", False):
        await message.answer("❌ You are banned from using this bot.")
        return
    
    # Handle different payload types
    if args.startswith("batch_"):
        unique_id = args.replace("batch_", "")
        await deliver_batch_resource(message, bot, unique_id, user_id)
    else:
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
    
    # Track message IDs for deletion
    message_ids = []
    
    try:
        channel_msg_id = file_data["channel_message_id"]
        
        # Send resource
        if file_data["file_type"] == "text":
            resource_msg = await message.answer(file_data["text_content"])
        else:
            resource_msg = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.PRIVATE_CHANNEL_ID,
                message_id=channel_msg_id
            )
        
        message_ids.append(resource_msg.message_id)
        
        # If zip file, send password
        if file_data["file_type"] == "document":
            password = await AdminConfigOperations.get_setting("zip_password")
            if not password:
                password = Config.DEFAULT_ZIP_PASSWORD
            
            pwd_msg = await message.answer(f"🔐 Password: `{password}`")
            message_ids.append(pwd_msg.message_id)
        
        # Send warning message
        deletion_time = await AdminConfigOperations.get_setting("deletion_time")
        if not deletion_time:
            deletion_time = Config.DEFAULT_DELETION_TIME
        
        warning_text = f"""⚠️ Tᴇʟᴇɢʀᴀᴍ Mғ Dᴏɴᴛ Lɪᴋᴇ Iᴛ Sᴏ....
Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {format_duration(deletion_time)}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."""
        
        warning_msg = await message.answer(warning_text)
        message_ids.append(warning_msg.message_id)
        
        # Get bot info for deeplink
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
        
    except Exception as e:
        await message.answer(f"❌ Error delivering resource: {e}")

async def deliver_batch_resource(message: Message, bot: Bot, unique_id: str, user_id: int):
    """Deliver batch resources to user"""
    file_data = await FileOperations.get_file_by_unique_id(unique_id)
    
    if not file_data or not file_data.get("is_batch", False):
        await message.answer("❌ Batch resource not found or has been removed.")
        return
    
    # Decrement access count
    await UserOperations.decrement_access_count(user_id)
    
    # Track message IDs
    message_ids = []
    batch_file_ids = file_data.get("batch_file_ids", [])
    
    # Send all batch files
    for file_info in batch_file_ids:
        try:
            resource_msg = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.PRIVATE_CHANNEL_ID,
                message_id=file_info["channel_message_id"]
            )
            message_ids.append(resource_msg.message_id)
        except Exception as e:
            print(f"Error sending batch file: {e}")
    
    # Send warning
    deletion_time = await AdminConfigOperations.get_setting("deletion_time")
    if not deletion_time:
        deletion_time = Config.DEFAULT_DELETION_TIME
    
    warning_text = f"""⚠️ Tᴇʟᴇɢʀᴀᴍ Mғ Dᴏɴᴛ Lɪᴋᴇ Iᴛ Sᴏ....
Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {format_duration(deletion_time)}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ."""
    
    warning_msg = await message.answer(warning_text)
    message_ids.append(warning_msg.message_id)
    
    # Schedule deletion
    bot_info = await bot.get_me()
    deeplink = f"https://t.me/{bot_info.username}?start=batch_{unique_id}"
    
    await deletion_scheduler.schedule_deletion(
        bot=bot,
        chat_id=message.chat.id,
        message_ids=message_ids,
        delay_minutes=deletion_time,
        deeplink=deeplink,
        unique_id=unique_id
    )

@router.callback_query(F.data == "close_message")
async def handle_close_button(callback: CallbackQuery):
    """Handle close button press"""
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")
    await callback.answer()