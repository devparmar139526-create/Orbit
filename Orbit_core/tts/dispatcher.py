# Orbit_core/tts/dispatcher.py
"""
TTS Dispatcher - routes text to speech output
Supports multiple TTS engines: pyttsx3, HiggsAudio (Microsoft Edge TTS)
"""

from Orbit_core.tts.pyttsx_tts import PyTTSEngine

class TTSDispatcher:
    def __init__(self, settings=None, engine_type: str = "pyttsx3", rate: int = 175, volume: float = 0.9):
        """Initialize TTS Dispatcher
        
        Args:
            settings: Settings object with TTS configuration
            engine_type: "pyttsx3" (default/fast) or "higgs" (high-quality neural)
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.settings = settings
        self.engine = None
        self.enabled = True
        self.engine_type = engine_type
        
        # Determine engine type from settings if available
        if settings and hasattr(settings, 'TTS_ENGINE'):
            self.engine_type = settings.TTS_ENGINE
        
        # Initialize the selected engine
        try:
            if self.engine_type == "higgs":
                self._init_higgs_audio()
            else:
                self._init_pyttsx3()
        except Exception as e:
            print(f"[WARNING] TTS initialization failed: {e}")
            self.enabled = False
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 TTS engine (default, fast, offline)"""
        try:
            if self.settings:
                self.engine = PyTTSEngine(settings=self.settings)
            else:
                self.engine = PyTTSEngine(rate=175, volume=0.9)
            print("[OK] TTS Engine: pyttsx3 (fast, offline)")
        except Exception as e:
            print(f"[ERROR] pyttsx3 initialization failed: {e}")
            raise
    
    def _init_higgs_audio(self):
        """Initialize HiggsAudio/Edge TTS engine (high-quality neural)"""
        try:
            from Orbit_core.tts.higgs_audio_tts import HiggsAudioTTS
            
            if self.settings:
                self.engine = HiggsAudioTTS(settings=self.settings)
            else:
                self.engine = HiggsAudioTTS()
            print("[OK] TTS Engine: HiggsAudio (Microsoft Edge Neural TTS)")
        except ImportError:
            print("[WARNING] HiggsAudio TTS not available, falling back to pyttsx3")
            print("          Install with: pip install edge-tts")
            self._init_pyttsx3()
        except Exception as e:
            print(f"[ERROR] HiggsAudio initialization failed: {e}")
            print("        Falling back to pyttsx3...")
            self._init_pyttsx3()
    
    def speak(self, text: str, wait: bool = True):
        """Speak text using TTS if enabled.
        
        Args:
            text: Text to speak
            wait: If True (default), wait until speaking is done before returning.
                  If False, speak in background and return immediately.
        """
        if self.enabled and text and self.engine:
            self.engine.speak(text, wait=wait)
    
    def stop(self):
        """Stops any currently speaking audio."""
        if self.enabled and self.engine:
            self.engine.stop()

    def enable(self):
        """Enable TTS output"""
        self.enabled = True
    
    def disable(self):
        """Disable TTS output"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if TTS is enabled"""
        return self.enabled
    
    def switch_engine(self, engine_type: str):
        """Switch to a different TTS engine
        
        Args:
            engine_type: "pyttsx3" or "higgs"
        """
        self.engine_type = engine_type
        try:
            if engine_type == "higgs":
                self._init_higgs_audio()
            else:
                self._init_pyttsx3()
            print(f"[OK] Switched to {engine_type} TTS engine")
        except Exception as e:
            print(f"[ERROR] Failed to switch engine: {e}")
