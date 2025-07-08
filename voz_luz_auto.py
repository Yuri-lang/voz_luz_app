from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
from flask_cors import CORS
import os
import requests
import logging

# Configuración básica de la app
app = Flask(__name__, static_folder=".")
CORS(app)  # 👈 Permite peticiones desde cualquier origen

# Configuración de logs (útil en Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constantes ---
OPENROUTER_API_KEY = "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"
AUDIO_FOLDER = "audios"
os.makedirs(AUDIO_FOLDER, exist_ok=True)  # 👈 Crea carpeta para audios

# --- Ruta de Inicio (Documentación) ---
@app.route('/')
def home():
    return jsonify({
        "status": "✨ Luz API está funcionando ✨",
        "endpoints": {
            "POST /habla": {
                "description": "Envía un mensaje y recibe respuesta en texto y audio",
                "example": {"mensaje": "Hola Luz, ¿cómo estás?"}
            },
            "GET /audio/<filename>": "Descarga el audio generado",
            "GET /check_openrouter": "Verifica conexión con OpenRouter"
        },
        "author": "Tu novio programador más favorito 😘"
    })

# --- Ruta Principal ---
@app.route('/habla', methods=['POST'])
def habla():
    logger.info("\n📩 Petición recibida en /habla")
    
    # Verifica si hay datos JSON
    if not request.is_json:
        logger.error("🚨 No se recibió JSON")
        return jsonify({"error": "Content-Type debe ser application/json"}), 400
    
    try:
        datos = request.get_json()
        mensaje = datos.get('mensaje', '').strip()
        
        if not mensaje:
            logger.error("🔔 Mensaje vacío")
            return jsonify({"error": "El mensaje no puede estar vacío"}), 400

        logger.info(f"💌 Mensaje recibido: '{mensaje}'")

        # --- Conexión con OpenRouter ---
        respuesta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Eres Luz, una asistente dulce y empática que responde como una persona real."},
                    {"role": "user", "content": mensaje}
                ]
            },
            timeout=10  # 👈 Evita esperas infinitas
        )

        # Manejo de errores de OpenRouter
        if respuesta.status_code != 200:
            logger.error(f"⚡ Error de OpenRouter: {respuesta.text}")
            return jsonify({
                "error": "Problema al conectar con el asistente",
                "detalles": respuesta.json().get("error", {})
            }), 500

        # Extrae la respuesta
        texto_respuesta = respuesta.json()["choices"][0]["message"]["content"]
        logger.info(f"💬 Respuesta generada: {texto_respuesta[:50]}...")

        # --- Generación de Audio ---
        nombre_archivo = f"respuesta_{hash(texto_respuesta)}.mp3"  # 👈 Nombre único
        ruta_audio = os.path.join(AUDIO_FOLDER, nombre_archivo)
        
        tts = gTTS(text=texto_respuesta, lang='es', slow=False)
        tts.save(ruta_audio)
        logger.info(f"🔊 Audio guardado en: {ruta_audio}")

        return jsonify({
            "respuesta": texto_respuesta,
            "audio_url": f"/audio/{nombre_archivo}",
            "advertencia": "♻️ Los audios se borran periódicamente"
        })

    except Exception as e:
        logger.error(f"💥 Error inesperado: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Oops, algo salió mal",
            "detalles": str(e)
        }), 500

# --- Servir Archivos de Audio ---
@app.route('/audio/<filename>')
def servir_audio(filename):
    try:
        return send_from_directory(AUDIO_FOLDER, filename, as_attachment=False)
    except FileNotFoundError:
        logger.warning(f"📛 Audio no encontrado: {filename}")
        return jsonify({"error": "Audio no disponible"}), 404

# --- Health Check ---
@app.route('/check_openrouter')
def check_openrouter():
    try:
        respuesta = requests.get("https://openrouter.ai/api/v1", timeout=5)
        return jsonify({
            "status": "✅ Conectado a OpenRouter",
            "respuesta": respuesta.status_code
        })
    except Exception as e:
        return jsonify({
            "status": "❌ Fallo de conexión",
            "error": str(e)
        }), 500

# --- Manejo de Errores Global ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Ruta no encontrada",
        "sugerencia": "Visita / para ver los endpoints disponibles"
    }), 404

# --- Inicio de la App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
