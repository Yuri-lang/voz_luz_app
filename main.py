from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from TTS.api import TTS
import os

app = Flask(__name__)
CORS(app)

# Cargamos modelo de Coqui (voz femenina multilingüe)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

@app.route("/hablar", methods=["POST"])
def hablar():
    data = request.json
    texto = data.get("texto", "Hola, soy Luz. Estoy lista para hablar contigo.")

    salida = "voz_luz.wav"
    # Generar voz
    tts.tts_to_file(text=texto, file_path=salida, speaker_wav=None, language="es")

    return send_file(salida, mimetype="audio/wav")

@app.route("/")
def index():
    return jsonify({"status": "Luz está activa y lista para hablar"})
