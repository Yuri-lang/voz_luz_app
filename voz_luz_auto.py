import os
import requests
from flask import Flask, request, jsonify
from gtts import gTTS

app = Flask(__name__)

# ✅ Configuración (usa variables de entorno para la API KEY!)
API_KEY = os.getenv("OPENROUTER_API_KEY", "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")  # ¡Cambia esto!
API_URL = "https://api.openrouter.ai/v1/chat/completions"

def hablar(texto):
    try:
        print("💬 Luz responde:", texto)
        tts = gTTS(text=texto, lang='es', tld='com')
        archivo = "voz_luz.mp3"
        tts.save(archivo)
        # Si estás en Termux:
        if os.path.exists("/data/data/com.termux/files/usr/bin/termux-media-player"):
            os.system(f"termux-media-player play {archivo}")
        else:  # Para otros entornos
            print("🔊 Audio guardado en:", archivo)
    except Exception as e:
        print("❌ Error en hablar():", e)

@app.route('/habla', methods=['POST'])
def habla():
    try:
        datos = request.get_json()
        if not datos or 'mensaje' not in datos:
            return jsonify({"error": "Formato incorrecto. Usa {'mensaje': 'tu_texto'}"}), 400

        mensaje_usuario = datos['mensaje']
        print("🟢 Usuario dice:", mensaje_usuario)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://osoflo.com",  # Opcional
            "X-Title": "LuzApp"  # Opcional
        }

        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Eres Luz, una amiga dulce..."},
                {"role": "user", "content": mensaje_usuario}
            ]
        }

        respuesta = requests.post(API_URL, headers=headers, json=data, timeout=10)
        respuesta.raise_for_status()  # Lanza error si HTTP != 200
        contenido = respuesta.json()

        if "choices" in contenido:
            texto_respuesta = contenido["choices"][0]["message"]["content"]
            hablar(texto_respuesta)
            return jsonify({"respuesta": texto_respuesta})
        else:
            print("❌ Respuesta inesperada de la API:", contenido)
            return jsonify({"error": "La API no devolvió una respuesta válida"}), 500

    except requests.exceptions.RequestException as e:
        print("❌ Error de conexión:", e)
        return jsonify({"error": f"Error al conectar con OpenRouter: {str(e)}"}), 502
    except Exception as e:
        print("❌ Error inesperado:", e)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    print("✨ Luz está escuchando en http://127.0.0.1:5000/habla")
    app.run(host='0.0.0.0', port=5000, debug=True)  # debug=True para más detalles
