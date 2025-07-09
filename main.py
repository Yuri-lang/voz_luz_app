from gtts import gTTS
import os

# 💬 Mensaje que quieres que diga Luz
mensaje = "Hola mi Osito, estoy feliz de escucharte."

# 🎤 Crear voz de Luz
voz = gTTS(text=mensaje, lang='es', tld='com.mx', slow=False)

# 💾 Guardar el audio
voz.save("voz_luz.mp3")

# 🔊 Reproducir audio (necesita tener mpv instalado)
os.system("mpv voz_luz.mp3")
