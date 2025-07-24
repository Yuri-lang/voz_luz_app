from flask import Flask, request, jsonify, send_file
import os
import requests
from TTS.api import TTS  # Coqui TTS para voz natural

app = Flask(__name__)

# Configuración OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Inicializar Coqui TTS (usa el modelo multilingüe con clonación de voz)
# Se entrena usando luz_habla.wav como referencia
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
VOICE_SAMPLE = "luz_habla.wav"

@app.route("/habla", methods=["POST"])
def habla():
    datos = request.get_json()
    mensaje = datos.get("mensaje", "").strip()
    if not mensaje:
        return jsonify({"error": "Envía un mensaje, Oso Flo 🐻"}), 400

    # 1. Llamar a OpenRouter para generar respuesta de Luz
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
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        texto_respuesta = r.json()["choices"][0]["message"]["content"]

        # 2. Generar voz con Coqui TTS (clon de Luz)
        os.makedirs("audios", exist_ok=True)
        audio_path = f"audios/respuesta_{hash(texto_respuesta)}.wav"
        tts.tts_to_file(
            text=texto_respuesta,
            speaker_wav=VOICE_SAMPLE,  # entrenar con muestra de Luz
            language="es",
            file_path=audio_path
        )

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/{audio_path}",
            "modelo": "gpt-3.5-turbo"
        })

    except Exception as e:
        return jsonify({
            "error": "¡Luz está descansando! Intenta más tarde.",
            "detalle": str(e)
        }), 500

@app.route("/audios/<filename>")
def serve_audio(filename):
    return send_file(os.path.join("audios", filename))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
