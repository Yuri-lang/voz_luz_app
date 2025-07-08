from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
import os
import requests

app = Flask(__name__, static_folder=".")

# Tu clave de OpenRouter
OPENROUTER_API_KEY = "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"

@app.route('/habla', methods=['POST'])
def habla():
    try:
        datos = request.get_json()
        mensaje = datos.get('mensaje', '')
        
        if not mensaje:
            return jsonify({'error': 'Mensaje vacío'}), 400

        # Enviar solicitud a OpenRouter
        respuesta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",  # Puedes cambiar por "mistralai/mistral-7b-instruct"
                "messages": [
                    {"role": "system", "content": "Eres Luz, una asistente dulce que responde como una persona real."},
                    {"role": "user", "content": mensaje}
                ]
            }
        )

        # 👇 Debug
        print("Código de estado:", respuesta.status_code)
        print("Texto completo:", respuesta.text)

        if respuesta.status_code != 200:
            return jsonify({'error': 'Error al conectar con OpenRouter'}), 500

        respuesta_json = respuesta.json()
        texto_respuesta = respuesta_json["choices"][0]["message"]["content"]

        # Generar respuesta de voz con gTTS
        tts = gTTS(text=texto_respuesta, lang='es')
        nombre_archivo = "respuesta.mp3"
        tts.save(nombre_archivo)

        return jsonify({"respuesta": texto_respuesta, "audio_url": f"/audio/{nombre_archivo}"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def servir_audio(filename):
    return send_from_directory('.', filename)

# ✅ Ruta de prueba de conexión
@app.route('/check_openrouter')
def check_openrouter():
    try:
        r = requests.get("https://openrouter.ai/api/v1")
        return jsonify({"estado": r.status_code, "contenido": r.text[:200]})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
