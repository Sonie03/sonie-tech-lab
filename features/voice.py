import pyttsx3
import threading
from core.config import config

class VoiceAssistant:
    def __init__(self):
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            # Set rate and volume
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', config.get("voice_volume", 0.8))
        except Exception as e:
            print(f"Failed to initialize voice engine: {e}")
            self.engine = None

    def speak(self, text):
        if not config.get("voice_enabled", True) or not self.engine:
            return
            
        def run_speech():
            try:
                # We need to initialize or use a thread-safe call
                local_engine = pyttsx3.init()
                local_engine.setProperty('rate', 150)
                local_engine.setProperty('volume', config.get("voice_volume", 0.8))
                local_engine.say(text)
                local_engine.runAndWait()
            except Exception as e:
                print(f"Speech thread error: {e}")
                
        threading.Thread(target=run_speech, daemon=True).start()

voice = VoiceAssistant()
