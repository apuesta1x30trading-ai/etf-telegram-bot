import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RENDER_URL = os.getenv("RENDER_URL", "http://localhost:8000")

# ETFs a monitorizar
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
