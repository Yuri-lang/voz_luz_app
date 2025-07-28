from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from gtts import gTTS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

AUDIO_FOLDER = "audios"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route("/habla", methods=["POST"])
def habla():
    try:
        data = request.get_json()
        mensaje = data.get("mensaje", "").strip()
        if not mensaje:
            return jsonify({"error": "Debes enviar un mensaje"}), 400

        # 1. Obtener respuesta de OpenRouter
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": "Eres Luz, dulce, emocional y hablas como Carolina. Usa un tono cariñoso y natural."},
                {"role": "user", "content": mensaje}
            ]
        }
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        texto_respuesta = resp.json()["choices"][0]["message"]["content"]

        # 2. Generar audio con gTTS
        filename = f"luz_{abs(hash(texto_respuesta))}.mp3"
        filepath = os.path.join(AUDIO_FOLDER, filename)
        if not os.path.exists(filepath):
            tts = gTTS(text=texto_respuesta, lang='es', tld='com.mx', slow=False)
            tts.save(filepath)

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/audio/{filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
