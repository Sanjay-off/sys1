

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

@router.message(Command("set_user_media_count"))
async def cmd_set_user_media_count(message: Message, state: FSMContext):
    """ADD media count for specific user (not replace)"""
    await state.set_state(UserManagementStates.waiting_for_paid_user_id)
    await message.answer(
        "👤 **Add User Media Count**\n\n"
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
        await message.answer("🔢 Enter the count to ADD (not replace):")
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a valid number:")

@router.message(UserManagementStates.waiting_for_paid_count)
async def process_paid_count(message: Message, state: FSMContext):
    """Process paid media count - ADD not replace"""
    try:
        count = int(message.text.strip())
        data = await state.get_data()
        user_id = data["user_id"]
        
        # Get current count
        user = await UserOperations.get_user(user_id)
        current_count = user.get("user_access_count", 0) if user else 0
        
        # ADD to existing count
        new_count = current_count + count
        await UserOperations.update_user(user_id, {"user_access_count": new_count})
        
        await message.answer(
            f"✅ Added {count} to user {user_id}\n"
            f"Previous: {current_count}\n"
            f"New Total: {new_count}"
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid count. Please enter a valid number:")