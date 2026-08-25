import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Importar configuraciones y handlers
from config import TELEGRAM_TOKEN
from bot.handlers.start import start, help_cmd
from bot.handlers.education import concepto_cmd, education_chat, get_concept_handlers

app = FastAPI()

# Crear aplicación del bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Registrar handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(CommandHandler("concepto", concepto_cmd))
application.add_handler(CommandHandler("conceptos", concepto_cmd))

# Handlers dinámicos para cada concepto
for handler in get_concept_handlers():
    application.add_handler(handler)

# Handler para mensajes de texto (asistente educativo)
application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, education_chat)
)

@app.post("/webhook")
async def webhook(request: Request):
    # de_json es el método correcto para parsear la actualización en v20+
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
@app.head("/")  # <-- Añade esta línea para que Render no cierre el servicio
async def health():
    return {"status": "ok", "message": "ETF Bot is running"}

@app.on_event("startup")
async def startup():
    render_url = os.getenv("RENDER_URL", "http://localhost:8000")
    webhook_url = f"{render_url}/webhook"
    print(f"🔗 Setting webhook to: {webhook_url}")
    await application.bot.set_webhook(webhook_url)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
