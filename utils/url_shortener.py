# ===========================================
# utils/url_shortener.py - FIXED
# ===========================================
import asyncio
import aiohttp
import random
from typing import Optional
from config.settings import Config

class URLShortener:
    @staticmethod
    async def shorten_url(destination_url: str) -> Optional[str]:
        """Randomly choose a URL shortener and shorten the URL"""
        if not Config.URL_SHORTENERS:
            print("⚠️  No URL shorteners configured")
            return None
        
        shorteners = list(Config.URL_SHORTENERS.keys())
        chosen = random.choice(shorteners)
        
        config = Config.URL_SHORTENERS[chosen]
        api_token = config["api_token"]
        base_url = config["base_url"]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{base_url}?api={api_token}&url={destination_url}"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Different shorteners have different response formats
                        if chosen == "get2short":
                            shortened = data.get("shortenedUrl")
                        elif chosen == "just2earn":
                            shortened = data.get("shortenedUrl")
                        else:
                            shortened = data.get("shortenedUrl") or data.get("shorturl") or data.get("short_url")
                        
                        if shortened:
                            print(f"✅ URL shortened with {chosen}: {shortened}")
                            return shortened
                        else:
                            print(f"⚠️  {chosen} returned no shortened URL: {data}")
                            return None
                    else:
                        print(f"⚠️  {chosen} returned status {response.status}")
                        return None
        except asyncio.TimeoutError:
            print(f"⚠️  {chosen} timeout")
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
            if "//" in base_url:
                domain = base_url.split("//")[1].split("/")[0]
                domains.append(domain)
        return domains