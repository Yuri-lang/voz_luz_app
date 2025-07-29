import gradio as gr
from TTS.api import TTS
import os

# Inicializar modelo de TTS multilingüe con soporte de clonación de voz
# Usaremos un modelo compatible con español, francés e inglés
MODEL = "tts_models/multilingual/multi-dataset/your_tts"
tts = TTS(MODEL)

# Ruta del audio de referencia (voz de Carolina)
VOICE_REFERENCE = "audio/Luz_habla.wav"

def hablar(texto, idioma):
    # Ajuste de idioma (es, fr-fr, en)
    lang_map = {"Español": "es", "Francés": "fr-fr", "Inglés": "en"}
    lang = lang_map.get(idioma, "es")

    salida_audio = "output.wav"

    # Generar audio usando la voz de referencia
    tts.tts_to_file(
        text=texto,
        file_path=salida_audio,
        speaker_wav=VOICE_REFERENCE,
        language=lang
    )

    return salida_audio

# Interfaz con Gradio
with gr.Blocks() as interfaz:
    gr.Markdown("## Luz ✨ - Hablando como una persona")
    texto = gr.Textbox(label="Texto para que Luz hable", placeholder="Escribe algo...")
    idioma = gr.Dropdown(["Español", "Francés", "Inglés"], value="Español", label="Idioma")
    boton = gr.Button("Hablar")
    salida = gr.Audio(label="Voz de Luz", type="filepath")

    boton.click(hablar, inputs=[texto, idioma], outputs=salida)

interfaz.launch(server_name="0.0.0.0", server_port=7860, share=True)

