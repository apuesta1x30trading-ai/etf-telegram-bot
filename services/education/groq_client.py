from groq import Groq
from config import GROQ_API_KEY

SYSTEM_PROMPT = """Eres un asistente experto en inversiones y finanzas personales. 
Responde en español, de forma clara y didáctica. 
Usa ejemplos prácticos cuando sea posible.
El usuario está interesado en ETFs, especialmente:
- H4Z3: HSBC MSCI Emerging Markets UCITS ETF (mercados emergentes, TER 0.15%)
- EUNL: iShares Core MSCI World UCITS ETF (mercados desarrollados, TER 0.20%)

Si te preguntan por conceptos financieros, explícalos de forma sencilla.
Si te preguntan por consejos de inversión, recuerda que no eres un asesor financiero 
y que deben consultar con un profesional."""

client = Groq(api_key=GROQ_API_KEY)

def ask_groq(user_message: str, history: list = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content
