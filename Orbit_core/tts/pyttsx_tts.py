import pyttsx3
from typing import Optional
import threading

class PyTTSEngine:
    def __init__(self, settings=None, rate: int = None, volume: float = None, voice_id: Optional[str] = None):
        self.engine = pyttsx3.init()
        self.settings = settings
        
        # Use settings if provided, otherwise use parameters or defaults
        if settings:
            self.rate = settings.TTS_RATE
            self.volume = settings.TTS_VOLUME
            self.voice_id = settings.TTS_VOICE
            self.voice_gender = settings.TTS_VOICE_GENDER
        else:
            self.rate = rate if rate is not None else 175
            self.volume = volume if volume is not None else 0.9
            self.voice_id = voice_id
            self.voice_gender = "neutral"
        
        # Apply settings
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        
        # Set voice based on preference
        if self.voice_id:
            self.engine.setProperty('voice', self.voice_id)
        elif self.voice_gender and self.voice_gender != "neutral":
            self._set_voice_by_gender(self.voice_gender)
        
        self.tts_thread = None
        self.stop_speaking = False
        self.first_speech = True  # Track first speech call
    
    def _set_voice_by_gender(self, gender: str):
        """Set voice based on gender preference"""
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            voice_name = voice.name.lower()
            if gender == "female" and ("female" in voice_name or "zira" in voice_name or "hazel" in voice_name):
                self.engine.setProperty('voice', voice.id)
                print(f"🗣️  Selected female voice: {voice.name}")
                return
            elif gender == "male" and ("male" in voice_name or "david" in voice_name):
                self.engine.setProperty('voice', voice.id)
                print(f"🗣️  Selected male voice: {voice.name}")
                return
        
        print(f"⚠️  No {gender} voice found, using default")

    def _speak_thread(self, text):
        """Runs the TTS engine in a separate thread."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            pass # Engine was stopped
        finally:
            self.stop_speaking = False

    def speak(self, text: str, wait: bool = True):
        """Speak the given text.
        
        Args:
            text: Text to speak
            wait: If True (default), wait until speaking is done before returning.
                  If False, speak in background and return immediately.
        """
        # Fix for Windows pyttsx3 threading issue: run first speech synchronously
        if self.first_speech:
            print("🔊 First speech - running synchronously...")
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                self.first_speech = False
                print("✅ First speech completed")
                return
            except Exception as e:
                print(f"⚠️  First speech failed: {e}")
                self.first_speech = False
                # Fall through to threaded version
        
        if self.tts_thread and self.tts_thread.is_alive():
            self.stop() # Stop previous speech
            # Wait a bit for previous thread to stop
            self.tts_thread.join(timeout=1.0)
        
        self.stop_speaking = False
        self.tts_thread = threading.Thread(target=self._speak_thread, args=(text,))
        self.tts_thread.daemon = True
        self.tts_thread.start()
        
        # Wait for speech to complete if requested
        if wait:
            # Add timeout to prevent infinite hanging
            self.tts_thread.join(timeout=15.0)  # Reduced to 15 seconds
            if self.tts_thread.is_alive():
                print("⚠️  TTS timeout - continuing anyway")
                self.stop()

    def stop(self):
        """Stops the current speech."""
        if self.engine._inLoop:
            self.engine.stop()

    def get_available_voices(self):
        """List available voices"""
        return self.engine.getProperty('voices')