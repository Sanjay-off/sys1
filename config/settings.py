import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Tokens
    ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
    USER_BOT_TOKEN = os.getenv("USER_BOT_TOKEN")
    
    # Admin IDs
    ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
    
    # MongoDB
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "telegram_resource_db")
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
    
    # Channels
    PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID"))
    
    # Server
    SERVER_HOST = os.getenv("SERVER_HOST", "192.168.1.33")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5000))
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")
    
    # URL Shorteners
    URL_SHORTENERS = {
        "get2short": {
            "api_token": os.getenv("GET2SHORT_API_TOKEN"),
            "base_url": os.getenv("GET2SHORT_BASE_URL", "https://get2short.com/st")
        },
        "just2earn": {
            "api_token": os.getenv("JUST2EARN_API_TOKEN"),
            "base_url": os.getenv("JUST2EARN_BASE_URL", "https://just2earn.com/api")
        }
    }
    
    # Message Effects
    FIRE_EFFECT_ID = os.getenv("FIRE_EFFECT_ID", "5104841245755180586")
    UNAUTHORIZED_EFFECT_ID = os.getenv("UNAUTHORIZED_EFFECT_ID", "5046589136895476101")
    
    # Defaults
    DEFAULT_MEDIA_ACCESS_COUNT = int(os.getenv("DEFAULT_MEDIA_ACCESS_COUNT", 10))
    DEFAULT_DELETION_TIME = int(os.getenv("DEFAULT_DELETION_TIME", 30))
    DEFAULT_ZIP_PASSWORD = os.getenv("DEFAULT_ZIP_PASSWORD", "telegram123")
    
    # Rate Limits
    BROADCAST_RATE_LIMIT = 2  # users per second
    USER_REQUEST_RATE_LIMIT = 5  # requests per minute
    
    # Token Settings
    MAX_TOKENS_PER_DAY = 15
    TOKEN_EXPIRY_DAYS = 2
    TOKEN_LENGTH = 100
    UNIQUE_ID_LENGTH = 10