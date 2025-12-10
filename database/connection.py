# ===========================================
# database/connection.py
# ===========================================
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import Config

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(Config.MONGO_URI)
        print(f"✅ Connected to MongoDB at {Config.MONGO_URI}")
    
    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("❌ MongoDB connection closed")
    
    @classmethod
    def get_db(cls):
        return cls.client[Config.MONGO_DB_NAME]
