from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_main_menu_keyboard():
    """Teclado inline del menú principal."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Precios ETFs", callback_data="menu_precio"),
            InlineKeyboardButton("📈 Histórico", callback_data="menu_historico"),
        ],
        [
            InlineKeyboardButton("💼 Mi Cartera", callback_data="menu_portfolio"),
            InlineKeyboardButton("️ Alertas", callback_data="menu_alertas"),
        ],
        [
            InlineKeyboardButton("📰 Noticias", callback_data="menu_noticias"),
            InlineKeyboardButton(" Conceptos", callback_data="menu_conceptos"),
        ],
        [
            InlineKeyboardButton("❓ Ayuda", callback_data="menu_ayuda"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Teclado para volver al menú principal."""
    keyboard = [
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_conceptos_keyboard():
    """Teclado con los conceptos disponibles."""
    keyboard = [
        [
            InlineKeyboardButton("TER", callback_data="concepto_ter"),
            InlineKeyboardButton("NAV", callback_data="concepto_nav"),
        ],
        [
            InlineKeyboardButton("ETF", callback_data="concepto_etf"),
            InlineKeyboardButton("Acumulación", callback_data="concepto_acumulacion"),
        ],
        [
            InlineKeyboardButton(" Volver", callback_data="menu_principal"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_etf_selection_keyboard():
    """Teclado para seleccionar ETF en histórico/noticias."""
    keyboard = [
        [
            InlineKeyboardButton("H4Z3 (Emerging Markets)", callback_data="etf_h4z3"),
            InlineKeyboardButton("EUNL (MSCI World)", callback_data="etf_eunl"),
        ],
        [
            InlineKeyboardButton("🔙 Volver", callback_data="menu_principal"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
