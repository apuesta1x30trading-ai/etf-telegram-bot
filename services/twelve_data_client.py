import os
from twelvedata import TDClient
from services.cache import price_cache

API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")

def get_etf_price(ticker: str, exchange: str = "EURONEXT"):
    """
    Obtiene el precio de un ETF usando Twelve Data.
    Exchange: EURONEXT (para ETFs europeos como H4Z3 y EUNL)
    """
    if not API_KEY:
        return {"error": "API key de Twelve Data no configurada"}
    
    try:
        cache_key = f"{ticker}_{exchange}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        td = TDClient(apikey=API_KEY)
        
        # Probar primero con EURONEXT
        quote = td.quote(symbol=f"{ticker}:{exchange}")
        
        # Verificar si hay datos válidos
        precio = getattr(quote, 'close', 0)
        
        # Si el precio es 0, intentar sin exchange (búsqueda global)
        if precio == 0 or precio is None:
            quote = td.quote(symbol=ticker)
        
        data = {
            "precio": float(getattr(quote, 'close', 0) or 0),
            "cambio": float(getattr(quote, 'percent_change', 0) or 0),
            "moneda": getattr(quote, 'currency', 'EUR'),
            "nombre": getattr(quote, 'symbol', ticker)
        }
        
        price_cache.set(cache_key, data)
        
        return data
        
    except Exception as e:
        return {"error": str(e)}
