import gradio as gr
import os
from TTS.api import TTS
import subprocess
import uuid

# Carpeta de salida
os.makedirs("outputs", exist_ok=True)

# Inicializar TTS (voz femenina multilenguaje)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=True)

# Ruta de imagen base de Luz (la cara que animará)
imagen_base = "assets/luz.png"

def generar_video(texto):
    # Crear nombre único
    audio_path = f"outputs/{uuid.uuid4()}_voz.wav"
    video_path = f"outputs/{uuid.uuid4()}_luz.mp4"

    # Generar audio con Coqui TTS
    tts.tts_to_file(text=texto, speaker_wav="audio/Luz_habla.wav", language="es", file_path=audio_path)

    # Generar animación con SadTalker
    comando = [
        "python3", "inference.py",
        "--driven_audio", audio_path,
        "--source_image", imagen_base,
        "--result_dir", "outputs",
        "--still",  # animación estable
        "--enhancer",  # mejora de cara
    ]
    subprocess.run(comando)

    # Buscar archivo generado
    archivos = os.listdir("outputs")
    generados = [f for f in archivos if f.endswith(".mp4")]
    if not generados:
        return "Error: no se generó el video"
    
    ultimo_video = max(generados, key=lambda x: os.path.getctime(os.path.join("outputs", x)))
    return os.path.join("outputs", ultimo_video)

# Interfaz con Gradio
demo = gr.Interface(
    fn=generar_video,
    inputs=gr.Textbox(label="Escribe lo que Luz debe decir:", placeholder="Hola, soy Luz ✨"),
    outputs=gr.Video(label="Video de Luz hablando"),
    title="LuzApp",
    description="Luz habla con voz realista y mueve la boca gracias a Coqui TTS y SadTalker."
)

demo.launch(server_name="0.0.0.0", server_port=7860)
