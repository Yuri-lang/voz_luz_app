from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from gtts import gTTS
import subprocess

app = Flask(__name__)
CORS(app)

# Configuración OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Carpetas para audios y animaciones
AUDIO_FOLDER = "audios"
VIDEO_FOLDER = "videos"
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

@app.route("/habla", methods=["POST"])
def habla():
    try:
        datos = request.get_json()
        mensaje = datos.get("mensaje", "").strip()
        if not mensaje:
            return jsonify({"error": "Envía un mensaje, Oso Flo 🐻"}), 400

        # 1. Obtener respuesta desde OpenRouter
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": "Eres Luz, hablas con voz dulce como Carolina y usas un tono cariñoso con emojis."},
                {"role": "user", "content": mensaje}
            ]
        }

        respuesta = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
        respuesta.raise_for_status()
        texto_respuesta = respuesta.json()["choices"][0]["message"]["content"]

        # 2. Generar audio con gTTS
        audio_file = f"voz_{hash(texto_respuesta)}.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_file)
        tts = gTTS(text=texto_respuesta, lang='es', tld='com.mx', slow=False)
        tts.save(audio_path)

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/audio/{audio_file}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/animar", methods=["POST"])
def animar():
    try:
        datos = request.get_json()
        audio_url = datos.get("audio_url")
        if not audio_url:
            return jsonify({"error": "Debes enviar la URL del audio generado"}), 400

        audio_path = os.path.join(AUDIO_FOLDER, os.path.basename(audio_url))
        video_file = f"animacion_{os.path.basename(audio_url).replace('.mp3', '.mp4')}"
        video_path = os.path.join(VIDEO_FOLDER, video_file)

        # 3. Ejecutar SadTalker (requiere que esté instalado en Render)
        subprocess.run([
            "sadtalker", "--driven_audio", audio_path,
            "--source_image", "assets/luz_inicio.png",
            "--output", video_path,
            "--still"
        ], check=True)

        return jsonify({
            "video_url": f"/video/{video_file}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/audio/<filename>")
def servir_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route("/video/<filename>")
def servir_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
