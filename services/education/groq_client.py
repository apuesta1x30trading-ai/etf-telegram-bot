import os
from groq import Groq

SYSTEM_PROMPT = """Eres un asistente experto en inversiones y finanzas personales. 
Responde en español, de forma clara y didáctica. 
Usa ejemplos prácticos cuando sea posible.
El usuario está interesado en ETFs, especialmente:
- H4Z3: HSBC MSCI Emerging Markets UCITS ETF (mercados emergentes, TER 0.15%)
- EUNL: iShares Core MSCI World UCITS ETF (mercados desarrollados, TER 0.20%)

Si te preguntan por conceptos financieros, explícalos de forma sencilla.
Si te preguntan por consejos de inversión, recuerda que no eres un asesor financiero 
y que deben consultar con un profesional."""

def get_groq_client():
    """Inicializa el cliente solo cuando se necesita, evitando crashes al inicio."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def ask_groq(user_message: str, history: list = None) -> str:
    client = get_groq_client()
    
    if not client:
        return "⚠️ *Error de configuración:* La clave de API de Groq no está configurada en el servidor. El administrador debe añadir la variable de entorno `GROQ_API_KEY` en Render."
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ *Error al conectar con Groq:* {str(e)}"
