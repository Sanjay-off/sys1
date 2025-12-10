# ===========================================
# user_bot/handlers/verification.py
# ===========================================
# from aiogram import Router
# from aiogram.filters import CommandStart
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# from database.operations import TokenOperations, UserOperations, AdminConfigOperations, TokenGeneratorCountOperations
# from database.models import TokenModel
# from config.settings import Config
# from utils.token_generator import generate_token, generate_unique_id
# from utils.url_shortener import URLShortener

# router = Router()

# @router.message(CommandStart(deep_link=True, magic=lambda x: x.args.startswith('verify_')))
# async def handle_verification_callback(message: Message):
#     """Handle verification callback from bypass server"""
#     user_id = message.from_user.id
#     args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
#     # Parse: verify_{unique_id}_{user_id}
#     parts = args.split('_')
#     if len(parts) != 3:
#         await message.answer("❌ Invalid verification link.")
#         return
    
#     unique_id = parts[1]
#     token_user_id = int(parts[2])
    
#     # Verify it's the same user
#     if user_id != token_user_id:
#         await message.answer("❌ This verification link is not for you.")
#         return
    
#     # Get token from database
#     token = await TokenOperations.get_token_by_unique_id(unique_id)
    
#     if not token:
#         await message.answer("❌ Token not found or expired.")
#         return
    
#     # Check token status
#     if token["status"] == "verified":
#         # Token verified successfully
#         # Add media access count to user
#         media_count = await AdminConfigOperations.get_setting("media_access_count")
#         if not media_count:
#             media_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
        
#         await UserOperations.increment_access_count(user_id, media_count)
        
#         # Delete token
#         await TokenOperations.delete_token(token["token"])
        
#         # Get updated user data
#         user = await UserOperations.get_user(user_id)
#         current_access = user.get("user_access_count", 0)
        
#         await message.answer(
#             f"✅ **Verification Successful!**\n\n"
#             f"You currently have **{current_access}** free media access."
#         )
    
#     elif token["status"] == "bypassed":
#         # Bypass detected
#         await message.answer(
#             "🚨 ʙʏᴘᴀss ᴅᴇᴛᴇᴄᴛᴇᴅ 🚨\n\n"
#             "ʜᴏᴡ ᴍᴀɴʏ ᴛɪᴍᴇs ʜᴀᴠᴇ ɪ ᴛᴏʟᴅ ʏᴏᴜ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛᴏ ᴏᴜᴛsᴍᴀʀᴛ ʏᴏᴜʀ ᴅᴀᴅ 🥸🖕\n\n"
#             "ɴᴏᴡ sᴏʟᴠᴇ ɪᴛ ᴘʀᴏᴘᴇʀʟʏ!!"
#         )
        
#         # Show current access count
#         user = await UserOperations.get_user(user_id)
#         current_access = user.get("user_access_count", 0) if user else 0
        
#         await message.answer(
#             f"You currently have **{current_access}** free media access."
#         )
    
#     else:
#         await message.answer("❌ Invalid token status.")

# @router.message(CommandStart(deep_link=True, magic=lambda x: x.args == 'newToken'))
# async def handle_new_token_request(message: Message):
#     """Handle new token generation request"""
#     user_id = message.from_user.id
#     username = message.from_user.first_name or message.from_user.username or "User"
    
#     # Check token generation limit
#     token_count_today = await TokenGeneratorCountOperations.get_count(user_id)
    
#     if token_count_today >= Config.MAX_TOKENS_PER_DAY:
#         await message.answer(
#             f"❌ **Daily Token Limit Reached**\n\n"
#             f"You have generated {token_count_today} tokens today.\n"
#             f"Maximum allowed: {Config.MAX_TOKENS_PER_DAY} tokens per day.\n\n"
#             f"Please try again tomorrow."
#         )
#         return
    
#     # Generate new token
#     token = generate_token(Config.TOKEN_LENGTH)
#     unique_id = generate_unique_id(Config.UNIQUE_ID_LENGTH)
    
#     # Save token to database
#     token_data = TokenModel.create(
#         token=token,
#         unique_id=unique_id,
#         created_by=user_id,
#         status="not_used"
#     )
#     await TokenOperations.create_token(token_data)
    
#     # Increment token generation count
#     await TokenGeneratorCountOperations.increment_count(user_id)
    
#     # Create verification URL
#     verification_url = f"{Config.SERVER_URL}/redirect?token={token}"
    
#     # Shorten URL
#     shortened_url = await URLShortener.shorten_url(verification_url)
#     if not shortened_url:
#         shortened_url = verification_url
    
#     # Get media access count
#     media_access_count = await AdminConfigOperations.get_setting("media_access_count")
#     if not media_access_count:
#         media_access_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
    
#     # Get "how to verify" link
#     verify_link = await AdminConfigOperations.get_setting("verify_link")
#     if not verify_link:
#         verify_link = "https://t.me/your_channel/how_to_verify"
    
#     # Create inline keyboard
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="✅ Verify Now", url=shortened_url)],
#         [InlineKeyboardButton(text="❓ How to Verify", url=verify_link)]
#     ])
    
#     verification_text = f"""⚡️ ʜᴇʏ, {username} ×~

# ›› ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ᴀ ᴛᴏᴋᴇɴ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴀᴄᴄᴇss ꜰᴏʀ {media_access_count} media ✅"""
    
#     await message.answer(
#         verification_text,
#         reply_markup=keyboard
#     )


# ===========================================
# user_bot/handlers/verification.py
# ===========================================
# from aiogram import Router
# from aiogram.filters import CommandStart
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# from database.operations import TokenOperations, UserOperations, AdminConfigOperations, TokenGeneratorCountOperations
# from database.models import TokenModel
# from config.settings import Config
# from utils.token_generator import generate_token, generate_unique_id
# from utils.url_shortener import URLShortener

# router = Router()

# @router.message(CommandStart(deep_link=True))
# async def handle_verification_callback(message: Message):
#     """Handle verification callback from bypass server"""
#     # Check if it's a verification callback
#     args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
#     if not args.startswith('verify_'):
#         return  # Not a verification callback, let other handlers process
    
#     user_id = message.from_user.id
    
#     # Parse: verify_{unique_id}_{user_id}
#     parts = args.split('_')
#     if len(parts) != 3:
#         await message.answer("❌ Invalid verification link.")
#         return
    
#     unique_id = parts[1]
#     token_user_id = int(parts[2])
    
#     # Verify it's the same user
#     if user_id != token_user_id:
#         await message.answer("❌ This verification link is not for you.")
#         return
    
#     # Get token from database
#     token = await TokenOperations.get_token_by_unique_id(unique_id)
    
#     if not token:
#         await message.answer("❌ Token not found or expired.")
#         return
    
#     # Check token status
#     if token["status"] == "verified":
#         # Token verified successfully
#         # Add media access count to user
#         media_count = await AdminConfigOperations.get_setting("media_access_count")
#         if not media_count:
#             media_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
        
#         await UserOperations.increment_access_count(user_id, media_count)
        
#         # Delete token
#         await TokenOperations.delete_token(token["token"])
        
#         # Get updated user data
#         user = await UserOperations.get_user(user_id)
#         current_access = user.get("user_access_count", 0)
        
#         await message.answer(
#             f"✅ **Verification Successful!**\n\n"
#             f"You currently have **{current_access}** free media access."
#         )
    
#     elif token["status"] == "bypassed":
#         # Bypass detected
#         await message.answer(
#             "🚨 ʙʏᴘᴀss ᴅᴇᴛᴇᴄᴛᴇᴅ 🚨\n\n"
#             "ʜᴏᴡ ᴍᴀɴʏ ᴛɪᴍᴇs ʜᴀᴠᴇ ɪ ᴛᴏʟᴅ ʏᴏᴜ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛᴏ ᴏᴜᴛsᴍᴀʀᴛ ʏᴏᴜʀ ᴅᴀᴅ 🥸🖕\n\n"
#             "ɴᴏᴡ sᴏʟᴠᴇ ɪᴛ ᴘʀᴏᴘᴇʀʟʏ!!"
#         )
        
#         # Show current access count
#         user = await UserOperations.get_user(user_id)
#         current_access = user.get("user_access_count", 0) if user else 0
        
#         await message.answer(
#             f"You currently have **{current_access}** free media access."
#         )
    
#     else:
#         await message.answer("❌ Invalid token status.")

# @router.message(CommandStart(deep_link=True))
# async def handle_new_token_request(message: Message):
#     """Handle new token generation request"""
#     args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
#     if args != 'newToken':
#         return  # Not a new token request
    
#     user_id = message.from_user.id
#     username = message.from_user.first_name or message.from_user.username or "User"
    
#     # Check token generation limit
#     token_count_today = await TokenGeneratorCountOperations.get_count(user_id)
    
#     if token_count_today >= Config.MAX_TOKENS_PER_DAY:
#         await message.answer(
#             f"❌ **Daily Token Limit Reached**\n\n"
#             f"You have generated {token_count_today} tokens today.\n"
#             f"Maximum allowed: {Config.MAX_TOKENS_PER_DAY} tokens per day.\n\n"
#             f"Please try again tomorrow."
#         )
#         return
    
#     # Generate new token
#     token = generate_token(Config.TOKEN_LENGTH)
#     unique_id = generate_unique_id(Config.UNIQUE_ID_LENGTH)
    
#     # Save token to database
#     token_data = TokenModel.create(
#         token=token,
#         unique_id=unique_id,
#         created_by=user_id,
#         status="not_used"
#     )
#     await TokenOperations.create_token(token_data)
    
#     # Increment token generation count
#     await TokenGeneratorCountOperations.increment_count(user_id)
    
#     # Create verification URL
#     verification_url = f"{Config.SERVER_URL}/redirect?token={token}"
    
#     # Shorten URL
#     shortened_url = await URLShortener.shorten_url(verification_url)
#     if not shortened_url:
#         shortened_url = verification_url
    
#     # Get media access count
#     media_access_count = await AdminConfigOperations.get_setting("media_access_count")
#     if not media_access_count:
#         media_access_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
    
#     # Get "how to verify" link
#     verify_link = await AdminConfigOperations.get_setting("verify_link")
#     if not verify_link:
#         verify_link = "https://t.me/your_channel/how_to_verify"
    
#     # Create inline keyboard
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="✅ Verify Now", url=shortened_url)],
#         [InlineKeyboardButton(text="❓ How to Verify", url=verify_link)]
#     ])
    
#     verification_text = f"""⚡️ ʜᴇʏ, {username} ×~

# ›› ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ᴀ ᴛᴏᴋᴇɴ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴀᴄᴄᴇss ꜰᴏʀ {media_access_count} media ✅"""
    
#     await message.answer(
#         verification_text,
#         reply_markup=keyboard
#     )


# ===========================================
# user_bot/handlers/verification.py
# ===========================================
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.operations import TokenOperations, UserOperations, AdminConfigOperations, TokenGeneratorCountOperations
from database.models import TokenModel
from config.settings import Config
from utils.token_generator import generate_token, generate_unique_id
from utils.url_shortener import URLShortener

router = Router()

@router.message(CommandStart(deep_link=True))
async def handle_verification_callback(message: Message):
    """Handle verification callback from bypass server"""
    # Check if it's a verification callback
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
    if not args.startswith('verify_'):
        return  # Not a verification callback, let other handlers process
    
    user_id = message.from_user.id
    
    # Parse: verify_{unique_id}_{user_id}
    parts = args.split('_')
    if len(parts) != 3:
        await message.answer("❌ Invalid verification link.")
        return
    
    unique_id = parts[1]
    token_user_id = int(parts[2])
    
    # Verify it's the same user
    if user_id != token_user_id:
        await message.answer("❌ This verification link is not for you.")
        return
    
    # Get token from database
    token = await TokenOperations.get_token_by_unique_id(unique_id)
    
    if not token:
        await message.answer("❌ Token not found or expired.")
        return
    
    # Check token status
    if token["status"] == "verified":
        # Token verified successfully
        # Add media access count to user
        media_count = await AdminConfigOperations.get_setting("media_access_count")
        if not media_count:
            media_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
        
        await UserOperations.increment_access_count(user_id, media_count)
        
        # Delete token
        await TokenOperations.delete_token(token["token"])
        
        # Get updated user data
        user = await UserOperations.get_user(user_id)
        current_access = user.get("user_access_count", 0)
        
        await message.answer(
            f"✅ **Verification Successful!**\n\n"
            f"You currently have **{current_access}** free media access."
        )
    
    elif token["status"] == "bypassed":
        # Bypass detected
        await message.answer(
            "🚨 ʙʏᴘᴀss ᴅᴇᴛᴇᴄᴛᴇᴅ 🚨\n\n"
            "ʜᴏᴡ ᴍᴀɴʏ ᴛɪᴍᴇs ʜᴀᴠᴇ ɪ ᴛᴏʟᴅ ʏᴏᴜ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛᴏ ᴏᴜᴛsᴍᴀʀᴛ ʏᴏᴜʀ ᴅᴀᴅ 🥸🖕\n\n"
            "ɴᴏᴡ sᴏʟᴠᴇ ɪᴛ ᴘʀᴏᴘᴇʀʟʏ!!"
        )
        
        # Show current access count
        user = await UserOperations.get_user(user_id)
        current_access = user.get("user_access_count", 0) if user else 0
        
        await message.answer(
            f"You currently have **{current_access}** free media access."
        )
    
    else:
        await message.answer("❌ Invalid token status.")

@router.message(CommandStart(deep_link=True))
async def handle_new_token_request(message: Message):
    """Handle new token generation request"""
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    
    if args != 'newToken':
        return  # Not a new token request
    
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

›› ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ᴀ ᴛᴏᴋᴇɴ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴀᴄᴄᴇss ꜰᴏʀ {media_access_count} media ✅"""
    
    await message.answer(
        verification_text,
        reply_markup=keyboard
    )