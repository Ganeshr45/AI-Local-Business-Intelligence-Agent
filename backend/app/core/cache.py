import time


class TTLCache:
    def __init__(self, ttl_seconds: int = 900):
        self.ttl_seconds = ttl_seconds
        self.store = {}

    def get(self, key: str):
        entry = self.store.get(key)
        if not entry:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self.store[key]
            return None
        return value

    def set(self, key: str, value):
        self.store[key] = (value, time.time() + self.ttl_seconds)


places_cache = TTLCache(ttl_seconds=3600)
search_cache = TTLCache(ttl_seconds=3600)
scrape_cache = TTLCache(ttl_seconds=3600)
