import os
import requests
from services.cache import price_cache

API_KEY = os.getenv("FMP_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_etf_price(ticker: str):
    """
    Obtiene el precio de un ETF usando Financial Modeling Prep.
    Soporta ETFs europeos como H4Z3 y EUNL.
    """
    if not API_KEY:
        return {"error": "API key de FMP no configurada"}
    
    try:
        cache_key = f"fmp_{ticker}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        # FMP usa el símbolo directo para ETFs europeos
        url = f"{BASE_URL}/quote/{ticker}?apikey={API_KEY}"
        
        response = requests.get(url, timeout=10)
        data_json = response.json()
        
        if not data_json or len(data_json) == 0:
            return {"error": f"No se encontró el símbolo '{ticker}' en FMP"}
        
        quote = data_json[0]
        
        price_data = {
            "precio": float(quote.get("price", 0)),
            "cambio": float(quote.get("changesPercentage", 0)),
            "moneda": quote.get("currency", "EUR"),
            "nombre": quote.get("name", ticker)
        }
        
        # Guardar en caché
        price_cache.set(cache_key, price_data)
        
        return price_data
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Error de conexión: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
