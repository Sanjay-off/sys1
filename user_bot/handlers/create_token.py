# ===========================================
# user_bot/handlers/create_token.py
# ===========================================
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.operations import TokenGeneratorCountOperations, TokenOperations, AdminConfigOperations
from database.models import TokenModel
from config.settings import Config
from utils.token_generator import generate_token, generate_unique_id
from utils.url_shortener import URLShortener

router = Router()

@router.message(Command("create_token"))
async def cmd_create_token(message: Message):
    """Create new verification token"""
    user_id = message.from_user.id
    username = message.from_user.first_name or message.from_user.username or "User"
    
    # Check token generation limit
    token_count_today = await TokenGeneratorCountOperations.get_count(user_id)
    
    if token_count_today >= Config.MAX_TOKENS_PER_DAY:
        await message.answer(
            f"❌ **Daily Token Limit Reached**\n\n"
            f"You have generated {token_count_today} tokens today.\n"
            f"Maximum allowed: {Config.MAX_TOKENS_PER_DAY} tokens per day.\n\n"
            f"Please try again tomorrow."
        )
        return
    
    # Generate new token
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
        shortened_url = verification_url
    
    # Get media access count
    media_access_count = await AdminConfigOperations.get_setting("media_access_count")
    if not media_access_count:
        media_access_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
    
    # Get "how to verify" link
    verify_link = await AdminConfigOperations.get_setting("verify_link")
    if not verify_link:
        verify_link = "https://t.me/your_channel/how_to_verify"
    
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Now", url=shortened_url)],
        [InlineKeyboardButton(text="❓ How to Verify", url=verify_link)]
    ])
    
    verification_text = f"""⚡️ ʜᴇʏ, {username} ×~

›› ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ᴀ ᴛᴏᴋᴇɴ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴀᴄᴄᴇss ꜰᴏʀ {media_access_count} media ✅

Tokens generated today: {token_count_today + 1}/{Config.MAX_TOKENS_PER_DAY}"""
    
    await message.answer(
        verification_text,
        reply_markup=keyboard
    )