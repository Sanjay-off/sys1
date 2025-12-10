

# ===========================================
# admin_bot/handlers/regenerate_post.py
# ===========================================
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import FileOperations
from utils.helpers import format_template
from config.settings import Config

router = Router()

class RegeneratePostStates(StatesGroup):
    waiting_for_post_no = State()

@router.message(Command("regenerate_post"))
async def cmd_regenerate_post(message: Message, state: FSMContext):
    """Start regenerate post process"""
    await state.set_state(RegeneratePostStates.waiting_for_post_no)
    await message.answer(
        "🔄 **Regenerate Post Template**\n\n"
        "Enter the **Post Number** to regenerate:\n\n"
        "Type /cancel to abort."
    )

@router.message(RegeneratePostStates.waiting_for_post_no)
async def process_regenerate(message: Message, state: FSMContext, bot: Bot):
    """Process post number and regenerate template"""
    try:
        post_no = int(message.text.strip())
        
        # Get file from database
        file_data = await FileOperations.get_file_by_post_no(post_no)
        
        if not file_data:
            await message.answer(
                f"❌ Post number {post_no} not found!\n\n"
                "Please enter a valid post number or type /cancel:"
            )
            return
        
        # Generate deeplink using USER BOT username
        from aiogram import Bot as TempBot
        from aiogram.client.session.aiohttp import AiohttpSession
        
        session = AiohttpSession()
        user_bot = TempBot(token=Config.USER_BOT_TOKEN, session=session)
        try:
            user_bot_info = await user_bot.get_me()
            
            unique_id = file_data["unique_id"]
            
            # Check if it's a batch
            if file_data.get("is_batch", False):
                deeplink = f"https://t.me/{user_bot_info.username}?start=batch_{unique_id}"
            else:
                deeplink = f"https://t.me/{user_bot_info.username}?start={unique_id}"
        finally:
            await session.close()
        
        # Format template
        template = format_template(
            post_no=file_data["post_no"],
            description=file_data["description"],
            extra_message=file_data["extra_message"],
            deeplink=deeplink
        )
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Download", url=deeplink)]
        ])
        
        # Send template
        await message.answer(
            "✅ **Template Regenerated Successfully!**\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        
        await message.answer(
            template,
            reply_markup=keyboard
        )
        
        batch_info = ""
        if file_data.get("is_batch", False):
            batch_count = len(file_data.get("batch_file_ids", []))
            batch_info = f"\n• Batch Files: {batch_count}"
        
        await message.answer(
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **Details:**\n"
            f"• Unique ID: `{unique_id}`\n"
            f"• Post No: {file_data['post_no']}\n"
            f"• File Type: {file_data['file_type']}{batch_info}"
        )
        
        # Clear FSM
        await state.clear()
    
    except ValueError:
        await message.answer("❌ Invalid post number. Please enter a valid number:")