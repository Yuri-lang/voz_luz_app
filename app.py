import gradio as gr
from TTS.api import TTS
import os

# Inicializamos modelo multilingüe (XTTS v2)
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=True)

# Ruta a la muestra de voz de Luz
SPEAKER_WAV = "audio/Luz_habla.wav"

# Función para generar voz
def hablar(texto, idioma):
    audio_path = "voz_luz.wav"
    tts.tts_to_file(
        text=texto,
        file_path=audio_path,
        speaker_wav=SPEAKER_WAV,
        language=idioma  # soporta es, en, fr, de, pt, it, nl, pl, ru, zh
    )
    return audio_path

# Interfaz de Gradio
with gr.Blocks() as demo:
    gr.Markdown("## Luz App - Voz Multilingüe ✨")

    texto = gr.Textbox(label="Texto a decir")
    idioma = gr.Dropdown(
        ["es", "en", "fr", "de", "pt", "it", "nl", "pl", "ru", "zh"],
        value="es",
        label="Idioma"
    )
    salida_audio = gr.Audio(label="Voz generada", type="filepath")
    boton = gr.Button("Hablar")

    boton.click(hablar, inputs=[texto, idioma], outputs=salida_audio)

demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
