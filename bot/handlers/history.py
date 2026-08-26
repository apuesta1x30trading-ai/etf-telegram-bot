from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS
import yfinance as yf
import matplotlib.pyplot as plt
import os
import tempfile

async def historico_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(f"⚠️ Uso: /historico <ETF>\nEjemplo: /historico EUNL\nDisponibles: {', '.join(ETFS.keys())}")
        return
    
    ticker_key = context.args[0].upper()
    if ticker_key not in ETFS:
        await update.message.reply_text(f"⚠️ ETF no soportado. Usa: {', '.join(ETFS.keys())}")
        return

    ticker = ETFS[ticker_key]["ticker_yf"]
    nombre = ETFS[ticker_key]["nombre"]
    
    await update.message.reply_text(f"📈 Generando gráfico de 1 año para {ticker_key}...")
    
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")
        
        if hist.empty:
            await update.message.reply_text("No hay datos históricos disponibles.")
            return

        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist['Close'], label='Precio de Cierre', color='#1f77b4', linewidth=2)
        plt.title(f"{nombre} ({ticker_key}) - Último Año", fontsize=14, fontweight='bold')
        plt.xlabel("Fecha", fontsize=12)
        plt.ylabel("Precio (EUR)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name
            plt.savefig(temp_path, format='png', dpi=150, bbox_inches='tight')
            plt.close()
        
        with open(temp_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=f"📊 Gráfico de 1 año de *{ticker_key}*", parse_mode="Markdown")
        
        os.remove(temp_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error al generar el gráfico: {str(e)}")
