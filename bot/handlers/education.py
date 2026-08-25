from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from services.education.groq_client import ask_groq
from services.education.concepts_db import get_concept
import json
import os

# Cargar base de conceptos
CONCEPTS_PATH = os.path.join(
    os.path.dirname(__file__), 
    "../../services/education/concepts_db.json"
)
with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
    CONCEPTS = json.load(f)

async def concepto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca un concepto en la base de datos local."""
    if not context.args:
        conceptos_list = "\n".join(f"• /concepto_{k}" for k in CONCEPTS.keys())
        await update.message.reply_text(
            f" *Conceptos disponibles:*\n\n{conceptos_list}\n\n"
            "O pregúntame directamente cualquier duda de inversión.",
            parse_mode="Markdown"
        )
        return
    
    key = context.args[0].lower()
    concept = CONCEPTS.get(key)
    
    if concept:
        texto = (
            f"📖 *{concept['titulo']}*\n\n"
            f"{concept['definicion']}\n\n"
            f"💡 *Ejemplo:* {concept['ejemplo']}\n\n"
            f"🎯 *Por qué importa:* {concept['relevancia']}"
        )
    else:
        texto = f"❓ No tengo '{key}' en mi base de conceptos. Prueba a preguntarme directamente."
    
    await update.message.reply_text(texto, parse_mode="Markdown")

async def education_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde dudas de inversión usando Groq."""
    user_message = update.message.text
    
    # Indicador de "escribiendo..."
    await update.message.reply_chat_action("typing")
    
    try:
        respuesta = ask_groq(user_message)
        await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Error al procesar tu pregunta: {str(e)}"
        )

# Handlers para cada concepto
def get_concept_handlers():
    handlers = []
    for key in CONCEPTS.keys():
        async def concept_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, k=key):
            concept = CONCEPTS[k]
            texto = (
                f"📖 *{concept['titulo']}*\n\n"
                f"{concept['definicion']}\n\n"
                f"💡 *Ejemplo:* {concept['ejemplo']}\n\n"
                f"🎯 *Por qué importa:* {concept['relevancia']}"
            )
            await update.message.reply_text(texto, parse_mode="Markdown")
        handlers.append(CommandHandler(f"concepto_{key}", concept_handler))
    return handlers
