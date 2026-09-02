from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS
import requests
import os
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
from datetime import datetime

API_KEY = os.getenv("EODHD_API_KEY", "")
BASE_URL = "https://eodhd.com/api"

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

    ticker = ETFS[ticker_key]["ticker_yf"]
    nombre = ETFS[ticker_key]["nombre"]
    
    await update.message.reply_text(f"📈 Generando gráfico de 1 año para {ticker_key}...")
    
    try:
        # Usar EODHD para datos históricos
        # Formato: H4Z3.XETRA o EUNL.XETRA
        symbol = f"{ticker}.XETRA"
        
        url = f"{BASE_URL}/eod/{symbol}"
        params = {
            "api_token": API_KEY,
            "from": "2025-08-26",  # 1 año atrás
            "to": "2026-08-26",
            "fmt": "json"
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            await update.message.reply_text(f"❌ Error al obtener datos: {response.status_code}")
            return
        
        data = response.json()
        
        if not data or len(data) == 0:
            await update.message.reply_text("No hay datos históricos disponibles para este ETF.")
            return
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        if df.empty:
            await update.message.reply_text("No hay datos para generar el gráfico.")
            return
        
        # Crear gráfico
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['close'], label='Precio de Cierre', color='#1f77b4', linewidth=2)
        plt.title(f"{nombre} ({ticker_key}) - Último Año", fontsize=14, fontweight='bold')
        plt.xlabel("Fecha", fontsize=12)
        plt.ylabel("Precio (EUR)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name
            plt.savefig(temp_path, format='png', dpi=150, bbox_inches='tight')
            plt.close()
        
        # Enviar imagen
        with open(temp_path, 'rb') as photo:
            caption = (
                f" *Gráfico de 1 año de {ticker_key}*\n"
                f" Precio actual: {df['close'].iloc[-1]:.2f} EUR\n"
                f"📈 Máx: {df['high'].max():.2f} | Mín: {df['low'].min():.2f} EUR"
            )
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode="Markdown")
        
        import os
        os.remove(temp_path)
        
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error de conexión: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al generar el gráfico: {str(e)}")
