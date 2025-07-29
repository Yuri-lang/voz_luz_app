import os
import gradio as gr
from TTS.api import TTS
import subprocess
import uuid

# --- CONFIGURACIÓN DE VOZ ---
# Modelo de TTS multilingüe de Coqui
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=True)

# Ruta donde se guardarán audios y videos temporales
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- FUNCIÓN PARA GENERAR VIDEO ---
def generar_video(texto):
    audio_id = str(uuid.uuid4())  # ID único para evitar conflictos
    audio_path = os.path.join(OUTPUT_DIR, f"{audio_id}.wav")
    video_path = os.path.join(OUTPUT_DIR, f"{audio_id}.mp4")

    # 1. Generar voz de Luz
    tts.tts_to_file(text=texto, file_path=audio_path)

    # 2. Generar video animado con SadTalker (Luz moviendo la boca)
    # Usa la imagen de Luz que tienes en assets
    source_image = "assets/luz.png"  # Asegúrate de que existe
    cmd = [
        "python", "inference.py",
        "--driven_audio", audio_path,
        "--source_image", source_image,
        "--result_dir", OUTPUT_DIR,
        "--still",  # Imagen fija (solo animar la boca)
        "--enhancer", "gfpgan"  # Para mejorar calidad
    ]

    subprocess.run(cmd, check=True)

    # Buscar el video generado (SadTalker crea un archivo dentro de outputs)
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".mp4") and audio_id in file:
            video_path = os.path.join(OUTPUT_DIR, file)
            break

    return video_path

# --- INTERFAZ WEB CON GRADIO ---
if __name__ == "__main__":
    interfaz = gr.Interface(
        fn=generar_video,
        inputs="text",
        outputs="video",
        title="Luz App - Voz y Boca Animada",
        description="Escribe algo y Luz lo dirá moviendo la boca ❤️"
    )
    interfaz.launch(share=True)  # Genera link público accesible
