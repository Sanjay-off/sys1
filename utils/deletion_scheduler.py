# ===========================================
# utils/deletion_scheduler.py
# ===========================================
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from aiogram import Bot

class DeletionScheduler:
    """Handles scheduled deletion of messages"""
    
    def __init__(self):
        self.scheduled_deletions: Dict[str, asyncio.Task] = {}
    
    async def schedule_deletion(
        self,
        bot: Bot,
        chat_id: int,
        message_ids: List[int],
        delay_minutes: int,
        deeplink: str,
        unique_id: str
    ):
        """Schedule messages for deletion"""
        deletion_key = f"{chat_id}_{unique_id}"
        
        # Cancel existing deletion if any
        if deletion_key in self.scheduled_deletions:
            self.scheduled_deletions[deletion_key].cancel()
        
        # Create deletion task
        task = asyncio.create_task(
            self._delete_after_delay(
                bot, chat_id, message_ids, delay_minutes, deeplink
            )
        )
        
        self.scheduled_deletions[deletion_key] = task
    
    async def _delete_after_delay(
        self,
        bot: Bot,
        chat_id: int,
        message_ids: List[int],
        delay_minutes: int,
        deeplink: str
    ):
        """Delete messages after specified delay"""
        try:
            # Wait for specified time
            await asyncio.sleep(delay_minutes * 60)
            
            # Delete all messages
            deleted_count = 0
            for msg_id in message_ids:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete message {msg_id}: {e}")
            
            print(f"✅ Deleted {deleted_count}/{len(message_ids)} messages")
            
            # Send "deleted" message with buttons
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="♻️ Click Here", url=deeplink)],
                [InlineKeyboardButton(text="❌ Close", callback_data="close_message")]
            ])
            
            deletion_text = """Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑

Iғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: [♻️ Cʟɪᴄᴋ Hᴇʀᴇ]({}) ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.""".format(deeplink)
            
            await bot.send_message(
                chat_id=chat_id,
                text=deletion_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        except asyncio.CancelledError:
            print("Deletion task cancelled")
        except Exception as e:
            print(f"Error in deletion task: {e}")

# Global deletion scheduler instance
deletion_scheduler = DeletionScheduler()