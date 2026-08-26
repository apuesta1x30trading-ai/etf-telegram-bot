import os
import requests
from services.cache import price_cache

API_KEY = os.getenv("EODHD_API_KEY", "")
BASE_URL = "https://eodhd.com/api"

def get_etf_price(ticker: str, exchange: str = "XETRA"):
    """
    Obtiene precios usando EOD Historical Data.
    Excelente cobertura de ETFs europeos.
    """
    if not API_KEY:
        return {"error": "API key de EODHD no configurada"}
    
    try:
        cache_key = f"eodhd_{ticker}_{exchange}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        # EODHD usa formato: SIMBOLO.EXCHANGE
        # Para ETFs europeos: H4Z3.XETRA o EUNL.XETRA
        symbol = f"{ticker}.{exchange}"
        
        url = f"{BASE_URL}/real-time/{symbol}"
        params = {
            "api_token": API_KEY,
            "fmt": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Error API: {response.status_code}"}
        
        data = response.json()
        
        # Verificar si hay error
        if "error" in data:
            return {"error": data["error"]}
        
        price = float(data.get("close", 0))
        if price == 0:
            return {"error": f"Símbolo '{symbol}' no encontrado"}
        
        # Calcular cambio
        previous_close = float(data.get("previousClose", price))
        cambio = ((price - previous_close) / previous_close * 100) if previous_close else 0
        
        price_data = {
            "precio": price,
            "cambio": float(cambio),
            "moneda": data.get("currency", "EUR"),
            "nombre": data.get("name", ticker)
        }
        
        price_cache.set(cache_key, price_data)
        return price_data
        
    except Exception as e:
        return {"error": str(e)}
