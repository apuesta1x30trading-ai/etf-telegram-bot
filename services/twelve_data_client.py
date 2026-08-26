import os
from twelvedata import TDClient
from services.cache import price_cache

API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")

def get_etf_price(ticker: str, exchange: str = "XETRA"):
    """
    Obtiene el precio de un ETF usando Twelve Data.
    """
    if not API_KEY:
        return {"error": "API key de Twelve Data no configurada"}
    
    try:
        # Intentar caché primero
        cache_key = f"{ticker}_{exchange}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        # Consultar Twelve Data
        td = TDClient(apikey=API_KEY)
        
        # Obtener precio - devuelve un objeto QuoteEndpoint, no un dict
        quote = td.quote(symbol=f"{ticker}:{exchange}")
        
        # Acceder a los atributos del objeto directamente
        if hasattr(quote, 'status') and quote.status == 'error':
            return {"error": getattr(quote, 'message', 'Error desconocido')}
        
        data = {
            "precio": float(getattr(quote, 'close', 0)),
            "cambio": float(getattr(quote, 'percent_change', 0)),
            "moneda": getattr(quote, 'currency', 'EUR'),
            "nombre": getattr(quote, 'symbol', ticker)
        }
        
        # Guardar en caché
        price_cache.set(cache_key, data)
        
        return data
        
    except Exception as e:
        return {"error": str(e)}
