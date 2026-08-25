import time
from typing import Dict, Any

class PriceCache:
    """Caché simple en memoria para precios de ETFs."""
    
    def __init__(self, ttl_seconds: int = 600):  # 10 minutos por defecto
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
    
    def get(self, ticker: str) -> Dict[str, Any] | None:
        """Obtiene el precio del caché si no ha expirado."""
        if ticker in self._cache:
            data = self._cache[ticker]
            if time.time() - data["timestamp"] < self._ttl:
                return data["data"]
            else:
                # Eliminar dato expirado
                del self._cache[ticker]
        return None
    
    def set(self, ticker: str, data: Dict[str, Any]):
        """Guarda un precio en el caché."""
        self._cache[ticker] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def clear(self):
        """Limpia todo el caché."""
        self._cache.clear()

# Instancia global del caché
price_cache = PriceCache(ttl_seconds=900)  # 15 minutos
