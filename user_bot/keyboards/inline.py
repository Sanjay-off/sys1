
# ===========================================
# user_bot/keyboards/inline.py
# ===========================================
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_verification_keyboard(verify_url: str, how_to_verify_url: str) -> InlineKeyboardMarkup:
    """Get verification keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Now", url=verify_url)],
        [InlineKeyboardButton(text="❓ How to Verify", url=how_to_verify_url)]
    ])

def get_force_sub_keyboard(channels: list, try_again_url: str) -> InlineKeyboardMarkup:
    """Get force subscription keyboard"""
    keyboard = []
    
    # Add channel buttons (2 per row)
    for i in range(0, len(channels), 2):
        row = []
        for j in range(2):
            if i + j < len(channels):
                channel = channels[i + j]
                channel_link = f"https://t.me/{channel['channel_username'].replace('@', '')}"
                row.append(
                    InlineKeyboardButton(
                        text=channel['placeholder'],
                        url=channel_link
                    )
                )
        keyboard.append(row)
    
    # Add try again button
    keyboard.append([
        InlineKeyboardButton(text="🔄 Try Again", url=try_again_url)
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_resource_deleted_keyboard(deeplink: str) -> InlineKeyboardMarkup:
    """Get keyboard for deleted resource message"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Click Here", url=deeplink)],
        [InlineKeyboardButton(text="❌ Close", callback_data="close_message")]
    ])