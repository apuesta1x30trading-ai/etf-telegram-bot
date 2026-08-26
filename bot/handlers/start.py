from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from bot.keyboards import get_main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "👋 *¡Bienvenido al Bot de ETFs!*\n\n"
        "Monitorizo tus inversiones y te ayudo a aprender sobre ellas.\n\n"
        "Selecciona una opción del menú:"
    )
    
    await update.message.reply_text(
        texto, 
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📖 *Comandos Disponibles:*\n\n"
        " *ETFs y Precios:*\n"
        "• /precio - Precios actuales\n"
        "• /historico <ETF> - Gráfico 1 año\n"
        "• /noticias <ETF> - Últimas noticias\n\n"
        "💼 *Cartera:*\n"
        "• /portfolio - Ver cartera\n"
        "• /add <ETF> <cantidad> - Añadir\n"
        "• /clear - Vaciar cartera\n\n"
        "⚠️ *Alertas:*\n"
        "• /alerta <ETF> <precio>\n\n"
        "📚 *Educación:*\n"
        "• /conceptos - Lista de conceptos\n"
        "• Escribe cualquier duda y te responderé\n\n"
        "❓ *Ayuda:*\n"
        "• /start - Menú principal\n"
        "• /help - Esta ayuda"
    )
    
    await update.message.reply_text(texto, parse_mode="Markdown")

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los clicks en los botones del menú."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "menu_principal":
        await start(update, context)
    
    elif data == "menu_precio":
        await query.edit_message_text(
            "📊 *Precios Actuales de tus ETFs*\n\n"
            "Usa el comando /precio para ver los precios actualizados.",
            parse_mode="Markdown"
        )
        # Ejecutar el comando precio automáticamente
        from bot.handlers.etf import precio_cmd
        await precio_cmd(update, context)
    
    elif data == "menu_historico":
        await query.edit_message_text(
            "📈 *Gráfico Histórico*\n\n"
            "Selecciona un ETF:",
            parse_mode="Markdown",
            reply_markup=get_etf_selection_keyboard()
        )
    
    elif data == "menu_portfolio":
        await query.edit_message_text(
            "💼 *Tu Cartera de Inversión*\n\n"
            "Usa /portfolio para ver tu cartera o /add para añadir.",
            parse_mode="Markdown"
        )
        from bot.handlers.portfolio import portfolio_cmd
        await portfolio_cmd(update, context)
    
    elif data == "menu_alertas":
        await query.edit_message_text(
            "⚠️ *Configurar Alerta de Precio*\n\n"
            "Usa: /alerta <ETF> <precio>\n"
            "Ejemplo: /alerta EUNL 130",
            parse_mode="Markdown"
        )
    
    elif data == "menu_noticias":
        await query.edit_message_text(
            " *Noticias de ETFs*\n\n"
            "Selecciona un ETF:",
            parse_mode="Markdown",
            reply_markup=get_etf_selection_keyboard()
        )
    
    elif data == "menu_conceptos":
        await query.edit_message_text(
            "📚 *Conceptos de Inversión*\n\n"
            "Selecciona un concepto:",
            parse_mode="Markdown",
            reply_markup=get_conceptos_keyboard()
        )
    
    elif data == "menu_ayuda":
        await help_cmd(update, context)
    
    elif data.startswith("etf_"):
        etf = data.split("_")[1].upper()
        # Determinar si venía de histórico o noticias
        # Por simplicidad, mostramos ambas opciones
        keyboard = [
            [
                InlineKeyboardButton("📈 Ver Histórico", callback_data=f"action_historico_{etf}"),
            ],
            [
                InlineKeyboardButton("📰 Ver Noticias", callback_data=f"action_noticias_{etf}"),
            ],
            [
                InlineKeyboardButton(" Volver", callback_data="menu_principal"),
            ],
        ]
        from telegram import InlineKeyboardMarkup
        await query.edit_message_text(
            f"Has seleccionado *{etf}*\n\n¿Qué quieres ver?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("action_"):
        action, etf = data.split("_")[1], data.split("_")[2]
        if action == "historico":
            from bot.handlers.history import historico_cmd
            await query.edit_message_text(f"📈 Generando gráfico para {etf}...")
            # Crear un update falso para pasar al handler
            class FakeUpdate:
                def __init__(self):
                    self.message = query.message
                    self.effective_chat = query.message.chat
            fake_update = FakeUpdate()
            class FakeContext:
                def __init__(self):
                    self.args = [etf]
                    self.bot = context.bot
            fake_context = FakeContext()
            await historico_cmd(fake_update, fake_context)
        elif action == "noticias":
            from bot.handlers.news import noticias_cmd
            await query.edit_message_text(f"📰 Buscando noticias para {etf}...")
            class FakeUpdate:
                def __init__(self):
                    self.message = query.message
                    self.effective_chat = query.message.chat
            fake_update = FakeUpdate()
            class FakeContext:
                def __init__(self):
                    self.args = [etf]
                    self.bot = context.bot
            fake_context = FakeContext()
            await noticias_cmd(fake_update, fake_context)
    
    elif data.startswith("concepto_"):
        concepto = data.split("_")[1]
        from bot.handlers.education import get_concept_handlers
        # Buscar el handler del concepto
        for handler in get_concept_handlers():
            if handler.command and concepto in handler.command:
                class FakeUpdate:
                    def __init__(self):
                        self.message = query.message
                        self.effective_chat = query.message.chat
                fake_update = FakeUpdate()
                class FakeContext:
                    def __init__(self):
                        self.args = [concepto]
                        self.bot = context.bot
                fake_context = FakeContext()
                await handler.callback(fake_update, fake_context)
                break

# Importar InlineKeyboardButton aquí para el callback
from telegram import InlineKeyboardButton
