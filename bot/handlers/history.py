import os
import tempfile
import yfinance as yf
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS

async def historico_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            f"⚠️ Uso: /historico <ETF>\n"
            f"Ejemplo: /historico EUNL\n"
            f"Disponibles: {', '.join(ETFS.keys())}"
        )
        return
    
    ticker_key = context.args[0].upper()
    if ticker_key not in ETFS:
        await update.message.reply_text(
            f"⚠️ ETF no soportado. Usa: {', '.join(ETFS.keys())}"
        )
        return

    ticker = ETFS[ticker_key]["ticker_yf"]  # Ej: H4Z3.DE o EUNL.DE
    nombre = ETFS[ticker_key]["nombre"]
    
    await update.message.reply_text(f"📈 Generando gráfico de 1 año para {ticker_key}...")
    
    try:
        # Obtener datos históricos de Yahoo Finance (no requiere API key)
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")
        
        if hist.empty:
            await update.message.reply_text(f"❌ No hay datos históricos disponibles para {ticker_key}.")
            return

        # Crear el gráfico
        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist['Close'], label='Precio de Cierre', color='#1f77b4', linewidth=2)
        plt.title(f"{nombre} ({ticker_key}) - Último Año", fontsize=14, fontweight='bold')
        plt.xlabel("Fecha", fontsize=12)
        plt.ylabel("Precio (EUR)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name
            plt.savefig(temp_path, format='png', dpi=150, bbox_inches='tight')
            plt.close()
        
        # Enviar la imagen a Telegram
        current_price = hist['Close'].iloc[-1]
        max_price = hist['High'].max()
        min_price = hist['Low'].min()
        
        caption = (
            f"📊 *Gráfico de 1 año de {ticker_key}*\n"
            f"💰 Precio actual: {current_price:.2f} EUR\n"
            f"📈 Máx: {max_price:.2f} | Mín: {min_price:.2f} EUR"
        )
        
        with open(temp_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode="Markdown")
        
        # Limpiar el archivo temporal
        os.remove(temp_path)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error al generar el gráfico: {str(e)}")
