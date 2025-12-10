# ===========================================
# user_bot/middlewares/verification_check.py
# ===========================================
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton

from database.operations import UserOperations, AdminConfigOperations, TokenGeneratorCountOperations, TokenOperations
from database.models import TokenModel
from config.settings import Config
from utils.token_generator import generate_token, generate_unique_id
from utils.url_shortener import URLShortener

class VerificationMiddleware(BaseMiddleware):
    """Middleware to check if user is verified (has media access count)"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        
        # Skip for /start, /help commands without deep link
        if event.text and event.text.startswith('/'):
            command = event.text.split()[0]
            args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
            
            # Skip verification for these cases
            if command in ['/start', '/help'] and not args:
                return await handler(event, data)
            
            # Skip verification for verification callback itself
            if args.startswith('verify_') or args == 'newToken':
                return await handler(event, data)
        
        # Only check for resource requests (deep link)
        if not (event.text and event.text.startswith('/start ')):
            return await handler(event, data)
        
        args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
        
        # Skip for verification payloads
        if args.startswith('verify_') or args == 'newToken':
            return await handler(event, data)
        
        user_id = event.from_user.id
        bot: Bot = data.get('bot')
        
        # Get user data
        user = await UserOperations.get_user(user_id)
        user_access_count = user.get("user_access_count", 0) if user else 0
        
        # Check if user is verified
        if user_access_count > 0:
            # User is verified, proceed to deliver resource
            return await handler(event, data)
        
        # User not verified, show verification template
        username = event.from_user.first_name or event.from_user.username or "User"
        
        # Get media access count from settings
        media_access_count = await AdminConfigOperations.get_setting("media_access_count")
        if not media_access_count:
            media_access_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
        
        # Check token generation limit (15 per day)
        token_count_today = await TokenGeneratorCountOperations.get_count(user_id)
        
        if token_count_today >= Config.MAX_TOKENS_PER_DAY:
            await event.answer(
                f"❌ **Daily Token Limit Reached**\n\n"
                f"You have generated {token_count_today} tokens today.\n"
                f"Maximum allowed: {Config.MAX_TOKENS_PER_DAY} tokens per day.\n\n"
                f"Please try again tomorrow."
            )
            return  # Stop processing
        
        # Generate verification token
        token = generate_token(Config.TOKEN_LENGTH)
        unique_id = generate_unique_id(Config.UNIQUE_ID_LENGTH)
        
        # Save token to database
        token_data = TokenModel.create(
            token=token,
            unique_id=unique_id,
            created_by=user_id,
            status="not_used"
        )
        await TokenOperations.create_token(token_data)
        
        # Increment token generation count
        await TokenGeneratorCountOperations.increment_count(user_id)
        
        # Create verification URL
        verification_url = f"{Config.SERVER_URL}/redirect?token={token}"
        
        # Shorten URL
        shortened_url = await URLShortener.shorten_url(verification_url)
        if not shortened_url:
            shortened_url = verification_url  # Fallback to direct URL
        
        # Get "how to verify" link
        verify_link = await AdminConfigOperations.get_setting("verify_link")
        if not verify_link:
            verify_link = "https://t.me/your_channel/how_to_verify"  # Default
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Verify Now", url=shortened_url)],
            [InlineKeyboardButton(text="❓ How to Verify", url=verify_link)]
        ])
        
        verification_text = f"""⚡️ ʜᴇʏ, {username} ×~

›› ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ᴀ ᴛᴏᴋᴇɴ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴀᴄᴄᴇss ꜰᴏʀ {media_access_count} media ✅"""
        
        await event.answer(
            verification_text,
            reply_markup=keyboard
        )
        return  # Stop processing