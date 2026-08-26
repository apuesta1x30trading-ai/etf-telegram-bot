from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import yfinance as yf
from config import ETFS
from services.cache import price_cache

async def precio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Obteniendo precios actuales de mercado...")
    
    mensaje = "📊 Precios Actuales de tus ETFs\n\n"
    
    for ticker_key, etf_info in ETFS.items():
        ticker = etf_info["ticker_yf"]  # ej: H4Z3.DE
        nombre = etf_info["nombre"]
        
        try:
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
                
                # Verificación de seguridad por si Yahoo devuelve datos vacíos
                if not info or ('currentPrice' not in info and 'regularMarketPrice' not in info):
                    raise Exception("Datos no disponibles temporalmente")
                
                precio = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                cambio = info.get('regularMarketChangePercent', 0)
                moneda = info.get('currency', 'EUR')
                
                # Guardar en caché por 1 hora
                price_cache.set(ticker, {
                    "precio": precio,
                    "cambio": cambio,
                    "moneda": moneda
                })
                fuente = ""
            
            emoji = "📈" if cambio > 0 else "📉" if cambio < 0 else "➖"
            
            mensaje += (
                f"{ticker_key} - {nombre}{fuente}\n"
                f"💰 Precio: {precio} {moneda}\n"
                f"{emoji} Variación hoy: {cambio:.2f}%\n\n"
            )
        except Exception as e:
            mensaje += f"⚠️ {ticker_key}: Datos no disponibles en este momento. Intenta más tarde.\n\n"
            
    await update.message.reply_text(mensaje)
