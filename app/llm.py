import httpx
import os

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

def ollama_chat(prompt: str, system_prompt: str = "") -> str:
    """
    Envía el prompt a Ollama y devuelve la respuesta como string.
    Si falla, retorna un mensaje de error amigable.
    """
    try:
        payload = {
            "model": "llama3.1:8b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        r = httpx.post(f"{OLLAMA}/v1/chat/completions", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        # Entra a la respuesta correcta
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error en Ollama: {e}")
        return "Error: no se pudo obtener la respuesta de Ollama"
