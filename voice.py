import speech_recognition as sr
import edge_tts
import pygame
import asyncio
import io

VOZ_MASCULINA = "pt-BR-AntonioNeural"
VOLUME_JARVIS = "-20%"

class JarvisVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()

    def interromper_fala(self):
        """Fix do AttributeError: Garante que a hotkey funcione."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    async def falar(self, texto):
        texto_pronuncia = texto.replace("Jarvis", "Járvis").replace("jarvis", "járvis")
        print(f"JARVIS: {texto}")

        try:
            communicate = edge_tts.Communicate(texto_pronuncia, VOZ_MASCULINA, volume=VOLUME_JARVIS)
            data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    data += chunk["data"]
            
            audio_buffer = io.BytesIO(data)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"Erro neural de voz: {e}")

    def escutar_passivo(self):
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=2)
                texto = self.recognizer.recognize_google(audio, language='pt-BR').lower()
                return any(x in texto for x in ["jarvis", "sir", "sistema"])
            except: return False

    def escutar_comando(self):
        with sr.Microphone() as source:
            print("\n[JARVIS: Às ordens, Senhor...]")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                return self.recognizer.recognize_google(audio, language='pt-BR')
            except: return None