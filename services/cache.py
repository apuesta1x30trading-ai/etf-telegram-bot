import time
from typing import Dict, Any

class PriceCache:
    """Caché en memoria con TTL de 1 hora para evitar rate limits de Yahoo Finance."""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hora = 3600 segundos
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Dict[str, Any] | None:
        if key in self._cache:
            data = self._cache[key]
            if time.time() - data["timestamp"] < self._ttl:
                return data["data"]
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, data: Dict[str, Any]):
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def clear(self):
        self._cache.clear()

# Instancia global
price_cache = PriceCache(ttl_seconds=3600)
