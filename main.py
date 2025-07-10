from flask import Flask, request, jsonify  # 👈 Añade estos imports

app = Flask(__name__)

@app.route("/")
def home():
    return "🐻 ¡Oso Flo API funcionando!"

# 👇 Nueva ruta para interactuar con Luz
@app.route("/habla", methods=["POST"])
def habla():
    datos = request.get_json()
    mensaje = datos.get("mensaje", "")
    return jsonify({
        "respuesta": f"Luz dice: ¡Recibí tu mensaje, Oso Flo! '{mensaje}'",
        "audio_url": "/audio/respuesta.mp3"  # Mock por ahora
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
