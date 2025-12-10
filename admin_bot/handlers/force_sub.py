
# ===========================================
# admin_bot/handlers/force_sub.py
# ===========================================
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import AdminConfigOperations
from database.models import AdminConfigModel

router = Router()

class ForceSubStates(StatesGroup):
    waiting_for_channel_link = State()
    waiting_for_placeholder = State()

@router.message(Command("add_force_sub"))
async def cmd_add_force_sub(message: Message, state: FSMContext):
    """Add force sub channel"""
    await state.set_state(ForceSubStates.waiting_for_channel_link)
    await message.answer(
        "📺 **Add Force Sub Channel**\n\n"
        "Send the channel link or channel ID (e.g., @channelname or -1001234567890):\n\n"
        "Type /cancel to abort."
    )

@router.message(ForceSubStates.waiting_for_channel_link)
async def process_channel_link(message: Message, state: FSMContext):
    """Process channel link"""
    channel_input = message.text.strip()
    
    # Extract channel username or ID
    if channel_input.startswith("@"):
        channel_username = channel_input
        channel_id = None  # Will be resolved later
    elif channel_input.startswith("-100"):
        try:
            channel_id = int(channel_input)
            channel_username = channel_input
        except:
            await message.answer("❌ Invalid channel ID. Please try again:")
            return
    else:
        await message.answer("❌ Invalid format. Please send @channelname or channel ID:")
        return
    
    await state.update_data(
        channel_username=channel_username,
        channel_id=channel_id or 0  # Placeholder
    )
    await state.set_state(ForceSubStates.waiting_for_placeholder)
    await message.answer("📝 Now enter the **placeholder text** for this channel:")

@router.message(ForceSubStates.waiting_for_placeholder)
async def process_placeholder(message: Message, state: FSMContext):
    """Process placeholder and save channel"""
    placeholder = message.text.strip()
    data = await state.get_data()
    
    # Create channel config
    channel_data = AdminConfigModel.create_force_sub_channel(
        channel_id=data["channel_id"],
        channel_username=data["channel_username"],
        placeholder=placeholder
    )
    
    await AdminConfigOperations.add_force_sub_channel(channel_data)
    
    await message.answer(
        f"✅ **Force Sub Channel Added!**\n\n"
        f"Channel: {data['channel_username']}\n"
        f"Placeholder: {placeholder}"
    )
    
    await state.clear()

@router.message(Command("list_force_sub"))
async def cmd_list_force_sub(message: Message):
    """List all force sub channels"""
    channels = await AdminConfigOperations.get_force_sub_channels()
    
    if not channels:
        await message.answer("📭 No force sub channels configured.")
        return
    
    text = "📺 **Force Sub Channels:**\n\n"
    for i, channel in enumerate(channels, 1):
        text += f"{i}. {channel['channel_username']}\n"
        text += f"   Placeholder: {channel['placeholder']}\n\n"
    
    await message.answer(text)

@router.message(Command("remove_force_sub"))
async def cmd_remove_force_sub(message: Message):
    """Remove force sub channel"""
    channels = await AdminConfigOperations.get_force_sub_channels()
    
    if not channels:
        await message.answer("📭 No force sub channels to remove.")
        return
    
    # Create inline keyboard with channels
    keyboard = []
    for channel in channels:
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {channel['placeholder']}",
                callback_data=f"remove_channel_{channel['channel_id']}"
            )
        ])
    
    await message.answer(
        "📺 **Select channel to remove:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("remove_channel_"))
async def process_remove_channel(callback: CallbackQuery):
    """Process channel removal"""
    channel_id = int(callback.data.split("_")[-1])
    
    await AdminConfigOperations.remove_force_sub_channel(channel_id)
    
    await callback.message.edit_text("✅ Channel removed from force sub list!")
    await callback.answer()