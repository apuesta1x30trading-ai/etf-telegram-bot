from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS
import yfinance as yf

# Almacenamiento en memoria (se reinicia con el bot)
active_alerts = {}

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso: /alerta <ETF> <precio>\nEjemplo: /alerta H4Z3 17.5")
        return
    
    ticker_key = context.args[0].upper()
    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ El precio debe ser un número.")
        return

    if ticker_key not in ETFS:
        await update.message.reply_text(f"⚠️ ETF no soportado. Usa: {', '.join(ETFS.keys())}")
        return

    chat_id = update.effective_chat.id
    active_alerts[chat_id] = {
        "ticker_key": ticker_key,
        "ticker": ETFS[ticker_key]["ticker_yf"],
        "target": target_price,
        "name": ETFS[ticker_key]["nombre"]
    }
    
    await update.message.reply_text(
        f"✅ *Alerta configurada*\n\nTe avisaré cuando *{ticker_key}* alcance {target_price} EUR.\n⚠️ _Nota: Las alertas se borran si el bot se reinicia._",
        parse_mode="Markdown"
    )

async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    if not active_alerts:
        return
    
    for chat_id, alert in list(active_alerts.items()):
        try:
            data = yf.Ticker(alert["ticker"])
            info = data.info
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            if not current_price:
                continue

            target = alert["target"]
            # Disparar si el precio está dentro del 1% del objetivo o lo cruzó
            if abs(current_price - target) / target < 0.01 or \
               (current_price >= target and info.get('regularMarketPreviousClose', target) < target) or \
               (current_price <= target and info.get('regularMarketPreviousClose', target) > target):
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🚨 *ALERTA DE PRECIO*\n\n{alert['ticker_key']} ha alcanzado tu objetivo de {target} EUR.\n💰 Precio actual: {current_price} EUR",
                    parse_mode="Markdown"
                )
                del active_alerts[chat_id] # Eliminar tras disparar
        except Exception:
            pass # Ignorar errores silenciosamente en background
