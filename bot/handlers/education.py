from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from services.education.groq_client import ask_groq
import json
import os

CONCEPTS_PATH = os.path.join(
    os.path.dirname(__file__), 
    "../../services/education/concepts_db.json"
)

try:
    with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
        CONCEPTS = json.load(f)
except FileNotFoundError:
    CONCEPTS = {}

async def concepto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        conceptos_list = "\n".join(f"• /concepto_{k}" for k in CONCEPTS.keys())
        await update.message.reply_text(
            f"📚 <b>Conceptos disponibles:</b>\n\n{conceptos_list}\n\n"
            "O pregúntame directamente cualquier duda de inversión.",
            parse_mode="HTML"
        )
        return
    
    key = context.args[0].lower()
    concept = CONCEPTS.get(key)
    
    if concept:
        texto = (
            f"📖 <b>{concept['titulo']}</b>\n\n"
            f"{concept['definicion']}\n\n"
            f"💡 <b>Ejemplo:</b> {concept['ejemplo']}\n\n"
            f"🎯 <b>Por qué importa:</b> {concept['relevancia']}"
        )
    else:
        texto = f"❓ No tengo '{key}' en mi base de conceptos. Prueba a preguntarme directamente o usa /conceptos para ver la lista."
    
    await update.message.reply_text(texto, parse_mode="HTML")

async def education_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_chat_action("typing")
    
    try:
        respuesta = ask_groq(user_message)
        # Enviamos sin parse_mode para que el Markdown de la IA no rompa nada
        await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error al procesar tu pregunta: {str(e)}")

def get_concept_handlers():
    handlers = []
    for key in CONCEPTS.keys():
        async def concept_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, k=key):
            concept = CONCEPTS[k]
            texto = (
                f"📖 <b>{concept['titulo']}</b>\n\n"
                f"{concept['definicion']}\n\n"
                f"💡 <b>Ejemplo:</b> {concept['ejemplo']}\n\n"
                f"🎯 <b>Por qué importa:</b> {concept['relevancia']}"
            )
            await update.message.reply_text(texto, parse_mode="HTML")
        handlers.append(CommandHandler(f"concepto_{key}", concept_handler))
    return handlers
