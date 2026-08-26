import yfinance as yf
import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ETFS

# Almacenamiento en memoria de usuarios suscritos (se reinicia con el bot)
# En un proyecto real, esto iría a una base de datos.
subscribed_users = set()

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
    """Calcula el RSI (Relative Strength Index) de 14 periodos."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

async def toggle_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activa o desactiva las señales automáticas para el usuario."""
    chat_id = update.effective_chat.id
    
    if chat_id in subscribed_users:
        subscribed_users.remove(chat_id)
        await update.message.reply_text("🔕 *Señales automáticas DESACTIVADAS.*\nYa no recibirás análisis de mercado.", parse_mode="Markdown")
    else:
        subscribed_users.add(chat_id)
        await update.message.reply_text(
            "🔔 *Señales automáticas ACTIVADAS.*\n\n"
            "Te avisaré si detecto:\n"
            "• Movimientos bruscos (>2.5% en un día)\n"
            "• RSI en sobreventa (<30) o sobrecompra (>70)\n\n"
            "⚠️ _Esto no es consejo financiero, haz tu propia investigación (DYOR)._",
            parse_mode="Markdown"
        )

async def check_market_signals(context: ContextTypes.DEFAULT_TYPE):
    """Trabajo en segundo plano: analiza el mercado y envía alertas."""
    if not subscribed_users:
        return # Nadie suscrito, no hacemos nada
    
    for ticker_key, etf_info in ETFS.items():
        ticker = etf_info["ticker_yf"]
        nombre = etf_info["nombre"]
        
        try:
            # Obtener datos de los últimos 3 meses para calcular RSI
            data = yf.Ticker(ticker).history(period="3mo")
            if data.empty:
                continue
            
            current_price = float(data['Close'].iloc[-1])
            prev_close = float(data['Close'].iloc[-2])
            daily_change_pct = ((current_price - prev_close) / prev_close) * 100
            
            rsi = calculate_rsi(data)
            
            signals = []
            
            # 1. Chequeo de Movimiento Brusco
            if abs(daily_change_pct) >= 2.5:
                direction = "📈 SUBIDA" if daily_change_pct > 0 else "📉 BAJADA"
                signals.append(f"• *Movimiento Brusco:* {direction} del {abs(daily_change_pct):.2f}% hoy.")
            
            # 2. Chequeo de RSI
            if rsi < 30:
                signals.append(f"• *RSI en Sobreventa:* {rsi:.1f} (Posible zona de COMPRA).")
            elif rsi > 70:
                signals.append(f"• *RSI en Sobrecompra:* {rsi:.1f} (Posible zona de VENTA/Toma de beneficios).")
            
            # Si hay señales, enviar a todos los suscritos
            if signals:
                mensaje = (
                    f"🚨 *SEÑAL DE MERCADO: {ticker_key}*\n"
                    f"_{nombre}_\n\n"
                    f"💰 Precio: {current_price:.2f} EUR\n\n"
                    + "\n".join(signals) + "\n\n"
                    "⚠️ _Recuerda: Esto es análisis técnico automático, no consejo financiero._"
                )
                
                for chat_id in list(subscribed_users):
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=mensaje, parse_mode="Markdown")
                    except Exception:
                        pass # Si el usuario bloqueó el bot, ignorar
        except Exception:
            pass # Ignorar errores de red de yfinance en background
