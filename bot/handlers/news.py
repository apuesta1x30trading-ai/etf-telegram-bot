from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS
import yfinance as yf

async def noticias_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(f"⚠️ Uso: /noticias <ETF>\nEjemplo: /noticias EUNL\nDisponibles: {', '.join(ETFS.keys())}")
        return
    
    ticker_key = context.args[0].upper()
    if ticker_key not in ETFS:
        await update.message.reply_text(f"⚠️ ETF no soportado. Usa: {', '.join(ETFS.keys())}")
        return

    ticker = ETFS[ticker_key]["ticker_yf"]
    await update.message.reply_text(f"📰 Buscando últimas noticias sobre {ticker_key}...")
    
    try:
        data = yf.Ticker(ticker)
        news_list = data.news
        
        if not news_list:
            await update.message.reply_text("No se encontraron noticias recientes para este ETF.")
            return
        
        mensaje = f"📰 *Últimas noticias sobre {ticker_key}*\n\n"
        for i, news in enumerate(news_list[:3], 1):
            title = news.get('title', 'Sin título')
            publisher = news.get('publisher', 'Desconocido')
            link = news.get('link', '')
            mensaje += f"{i}. *{title}*\n   📌 {publisher}\n   🔗 [Leer más]({link})\n\n"
        
        await update.message.reply_text(mensaje, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener noticias: {str(e)}")
