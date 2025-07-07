from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
import os
import requests

app = Flask(__name__)

# 👇 Tu clave API de OpenRouter (ya incluida)
OPENROUTER_API_KEY = "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"

# 📁 Crear carpeta de audios si no existe
AUDIO_FOLDER = "static"
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

@app.route('/habla', methods=['POST'])
def habla():
    try:
        datos = request.get_json()
        mensaje = datos.get('mensaje', '').strip()

        if not mensaje:
            return jsonify({'error': 'Mensaje vacío'}), 400

        # 📡 Llamada a la API de OpenRouter
        respuesta = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Eres Luz, una asistente dulce y brillante que habla como una persona real."},
                    {"role": "user", "content": mensaje}
                ]
            }
        )

        if respuesta.status_code != 200:
            return jsonify({'error': 'Error al conectar con OpenRouter'}), 500

        data = respuesta.json()
        texto_respuesta = data["choices"][0]["message"]["content"]

        # 🔊 Generar audio con gTTS
        nombre_archivo = "respuesta.mp3"
        ruta_archivo = os.path.join(AUDIO_FOLDER, nombre_archivo)
        tts = gTTS(text=texto_respuesta, lang='es')
        tts.save(ruta_archivo)

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/audio/{nombre_archivo}"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def servir_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
