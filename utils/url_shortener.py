
# ===========================================
# utils/url_shortener.py
# ===========================================
import aiohttp
import random
from typing import Optional
from config.settings import Config

class URLShortener:
    @staticmethod
    async def shorten_url(destination_url: str) -> Optional[str]:
        """Randomly choose a URL shortener and shorten the URL"""
        shorteners = list(Config.URL_SHORTENERS.keys())
        chosen = random.choice(shorteners)
        
        config = Config.URL_SHORTENERS[chosen]
        api_token = config["api_token"]
        base_url = config["base_url"]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{base_url}?api={api_token}&url={destination_url}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Different shorteners have different response formats
                        if chosen == "get2short":
                            return data.get("shortenedUrl")
                        elif chosen == "just2earn":
                            return data.get("shortenedUrl")
                    return None
        except Exception as e:
            print(f"❌ Error shortening URL with {chosen}: {e}")
            return None
    
    @staticmethod
    def get_whitelist_domains() -> list:
        """Get list of whitelisted domains from URL shorteners"""
        domains = []
        for config in Config.URL_SHORTENERS.values():
            base_url = config["base_url"]
            # Extract domain from base URL
            domain = base_url.split("//")[1].split("/")[0]
            domains.append(domain)
        return domains
