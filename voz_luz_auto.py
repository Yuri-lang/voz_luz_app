from flask import Flask, request, jsonify
from gtts import gTTS
import os
import openai
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "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"  # Usa tu clave válida

@app.route('/habla', methods=['POST'])
def habla():
    try:
        datos = request.get_json()
        mensaje = datos.get('mensaje', '')
        
        if not mensaje:
            return jsonify({'error': 'Mensaje vacío'}), 400

        # Consulta a OpenRouter (como GPT)
        respuesta = requests.post(
            'https://api.openrouter.ai/v1/chat/completions',
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

        respuesta_json = respuesta.json()
        texto_respuesta = respuesta_json["choices"][0]["message"]["content"]

        # Generar audio con gTTS
        tts = gTTS(text=texto_respuesta, lang='es')
        nombre_archivo = "respuesta.mp3"
        tts.save(nombre_archivo)

        return jsonify({"respuesta": texto_respuesta, "audio_url": f"/audio/{nombre_archivo}"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def servir_audio(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
