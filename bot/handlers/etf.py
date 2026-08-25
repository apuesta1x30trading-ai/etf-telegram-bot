from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import yfinance as yf
from config import ETFS
from services.cache import price_cache
import html

def escape_html(text: str) -> str:
    """Escapa caracteres especiales HTML para evitar errores de parseo."""
    return html.escape(str(text))

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
            
            emoji = "📈" if cambio > 0 else "📉" if cambio < 0 else "➖"
            
            # ESCAPAR todos los datos dinámicos para evitar errores HTML
            nombre_escaped = escape_html(nombre)
            precio_escaped = escape_html(str(precio))
            moneda_escaped = escape_html(str(moneda))
            cambio_escaped = escape_html(f"{cambio:.2f}")
            fuente_escaped = escape_html(fuente)
            
            mensaje += (
                f"<b>{ticker_key}</b> ({nombre_escaped}){fuente_escaped}\n"
                f"💰 Precio: <code>{precio_escaped} {moneda_escaped}</code>\n"
                f"{emoji} Variación hoy: <code>{cambio_escaped}%</code>\n\n"
            )
        except Exception as e:
            error_escaped = escape_html(str(e))
            mensaje += f"❌ Error al obtener datos de {ticker_key}: {error_escaped}\n\n"
            
    await update.message.reply_text(mensaje, parse_mode="HTML")
