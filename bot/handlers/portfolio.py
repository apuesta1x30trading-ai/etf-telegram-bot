from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS
import yfinance as yf

async def portfolio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if 'portfolio' not in context.user_data:
        context.user_data['portfolio'] = {}
    
    portfolio = context.user_data['portfolio']
    
    if not portfolio:
        await update.message.reply_text(
            "📂 *Tu cartera está vacía.*\n\n"
            "Usa /añadir <ETF> <cantidad> para empezar.\n"
            "Ejemplo: /añadir EUNL 10",
            parse_mode="Markdown"
        )
        return
    
    mensaje = "💼 *Tu Cartera de Inversión*\n\n"
    total_value = 0.0
    
    for ticker_key, shares in portfolio.items():
        if ticker_key in ETFS:
            ticker = ETFS[ticker_key]["ticker_yf"]
            data = yf.Ticker(ticker)
            info = data.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            value = price * shares if price else 0
            total_value += value
            
            mensaje += f"• *{ticker_key}*: {shares} acciones @ {price:.2f} EUR = *{value:.2f} EUR*\n"
    
    mensaje += f"\n💰 *Valor Total Estimado*: {total_value:.2f} EUR\n\n⚠️ _Nota: La cartera se reinicia si el bot se reinicia._"
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def add_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso: /añadir <ETF> <cantidad>\nEjemplo: /añadir H4Z3 50")
        return
    
    ticker_key = context.args[0].upper()
    try:
        shares = float(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ La cantidad debe ser un número.")
        return
    
    if ticker_key not in ETFS:
        await update.message.reply_text(f"⚠️ ETF no soportado. Usa: {', '.join(ETFS.keys())}")
        return
    
    if 'portfolio' not in context.user_data:
        context.user_data['portfolio'] = {}
    
    current = context.user_data['portfolio'].get(ticker_key, 0)
    context.user_data['portfolio'][ticker_key] = current + shares
    
    await update.message.reply_text(f"✅ Añadido: {shares} acciones de {ticker_key}.\nTotal: {context.user_data['portfolio'][ticker_key]} acciones.")

async def clear_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['portfolio'] = {}
    await update.message.reply_text("🗑️ Cartera vaciada correctamente.")
