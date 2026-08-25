import os

# Render inyecta estas variables directamente. 
# Si faltan, asignamos un valor por defecto para que no crashee al importar.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TU_TOKEN_AQUI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
RENDER_URL = os.getenv("RENDER_URL", "http://localhost:8000")

# Configuración de los ETFs a monitorizar
ETFS = {
    "H4Z3": {
        "ticker_yf": "H4Z3.DE",
        "nombre": "HSBC MSCI Emerging Markets UCITS ETF",
        "isin": "IE000KCS7J59",
        "ter": "0.15%",
    },
    "EUNL": {
        "ticker_yf": "EUNL.DE",
        "nombre": "iShares Core MSCI World UCITS ETF",
        "isin": "IE00B4L5Y983",
        "ter": "0.20%",
    },
}
