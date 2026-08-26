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
                
                # Intentar obtener el precio de diferentes formas
                precio = None
                for key in ['currentPrice', 'regularMarketPrice', 'previousClose', 'bid', 'ask']:
                    if key in info and info[key] is not None:
                        precio = info[key]
                        break
                
                if precio is None:
                    # Último intento: usar fast_info
                    try:
                        fast_info = data.fast_info
                        precio = float(fast_info.last_price)
                    except:
                        raise Exception("No se pudo obtener el precio")
                
                # Obtener cambio porcentual
                cambio = info.get('regularMarketChangePercent', 0)
                if cambio is None:
                    cambio = 0
                
                # Obtener moneda
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
                f"{ticker_key} - {nombre}{fuente}\n"
                f"💰 Precio: {precio} {moneda}\n"
                f"{emoji} Variación hoy: {cambio:.2f}%\n\n"
            )
        except Exception as e:
            # Mensaje más informativo
            mensaje += f"️ {ticker_key}: Temporalmente sin datos. Intenta en unos minutos.\n\n"
            
    await update.message.reply_text(mensaje)
