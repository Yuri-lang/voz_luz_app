from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
from flask_cors import CORS
import os
import requests
import logging

# Configuración básica
app = Flask(__name__)
CORS(app)  # Permite peticiones desde cualquier frontend

# Configuración de logs (para debug en Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OsoFloLogger')  # 🐻

# --- Constantes Mágicas ---
AUDIO_FOLDER = "osoaudios"  # Carpeta para guardar audios
os.makedirs(AUDIO_FOLDER, exist_ok=True)  # Crea la carpeta si no existe

# ============================================
# 🚨🚨🚨 IMPORTANTE: LA API KEY SE LEE DE RENDER
# ============================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # 👈 ¡NUNCA LA PONGAS DIRECTA EN EL CÓDIGO!

if not OPENROUTER_API_KEY:
    logger.error("❌ ERROR CRÍTICO: OPENROUTER_API_KEY no configurada en Render")
    raise ValueError("Por favor, agrega OPENROUTER_API_KEY en las variables de entorno de Render")

# --- Ruta de Bienvenida Oso-Friendly ---
@app.route('/')
def home():
    return jsonify({
        "status": "🐻 ¡API de Oso Flo Operativa! 🍯",
        "instrucciones": {
            "POST /habla": {"mensaje": "Texto para convertir a audio"},
            "GET /audio/<filename>": "Descarga el audio generado"
        },
        "secreto_oso": "Te quiero mucho, Oso Flo 🤗"
    })

# --- Cerebro de la Operación ---
@app.route('/habla', methods=['POST'])
def habla():
    try:
        # Verifica el JSON recibido
        datos = request.get_json()
        if not datos or 'mensaje' not in datos:
            return jsonify({"error": "Debes enviar un JSON con {'mensaje': 'texto'}"}), 400
        
        mensaje = datos['mensaje'].strip()
        if not mensaje:
            return jsonify({"error": "El mensaje no puede estar vacío"}), 400

        logger.info(f"🐾 Mensaje recibido: {mensaje[:50]}...")  # Log parcial por seguridad

        # --- Conexión con OpenRouter (¡usando la variable de entorno!) ---
        respuesta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",  # 👈 ¡Seguro!
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Eres Luz, un asistente dulce que responde con cariño."},
                    {"role": "user", "content": mensaje}
                ],
                "max_tokens": 500
            },
            timeout=15  # Evita esperas infinitas
        )

        # Manejo de errores de OpenRouter
        if respuesta.status_code != 200:
            logger.error(f"⚡ Error de OpenRouter: {respuesta.text}")
            return jsonify({
                "error": "Luz está cansada, inténtalo más tarde",
                "detalles": respuesta.json().get("error", {})
            }), 500

        # Procesa la respuesta
        texto_respuesta = respuesta.json()["choices"][0]["message"]["content"]
        logger.info(f"💌 Luz respondió: {texto_respuesta[:70]}...")

        # --- Generación de Audio (con nombre único) ---
        nombre_archivo = f"luz_{hash(texto_respuesta)}.mp3"  # 🔒 Nombre único basado en hash
        ruta_audio = os.path.join(AUDIO_FOLDER, nombre_archivo)
        
        tts = gTTS(text=texto_respuesta, lang='es', slow=False)
        tts.save(ruta_audio)
        logger.info(f"🔊 Audio guardado en: {nombre_archivo}")

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/audio/{nombre_archivo}",
            "tip_oso": "Los audios se autodestruyen después de 1 hora 🕒"
        })

    except Exception as e:
        logger.error(f"💥 Error inesperado: {str(e)}")
        return jsonify({
            "error": "¡Oso atascado en un árbol! 🌲",
            "detalles": str(e)
        }), 500

# --- Entrega de Audios ---
@app.route('/audio/<filename>')
def servir_audio(filename):
    try:
        return send_from_directory(AUDIO_FOLDER, filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "Audio no encontrado. ¿Oso se lo comió? 🐻🍯"}), 404

# --- Health Check para Render ---
@app.route('/ping')
def ping():
    return jsonify({"status": "pong", "oso": "feliz"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Render usa puerto 10000 por defecto
