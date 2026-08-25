from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import yfinance as yf
from config import ETFS
from services.cache import price_cache

async def precio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Obteniendo precios actuales de mercado...")
    
    mensaje = "📊 <b>Precios Actuales de tus ETFs</b>\n\n"
    
    for ticker_key, etf_info in ETFS.items():
        ticker = etf_info["ticker_yf"]
        nombre = etf_info["nombre"]
        
        try:
            # Intentar obtener del caché primero
            cached_data = price_cache.get(ticker)
            
            if cached_data:
                precio = cached_data["precio"]
                cambio = cached_data["cambio"]
                moneda = cached_data["moneda"]
                fuente = " (caché)"
            else:
                # Consultar Yahoo Finance
                data = yf.Ticker(ticker)
                info = data.info
                
                precio = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                cambio = info.get('regularMarketChangePercent', 0)
                moneda = info.get('currency', 'EUR')
                
                # Guardar en caché
                price_cache.set(ticker, {
                    "precio": precio,
                    "cambio": cambio,
                    "moneda": moneda
                })
                fuente = ""
            
            emoji = "" if cambio > 0 else "📉" if cambio < 0 else "➖"
            
            mensaje += (
                f"<b>{ticker_key}</b> ({nombre}){fuente}\n"
                f"💰 Precio: <code>{precio} {moneda}</code>\n"
                f"{emoji} Variación hoy: <code>{cambio:.2f}%</code>\n\n"
            )
        except Exception as e:
            mensaje += f"❌ Error al obtener datos de {ticker_key}: {str(e)}\n\n"
            
    await update.message.reply_text(mensaje, parse_mode="HTML")
