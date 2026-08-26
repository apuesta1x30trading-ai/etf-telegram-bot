import os
from twelvedata import TDClient
from services.cache import price_cache

# Inicializar cliente
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
        
        # Consultar Twelve Data - NOTA: usar 'apikey' no 'api_key'
        td = TDClient(apikey=API_KEY)
        
        # Obtener precio en tiempo real
        quote = td.quote(symbol=f"{ticker}:{exchange}")
        
        if quote.get("status") == "error":
            return {"error": quote.get("message", "Error desconocido")}
        
        data = {
            "precio": float(quote.get("close", 0)),
            "cambio": float(quote.get("percent_change", 0)),
            "moneda": quote.get("currency", "EUR"),
            "nombre": quote.get("symbol", ticker)
        }
        
        # Guardar en caché
        price_cache.set(cache_key, data)
        
        return data
        
    except Exception as e:
        return {"error": str(e)}
