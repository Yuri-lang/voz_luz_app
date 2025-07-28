from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
from TTS.api import TTS

app = Flask(__name__)
CORS(app)

# Ruta a la voz de Luz (debe estar en el mismo directorio en Render)
VOICE_SAMPLE = "Luz_habla.wav"

# Modelo de Coqui-TTS (multilingüe y soporta clonación de voz)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

@app.route("/hablar", methods=["POST"])
def hablar():
    try:
        data = request.json
        texto = data.get("texto", "")

        if not texto:
            return jsonify({"error": "Texto vacío"}), 400

        # Crear archivo temporal para guardar la voz generada
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            salida = temp_audio.name

        # Generar voz clonada de Luz
        tts.tts_to_file(
            text=texto,
            speaker_wav=VOICE_SAMPLE,
            language="es",
            file_path=salida
        )

        # Devolver el archivo de audio
        return send_file(salida, mimetype="audio/wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Luz está lista y hablando con emociones ✨"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
