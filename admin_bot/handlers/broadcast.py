
# # ===========================================
# # admin_bot/handlers/broadcast.py
# # ===========================================
# from aiogram import Router, Bot
# from aiogram.filters import Command, StateFilter
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# import asyncio
# from datetime import datetime, timedelta

# from database.operations import UserOperations, BroadcastOperations
# from database.models import BroadcastModel
# from config.settings import Config
# from utils.helpers import get_file_info

# router = Router()

# class BroadcastStates(StatesGroup):
#     waiting_for_content = State()
#     waiting_for_duration = State()

# @router.message(Command("broadcast"))
# async def cmd_broadcast(message: Message, state: FSMContext):
#     """Start broadcast process"""
#     await state.set_state(BroadcastStates.waiting_for_content)
#     await message.answer(
#         "📢 **Broadcast Message**\n\n"
#         "Send the content to broadcast (photo, video, document, or text):\n\n"
#         "Type /cancel to abort."
#     )

# @router.message(BroadcastStates.waiting_for_content)
# async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
#     """Process broadcast content"""
#     file_info = get_file_info(message)
    
#     if file_info["file_type"] == "unknown":
#         await message.answer("❌ Unknown content type. Please send a valid message.")
#         return
    
#     # Forward to private channel
#     try:
#         forwarded_msg = await bot.forward_message(
#             chat_id=Config.PRIVATE_CHANNEL_ID,
#             from_chat_id=message.chat.id,
#             message_id=message.message_id
#         )
        
#         await state.update_data(
#             message_id=message.message_id,
#             channel_message_id=forwarded_msg.message_id,
#             file_type=file_info["file_type"],
#             file_id=file_info["file_id"],
#             text_content=file_info["text_content"],
#             caption=message.caption
#         )
        
#         await state.set_state(BroadcastStates.waiting_for_duration)
#         await message.answer(
#             "✅ Content uploaded!\n\n"
#             "⏰ Enter duration in hours (how long the message should stay):"
#         )
    
#     except Exception as e:
#         await message.answer(f"❌ Error uploading content: {e}")
#         await state.clear()

# @router.message(BroadcastStates.waiting_for_duration)
# async def process_broadcast_duration(message: Message, state: FSMContext, bot: Bot):
#     """Process duration and start broadcasting"""
#     try:
#         duration_hours = int(message.text.strip())
#         data = await state.get_data()
        
#         # Create broadcast record
#         broadcast_data = BroadcastModel.create(
#             message_id=data["message_id"],
#             channel_message_id=data["channel_message_id"],
#             file_type=data["file_type"],
#             file_id=data.get("file_id"),
#             text_content=data.get("text_content"),
#             caption=data.get("caption"),
#             duration_hours=duration_hours
#         )
        
#         broadcast_id = await BroadcastOperations.create_broadcast(broadcast_data)
        
#         status_msg = await message.answer(
#             "📤 Starting broadcast...\n"
#             f"Duration: {duration_hours} hours\n"
#             "Progress: 0/?"
#         )
        
#         # Get all user IDs
#         user_ids = await UserOperations.get_all_user_ids()
#         total_users = len(user_ids)
#         sent_count = 0
#         failed_count = 0
        
#         # Broadcast to users (2 per second)
#         for i, user_id in enumerate(user_ids):
#             try:
#                 if data["file_type"] == "text":
#                     await bot.send_message(
#                         chat_id=user_id,
#                         text=data["text_content"]
#                     )
#                 else:
#                     await bot.copy_message(
#                         chat_id=user_id,
#                         from_chat_id=Config.PRIVATE_CHANNEL_ID,
#                         message_id=data["channel_message_id"]
#                     )
#                 sent_count += 1
#             except Exception as e:
#                 failed_count += 1
#                 print(f"Failed to send to {user_id}: {e}")
            
#             # Rate limiting: 2 users per second
#             if (i + 1) % 2 == 0:
#                 await asyncio.sleep(1)
            
#             # Update status every 10 users
#             if (i + 1) % 10 == 0:
#                 try:
#                     await status_msg.edit_text(
#                         f"📤 Broadcasting...\n"
#                         f"Duration: {duration_hours} hours\n"
#                         f"Progress: {i + 1}/{total_users}\n"
#                         f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}"
#                     )
#                 except:
#                     pass
        
#         # Update broadcast stats
#         await BroadcastOperations.update_broadcast_stats(
#             broadcast_id, sent_count, failed_count
#         )
        
#         # Set delete time
#         delete_at = datetime.utcnow() + timedelta(hours=duration_hours)
#         await BroadcastOperations.set_broadcast_delete_time(broadcast_id, delete_at)
        
#         # Final status
#         await status_msg.edit_text(
#             f"✅ **Broadcast Complete!**\n\n"
#             f"Total Users: {total_users}\n"
#             f"✅ Sent: {sent_count}\n"
#             f"❌ Failed: {failed_count}\n"
#             f"⏰ Will be deleted in {duration_hours} hours"
#         )
        
#         # TODO: Implement auto-deletion in Phase 4
        
#         await state.clear()
    
#     except ValueError:
#         await message.answer("❌ Invalid duration. Please enter a valid number:")




# # ===========================================
# # admin_bot/handlers/broadcast.py
# # ===========================================
# from aiogram import Router, Bot
# from aiogram.filters import Command, StateFilter
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# import asyncio
# from datetime import datetime, timedelta

# from database.operations import UserOperations, BroadcastOperations
# from database.models import BroadcastModel
# from config.settings import Config
# from utils.helpers import get_file_info

# router = Router()

# class BroadcastStates(StatesGroup):
#     waiting_for_content = State()
#     waiting_for_duration = State()

# @router.message(Command("broadcast"))
# async def cmd_broadcast(message: Message, state: FSMContext):
#     """Start broadcast process"""
#     await state.set_state(BroadcastStates.waiting_for_content)
#     await message.answer(
#         "📢 **Broadcast Message**\n\n"
#         "Send the content to broadcast (photo, video, document, or text):\n\n"
#         "Type /cancel to abort."
#     )

# @router.message(BroadcastStates.waiting_for_content)
# async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
#     """Process broadcast content"""
#     file_info = get_file_info(message)
    
#     if file_info["file_type"] == "unknown":
#         await message.answer("❌ Unknown content type. Please send a valid message.")
#         return
    
#     # Forward to private channel
#     try:
#         forwarded_msg = await bot.forward_message(
#             chat_id=Config.PRIVATE_CHANNEL_ID,
#             from_chat_id=message.chat.id,
#             message_id=message.message_id
#         )
        
#         await state.update_data(
#             message_id=message.message_id,
#             channel_message_id=forwarded_msg.message_id,
#             file_type=file_info["file_type"],
#             file_id=file_info["file_id"],
#             text_content=file_info["text_content"],
#             caption=message.caption
#         )
        
#         await state.set_state(BroadcastStates.waiting_for_duration)
#         await message.answer(
#             "✅ Content uploaded!\n\n"
#             "⏰ Enter duration in hours (how long the message should stay):"
#         )
    
#     except Exception as e:
#         await message.answer(f"❌ Error uploading content: {e}")
#         await state.clear()

# @router.message(BroadcastStates.waiting_for_duration)
# async def process_broadcast_duration(message: Message, state: FSMContext, bot: Bot):
#     """Process duration and start broadcasting"""
#     try:
#         duration_hours = int(message.text.strip())
#         data = await state.get_data()
        
#         # Create broadcast record
#         broadcast_data = BroadcastModel.create(
#             message_id=data["message_id"],
#             channel_message_id=data["channel_message_id"],
#             file_type=data["file_type"],
#             file_id=data.get("file_id"),
#             text_content=data.get("text_content"),
#             caption=data.get("caption"),
#             duration_hours=duration_hours
#         )
        
#         broadcast_id = await BroadcastOperations.create_broadcast(broadcast_data)
        
#         status_msg = await message.answer(
#             "📤 Starting broadcast...\n"
#             f"Duration: {duration_hours} hours\n"
#             "Progress: 0/?"
#         )
        
#         # Get all user IDs
#         user_ids = await UserOperations.get_all_user_ids()
#         total_users = len(user_ids)
#         sent_count = 0
#         failed_count = 0
        
#         # Broadcast to users (2 per second)
#         for i, user_id in enumerate(user_ids):
#             try:
#                 if data["file_type"] == "text":
#                     await bot.send_message(
#                         chat_id=user_id,
#                         text=data["text_content"]
#                     )
#                 else:
#                     await bot.copy_message(
#                         chat_id=user_id,
#                         from_chat_id=Config.PRIVATE_CHANNEL_ID,
#                         message_id=data["channel_message_id"]
#                     )
#                 sent_count += 1
#             except Exception as e:
#                 failed_count += 1
#                 print(f"Failed to send to {user_id}: {e}")
            
#             # Rate limiting: 2 users per second
#             if (i + 1) % 2 == 0:
#                 await asyncio.sleep(1)
            
#             # Update status every 10 users
#             if (i + 1) % 10 == 0:
#                 try:
#                     await status_msg.edit_text(
#                         f"📤 Broadcasting...\n"
#                         f"Duration: {duration_hours} hours\n"
#                         f"Progress: {i + 1}/{total_users}\n"
#                         f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}"
#                     )
#                 except:
#                     pass
        
#         # Update broadcast stats
#         await BroadcastOperations.update_broadcast_stats(
#             broadcast_id, sent_count, failed_count
#         )
        
#         # Set delete time
#         delete_at = datetime.utcnow() + timedelta(hours=duration_hours)
#         await BroadcastOperations.set_broadcast_delete_time(broadcast_id, delete_at)
        
#         # Final status
#         await status_msg.edit_text(
#             f"✅ **Broadcast Complete!**\n\n"
#             f"Total Users: {total_users}\n"
#             f"✅ Sent: {sent_count}\n"
#             f"❌ Failed: {failed_count}\n"
#             f"⏰ Will be deleted in {duration_hours} hours"
#         )
        
#         # TODO: Implement auto-deletion in Phase 4
        
#         await state.clear()
    
#     except ValueError:
#         await message.answer("❌ Invalid duration. Please enter a valid number:")


# ===========================================
# admin_bot/handlers/broadcast.py
# ===========================================
# from aiogram import Router, Bot
# from aiogram.filters import Command, StateFilter
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# import asyncio
# from datetime import datetime, timedelta

# from database.operations import UserOperations, BroadcastOperations
# from database.models import BroadcastModel
# from config.settings import Config
# from utils.helpers import get_file_info

# router = Router()

# class BroadcastStates(StatesGroup):
#     waiting_for_content = State()
#     waiting_for_duration = State()

# @router.message(Command("broadcast"))
# async def cmd_broadcast(message: Message, state: FSMContext):
#     """Start broadcast process"""
#     await state.set_state(BroadcastStates.waiting_for_content)
#     await message.answer(
#         "📢 **Broadcast Message**\n\n"
#         "Send the content to broadcast (photo, video, document, or text):\n\n"
#         "Type /cancel to abort."
#     )

# @router.message(BroadcastStates.waiting_for_content)
# async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
#     """Process broadcast content"""
#     file_info = get_file_info(message)
    
#     if file_info["file_type"] == "unknown":
#         await message.answer("❌ Unknown content type. Please send a valid message.")
#         return
    
#     # Forward to private channel
#     try:
#         forwarded_msg = await bot.forward_message(
#             chat_id=Config.PRIVATE_CHANNEL_ID,
#             from_chat_id=message.chat.id,
#             message_id=message.message_id
#         )
        
#         await state.update_data(
#             message_id=message.message_id,
#             channel_message_id=forwarded_msg.message_id,
#             file_type=file_info["file_type"],
#             file_id=file_info["file_id"],
#             text_content=file_info["text_content"],
#             caption=message.caption
#         )
        
#         await state.set_state(BroadcastStates.waiting_for_duration)
#         await message.answer(
#             "✅ Content uploaded!\n\n"
#             "⏰ Enter duration in hours (how long the message should stay):"
#         )
    
#     except Exception as e:
#         await message.answer(f"❌ Error uploading content: {e}")
#         await state.clear()

# @router.message(BroadcastStates.waiting_for_duration)
# async def process_broadcast_duration(message: Message, state: FSMContext, bot: Bot):
#     """Process duration and start broadcasting"""
#     try:
#         duration_hours = int(message.text.strip())
#         data = await state.get_data()
        
#         # Create broadcast record
#         broadcast_data = BroadcastModel.create(
#             message_id=data["message_id"],
#             channel_message_id=data["channel_message_id"],
#             file_type=data["file_type"],
#             file_id=data.get("file_id"),
#             text_content=data.get("text_content"),
#             caption=data.get("caption"),
#             duration_hours=duration_hours
#         )
        
#         broadcast_id = await BroadcastOperations.create_broadcast(broadcast_data)
        
#         status_msg = await message.answer(
#             "📤 Starting broadcast...\n"
#             f"Duration: {duration_hours} hours\n"
#             "Progress: 0/?"
#         )
        
#         # Get all user IDs
#         user_ids = await UserOperations.get_all_user_ids()
#         total_users = len(user_ids)
#         sent_count = 0
#         failed_count = 0
        
#         # Broadcast to users (2 per second)
#         for i, user_id in enumerate(user_ids):
#             try:
#                 if data["file_type"] == "text":
#                     await bot.send_message(
#                         chat_id=user_id,
#                         text=data["text_content"]
#                     )
#                 else:
#                     await bot.copy_message(
#                         chat_id=user_id,
#                         from_chat_id=Config.PRIVATE_CHANNEL_ID,
#                         message_id=data["channel_message_id"]
#                     )
#                 sent_count += 1
#             except Exception as e:
#                 failed_count += 1
#                 print(f"Failed to send to {user_id}: {e}")
            
#             # Rate limiting: 2 users per second
#             if (i + 1) % 2 == 0:
#                 await asyncio.sleep(1)
            
#             # Update status every 10 users
#             if (i + 1) % 10 == 0:
#                 try:
#                     await status_msg.edit_text(
#                         f"📤 Broadcasting...\n"
#                         f"Duration: {duration_hours} hours\n"
#                         f"Progress: {i + 1}/{total_users}\n"
#                         f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}"
#                     )
#                 except:
#                     pass
        
#         # Update broadcast stats
#         await BroadcastOperations.update_broadcast_stats(
#             broadcast_id, sent_count, failed_count
#         )
        
#         # Set delete time
#         delete_at = datetime.utcnow() + timedelta(hours=duration_hours)
#         await BroadcastOperations.set_broadcast_delete_time(broadcast_id, delete_at)
        
#         # Final status
#         await status_msg.edit_text(
#             f"✅ **Broadcast Complete!**\n\n"
#             f"Total Users: {total_users}\n"
#             f"✅ Sent: {sent_count}\n"
#             f"❌ Failed: {failed_count}\n"
#             f"⏰ Will be deleted in {duration_hours} hours"
#         )
        
#         # TODO: Implement auto-deletion in Phase 4
        
#         await state.clear()
    
#     except ValueError:
#         await message.answer("❌ Invalid duration. Please enter a valid number:")



# ===========================================
# admin_bot/handlers/broadcast.py
# ===========================================
# from aiogram import Router, Bot
# from aiogram.filters import Command, StateFilter
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# import asyncio
# from datetime import datetime, timedelta

# from database.operations import UserOperations, BroadcastOperations
# from database.models import BroadcastModel
# from config.settings import Config
# from utils.helpers import get_file_info

# router = Router()

# class BroadcastStates(StatesGroup):
#     waiting_for_content = State()
#     waiting_for_duration = State()

# @router.message(Command("broadcast"))
# async def cmd_broadcast(message: Message, state: FSMContext):
#     """Start broadcast process"""
#     await state.set_state(BroadcastStates.waiting_for_content)
#     await message.answer(
#         "📢 **Broadcast Message**\n\n"
#         "Send the content to broadcast (photo, video, document, or text):\n\n"
#         "Type /cancel to abort."
#     )

# @router.message(BroadcastStates.waiting_for_content)
# async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
#     """Process broadcast content"""
#     file_info = get_file_info(message)
    
#     if file_info["file_type"] == "unknown":
#         await message.answer("❌ Unknown content type. Please send a valid message.")
#         return
    
#     # Forward to private channel
#     try:
#         forwarded_msg = await bot.forward_message(
#             chat_id=Config.PRIVATE_CHANNEL_ID,
#             from_chat_id=message.chat.id,
#             message_id=message.message_id
#         )
        
#         await state.update_data(
#             message_id=message.message_id,
#             channel_message_id=forwarded_msg.message_id,
#             file_type=file_info["file_type"],
#             file_id=file_info["file_id"],
#             text_content=file_info["text_content"],
#             caption=message.caption
#         )
        
#         await state.set_state(BroadcastStates.waiting_for_duration)
#         await message.answer(
#             "✅ Content uploaded!\n\n"
#             "⏰ Enter duration in hours (how long the message should stay):"
#         )
    
#     except Exception as e:
#         await message.answer(f"❌ Error uploading content: {e}")
#         await state.clear()

# @router.message(BroadcastStates.waiting_for_duration)
# async def process_broadcast_duration(message: Message, state: FSMContext, bot: Bot):
#     """Process duration and start broadcasting"""
#     try:
#         duration_hours = int(message.text.strip())
#         data = await state.get_data()
        
#         # Create broadcast record
#         broadcast_data = BroadcastModel.create(
#             message_id=data["message_id"],
#             channel_message_id=data["channel_message_id"],
#             file_type=data["file_type"],
#             file_id=data.get("file_id"),
#             text_content=data.get("text_content"),
#             caption=data.get("caption"),
#             duration_hours=duration_hours
#         )
        
#         broadcast_id = await BroadcastOperations.create_broadcast(broadcast_data)
        
#         status_msg = await message.answer(
#             "📤 Starting broadcast...\n"
#             f"Duration: {duration_hours} hours\n"
#             "Progress: 0/?"
#         )
        
#         # Get all user IDs
#         user_ids = await UserOperations.get_all_user_ids()
#         total_users = len(user_ids)
#         sent_count = 0
#         failed_count = 0
        
#         # Broadcast to users (2 per second)
#         for i, user_id in enumerate(user_ids):
#             try:
#                 if data["file_type"] == "text":
#                     await bot.send_message(
#                         chat_id=user_id,
#                         text=data["text_content"]
#                     )
#                 else:
#                     await bot.copy_message(
#                         chat_id=user_id,
#                         from_chat_id=Config.PRIVATE_CHANNEL_ID,
#                         message_id=data["channel_message_id"]
#                     )
#                 sent_count += 1
#             except Exception as e:
#                 failed_count += 1
#                 print(f"Failed to send to {user_id}: {e}")
            
#             # Rate limiting: 2 users per second
#             if (i + 1) % 2 == 0:
#                 await asyncio.sleep(1)
            
#             # Update status every 10 users
#             if (i + 1) % 10 == 0:
#                 try:
#                     await status_msg.edit_text(
#                         f"📤 Broadcasting...\n"
#                         f"Duration: {duration_hours} hours\n"
#                         f"Progress: {i + 1}/{total_users}\n"
#                         f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}"
#                     )
#                 except:
#                     pass
        
#         # Update broadcast stats
#         await BroadcastOperations.update_broadcast_stats(
#             broadcast_id, sent_count, failed_count
#         )
        
#         # Set delete time
#         delete_at = datetime.utcnow() + timedelta(hours=duration_hours)
#         await BroadcastOperations.set_broadcast_delete_time(broadcast_id, delete_at)
        
#         # Final status
#         await status_msg.edit_text(
#             f"✅ **Broadcast Complete!**\n\n"
#             f"Total Users: {total_users}\n"
#             f"✅ Sent: {sent_count}\n"
#             f"❌ Failed: {failed_count}\n"
#             f"⏰ Will be deleted in {duration_hours} hours"
#         )
        
#         # TODO: Implement auto-deletion in Phase 4
        
#         await state.clear()
    
#     except ValueError:
#         await message.answer("❌ Invalid duration. Please enter a valid number:")



# # ===========================================
# # admin_bot/handlers/broadcast.py - UPDATED WITH AUTO-DELETION
# # ===========================================
# from aiogram import Router, Bot
# from aiogram.filters import Command, StateFilter
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# import asyncio
# from datetime import datetime, timedelta

# from database.operations import UserOperations, BroadcastOperations
# from database.models import BroadcastModel
# from config.settings import Config
# from utils.helpers import get_file_info

# router = Router()

# class BroadcastStates(StatesGroup):
#     waiting_for_content = State()
#     waiting_for_duration = State()

# # Store broadcast message IDs for deletion
# broadcast_messages: dict = {}  # {broadcast_id: {user_id: [message_ids]}}

# @router.message(Command("broadcast"))
# async def cmd_broadcast(message: Message, state: FSMContext):
#     """Start broadcast process"""
#     await state.set_state(BroadcastStates.waiting_for_content)
#     await message.answer(
#         "📢 **Broadcast Message**\n\n"
#         "Send the content to broadcast (photo, video, document, or text):\n\n"
#         "Type /cancel to abort."
#     )

# @router.message(BroadcastStates.waiting_for_content)
# async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
#     """Process broadcast content"""
#     file_info = get_file_info(message)
    
#     if file_info["file_type"] == "unknown":
#         await message.answer("❌ Unknown content type. Please send a valid message.")
#         return
    
#     # Forward to private channel
#     try:
#         forwarded_msg = await bot.forward_message(
#             chat_id=Config.PRIVATE_CHANNEL_ID,
#             from_chat_id=message.chat.id,
#             message_id=message.message_id
#         )
        
#         await state.update_data(
#             message_id=message.message_id,
#             channel_message_id=forwarded_msg.message_id,
#             file_type=file_info["file_type"],
#             file_id=file_info["file_id"],
#             text_content=file_info["text_content"],
#             caption=message.caption
#         )
        
#         await state.set_state(BroadcastStates.waiting_for_duration)
#         await message.answer(
#             "✅ Content uploaded!\n\n"
#             "⏰ Enter duration in hours (how long the message should stay):"
#         )
    
#     except Exception as e:
#         await message.answer(f"❌ Error uploading content: {e}")
#         await state.clear()

# @router.message(BroadcastStates.waiting_for_duration)
# async def process_broadcast_duration(message: Message, state: FSMContext, bot: Bot):
#     """Process duration and start broadcasting"""
#     try:
#         duration_hours = int(message.text.strip())
#         data = await state.get_data()
        
#         # Create broadcast record
#         broadcast_data = BroadcastModel.create(
#             message_id=data["message_id"],
#             channel_message_id=data["channel_message_id"],
#             file_type=data["file_type"],
#             file_id=data.get("file_id"),
#             text_content=data.get("text_content"),
#             caption=data.get("caption"),
#             duration_hours=duration_hours
#         )
        
#         broadcast_id = await BroadcastOperations.create_broadcast(broadcast_data)
#         broadcast_messages[broadcast_id] = {}
        
#         status_msg = await message.answer(
#             "📤 Starting broadcast...\n"
#             f"Duration: {duration_hours} hours\n"
#             "Progress: 0/?"
#         )
        
#         # Get all user IDs
#         user_ids = await UserOperations.get_all_user_ids()
#         total_users = len(user_ids)
#         sent_count = 0
#         failed_count = 0
        
#         # Broadcast to users (2 per second)
#         for i, user_id in enumerate(user_ids):
#             try:
#                 if data["file_type"] == "text":
#                     sent_msg = await bot.send_message(
#                         chat_id=user_id,
#                         text=data["text_content"]
#                     )
#                 else:
#                     sent_msg = await bot.copy_message(
#                         chat_id=user_id,
#                         from_chat_id=Config.PRIVATE_CHANNEL_ID,
#                         message_id=data["channel_message_id"]
#                     )
                
#                 # Store message ID for deletion
#                 if broadcast_id not in broadcast_messages:
#                     broadcast_messages[broadcast_id] = {}
#                 broadcast_messages[broadcast_id][user_id] = [sent_msg.message_id]
                
#                 sent_count += 1
#             except Exception as e:
#                 failed_count += 1
#                 print(f"Failed to send to {user_id}: {e}")
            
#             # Rate limiting
#             if (i + 1) % 2 == 0:
#                 await asyncio.sleep(1)
            
#             # Update status every 10 users
#             if (i + 1) % 10 == 0:
#                 try:
#                     await status_msg.edit_text(
#                         f"📤 Broadcasting...\n"
#                         f"Duration: {duration_hours} hours\n"
#                         f"Progress: {i + 1}/{total_users}\n"
#                         f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}"
#                     )
#                 except:
#                     pass
        
#         # Update stats
#         await BroadcastOperations.update_broadcast_stats(
#             broadcast_id, sent_count, failed_count
#         )
        
#         # Set delete time
#         delete_at = datetime.utcnow() + timedelta(hours=duration_hours)
#         await BroadcastOperations.set_broadcast_delete_time(broadcast_id, delete_at)
        
#         # Final status
#         await status_msg.edit_text(
#             f"✅ **Broadcast Complete!**\n\n"
#             f"Total Users: {total_users}\n"
#             f"✅ Sent: {sent_count}\n"
#             f"❌ Failed: {failed_count}\n"
#             f"⏰ Will be deleted in {duration_hours} hours"
#         )
        
#         # Schedule deletion
#         asyncio.create_task(
#             delete_broadcast_after_delay(
#                 bot, broadcast_id, duration_hours * 60
#             )
#         )
        
#         await state.clear()
    
#     except ValueError:
#         await message.answer("❌ Invalid duration. Please enter a valid number:")

# async def delete_broadcast_after_delay(bot: Bot, broadcast_id: str, delay_minutes: int):
#     """Delete broadcast messages after specified delay"""
#     try:
#         await asyncio.sleep(delay_minutes * 60)
        
#         if broadcast_id not in broadcast_messages:
#             return
        
#         deleted_count = 0
#         total_messages = 0
        
#         for user_id, message_ids in broadcast_messages[broadcast_id].items():
#             total_messages += len(message_ids)
#             for msg_id in message_ids:
#                 try:
#                     await bot.delete_message(chat_id=user_id, message_id=msg_id)
#                     deleted_count += 1
#                 except Exception as e:
#                     print(f"Failed to delete broadcast message: {e}")
        
#         print(f"✅ Deleted {deleted_count}/{total_messages} broadcast messages")
        
#         # Clean up
#         del broadcast_messages[broadcast_id]
        
#     except Exception as e:
#         print(f"Error in broadcast deletion: {e}")



# ===========================================
# admin_bot/handlers/broadcast.py - UPDATED WITH AUTO-DELETION
# ===========================================
from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from datetime import datetime, timedelta

from database.operations import UserOperations, BroadcastOperations
from database.models import BroadcastModel
from config.settings import Config
from utils.helpers import get_file_info

router = Router()

class BroadcastStates(StatesGroup):
    waiting_for_content = State()
    waiting_for_duration = State()

# Store broadcast message IDs for deletion
broadcast_messages: dict = {}  # {broadcast_id: {user_id: [message_ids]}}

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Start broadcast process"""
    await state.set_state(BroadcastStates.waiting_for_content)
    await message.answer(
        "📢 **Broadcast Message**\n\n"
        "Send the content to broadcast (photo, video, document, or text):\n\n"
        "Type /cancel to abort."
    )

@router.message(BroadcastStates.waiting_for_content)
async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):
    """Process broadcast content"""
    file_info = get_file_info(message)
    
    if file_info["file_type"] == "unknown":
        await message.answer("❌ Unknown content type. Please send a valid message.")
        return
    
    # Forward to private channel
    try:
        forwarded_msg = await bot.forward_message(
            chat_id=Config.PRIVATE_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        await state.update_data(
            message_id=message.message_id,
            channel_message_id=forwarded_msg.message_id,
            file_type=file_info["file_type"],
            file_id=file_info["file_id"],
            text_content=file_info["text_content"],
            caption=message.caption
        )
        
        await state.set_state(BroadcastStates.waiting_for_duration)
        await message.answer(
            "✅ Content uploaded!\n\n"
            "⏰ Enter duration in hours (how long the message should stay):"
        )
    
    except Exception as e:
        await message.answer(f"❌ Error uploading content: {e}")
        await state.clear()

@router.message(BroadcastStates.waiting_for_duration)
async def process_broadcast_duration(message: Message, state: FSMContext, bot: Bot):
    """Process duration and start broadcasting"""
    try:
        duration_hours = int(message.text.strip())
        data = await state.get_data()
        
        # Create broadcast record
        broadcast_data = BroadcastModel.create(
            message_id=data["message_id"],
            channel_message_id=data["channel_message_id"],
            file_type=data["file_type"],
            file_id=data.get("file_id"),
            text_content=data.get("text_content"),
            caption=data.get("caption"),
            duration_hours=duration_hours
        )
        
        broadcast_id = await BroadcastOperations.create_broadcast(broadcast_data)
        broadcast_messages[broadcast_id] = {}
        
        status_msg = await message.answer(
            "📤 Starting broadcast...\n"
            f"Duration: {duration_hours} hours\n"
            "Progress: 0/?"
        )
        
        # IMPORTANT: Get all user IDs from users collection
        # These are users who have started the USER BOT, not admin bot
        user_ids = await UserOperations.get_all_user_ids()
        total_users = len(user_ids)
        
        if total_users == 0:
            await status_msg.edit_text("❌ No users found in database!")
            await state.clear()
            return
        
        sent_count = 0
        failed_count = 0
        
        # Create user bot instance to send messages
        from config.settings import Config
        from aiogram import Bot as UserBotInstance
        from aiogram.client.session.aiohttp import AiohttpSession
        
        session = AiohttpSession()
        user_bot = UserBotInstance(token=Config.USER_BOT_TOKEN, session=session)
        
        # Broadcast to users (2 per second)
        for i, user_id in enumerate(user_ids):
            try:
                if data["file_type"] == "text":
                    sent_msg = await user_bot.send_message(
                        chat_id=user_id,
                        text=data["text_content"]
                    )
                else:
                    sent_msg = await user_bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=Config.PRIVATE_CHANNEL_ID,
                        message_id=data["channel_message_id"]
                    )
                
                # Store message ID for deletion
                if broadcast_id not in broadcast_messages:
                    broadcast_messages[broadcast_id] = {}
                broadcast_messages[broadcast_id][user_id] = [sent_msg.message_id]
                
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send to {user_id}: {e}")
            
            # Rate limiting
            if (i + 1) % 2 == 0:
                await asyncio.sleep(1)
            
            # Update status every 10 users
            if (i + 1) % 10 == 0:
                try:
                    await status_msg.edit_text(
                        f"📤 Broadcasting...\n"
                        f"Duration: {duration_hours} hours\n"
                        f"Progress: {i + 1}/{total_users}\n"
                        f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}"
                    )
                except:
                    pass
        
        # Close user bot session
        await session.close()
        
        # Update stats
        await BroadcastOperations.update_broadcast_stats(
            broadcast_id, sent_count, failed_count
        )
        
        # Set delete time
        delete_at = datetime.utcnow() + timedelta(hours=duration_hours)
        await BroadcastOperations.set_broadcast_delete_time(broadcast_id, delete_at)
        
        # Final status
        await status_msg.edit_text(
            f"✅ **Broadcast Complete!**\n\n"
            f"Total Users: {total_users}\n"
            f"✅ Sent: {sent_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"⏰ Will be deleted in {duration_hours} hours"
        )
        
        # Schedule deletion (use user bot for deletion)
        asyncio.create_task(
            delete_broadcast_after_delay(
                Config.USER_BOT_TOKEN, broadcast_id, duration_hours * 60
            )
        )
        
        await state.clear()
    
    except ValueError:
        await message.answer("❌ Invalid duration. Please enter a valid number:")

async def delete_broadcast_after_delay(user_bot_token: str, broadcast_id: str, delay_minutes: int):
    """Delete broadcast messages after specified delay"""
    try:
        await asyncio.sleep(delay_minutes * 60)
        
        if broadcast_id not in broadcast_messages:
            return
        
        # Create user bot instance
        from aiogram import Bot as UserBotInstance
        from aiogram.client.session.aiohttp import AiohttpSession
        
        session = AiohttpSession()
        user_bot = UserBotInstance(token=user_bot_token, session=session)
        
        deleted_count = 0
        total_messages = 0
        
        for user_id, message_ids in broadcast_messages[broadcast_id].items():
            total_messages += len(message_ids)
            for msg_id in message_ids:
                try:
                    await user_bot.delete_message(chat_id=user_id, message_id=msg_id)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete broadcast message: {e}")
        
        await session.close()
        
        print(f"✅ Deleted {deleted_count}/{total_messages} broadcast messages")
        
        # Clean up
        del broadcast_messages[broadcast_id]
        
    except Exception as e:
        print(f"Error in broadcast deletion: {e}")