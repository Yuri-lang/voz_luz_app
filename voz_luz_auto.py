from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
import os
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "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"

# Crear carpeta 'static' si no existe
os.makedirs("static", exist_ok=True)

@app.route('/habla', methods=['POST'])
def habla():
    try:
        datos = request.get_json()
        mensaje = datos.get('mensaje', '')

        if not mensaje:
            return jsonify({'error': 'Mensaje vacío'}), 400

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

        texto_respuesta = respuesta.json()["choices"][0]["message"]["content"]

        tts = gTTS(text=texto_respuesta, lang='es')
        filename = "respuesta.mp3"
        filepath = os.path.join("static", filename)
        tts.save(filepath)

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/audio/{filename}"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def servir_audio(filename):
    return send_from_directory("static", filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
