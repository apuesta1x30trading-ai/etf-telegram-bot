import os
import requests
from services.cache import price_cache

API_KEY = os.getenv("FMP_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_etf_price(ticker: str):
    """
    Obtiene el precio de un ETF usando Financial Modeling Prep.
    """
    if not API_KEY:
        return {"error": "API key de FMP no configurada"}
    
    try:
        cache_key = f"fmp_{ticker}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        # Intentar con diferentes formatos de símbolo
        symbols_to_try = [
            ticker,                    # H4Z3
            f"{ticker}.DE",           # H4Z3.DE
            f"{ticker}.XETRA",        # H4Z3.XETRA
        ]
        
        for symbol in symbols_to_try:
            url = f"{BASE_URL}/quote/{symbol}?apikey={API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                continue
                
            data_json = response.json()
            
            # Si encontramos datos válidos
            if data_json and len(data_json) > 0:
                quote = data_json[0]
                
                # Verificar que tenga precio válido
                price = quote.get("price", 0)
                if price and price > 0:
                    price_data = {
                        "precio": float(price),
                        "cambio": float(quote.get("changesPercentage", 0)),
                        "moneda": quote.get("currency", "EUR"),
                        "nombre": quote.get("name", ticker)
                    }
                    
                    price_cache.set(cache_key, price_data)
                    return price_data
        
        # Si llegamos aquí, no encontramos el símbolo en ningún formato
        return {"error": f"ETF '{ticker}' no encontrado en FMP. Verifica que el símbolo sea correcto."}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Error de conexión: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}
