from flask import Flask, request, jsonify
from gtts import gTTS
import os
import requests  # 👈 Necesario para OpenRouter

app = Flask(__name__)

# Configuración OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # 🚨 Usa variables de entorno!
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/habla", methods=["POST"])
def habla():
    # 1. Validar entrada
    datos = request.get_json()
    mensaje = datos.get("mensaje", "").strip()
    if not mensaje:
        return jsonify({"error": "Envía un mensaje, Oso Flo 🐻"}), 400

    # 2. Llamar a OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Eres Luz, un asistente dulce y empático. Responde como un humano cercano."},
            {"role": "user", "content": mensaje}
        ]
    }

    try:
        respuesta = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=10)
        respuesta.raise_for_status()  # Lanza error si hay fallos HTTP
        texto_respuesta = respuesta.json()["choices"][0]["message"]["content"]

        # 3. Generar audio
        tts = gTTS(text=texto_respuesta, lang='es', tld='com.mx', slow=False)
        audio_path = f"audios/respuesta_{hash(texto_respuesta)}.mp3"
        tts.save(audio_path)

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/{audio_path}",
            "modelo": "gpt-3.5-turbo"
        })

    except Exception as e:
        return jsonify({
            "error": "¡Luz está cansada! Intenta más tarde",
            "detalle": str(e)
        }), 500

if __name__ == "__main__":
    os.makedirs("audios", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
