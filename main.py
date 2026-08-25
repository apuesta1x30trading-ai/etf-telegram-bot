from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handlers.start import start, help_cmd
from bot.handlers.education import concepto_cmd, education_chat, get_concept_handlers
from config import TELEGRAM_TOKEN

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
    update = Update.de_await(await request.json(), application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
async def health():
    return {"status": "ok", "message": "ETF Bot is running"}

@app.on_event("startup")
async def startup():
    webhook_url = f"{os.getenv('RENDER_URL')}/webhook"
    await application.bot.set_webhook(webhook_url)
    print(f"Webhook set to {webhook_url}")

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
