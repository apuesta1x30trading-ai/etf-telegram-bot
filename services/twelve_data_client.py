import os
from twelvedata import TDClient
from services.cache import price_cache

API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")

def get_etf_price(ticker: str):
    """
    Obtiene el precio de un ETF usando Twelve Data.
    Formato correcto para bolsa alemana: SIMBOLO.XETRA
    """
    if not API_KEY:
        return {"error": "API key de Twelve Data no configurada"}
    
    try:
        cache_key = f"td_{ticker}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        td = TDClient(apikey=API_KEY)
        
        # 1. Intentar con el formato correcto para XETRA (ej: EUNL.XETRA)
        symbol_to_try = f"{ticker}.XETRA"
        quote = td.quote(symbol=symbol_to_try)
        
        precio = getattr(quote, 'close', 0)
        
        # 2. Si no encuentra precio, intentar con el símbolo global (sin exchange)
        if not precio or precio == 0:
            quote = td.quote(symbol=ticker)
            precio = getattr(quote, 'close', 0)
            
        # 3. Si sigue sin haber precio, devolver error claro
        if not precio or precio == 0:
            return {"error": f"No se encontró el símbolo '{ticker}' en Twelve Data."}

        data = {
            "precio": float(precio),
            "cambio": float(getattr(quote, 'percent_change', 0) or 0),
            "moneda": getattr(quote, 'currency', 'EUR'),
            "nombre": getattr(quote, 'name', ticker)
        }
        
        # Guardar en caché
        price_cache.set(cache_key, data)
        
        return data
        
    except Exception as e:
        return {"error": str(e)}
