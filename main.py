import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
from bot.handlers.start import start, help_cmd
from bot.handlers.education import concepto_cmd, education_chat, get_concept_handlers

app = FastAPI()

# 1. Construir la aplicación del bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

# 2. Registrar handlers básicos
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(CommandHandler("concepto", concepto_cmd))
application.add_handler(CommandHandler("conceptos", concepto_cmd))

# 3. Registrar handlers dinámicos para cada concepto del JSON
for handler in get_concept_handlers():
    application.add_handler(handler)

# 4. Handler para chat libre (asistente educativo)
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, education_chat))

# 5. Handler para precios de ETFs (si el archivo existe)
try:
    from bot.handlers.etf import precio_cmd
    application.add_handler(CommandHandler("precio", precio_cmd))
except ImportError:
    pass # Si aún no has creado el archivo etf.py, no fallará

@app.post("/webhook")
async def webhook(request: Request):
    # Parsear la actualización de Telegram
    update = Update.de_json(await request.json(), application.bot)
    # Procesar la actualización
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
@app.head("/")  # Permite los chequeos de salud de Render sin errores 405
async def health():
    return {"status": "ok", "message": "ETF Bot is running"}

@app.on_event("startup")
async def startup():
    render_url = os.getenv("RENDER_URL", "http://localhost:8000")
    webhook_url = f"{render_url}/webhook"
    print(f"🔗 Configurando webhook en: {webhook_url}")
    
    # ¡CRUCIAL! Inicializar la aplicación antes de procesar updates
    await application.initialize()
    await application.bot.set_webhook(webhook_url)
    print("✅ Bot inicializado y webhook configurado correctamente.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
