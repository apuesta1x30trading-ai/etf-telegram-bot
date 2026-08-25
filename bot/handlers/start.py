from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "👋 *¡Bienvenido al Bot de ETFs!*\n\n"
        "Monitorizo tus inversiones y te ayudo a aprender sobre ellas.\n\n"
        "📊 *Comandos de ETFs:*\n"
        "• /precio - Precios actuales de H4Z3 y EUNL\n"
        "• /comparar - Comparativa de rendimiento\n"
        "• /portfolio - Tu cartera simulada\n"
        "• /alertas - Configurar alertas de precio\n\n"
        "📚 *Aprende sobre inversión:*\n"
        "• /conceptos - Lista de conceptos disponibles\n"
        "• /concepto_[nombre] - Explicación detallada\n"
        "• O simplemente *pregúntame* cualquier duda\n\n"
        "💡 *Ejemplos de preguntas:*\n"
        "• ¿Qué es el TER?\n"
        "• ¿Diferencia entre acumulación y distribución?\n"
        "• ¿Cuál es mejor, H4Z3 o EUNL?"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
