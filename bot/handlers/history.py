import os
import requests
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS

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

    raw_ticker = ETFS[ticker_key]["ticker_yf"]
    nombre = ETFS[ticker_key]["nombre"]
    
    # Limpiar el ticker para EODHD (quitar .DE o .L si existe en la config)
    ticker = raw_ticker.replace(".DE", "").replace(".L", "")
    
    await update.message.reply_text(f"📈 Generando gráfico de 1 año para {ticker_key}...")
    
    # EODHD a veces usa sufijos diferentes para históricos. Probamos en orden:
    symbols_to_try = [f"{ticker}.XETRA", f"{ticker}.L", ticker]
    
    df = None
    last_error = ""
    
    for symbol in symbols_to_try:
        try:
            url = f"{BASE_URL}/eod/{symbol}"
            params = {
                "api_token": API_KEY,
                "period": "d",
                "fmt": "json"
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 404:
                last_error = f"404: Símbolo '{symbol}' no encontrado en EODHD."
                continue
            elif response.status_code != 200:
                last_error = f"Error HTTP {response.status_code}: {response.text}"
                continue
            
            data = response.json()
            
            if isinstance(data, dict) and "error" in data:
                last_error = f"API Error: {data['error']}"
                continue
                
            if not data or len(data) == 0:
                last_error = f"Sin datos históricos para '{symbol}'."
                continue
            
            # Convertir a DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Si llegamos aquí, tenemos datos válidos. ¡Salimos del bucle!
            break
            
        except Exception as e:
            last_error = str(e)
            continue

    if df is None or df.empty:
        await update.message.reply_text(
            f"❌ No se pudieron obtener datos históricos.\n"
            f"Último error: {last_error}\n\n"
            f"💡 Verifica que la variable EODHD_API_KEY esté correctamente configurada en Render."
        )
        return

    try:
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
                f"📊 *Gráfico de 1 año de {ticker_key}*\n"
                f"💰 Precio actual: {df['close'].iloc[-1]:.2f} EUR\n"
                f"📈 Máx: {df['high'].max():.2f} | Mín: {df['low'].min():.2f} EUR"
            )
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode="Markdown")
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error al generar el gráfico: {str(e)}")
