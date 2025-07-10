from flask import Flask, request, jsonify
from gtts import gTTS  # 👈 Añade esto para audio real
import os

app = Flask(__name__)

@app.route("/habla", methods=["POST"])
def habla():
    datos = request.get_json()
    mensaje = datos.get("mensaje", "").strip()
    
    if not mensaje:
        return jsonify({"error": "El mensaje no puede estar vacío"}), 400

    # Genera audio (ejemplo básico)
    tts = gTTS(text=f"Recibí: {mensaje}", lang='es')
    audio_path = "audios/respuesta.mp3"
    tts.save(audio_path)

    return jsonify({
        "status": "success",
        "message": "🐻 ¡Luz te escucha!",
        "audio": audio_path,
        "input": mensaje  # Para debug
    })

if __name__ == "__main__":
    os.makedirs("audios", exist_ok=True)  # Crea carpeta para audios
    app.run(host='0.0.0.0', port=5000)
