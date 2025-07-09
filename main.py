from flask import Flask

# 👇 La variable DEBE llamarse 'app' para Gunicorn
app = Flask(__name__)  # ¡Esta línea es crucial!

@app.route("/")
def home():
    return "🐻 ¡Oso Flo API funcionando!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
