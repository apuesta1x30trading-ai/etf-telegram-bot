from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def demo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """📊 Precios Actuales de tus ETFs (DEMO)

H4Z3 - HSBC MSCI Emerging Markets UCITS ETF
 Precio: 45.32 EUR
 Variación hoy: +1.23%

EUNL - iShares Core MSCI World UCITS ETF
💰 Precio: 126.50 EUR
📉 Variación hoy: -0.45%

️ Estos son datos de ejemplo. El comando /precio mostrará datos reales cuando Yahoo Finance permita las peticiones."""
    
    await update.message.reply_text(mensaje)
