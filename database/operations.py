# # ===========================================
# # database/operations.py
# # ===========================================
# from datetime import datetime, timedelta
# from typing import Optional, List, Dict, Any
# from database.connection import Database
# from database.models import *
# from config.settings import Config

# class FileOperations:
#     @staticmethod
#     async def create_file(file_data: Dict[str, Any]) -> str:
#         db = Database.get_db()
#         result = await db.files.insert_one(file_data)
#         return str(result.inserted_id)
    
#     @staticmethod
#     async def get_file_by_unique_id(unique_id: str) -> Optional[Dict]:
#         db = Database.get_db()
#         return await db.files.find_one({"unique_id": unique_id})
    
#     @staticmethod
#     async def get_file_by_post_no(post_no: int) -> Optional[Dict]:
#         db = Database.get_db()
#         return await db.files.find_one({"post_no": post_no})
    
#     @staticmethod
#     async def post_no_exists(post_no: int) -> bool:
#         db = Database.get_db()
#         return await db.files.find_one({"post_no": post_no}) is not None
    
#     @staticmethod
#     async def get_all_files() -> List[Dict]:
#         db = Database.get_db()
#         cursor = db.files.find()
#         return await cursor.to_list(length=None)

# class UserOperations:
#     @staticmethod
#     async def create_user(user_data: Dict[str, Any]) -> str:
#         db = Database.get_db()
#         result = await db.users.insert_one(user_data)
#         return str(result.inserted_id)
    
#     @staticmethod
#     async def get_user(user_id: int) -> Optional[Dict]:
#         db = Database.get_db()
#         return await db.users.find_one({"user_id": user_id})
    
#     @staticmethod
#     async def update_user(user_id: int, update_data: Dict[str, Any]):
#         db = Database.get_db()
#         await db.users.update_one(
#             {"user_id": user_id},
#             {"$set": update_data}
#         )
    
#     @staticmethod
#     async def increment_access_count(user_id: int, count: int):
#         db = Database.get_db()
#         await db.users.update_one(
#             {"user_id": user_id},
#             {"$inc": {"user_access_count": count}}
#         )
    
#     @staticmethod
#     async def decrement_access_count(user_id: int):
#         db = Database.get_db()
#         user = await UserOperations.get_user(user_id)
#         if user and user["user_access_count"] > 0:
#             await db.users.update_one(
#                 {"user_id": user_id},
#                 {"$inc": {"user_access_count": -1}}
#             )
    
#     @staticmethod
#     async def add_join_request(user_id: int, channel_id: int):
#         db = Database.get_db()
#         await db.users.update_one(
#             {"user_id": user_id},
#             {"$addToSet": {"join_requests": channel_id}}
#         )
    
#     @staticmethod
#     async def get_verified_users_count() -> int:
#         db = Database.get_db()
#         return await db.users.count_documents({"user_access_count": {"$gt": 0}})
    
#     @staticmethod
#     async def get_all_user_ids() -> List[int]:
#         db = Database.get_db()
#         cursor = db.users.find({}, {"user_id": 1})
#         users = await cursor.to_list(length=None)
#         return [user["user_id"] for user in users]
    
#     @staticmethod
#     async def ban_user(user_id: int):
#         db = Database.get_db()
#         await db.users.update_one(
#             {"user_id": user_id},
#             {"$set": {"is_banned": True}}
#         )
    
#     @staticmethod
#     async def unban_user(user_id: int):
#         db = Database.get_db()
#         await db.users.update_one(
#             {"user_id": user_id},
#             {"$set": {"is_banned": False}}
#         )

# class TokenOperations:
#     @staticmethod
#     async def create_token(token_data: Dict[str, Any]) -> str:
#         db = Database.get_db()
#         result = await db.tokens.insert_one(token_data)
#         return str(result.inserted_id)
    
#     @staticmethod
#     async def get_token(token: str) -> Optional[Dict]:
#         db = Database.get_db()
#         return await db.tokens.find_one({"token": token})
    
#     @staticmethod
#     async def update_token_status(token: str, status: str):
#         db = Database.get_db()
#         await db.tokens.update_one(
#             {"token": token},
#             {"$set": {"status": status}}
#         )
    
#     @staticmethod
#     async def delete_token(token: str):
#         db = Database.get_db()
#         await db.tokens.delete_one({"token": token})
    
#     @staticmethod
#     async def delete_expired_tokens():
#         db = Database.get_db()
#         expiry_date = datetime.utcnow() - timedelta(days=Config.TOKEN_EXPIRY_DAYS)
#         result = await db.tokens.delete_many({"created_at": {"$lt": expiry_date}})
#         return result.deleted_count

# class TokenGeneratorCountOperations:
#     @staticmethod
#     async def get_count(user_id: int) -> int:
#         db = Database.get_db()
#         today = datetime.utcnow().date().isoformat()
#         record = await db.token_generator_count.find_one({
#             "user_id": user_id,
#             "date": today
#         })
#         return record["token_generated"] if record else 0
    
#     @staticmethod
#     async def increment_count(user_id: int):
#         db = Database.get_db()
#         today = datetime.utcnow().date().isoformat()
#         await db.token_generator_count.update_one(
#             {"user_id": user_id, "date": today},
#             {"$inc": {"token_generated": 1}},
#             upsert=True
#         )
    
#     @staticmethod
#     async def clear_old_counts():
#         db = Database.get_db()
#         today = datetime.utcnow().date().isoformat()
#         result = await db.token_generator_count.delete_many({"date": {"$ne": today}})
#         return result.deleted_count

# class AdminConfigOperations:
#     @staticmethod
#     async def add_force_sub_channel(channel_data: Dict[str, Any]):
#         db = Database.get_db()
#         await db.admin_config.insert_one(channel_data)
    
#     @staticmethod
#     async def get_force_sub_channels() -> List[Dict]:
#         db = Database.get_db()
#         cursor = db.admin_config.find({"type": "force_sub_channel"})
#         return await cursor.to_list(length=None)
    
#     @staticmethod
#     async def remove_force_sub_channel(channel_id: int):
#         db = Database.get_db()
#         await db.admin_config.delete_one({
#             "type": "force_sub_channel",
#             "channel_id": channel_id
#         })
    
#     @staticmethod
#     async def get_setting(key: str) -> Optional[Any]:
#         db = Database.get_db()
#         record = await db.admin_config.find_one({"type": "setting", "key": key})
#         return record["value"] if record else None
    
#     @staticmethod
#     async def set_setting(key: str, value: Any):
#         db = Database.get_db()
#         await db.admin_config.update_one(
#             {"type": "setting", "key": key},
#             {"$set": {"value": value, "updated_at": datetime.utcnow()}},
#             upsert=True
#         )

# class BroadcastOperations:
#     @staticmethod
#     async def create_broadcast(broadcast_data: Dict[str, Any]) -> str:
#         db = Database.get_db()
#         result = await db.broadcast.insert_one(broadcast_data)
#         return str(result.inserted_id)
    
#     @staticmethod
#     async def update_broadcast_stats(broadcast_id: str, sent: int, failed: int):
#         db = Database.get_db()
#         from bson import ObjectId
#         await db.broadcast.update_one(
#             {"_id": ObjectId(broadcast_id)},
#             {
#                 "$inc": {"sent_count": sent, "failed_count": failed}
#             }
#         )
    
#     @staticmethod
#     async def set_broadcast_delete_time(broadcast_id: str, delete_at: datetime):
#         db = Database.get_db()
#         from bson import ObjectId
#         await db.broadcast.update_one(
#             {"_id": ObjectId(broadcast_id)},
#             {"$set": {"delete_at": delete_at}}
#         )

# ===========================================
# database/operations.py
# ===========================================
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from database.connection import Database
from database.models import *
from config.settings import Config

class FileOperations:
    @staticmethod
    async def create_file(file_data: Dict[str, Any]) -> str:
        db = Database.get_db()
        result = await db.files.insert_one(file_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_file_by_unique_id(unique_id: str) -> Optional[Dict]:
        db = Database.get_db()
        return await db.files.find_one({"unique_id": unique_id})
    
    @staticmethod
    async def get_file_by_post_no(post_no: int) -> Optional[Dict]:
        db = Database.get_db()
        return await db.files.find_one({"post_no": post_no})
    
    @staticmethod
    async def post_no_exists(post_no: int) -> bool:
        db = Database.get_db()
        return await db.files.find_one({"post_no": post_no}) is not None
    
    @staticmethod
    async def get_all_files() -> List[Dict]:
        db = Database.get_db()
        cursor = db.files.find()
        return await cursor.to_list(length=None)

class UserOperations:
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> str:
        db = Database.get_db()
        result = await db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_user(user_id: int) -> Optional[Dict]:
        db = Database.get_db()
        return await db.users.find_one({"user_id": user_id})
    
    @staticmethod
    async def update_user(user_id: int, update_data: Dict[str, Any]):
        db = Database.get_db()
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    @staticmethod
    async def increment_access_count(user_id: int, count: int):
        db = Database.get_db()
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"user_access_count": count}}
        )
    
    @staticmethod
    async def decrement_access_count(user_id: int):
        db = Database.get_db()
        user = await UserOperations.get_user(user_id)
        if user and user["user_access_count"] > 0:
            await db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"user_access_count": -1}}
            )
    
    @staticmethod
    async def add_join_request(user_id: int, channel_id: int):
        db = Database.get_db()
        await db.users.update_one(
            {"user_id": user_id},
            {"$addToSet": {"join_requests": channel_id}}
        )
    
    @staticmethod
    async def get_verified_users_count() -> int:
        db = Database.get_db()
        return await db.users.count_documents({"user_access_count": {"$gt": 0}})
    
    @staticmethod
    async def get_all_user_ids() -> List[int]:
        db = Database.get_db()
        cursor = db.users.find({}, {"user_id": 1})
        users = await cursor.to_list(length=None)
        return [user["user_id"] for user in users]
    
    @staticmethod
    async def ban_user(user_id: int):
        db = Database.get_db()
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True}}
        )
    
    @staticmethod
    async def unban_user(user_id: int):
        db = Database.get_db()
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False}}
        )

class TokenOperations:
    @staticmethod
    async def create_token(token_data: Dict[str, Any]) -> str:
        db = Database.get_db()
        result = await db.tokens.insert_one(token_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_token(token: str) -> Optional[Dict]:
        db = Database.get_db()
        return await db.tokens.find_one({"token": token})
    
    @staticmethod
    async def get_token_by_unique_id(unique_id: str) -> Optional[Dict]:
        db = Database.get_db()
        return await db.tokens.find_one({"unique_id": unique_id})
    
    @staticmethod
    async def update_token_status(token: str, status: str):
        db = Database.get_db()
        await db.tokens.update_one(
            {"token": token},
            {"$set": {"status": status}}
        )
    
    @staticmethod
    async def delete_token(token: str):
        db = Database.get_db()
        await db.tokens.delete_one({"token": token})
    
    @staticmethod
    async def delete_expired_tokens():
        db = Database.get_db()
        expiry_date = datetime.utcnow() - timedelta(days=Config.TOKEN_EXPIRY_DAYS)
        result = await db.tokens.delete_many({"created_at": {"$lt": expiry_date}})
        return result.deleted_count

class TokenGeneratorCountOperations:
    @staticmethod
    async def get_count(user_id: int) -> int:
        db = Database.get_db()
        today = datetime.utcnow().date().isoformat()
        record = await db.token_generator_count.find_one({
            "user_id": user_id,
            "date": today
        })
        return record["token_generated"] if record else 0
    
    @staticmethod
    async def increment_count(user_id: int):
        db = Database.get_db()
        today = datetime.utcnow().date().isoformat()
        await db.token_generator_count.update_one(
            {"user_id": user_id, "date": today},
            {"$inc": {"token_generated": 1}},
            upsert=True
        )
    
    @staticmethod
    async def clear_old_counts():
        db = Database.get_db()
        today = datetime.utcnow().date().isoformat()
        result = await db.token_generator_count.delete_many({"date": {"$ne": today}})
        return result.deleted_count

class AdminConfigOperations:
    @staticmethod
    async def add_force_sub_channel(channel_data: Dict[str, Any]):
        db = Database.get_db()
        await db.admin_config.insert_one(channel_data)
    
    @staticmethod
    async def get_force_sub_channels() -> List[Dict]:
        db = Database.get_db()
        cursor = db.admin_config.find({"type": "force_sub_channel"})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def remove_force_sub_channel(channel_id: int):
        db = Database.get_db()
        await db.admin_config.delete_one({
            "type": "force_sub_channel",
            "channel_id": channel_id
        })
    
    @staticmethod
    async def get_setting(key: str) -> Optional[Any]:
        db = Database.get_db()
        record = await db.admin_config.find_one({"type": "setting", "key": key})
        return record["value"] if record else None
    
    @staticmethod
    async def set_setting(key: str, value: Any):
        db = Database.get_db()
        await db.admin_config.update_one(
            {"type": "setting", "key": key},
            {"$set": {"value": value, "updated_at": datetime.utcnow()}},
            upsert=True
        )

class BroadcastOperations:
    @staticmethod
    async def create_broadcast(broadcast_data: Dict[str, Any]) -> str:
        db = Database.get_db()
        result = await db.broadcast.insert_one(broadcast_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def update_broadcast_stats(broadcast_id: str, sent: int, failed: int):
        db = Database.get_db()
        from bson import ObjectId
        await db.broadcast.update_one(
            {"_id": ObjectId(broadcast_id)},
            {
                "$inc": {"sent_count": sent, "failed_count": failed}
            }
        )
    
    @staticmethod
    async def set_broadcast_delete_time(broadcast_id: str, delete_at: datetime):
        db = Database.get_db()
        from bson import ObjectId
        await db.broadcast.update_one(
            {"_id": ObjectId(broadcast_id)},
            {"$set": {"delete_at": delete_at}}
        )