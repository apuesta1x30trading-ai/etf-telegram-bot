from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS
from services.fmp_client import get_etf_price

async def precio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Obteniendo precios actuales de mercado...")
    
    mensaje = " Precios Actuales de tus ETFs\n\n"
    
    for ticker_key, etf_info in ETFS.items():
        # FMP usa el símbolo sin sufijo (.DE)
        raw_ticker = etf_info.get("ticker_yf", ticker_key)
        ticker = raw_ticker.replace(".DE", "").replace(".F", "")
        nombre = etf_info["nombre"]
        
        data = get_etf_price(ticker)
        
        if "error" in data:
            mensaje += f"❌ Error con {ticker_key}: {data['error']}\n\n"
        else:
            precio = data["precio"]
            cambio = data["cambio"]
            moneda = data["moneda"]
            
            emoji = "" if cambio > 0 else "📉" if cambio < 0 else "➖"
            
            mensaje += (
                f"{ticker_key} - {nombre}\n"
                f"💰 Precio: {precio} {moneda}\n"
                f"{emoji} Variación hoy: {cambio:.2f}%\n\n"
            )
    
    await update.message.reply_text(mensaje)
