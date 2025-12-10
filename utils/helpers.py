
# ===========================================
# utils/helpers.py
# ===========================================
from datetime import datetime
from typing import Optional
from aiogram.types import Message, ContentType

def get_file_info(message: Message) -> dict:
    """Extract file information from message"""
    if message.photo:
        return {
            "file_type": "photo",
            "file_id": message.photo[-1].file_id,
            "text_content": None
        }
    elif message.video:
        return {
            "file_type": "video",
            "file_id": message.video.file_id,
            "text_content": None
        }
    elif message.document:
        return {
            "file_type": "document",
            "file_id": message.document.file_id,
            "text_content": None
        }
    elif message.audio:
        return {
            "file_type": "audio",
            "file_id": message.audio.file_id,
            "text_content": None
        }
    elif message.voice:
        return {
            "file_type": "voice",
            "file_id": message.voice.file_id,
            "text_content": None
        }
    elif message.video_note:
        return {
            "file_type": "video_note",
            "file_id": message.video_note.file_id,
            "text_content": None
        }
    elif message.text:
        return {
            "file_type": "text",
            "file_id": None,
            "text_content": message.text or message.caption
        }
    else:
        return {
            "file_type": "unknown",
            "file_id": None,
            "text_content": None
        }

def format_template(post_no: int, description: str, extra_message: str, deeplink: str) -> str:
    """Format the resource template"""
    return f"""Post no-{post_no}

Description-{description}

{extra_message}"""

def is_zip_file(filename: Optional[str]) -> bool:
    """Check if file is a zip file"""
    if not filename:
        return False
    return filename.lower().endswith('.zip')

def format_duration(minutes: int) -> str:
    """Format duration for display"""
    if minutes < 60:
        return f"{minutes} Minutes"
    hours = minutes // 60
    remaining_mins = minutes % 60
    if remaining_mins == 0:
        return f"{hours} Hour{'s' if hours > 1 else ''}"
    return f"{hours} Hour{'s' if hours > 1 else ''} {remaining_mins} Minutes"
