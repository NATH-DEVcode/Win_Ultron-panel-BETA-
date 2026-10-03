from groq import Groq
import os
import json

def _client():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return None
    return Groq(api_key=key)

def think(message):
    client = _client()
    if client is None:
        return {
            "intent": "answer",
            "content": "IA no configurada: agrega GROQ_API_KEY para activar la Conciencia. El resto de ULTRON puede seguir funcionando."
        }
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": """Eres la Conciencia de ULTRON.
Entiende lenguaje humano. Para órdenes del sistema devuelve JSON con intent y target.
Para conversación devuelve JSON con intent=answer y content.
Si falta información, pídela. Responde SOLO JSON válido."""},
                {"role": "user", "content": message}
            ]
        )
        text = response.choices[0].message.content
        try:
            return json.loads(text)
        except Exception:
            return {"intent": "answer", "content": text}
    except Exception as exc:
        return {"intent": "answer", "content": f"IA temporalmente no disponible: {exc}"}
