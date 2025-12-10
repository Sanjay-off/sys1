# ===========================================
# utils/token_generator.py
# ===========================================
import secrets
from config.settings import Config

def generate_token(length: int = Config.TOKEN_LENGTH) -> str:
    """Generate a URL-safe base64 token"""
    return secrets.token_urlsafe(length)[:length]

def generate_unique_id(length: int = Config.UNIQUE_ID_LENGTH) -> str:
    """Generate a unique ID for resources"""
    return secrets.token_urlsafe(length)[:length]

def generate_batch_unique_id(length: int = 30) -> str:
    """Generate a unique ID for batch resources"""
    return secrets.token_urlsafe(length)[:length]