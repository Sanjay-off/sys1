# ===========================================
# database/models.py
# ===========================================
from datetime import datetime
from typing import Optional, Dict, Any

class FileModel:
    """Model for file collection"""
    @staticmethod
    def create(
        unique_id: str,
        post_no: int,
        description: str,
        extra_message: str,
        file_type: str,
        file_id: Optional[str] = None,
        text_content: Optional[str] = None,
        channel_message_id: int = None,
        is_batch: bool = False,
        batch_file_ids: list = None
    ) -> Dict[str, Any]:
        return {
            "unique_id": unique_id,
            "post_no": post_no,
            "description": description,
            "extra_message": extra_message,
            "file_type": file_type,
            "file_id": file_id,
            "text_content": text_content,
            "channel_message_id": channel_message_id,
            "is_batch": is_batch,
            "batch_file_ids": batch_file_ids or [],
            "created_at": datetime.utcnow()
        }

class UserModel:
    """Model for users collection"""
    @staticmethod
    def create(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        user_access_count: int = 0,
        is_banned: bool = False,
        verified_until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "user_access_count": user_access_count,
            "is_banned": is_banned,
            "verified_until": verified_until,
            "join_requests": [],  # List of channel IDs user requested to join
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }

class TokenModel:
    """Model for tokens collection"""
    @staticmethod
    def create(
        token: str,
        unique_id: str,
        created_by: int,
        status: str = "not_used"
    ) -> Dict[str, Any]:
        return {
            "token": token,
            "unique_id": unique_id,
            "created_by": created_by,
            "status": status,  # not_used | verified | bypassed
            "created_at": datetime.utcnow()
        }

class BroadcastModel:
    """Model for broadcast collection"""
    @staticmethod
    def create(
        message_id: int,
        channel_message_id: int,
        file_type: str,
        file_id: Optional[str] = None,
        text_content: Optional[str] = None,
        caption: Optional[str] = None,
        duration_hours: int = 24,
        sent_count: int = 0,
        failed_count: int = 0
    ) -> Dict[str, Any]:
        return {
            "message_id": message_id,
            "channel_message_id": channel_message_id,
            "file_type": file_type,
            "file_id": file_id,
            "text_content": text_content,
            "caption": caption,
            "duration_hours": duration_hours,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "created_at": datetime.utcnow(),
            "delete_at": None  # Will be set after broadcast completes
        }

class AdminConfigModel:
    """Model for admin_config collection"""
    @staticmethod
    def create_force_sub_channel(
        channel_id: int,
        channel_username: str,
        placeholder: str
    ) -> Dict[str, Any]:
        return {
            "type": "force_sub_channel",
            "channel_id": channel_id,
            "channel_username": channel_username,
            "placeholder": placeholder,
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_setting(key: str, value: Any) -> Dict[str, Any]:
        return {
            "type": "setting",
            "key": key,
            "value": value,
            "updated_at": datetime.utcnow()
        }

class TokenGeneratorCountModel:
    """Model for token generator count collection"""
    @staticmethod
    def create(user_id: int, count: int = 1) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "token_generated": count,
            "date": datetime.utcnow().date().isoformat()
        }