import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, JobQueue, CallbackQueryHandler

from config import TELEGRAM_TOKEN
from bot.handlers.start import start, help_cmd, menu_callback
from bot.handlers.education import concepto_cmd, education_chat, get_concept_handlers
from bot.handlers.etf import precio_cmd
from bot.handlers.alerts import set_alert, check_alerts
from bot.handlers.history import historico_cmd
from bot.handlers.portfolio import portfolio_cmd, add_asset, clear_portfolio
from bot.handlers.news import noticias_cmd

app = FastAPI()

# 1. Construir la aplicación con JobQueue habilitado
application = Application.builder().token(TELEGRAM_TOKEN).job_queue(JobQueue()).build()

# 2. Registrar handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(CommandHandler("concepto", concepto_cmd))
application.add_handler(CommandHandler("conceptos", concepto_cmd))
application.add_handler(CommandHandler("precio", precio_cmd))
application.add_handler(CommandHandler("alerta", set_alert))
application.add_handler(CommandHandler("historico", historico_cmd))
application.add_handler(CommandHandler("portfolio", portfolio_cmd))
application.add_handler(CommandHandler("add", add_asset))
application.add_handler(CommandHandler("clear", clear_portfolio))
application.add_handler(CommandHandler("noticias", noticias_cmd))

# Handler para los botones del menú inline
application.add_handler(CallbackQueryHandler(menu_callback))

for handler in get_concept_handlers():
    application.add_handler(handler)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, education_chat))

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
@app.head("/")
async def health():
    return {"status": "ok", "message": "ETF Bot is running"}

@app.on_event("startup")
async def startup():
    render_url = os.getenv("RENDER_URL", "http://localhost:8000")
    webhook_url = f"{render_url}/webhook"
    print(f"🔗 Configurando webhook en: {webhook_url}")
    
    await application.initialize()
    await application.bot.set_webhook(webhook_url)
    
    # Programar el chequeo de alertas cada 15 minutos (900 segundos)
    application.job_queue.run_repeating(check_alerts, interval=900, first=60)
    print("✅ Bot inicializado, webhook configurado y alertas programadas.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
