

# =======# ===========================================
# user_bot/middlewares/force_sub.py
# ===========================================
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from database.operations import AdminConfigOperations, UserOperations

class ForceSubscriptionMiddleware(BaseMiddleware):
    """Middleware to check if user has joined all force subscription channels"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        
        # Skip for commands without deep link
        if event.text and event.text.startswith('/'):
            command = event.text.split()[0]
            args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
            
            # Skip for these commands
            if command in ['/start', '/help']:
                # If no args, skip middleware
                if not args:
                    return await handler(event, data)
                # If args are verify_ or newToken, skip
                if args.startswith('verify_') or args == 'newToken':
                    return await handler(event, data)
        
        # Only check for resource requests (deep link with unique_id)
        if not (event.text and event.text.startswith('/start ')):
            return await handler(event, data)
        
        args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
        
        # Skip for verification payloads
        if not args or args.startswith('verify_') or args == 'newToken':
            return await handler(event, data)
        
        user_id = event.from_user.id
        bot: Bot = data.get('bot')
        
        # Get all force sub channels
        force_sub_channels = await AdminConfigOperations.get_force_sub_channels()
        
        if not force_sub_channels:
            # No force sub configured, proceed
            return await handler(event, data)
        
        # Get user data
        user = await UserOperations.get_user(user_id)
        user_join_requests = user.get("join_requests", []) if user else []
        
        # Check membership for each channel
        not_joined = []
        
        for channel in force_sub_channels:
            channel_id = channel["channel_id"]
            
            # Check if user has made a join request (for private channels)
            if channel_id in user_join_requests:
                continue  # User considered subscribed
            
            # Check actual membership
            try:
                member = await bot.get_chat_member(
                    chat_id=channel_id,
                    user_id=user_id
                )
                
                # Check if user is member/admin/creator
                if member.status in ['member', 'administrator', 'creator']:
                    # Add to join_requests to skip future checks
                    await UserOperations.add_join_request(user_id, channel_id)
                else:
                    not_joined.append(channel)
            
            except TelegramBadRequest:
                # User not in channel or channel not found
                not_joined.append(channel)
            except Exception as e:
                print(f"Error checking membership for {channel_id}: {e}")
                not_joined.append(channel)
        
        # If user hasn't joined all channels, show force sub message
        if not_joined:
            username = event.from_user.first_name or event.from_user.username or "User"
            
            # Create inline keyboard with channels (2 per row)
            keyboard = []
            for i in range(0, len(not_joined), 2):
                row = []
                for j in range(2):
                    if i + j < len(not_joined):
                        channel = not_joined[i + j]
                        # Create button with channel link
                        # Remove @ symbol and use proper format
                        channel_username = channel['channel_username']
                        if channel_username.startswith('@'):
                            channel_username = channel_username[1:]  # Remove @
                        channel_link = f"https://t.me/{channel_username}"
                        row.append(
                            InlineKeyboardButton(
                                text=channel['placeholder'],
                                url=channel_link
                            )
                        )
                keyboard.append(row)
            
            # Add "Try Again" button with same deep link
            bot_info = await bot.get_me()
            try_again_link = f"https://t.me/{bot_info.username}?start={args}"
            
            keyboard.append([
                InlineKeyboardButton(
                    text="🔄 Try Again",
                    url=try_again_link
                )
            ])
            
            force_sub_text = f"""›› ʜᴇʏ, {username} ×

ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ,
sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs."""
            
            await event.answer(
                force_sub_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            return  # Stop processing
        
        # User joined all channels, proceed
        return await handler(event, data)
