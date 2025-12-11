
# ===========================================
# admin_bot/keyboards/menu.py
# ===========================================
from aiogram.types import BotCommand

def get_admin_commands():
    """Get list of admin bot commands"""
    return [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="generate_link", description="Generate resource link"),
        BotCommand(command="regenerate_post", description="Regenerate post template"),
        BotCommand(command="broadcast", description="Broadcast message to all users"),
        BotCommand(command="add_force_sub", description="Add force sub channel"),
        BotCommand(command="remove_force_sub", description="Remove force sub channel"),
        BotCommand(command="list_force_sub", description="List force sub channels"),
        BotCommand(command="verification_stats", description="View verification statistics"),
        BotCommand(command="ban_user", description="Ban a user"),
        BotCommand(command="unban_user", description="Unban a user"),
        BotCommand(command="set_verified", description="Verify a user manually"),
        BotCommand(command="unset_verified", description="Unverify a user"),
        BotCommand(command="set_media_count", description="Set free media access count"),
        BotCommand(command="generate_batch", description="Generate batch resource link"),
        BotCommand(command="set_password", description="Set zip file password"),
        BotCommand(command="set_deletion_time", description="Set resource deletion time"),
        BotCommand(command="set_user_media_count", description="Set paid media count for user"),
        BotCommand(command="set_verify_link", description="Set how to verify link"),
        BotCommand(command="stats", description="View system statistics"),
        BotCommand(command="user_info", description="Get user information"),
        BotCommand(command="resource_info", description="Get resource information"),
        BotCommand(command="delete_resource", description="Delete a resource"),
        BotCommand(command="clear_old_tokens", description="Clear expired tokens"),
        BotCommand(command="backup_db", description="Database backup instructions"),
        BotCommand(command="system_health", description="Check system health"),
        BotCommand(command="cancel", description="Cancel current operation"),
    ]
