

# ===========================================
# user_bot/handlers/join_request.py
# ===========================================
from aiogram import Router, F
from aiogram.types import ChatJoinRequest

from database.operations import UserOperations, AdminConfigOperations

router = Router()

@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    """Handle join requests to private channels"""
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id
    
    # Check if this channel is in force sub list
    force_sub_channels = await AdminConfigOperations.get_force_sub_channels()
    channel_ids = [ch["channel_id"] for ch in force_sub_channels]
    
    if chat_id in channel_ids:
        # Add to user's join requests
        await UserOperations.add_join_request(user_id, chat_id)
        print(f"✅ Join request tracked: User {user_id} → Channel {chat_id}")