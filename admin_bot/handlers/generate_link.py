#


# ===========================================
# admin_bot/handlers/generate_link.py
# ===========================================
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.settings import Config
from database.operations import FileOperations
from database.models import FileModel
from utils.helpers import get_file_info, format_template, is_zip_file
from utils.token_generator import generate_unique_id

router = Router()

class GenerateLinkStates(StatesGroup):
    waiting_for_resource = State()
    waiting_for_post_no = State()
    waiting_for_description = State()
    waiting_for_extra_message = State()

@router.message(Command("generate_link"))
async def cmd_generate_link(message: Message, state: FSMContext):
    """Start generate link process"""
    await state.set_state(GenerateLinkStates.waiting_for_resource)
    await message.answer(
        "📤 **Generate Link Process Started**\n\n"
        "Please upload the resource (photo, video, document, or text message).\n\n"
        "Type /cancel to abort."
    )

@router.message(GenerateLinkStates.waiting_for_resource)
async def process_resource(message: Message, state: FSMContext, bot: Bot):
    """Process uploaded resource"""
    # Get file info
    file_info = get_file_info(message)
    
    if file_info["file_type"] == "unknown":
        await message.answer("❌ Unknown file type. Please upload a valid resource.")
        return
    
    # Forward to private channel
    try:
        forwarded_msg = await bot.forward_message(
            chat_id=Config.PRIVATE_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        # Store resource info in FSM
        await state.update_data(
            file_type=file_info["file_type"],
            file_id=file_info["file_id"],
            text_content=file_info["text_content"],
            channel_message_id=forwarded_msg.message_id
        )
        
        await state.set_state(GenerateLinkStates.waiting_for_post_no)
        await message.answer(
            "✅ Resource uploaded to private channel!\n\n"
            "Now, enter the **Post Number** (must be unique):"
        )
    
    except Exception as e:
        await message.answer(f"❌ Error uploading to private channel: {e}")
        await state.clear()

@router.message(GenerateLinkStates.waiting_for_post_no)
async def process_post_no(message: Message, state: FSMContext):
    """Process post number"""
    try:
        post_no = int(message.text.strip())
        
        # Check if post_no already exists
        if await FileOperations.post_no_exists(post_no):
            await message.answer(
                f"❌ Post number {post_no} already exists!\n\n"
                "Please enter a different post number:"
            )
            return
        
        await state.update_data(post_no=post_no)
        await state.set_state(GenerateLinkStates.waiting_for_description)
        await message.answer("📝 Enter the **Description**:")
    
    except ValueError:
        await message.answer("❌ Invalid post number. Please enter a valid number:")

@router.message(GenerateLinkStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Process description"""
    description = message.text.strip()
    
    await state.update_data(description=description)
    await state.set_state(GenerateLinkStates.waiting_for_extra_message)
    await message.answer("💬 Enter the **Extra Message**:")

@router.message(GenerateLinkStates.waiting_for_extra_message)
async def process_extra_message(message: Message, state: FSMContext, bot: Bot):
    """Process extra message and generate link"""
    extra_message = message.text.strip()
    
    # Get all data from FSM
    data = await state.get_data()
    
    # Generate unique ID
    unique_id = generate_unique_id(30)
    
    # Create file record
    file_data = FileModel.create(
        unique_id=unique_id,
        post_no=data["post_no"],
        description=data["description"],
        extra_message=extra_message,
        file_type=data["file_type"],
        file_id=data.get("file_id"),
        text_content=data.get("text_content"),
        channel_message_id=data["channel_message_id"]
    )
    
    # Save to database
    await FileOperations.create_file(file_data)
    
    # Generate deeplink - Get USER BOT username
    from config.settings import Config
    from aiogram import Bot as TempBot
    from aiogram.client.session.aiohttp import AiohttpSession
    
    # Create temporary user bot instance
    session = AiohttpSession()
    user_bot = TempBot(token=Config.USER_BOT_TOKEN, session=session)
    try:
        user_bot_info = await user_bot.get_me()
        deeplink = f"https://t.me/{user_bot_info.username}?start={unique_id}"
    finally:
        await session.close()
    
    # Format template
    template = format_template(
        post_no=data["post_no"],
        description=data["description"],
        extra_message=extra_message,
        deeplink=deeplink
    )
    
    # Create inline keyboard with download button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Download", url=deeplink)]
    ])
    
    # Send template to admin
    await message.answer(
        "✅ **Link Generated Successfully!**\n\n"
        "Here's your template (copy and post to public group):\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    
    await message.answer(
        template,
        reply_markup=keyboard
    )
    
    await message.answer(
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 **Details:**\n"
        f"• Unique ID: `{unique_id}`\n"
        f"• Post No: {data['post_no']}\n"
        f"• File Type: {data['file_type']}\n"
        f"• Channel Message ID: {data['channel_message_id']}"
    )
    
    # Clear FSM
    await state.clear()

@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel any ongoing operation"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("❌ No operation to cancel.")
        return
    
    await state.clear()
    await message.answer("✅ Operation cancelled.")