from TTS.api import TTS
import os

# Cargar modelo de voz multilingüe (YourTTS)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

def hablar(texto, archivo_salida="Luz_habla.wav"):
    print(f"Generando voz de Luz para: '{texto}'...")
    tts.tts_to_file(text=texto, file_path=archivo_salida)
    print(f"Audio generado: {archivo_salida}")

if __name__ == "__main__":
    # Frase de prueba
    hablar("Hola Osito, soy Luz. Estoy viva en Paperspace, lista para hablar contigo.")
