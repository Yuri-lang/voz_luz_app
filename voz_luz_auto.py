from flask import Flask, request, jsonify
from gtts import gTTS
import os
import requests

app = Flask(__name__)

# --- Configuración segura ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # 🚨 La clave va en Render!

@app.route("/habla", methods=["POST"])
def habla():
    try:
        mensaje = request.json.get("mensaje")
        if not mensaje:
            return jsonify({"error": "Se necesita un mensaje"}), 400

        # --- Conexión con OpenRouter ---
        respuesta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": mensaje}]
            }
        )

        texto_respuesta = respuesta.json()["choices"][0]["message"]["content"]
        
        # --- Generar audio ---
        tts = gTTS(text=texto_respuesta, lang="es")
        tts.save("audios/respuesta.mp3")

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": "/audio/respuesta.mp3"
        })

    except Exception as e:
        return jsonify({"error": f"¡Oso atascado! {str(e)}"}), 500

@app.route("/audio/<filename>")
def servir_audio(filename):
    return send_from_directory("audios", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render usa puerto 10000
