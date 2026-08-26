import os
import requests
from services.cache import price_cache

API_KEY = os.getenv("FINNHUB_API_KEY", "")
BASE_URL = "https://finnhub.io/api/v1"

def get_etf_price(ticker: str, exchange: str = "DE"):
    """
    Obtiene el precio de un ETF usando Finnhub.
    exchange: DE (XETRA), L (Londres), etc.
    """
    if not API_KEY:
        return {"error": "API key de Finnhub no configurada"}
    
    try:
        cache_key = f"finnhub_{ticker}_{exchange}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        # Finnhub usa formato: EXCHANGE:TICKER
        # Ejemplo: DE:H4Z3 o L:EUNL
        symbol = f"{exchange.upper()}:{ticker}"
        
        url = f"{BASE_URL}/quote"
        params = {
            "symbol": symbol,
            "token": API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Error API: {response.status_code}"}
        
        data = response.json()
        
        # Verificar si hay datos válidos
        current_price = data.get("c", 0)  # 'c' = current price
        
        if not current_price or current_price == 0:
            # Intentar sin exchange (solo ticker)
            return get_etf_price_simple(ticker)
        
        # Calcular cambio porcentual
        previous_close = data.get("pc", 0)  # 'pc' = previous close
        cambio = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
        
        price_data = {
            "precio": float(current_price),
            "cambio": float(cambio),
            "moneda": "EUR" if exchange == "DE" else "GBP" if exchange == "L" else "USD",
            "nombre": ticker
        }
        
        price_cache.set(cache_key, price_data)
        return price_data
        
    except Exception as e:
        return {"error": str(e)}

def get_etf_price_simple(ticker: str):
    """Fallback: intentar solo con el ticker sin exchange."""
    if not API_KEY:
        return {"error": "API key no configurada"}
    
    try:
        url = f"{BASE_URL}/quote"
        params = {
            "symbol": ticker,
            "token": API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Error API: {response.status_code}"}
        
        data = response.json()
        current_price = data.get("c", 0)
        
        if not current_price or current_price == 0:
            return {"error": f"Símbolo '{ticker}' no encontrado en Finnhub"}
        
        previous_close = data.get("pc", 0)
        cambio = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
        
        price_data = {
            "precio": float(current_price),
            "cambio": float(cambio),
            "moneda": "EUR",
            "nombre": ticker
        }
        
        return price_data
        
    except Exception as e:
        return {"error": str(e)}
