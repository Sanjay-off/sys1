
# ===========================================
# admin_bot/handlers/settings.py
# ===========================================
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import AdminConfigOperations
from config.settings import Config

router = Router()

class SettingsStates(StatesGroup):
    waiting_for_media_count = State()
    waiting_for_password = State()
    waiting_for_deletion_time = State()
    waiting_for_verify_link = State()

@router.message(Command("set_media_count"))
async def cmd_set_media_count(message: Message, state: FSMContext):
    """Set free media access count"""
    await state.set_state(SettingsStates.waiting_for_media_count)
    await message.answer(
        "🔢 **Set Free Media Access Count**\n\n"
        "Enter the count (number of free media access per verification):\n\n"
        "Type /cancel to abort."
    )

@router.message(SettingsStates.waiting_for_media_count)
async def process_media_count(message: Message, state: FSMContext):
    """Process media count"""
    try:
        count = int(message.text.strip())
        await AdminConfigOperations.set_setting("media_access_count", count)
        await message.answer(f"✅ Free media access count set to {count}.")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid count. Please enter a valid number:")

@router.message(Command("set_password"))
async def cmd_set_password(message: Message, state: FSMContext):
    """Set zip file password"""
    await state.set_state(SettingsStates.waiting_for_password)
    await message.answer(
        "🔐 **Set Zip File Password**\n\n"
        "Enter the new password for zip files:\n\n"
        "Type /cancel to abort."
    )

@router.message(SettingsStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """Process password"""
    password = message.text.strip()
    await AdminConfigOperations.set_setting("zip_password", password)
    await message.answer(f"✅ Zip file password set to: `{password}`")
    await state.clear()

@router.message(Command("set_deletion_time"))
async def cmd_set_deletion_time(message: Message, state: FSMContext):
    """Set resource deletion time"""
    await state.set_state(SettingsStates.waiting_for_deletion_time)
    await message.answer(
        "⏰ **Set Deletion Time**\n\n"
        "Enter deletion time in minutes:\n\n"
        "Type /cancel to abort."
    )

@router.message(SettingsStates.waiting_for_deletion_time)
async def process_deletion_time(message: Message, state: FSMContext):
    """Process deletion time"""
    try:
        minutes = int(message.text.strip())
        await AdminConfigOperations.set_setting("deletion_time", minutes)
        
        from utils.helpers import format_duration
        await message.answer(
            f"✅ Deletion time set to {format_duration(minutes)}."
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid time. Please enter a valid number:")

@router.message(Command("set_verify_link"))
async def cmd_set_verify_link(message: Message, state: FSMContext):
    """Set how to verify link"""
    await state.set_state(SettingsStates.waiting_for_verify_link)
    await message.answer(
        "🔗 **Set How To Verify Link**\n\n"
        "Send the deeplink (e.g., t.me/channel/123):\n\n"
        "Type /cancel to abort."
    )

@router.message(SettingsStates.waiting_for_verify_link)
async def process_verify_link(message: Message, state: FSMContext):
    """Process verify link"""
    link = message.text.strip()
    await AdminConfigOperations.set_setting("verify_link", link)
    await message.answer(f"✅ How to verify link set to: {link}")
    await state.clear()