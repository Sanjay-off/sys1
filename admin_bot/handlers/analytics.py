# ===========================================
# admin_bot/handlers/analytics.py
# ===========================================
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta

from database.operations import (
    UserOperations, FileOperations, TokenOperations,
    BroadcastOperations, AdminConfigOperations
)
from database.connection import Database

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show comprehensive statistics"""
    db = Database.get_db()
    
    # User stats
    total_users = await db.users.count_documents({})
    verified_users = await UserOperations.get_verified_users_count()
    banned_users = await db.users.count_documents({"is_banned": True})
    
    # Resource stats
    total_resources = await db.files.count_documents({})
    batch_resources = await db.files.count_documents({"is_batch": True})
    single_resources = total_resources - batch_resources
    
    # Token stats (today)
    today = datetime.utcnow().date().isoformat()
    tokens_today = await db.token_generator_count.count_documents({"date": today})
    
    # Get total tokens generated today
    pipeline = [
        {"$match": {"date": today}},
        {"$group": {"_id": None, "total": {"$sum": "$token_generated"}}}
    ]
    result = await db.token_generator_count.aggregate(pipeline).to_list(1)
    total_tokens_today = result[0]["total"] if result else 0
    
    # Force sub channels
    force_sub_count = len(await AdminConfigOperations.get_force_sub_channels())
    
    # Broadcast stats
    total_broadcasts = await db.broadcast.count_documents({})
    
    stats_text = f"""📊 **System Statistics**

👥 **Users:**
• Total Users: {total_users}
• Verified Users: {verified_users}
• Banned Users: {banned_users}
• Active Users: {total_users - banned_users}

📁 **Resources:**
• Total Resources: {total_resources}
• Single Resources: {single_resources}
• Batch Resources: {batch_resources}

🎫 **Tokens (Today):**
• Users Generated: {tokens_today}
• Total Tokens: {total_tokens_today}

📺 **Channels:**
• Force Sub Channels: {force_sub_count}

📢 **Broadcasts:**
• Total Sent: {total_broadcasts}

⏰ **Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"""
    
    await message.answer(stats_text)

@router.message(Command("user_info"))
async def cmd_user_info(message: Message):
    """Get detailed user information"""
    # Extract user ID from command
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /user_info <user_id>")
        return
    
    try:
        user_id = int(parts[1])
        user = await UserOperations.get_user(user_id)
        
        if not user:
            await message.answer(f"❌ User {user_id} not found in database.")
            return
        
        # Get token generation count
        from database.operations import TokenGeneratorCountOperations
        token_count = await TokenGeneratorCountOperations.get_count(user_id)
        
        info_text = f"""👤 **User Information**

**User ID:** `{user_id}`
**Username:** @{user['username'] or 'N/A'}
**First Name:** {user['first_name'] or 'N/A'}

📊 **Stats:**
• Media Access Count: {user['user_access_count']}
• Banned: {'Yes ❌' if user['is_banned'] else 'No ✅'}
• Tokens Generated Today: {token_count}/15

📅 **Activity:**
• Joined: {user['created_at'].strftime('%Y-%m-%d %H:%M')}
• Last Active: {user['last_active'].strftime('%Y-%m-%d %H:%M')}

📺 **Subscriptions:**
• Joined Channels: {len(user.get('join_requests', []))}"""
        
        if user.get('verified_until'):
            info_text += f"\n• Verified Until: {user['verified_until'].strftime('%Y-%m-%d %H:%M')}"
        
        await message.answer(info_text)
    
    except ValueError:
        await message.answer("❌ Invalid user ID. Please enter a number.")

@router.message(Command("resource_info"))
async def cmd_resource_info(message: Message):
    """Get resource information by post number"""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /resource_info <post_no>")
        return
    
    try:
        post_no = int(parts[1])
        file_data = await FileOperations.get_file_by_post_no(post_no)
        
        if not file_data:
            await message.answer(f"❌ Post number {post_no} not found.")
            return
        
        info_text = f"""📁 **Resource Information**

**Post Number:** {post_no}
**Unique ID:** `{file_data['unique_id']}`
**Type:** {file_data['file_type']}
**Description:** {file_data['description']}
**Extra Message:** {file_data['extra_message']}

📊 **Details:**
• Channel Message ID: {file_data['channel_message_id']}
• Created: {file_data['created_at'].strftime('%Y-%m-%d %H:%M')}"""
        
        if file_data.get('is_batch'):
            info_text += f"\n• Batch Files: {len(file_data.get('batch_file_ids', []))}"
        
        await message.answer(info_text)
    
    except ValueError:
        await message.answer("❌ Invalid post number. Please enter a number.")

@router.message(Command("delete_resource"))
async def cmd_delete_resource(message: Message):
    """Delete a resource by post number"""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /delete_resource <post_no>")
        return
    
    try:
        post_no = int(parts[1])
        db = Database.get_db()
        
        result = await db.files.delete_one({"post_no": post_no})
        
        if result.deleted_count > 0:
            await message.answer(f"✅ Resource with post number {post_no} deleted successfully.")
        else:
            await message.answer(f"❌ Post number {post_no} not found.")
    
    except ValueError:
        await message.answer("❌ Invalid post number. Please enter a number.")

@router.message(Command("clear_old_tokens"))
async def cmd_clear_old_tokens(message: Message):
    """Manually clear expired tokens"""
    deleted = await TokenOperations.delete_expired_tokens()
    await message.answer(f"✅ Cleared {deleted} expired tokens.")

@router.message(Command("backup_db"))
async def cmd_backup_db(message: Message):
    """Show backup instructions"""
    backup_text = """💾 **Database Backup Instructions**

To backup your MongoDB database:

**Option 1: Manual Backup**
```bash
mongodump --db telegram_resource_db --out /backup/path
```

**Option 2: Automated Backup Script**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --db telegram_resource_db --out /backup/telegram_backup_$DATE
```

**Restore Backup:**
```bash
mongorestore --db telegram_resource_db /backup/path/telegram_resource_db
```

**Important Collections:**
• users - User data
• files - Resources
• tokens - Verification tokens
• admin_config - Settings & channels
• broadcast - Broadcast history"""
    
    await message.answer(backup_text)

@router.message(Command("system_health"))
async def cmd_system_health(message: Message):
    """Check system health"""
    from database.connection import Database
    
    health_text = "🏥 **System Health Check**\n\n"
    
    # Check MongoDB
    try:
        db = Database.get_db()
        await db.command("ping")
        health_text += "✅ MongoDB: Connected\n"
    except Exception as e:
        health_text += f"❌ MongoDB: Error - {str(e)}\n"
    
    # Check private channel
    try:
        from aiogram import Bot
        from config.settings import Config
        bot = message.bot
        chat = await bot.get_chat(Config.PRIVATE_CHANNEL_ID)
        health_text += f"✅ Private Channel: Accessible\n"
        health_text += f"   └─ Name: {chat.title}\n"
    except Exception as e:
        health_text += f"❌ Private Channel: Error - {str(e)}\n"
    
    # Check force sub channels
    channels = await AdminConfigOperations.get_force_sub_channels()
    healthy_channels = 0
    for channel in channels:
        try:
            chat = await bot.get_chat(channel['channel_id'])
            healthy_channels += 1
        except:
            pass
    
    health_text += f"✅ Force Sub Channels: {healthy_channels}/{len(channels)} accessible\n"
    
    # Memory/Resource usage
    import psutil
    import os
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    health_text += f"\n📊 **Resources:**\n"
    health_text += f"• Memory Usage: {memory_mb:.2f} MB\n"
    health_text += f"• CPU Usage: {process.cpu_percent()}%\n"
    
    await message.answer(health_text)

# Add these commands to menu
# def get_admin_commands():
#     """Updated admin commands list"""
#     from aiogram.types import BotCommand
#     return [
#         # ... existing commands ...
#         BotCommand(command="stats", description="View system statistics"),
#         BotCommand(command="user_info", description="Get user information"),
#         BotCommand(command="resource_info", description="Get resource information"),
#         BotCommand(command="delete_resource", description="Delete a resource"),
#         BotCommand(command="clear_old_tokens", description="Clear expired tokens"),
#         BotCommand(command="backup_db", description="Database backup instructions"),
#         BotCommand(command="system_health", description="Check system health"),
#     ]