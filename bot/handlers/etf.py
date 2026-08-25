from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import yfinance as yf
from config import ETFS

async def precio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Obteniendo precios actuales de mercado...")
    
    mensaje = "📊 <b>Precios Actuales de tus ETFs</b>\n\n"
    
    for ticker_key, etf_info in ETFS.items():
        ticker = etf_info["ticker_yf"]
        nombre = etf_info["nombre"]
        
        try:
            data = yf.Ticker(ticker)
            info = data.info
            
            precio = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            cambio = info.get('regularMarketChangePercent', 0)
            moneda = info.get('currency', 'EUR')
            
            emoji = "📈" if cambio > 0 else "📉" if cambio < 0 else "➖"
            
            # Usamos HTML (<b> y <code>) que es mucho más seguro que Markdown
            mensaje += (
                f"<b>{ticker_key}</b> ({nombre})\n"
                f"💰 Precio: <code>{precio} {moneda}</code>\n"
                f"{emoji} Variación hoy: <code>{cambio:.2f}%</code>\n\n"
            )
        except Exception as e:
            mensaje += f"❌ Error al obtener datos de {ticker_key}: {str(e)}\n\n"
            
    await update.message.reply_text(mensaje, parse_mode="HTML")
