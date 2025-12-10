

# ===========================================
# user_bot/handlers/help.py
# ===========================================
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    username = message.from_user.first_name or message.from_user.username or "User"
    
    help_text = f"""⁉️ Hᴇʟʟᴏ {username} ~

I ᴀᴍ ᴀ ғɪʟᴇ sᴜᴘᴘʟɪᴇʀ ʙᴏᴛ ᴀɴᴅ ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇs ғɪʟᴇs ғʀᴏᴍ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟs. Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ Mᴇɴᴛɪᴏɴᴇᴅ Cʜᴀɴɴᴇʟs ᴛᴏ ɢᴇᴛ Fɪʟᴇs ᴏʀ ɪɴɪᴛɪᴀᴛᴇ ᴍᴇssᴀɢᴇs...

/help - Oᴘᴇɴ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ !
Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴀʙᴏᴠᴇ ᴄᴏᴍᴍᴀɴᴅs ᴡɪᴛʜᴏᴜᴛ ᴊᴏɪɴɪɴɢ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs"""
    
    await message.answer(help_text)