
# ===========================================
# admin_bot/handlers/user_management.py
# ===========================================
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from database.operations import UserOperations, AdminConfigOperations
from config.settings import Config

router = Router()

class UserManagementStates(StatesGroup):
    waiting_for_ban_user_id = State()
    waiting_for_unban_user_id = State()
    waiting_for_verify_user_id = State()
    waiting_for_verify_duration = State()
    waiting_for_unverify_user_id = State()
    waiting_for_paid_user_id = State()
    waiting_for_paid_count = State()

@router.message(Command("verification_stats"))
async def cmd_verification_stats(message: Message):
    """Show verification statistics"""
    verified_count = await UserOperations.get_verified_users_count()
    
    await message.answer(
        f"📊 **Verification Statistics**\n\n"
        f"✅ Verified Users: {verified_count}"
    )

@router.message(Command("ban_user"))
async def cmd_ban_user(message: Message, state: FSMContext):
    """Ban a user"""
    await state.set_state(UserManagementStates.waiting_for_ban_user_id)
    await message.answer(
        "🚫 **Ban User**\n\n"
        "Enter the user ID to ban:\n\n"
        "Type /cancel to abort."
    )

@router.message(UserManagementStates.waiting_for_ban_user_id)
async def process_ban_user(message: Message, state: FSMContext):
    """Process ban user"""
    try:
        user_id = int(message.text.strip())
        await UserOperations.ban_user(user_id)
        await message.answer(f"✅ User {user_id} has been banned.")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a valid number:")

@router.message(Command("unban_user"))
async def cmd_unban_user(message: Message, state: FSMContext):
    """Unban a user"""
    await state.set_state(UserManagementStates.waiting_for_unban_user_id)
    await message.answer(
        "✅ **Unban User**\n\n"
        "Enter the user ID to unban:\n\n"
        "Type /cancel to abort."
    )

@router.message(UserManagementStates.waiting_for_unban_user_id)
async def process_unban_user(message: Message, state: FSMContext):
    """Process unban user"""
    try:
        user_id = int(message.text.strip())
        await UserOperations.unban_user(user_id)
        await message.answer(f"✅ User {user_id} has been unbanned.")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a valid number:")

@router.message(Command("set_verified"))
async def cmd_set_verified(message: Message, state: FSMContext):
    """Manually verify a user"""
    await state.set_state(UserManagementStates.waiting_for_verify_user_id)
    await message.answer(
        "✅ **Set User Verified**\n\n"
        "Enter the user ID:\n\n"
        "Type /cancel to abort."
    )

@router.message(UserManagementStates.waiting_for_verify_user_id)
async def process_verify_user_id(message: Message, state: FSMContext):
    """Process verify user ID"""
    try:
        user_id = int(message.text.strip())
        await state.update_data(user_id=user_id)
        await state.set_state(UserManagementStates.waiting_for_verify_duration)
        await message.answer("⏰ Enter duration in hours (e.g., 24 for 1 day):")
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a valid number:")

@router.message(UserManagementStates.waiting_for_verify_duration)
async def process_verify_duration(message: Message, state: FSMContext):
    """Process verify duration"""
    try:
        hours = int(message.text.strip())
        data = await state.get_data()
        user_id = data["user_id"]
        
        verified_until = datetime.utcnow() + timedelta(hours=hours)
        media_count = await AdminConfigOperations.get_setting("media_access_count")
        if not media_count:
            media_count = Config.DEFAULT_MEDIA_ACCESS_COUNT
        
        await UserOperations.update_user(user_id, {
            "verified_until": verified_until,
            "user_access_count": media_count
        })
        
        await message.answer(
            f"✅ User {user_id} verified for {hours} hours with {media_count} media access."
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid duration. Please enter a valid number:")

@router.message(Command("unset_verified"))
async def cmd_unset_verified(message: Message, state: FSMContext):
    """Unverify a user"""
    await state.set_state(UserManagementStates.waiting_for_unverify_user_id)
    await message.answer(
        "❌ **Unverify User**\n\n"
        "Enter the user ID:\n\n"
        "Type /cancel to abort."
    )

@router.message(UserManagementStates.waiting_for_unverify_user_id)
async def process_unverify_user(message: Message, state: FSMContext):
    """Process unverify user"""
    try:
        user_id = int(message.text.strip())
        await UserOperations.update_user(user_id, {
            "user_access_count": 0,
            "verified_until": None
        })
        await message.answer(f"✅ User {user_id} has been unverified.")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a valid number:")

@router.message(Command("set_user_media_count"))
async def cmd_set_user_media_count(message: Message, state: FSMContext):
    """Set paid media count for specific user"""
    await state.set_state(UserManagementStates.waiting_for_paid_user_id)
    await message.answer(
        "👤 **Set User Media Count**\n\n"
        "Enter the user ID:\n\n"
        "Type /cancel to abort."
    )

@router.message(UserManagementStates.waiting_for_paid_user_id)
async def process_paid_user_id(message: Message, state: FSMContext):
    """Process paid user ID"""
    try:
        user_id = int(message.text.strip())
        await state.update_data(user_id=user_id)
        await state.set_state(UserManagementStates.waiting_for_paid_count)
        await message.answer("🔢 Enter the media access count:")
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a valid number:")

@router.message(UserManagementStates.waiting_for_paid_count)
async def process_paid_count(message: Message, state: FSMContext):
    """Process paid media count"""
    try:
        count = int(message.text.strip())
        data = await state.get_data()
        user_id = data["user_id"]
        
        await UserOperations.update_user(user_id, {"user_access_count": count})
        
        await message.answer(f"✅ User {user_id} media access count set to {count}.")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid count. Please enter a valid number:")