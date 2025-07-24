from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import requests
from TTS.api import TTS

app = Flask(__name__)
CORS(app)

# Configuración OpenRouter (para generar respuestas de texto)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Inicializar TTS de Coqui
# Usamos modelo multilingüe y soporta speaker embedding
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

# Archivo de referencia para clonar la voz (muestra de Carolina)
VOICE_SAMPLE = "luz_habla.wav"

@app.route("/habla", methods=["POST"])
def habla():
    datos = request.get_json()
    mensaje = datos.get("mensaje", "").strip()

    if not mensaje:
        return jsonify({"error": "Debes enviar un mensaje"}), 400

    # Paso 1: obtener respuesta de Luz desde OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Eres Luz, una asistente dulce y emocional. Habla de forma natural."},
            {"role": "user", "content": mensaje}
        ]
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        texto_respuesta = r.json()["choices"][0]["message"]["content"]

        # Paso 2: generar voz con Coqui (usando embedding de Carolina)
        audio_path = f"audios/luz_{hash(texto_respuesta)}.wav"
        os.makedirs("audios", exist_ok=True)

        tts.tts_to_file(
            text=texto_respuesta,
            speaker_wav=VOICE_SAMPLE,
            file_path=audio_path,
            language="es"
        )

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/{audio_path}",
            "voz": "Carolina (Luz)"
        })

    except Exception as e:
        return jsonify({"error": "Luz está descansando", "detalle": str(e)}), 500

@app.route("/audios/<path:filename>")
def serve_audio(filename):
    return send_file(os.path.join("audios", filename))

if __name__ == "__main__":
    os.makedirs("audios", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
