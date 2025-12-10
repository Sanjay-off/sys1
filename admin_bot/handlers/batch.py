



# ===========================================
# admin_bot/handlers/batch.py
# ===========================================
from aiogram import F, Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import FileOperations
from database.models import FileModel
from utils.helpers import get_file_info, format_template
from utils.token_generator import generate_batch_unique_id

router = Router()

class BatchStates(StatesGroup):
    collecting_files = State()
    waiting_for_post_no = State()
    waiting_for_description = State()
    waiting_for_extra_message = State()

@router.message(Command("generate_batch"))
async def cmd_generate_batch(message: Message, state: FSMContext):
    """Start batch generation process"""
    await state.set_state(BatchStates.collecting_files)
    await state.update_data(batch_files=[])
    await message.answer(
        "📦 **Generate Batch Link**\n\n"
        "Start uploading files one by one. When done, type 'done'.\n\n"
        "Type /cancel to abort."
    )

@router.message(BatchStates.collecting_files, F.text.lower() == "done")
async def finish_collecting_files(message: Message, state: FSMContext):
    """Finish collecting files"""
    data = await state.get_data()
    batch_files = data.get("batch_files", [])
    
    if not batch_files:
        await message.answer("❌ No files collected. Please upload at least one file.")
        return
    
    await state.set_state(BatchStates.waiting_for_post_no)
    await message.answer(
        f"✅ {len(batch_files)} files collected!\n\n"
        "Now enter the **Post Number** (must be unique):"
    )

@router.message(BatchStates.collecting_files)
async def collect_batch_file(message: Message, state: FSMContext, bot: Bot):
    """Collect batch files"""
    from config.settings import Config
    
    file_info = get_file_info(message)
    
    if file_info["file_type"] == "unknown":
        await message.answer("❌ Unknown file type. Please upload a valid file.")
        return
    
    # Forward to private channel
    try:
        forwarded_msg = await bot.forward_message(
            chat_id=Config.PRIVATE_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        data = await state.get_data()
        batch_files = data.get("batch_files", [])
        
        batch_files.append({
            "file_type": file_info["file_type"],
            "file_id": file_info["file_id"],
            "text_content": file_info["text_content"],
            "channel_message_id": forwarded_msg.message_id
        })
        
        await state.update_data(batch_files=batch_files)
        await message.answer(
            f"✅ File #{len(batch_files)} added!\n\n"
            "Upload next file or type 'done' to finish."
        )
    
    except Exception as e:
        await message.answer(f"❌ Error uploading file: {e}")

@router.message(BatchStates.waiting_for_post_no)
async def process_batch_post_no(message: Message, state: FSMContext):
    """Process batch post number"""
    try:
        post_no = int(message.text.strip())
        
        if await FileOperations.post_no_exists(post_no):
            await message.answer(
                f"❌ Post number {post_no} already exists!\n\n"
                "Please enter a different post number:"
            )
            return
        
        await state.update_data(post_no=post_no)
        await state.set_state(BatchStates.waiting_for_description)
        await message.answer("📝 Enter the **Description**:")
    
    except ValueError:
        await message.answer("❌ Invalid post number. Please enter a valid number:")

@router.message(BatchStates.waiting_for_description)
async def process_batch_description(message: Message, state: FSMContext):
    """Process batch description"""
    description = message.text.strip()
    
    await state.update_data(description=description)
    await state.set_state(BatchStates.waiting_for_extra_message)
    await message.answer("💬 Enter the **Extra Message**:")

@router.message(BatchStates.waiting_for_extra_message)
async def process_batch_extra_message(message: Message, state: FSMContext, bot: Bot):
    """Process extra message and generate batch link"""
    extra_message = message.text.strip()
    data = await state.get_data()
    
    # Generate unique ID for batch
    unique_id = generate_batch_unique_id()
    
    # Create file record for batch
    file_data = FileModel.create(
        unique_id=unique_id,
        post_no=data["post_no"],
        description=data["description"],
        extra_message=extra_message,
        file_type="batch",
        is_batch=True,
        batch_file_ids=data["batch_files"]
    )
    
    await FileOperations.create_file(file_data)
    
    # Generate deeplink - Get USER BOT username
    from config.settings import Config
    from aiogram import Bot as TempBot
    from aiogram.client.session.aiohttp import AiohttpSession
    
    session = AiohttpSession()
    user_bot = TempBot(token=Config.USER_BOT_TOKEN, session=session)
    try:
        user_bot_info = await user_bot.get_me()
        deeplink = f"https://t.me/{user_bot_info.username}?start=batch_{unique_id}"
    finally:
        await session.close()
    
    # Format template
    template = format_template(
        post_no=data["post_no"],
        description=data["description"],
        extra_message=extra_message,
        deeplink=deeplink
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Download", url=deeplink)]
    ])
    
    await message.answer("✅ **Batch Link Generated Successfully!**\n\n━━━━━━━━━━━━━━━━━━━━")
    await message.answer(template, reply_markup=keyboard)
    await message.answer(
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 **Details:**\n"
        f"• Unique ID: `{unique_id}`\n"
        f"• Post No: {data['post_no']}\n"
        f"• Total Files: {len(data['batch_files'])}"
    )
    
    await state.clear()