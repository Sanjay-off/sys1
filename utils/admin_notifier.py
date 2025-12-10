# ===========================================
# utils/admin_notifier.py
# ===========================================
from aiogram import Bot
from config.settings import Config
from typing import Optional
from datetime import datetime

class AdminNotifier:
    """Send notifications to admins"""
    
    @staticmethod
    async def notify_error(bot: Bot, error_message: str, context: Optional[str] = None):
        """Notify admins about errors"""
        notification = f"🚨 **ERROR ALERT**\n\n"
        notification += f"**Error:** {error_message}\n"
        if context:
            notification += f"**Context:** {context}\n"
        notification += f"**Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=notification,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")
    
    @staticmethod
    async def notify_channel_unavailable(bot: Bot, channel_id: int):
        """Notify when private channel is unavailable"""
        notification = f"⚠️ **CHANNEL ALERT**\n\n"
        notification += f"Private channel `{channel_id}` is unavailable!\n"
        notification += f"Please check if bot has admin rights."
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=notification,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")
    
    @staticmethod
    async def notify_force_sub_removed(bot: Bot, channel_username: str):
        """Notify when force sub channel is removed/unavailable"""
        notification = f"⚠️ **FORCE SUB ALERT**\n\n"
        notification += f"Channel `{channel_username}` is unavailable or bot was removed!\n"
        notification += f"Consider removing it from force sub list."
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=notification,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")