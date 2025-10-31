"""
Speech-to-Text using speech_recognition library
Supports multiple engines: Google, Sphinx (offline), etc.
"""

import speech_recognition as sr
from typing import Optional

class SpeechRecognizer:
    def __init__(self, settings=None, timeout: int = None, phrase_limit: int = None):
        self.recognizer = sr.Recognizer()
        self.settings = settings
        
        # Use settings if provided, otherwise use parameters or defaults
        if settings:
            self.timeout = settings.STT_TIMEOUT
            self.phrase_limit = settings.STT_PHRASE_LIMIT
            self.energy_threshold = settings.STT_ENERGY_THRESHOLD
            self.language = settings.STT_LANGUAGE
            self.engine = settings.STT_ENGINE
        else:
            self.timeout = timeout if timeout is not None else 10
            self.phrase_limit = phrase_limit if phrase_limit is not None else 15
            self.energy_threshold = 0
            self.language = "en-US"
            self.engine = "google"
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            self.mic_available = True
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            print("   Please check your microphone connection.")
            self.mic_available = False
            return
        
        # Adjust for ambient noise
        try:
            print("🎤 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                # Improve microphone settings for better recognition
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.dynamic_energy_adjustment_damping = 0.15
                self.recognizer.dynamic_energy_ratio = 1.5
                self.recognizer.pause_threshold = 0.8  # Shorter pause detection
                self.recognizer.non_speaking_duration = 0.5  # Faster detection
                
                if self.energy_threshold > 0:
                    self.recognizer.energy_threshold = self.energy_threshold
                    print(f"   Using manual energy threshold: {self.energy_threshold}")
                else:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                    print(f"   Auto-adjusted energy threshold: {self.recognizer.energy_threshold}")
            print("✅ Microphone ready (improved sensitivity)")
        except Exception as e:
            print(f"⚠️  Microphone calibration warning: {e}")
    
    def listen(self) -> Optional[str]:
        """Listen for speech and convert to text"""
        if not self.mic_available:
            print("❌ Microphone not available")
            return None
        
        try:
            with self.microphone as source:
                print("🎤 Listening... (speak now)")
                
                try:
                    # Listen with timeout
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.timeout,
                        phrase_time_limit=self.phrase_limit
                    )
                    print("🔄 Processing speech...")
                except sr.WaitTimeoutError:
                    print("⏱️  No speech detected (timeout)")
                    return None
            
            # Try recognition based on configured engine
            return self._recognize_audio(audio)
        
        except OSError as e:
            print(f"❌ Microphone error: {e}")
            print("   Possible causes:")
            print("   - Microphone disconnected")
            print("   - Permission denied")
            print("   - Microphone in use by another app")
            return None
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def _recognize_audio(self, audio) -> Optional[str]:
        """Recognize audio using configured engine with fallback"""
        # Try primary engine
        if self.engine == "google":
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"✅ Recognized (Google): '{text}'")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand audio (unclear speech)")
                return None
            except sr.RequestError as e:
                print(f"⚠️  Google Speech API error: {e}")
                print("   Trying offline recognition...")
                # Fallback to Sphinx
                return self._recognize_sphinx(audio)
        
        elif self.engine == "sphinx":
            return self._recognize_sphinx(audio)
        
        else:
            print(f"⚠️  Unknown STT engine: {self.engine}, using Google")
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"✅ Recognized: '{text}'")
                return text
            except:
                return None
    
    def _recognize_sphinx(self, audio) -> Optional[str]:
        """Recognize audio using offline Sphinx"""
        try:
            text = self.recognizer.recognize_sphinx(audio)
            print(f"✅ Recognized (offline): '{text}'")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio (offline)")
            return None
        except sr.RequestError:
            print("❌ Offline recognition not available")
            print("   Install with: pip install pocketsphinx")
            return None
    
    def listen_for_wake_word(self, wake_words=None) -> bool:
        """Listen for wake word activation with fuzzy matching
        
        Args:
            wake_words: Single wake word (str) or list of wake words (list)
        
        Returns:
            bool: True if any wake word detected
        """
        # Handle wake words parameter
        if wake_words is None and self.settings:
            wake_words = self.settings.WAKE_WORD
        elif wake_words is None:
            wake_words = "orbit"
        
        # Convert single wake word to list
        if isinstance(wake_words, str):
            wake_words = [wake_words]
        
        # Don't print multiple times - listen silently
        if not self.mic_available:
            return False
        
        try:
            with self.microphone as source:
                # Shorter timeout for wake word detection (5 seconds)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            # Try to recognize
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                text_lower = text.lower()
                
                print(f"   Heard: '{text}'")
                
                # Check for wake words with fuzzy matching
                for wake_word in wake_words:
                    wake_word_lower = wake_word.lower()
                    
                    # Exact match or contains wake word
                    if wake_word_lower in text_lower:
                        print(f"✅ Wake word '{wake_word}' detected!")
                        return True
                    
                    # Fuzzy match for common misrecognitions
                    if wake_word_lower == "orbit":
                        # Common misrecognitions of "orbit"
                        if any(word in text_lower for word in ["orbit", "or bit", "orbits", "or bet", "orb it"]):
                            print(f"✅ Wake word 'orbit' detected (fuzzy match)")
                            return True
                    elif wake_word_lower == "orb":
                        # Common misrecognitions of "orb"
                        if any(word in text_lower for word in ["orb", "orbs", "orbe", "herb"]):
                            print(f"✅ Wake word 'orb' detected (fuzzy match)")
                            return True
                
                # No wake word found
                print(f"   ⏭️  No wake word detected, waiting...")
                return False
                
            except sr.UnknownValueError:
                # Could not understand - just continue listening
                return False
            except sr.RequestError:
                # API error - try offline
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    text_lower = text.lower()
                    for wake_word in wake_words:
                        if wake_word.lower() in text_lower:
                            print(f"✅ Wake word '{wake_word}' detected (offline)!")
                            return True
                except:
                    pass
                return False
        
        except sr.WaitTimeoutError:
            # Timeout - just continue
            return False
        except Exception as e:
            # Any other error - continue
            return False
    
    def continuous_listen_for_wake_word(self, wake_word: str = None, callback=None):
        """Continuously listen for wake word in background"""
        if wake_word is None and self.settings:
            wake_word = self.settings.WAKE_WORD
        elif wake_word is None:
            wake_word = "orbit"
        
        print(f"👂 Continuous listening for wake word: '{wake_word}'...")
        print("   Press Ctrl+C to stop")
        
        while True:
            try:
                if self.listen_for_wake_word(wake_word):
                    if callback:
                        callback()
                    else:
                        print(f"🎯 Wake word '{wake_word}' detected!")
                        return True
            except KeyboardInterrupt:
                print("\n⏹️  Stopping wake word detection")
                break
            except Exception as e:
                print(f"⚠️  Error in wake word detection: {e}")
                continue
        
        return False
    
    def test_microphone(self) -> bool:
        """Test microphone setup"""
        print("\n" + "="*50)
        print("🎤 MICROPHONE TEST")
        print("="*50)
        
        if not self.mic_available:
            print("❌ Microphone not initialized")
            return False
        
        # List available microphones
        print("\n📋 Available microphones:")
        try:
            mics = sr.Microphone.list_microphone_names()
            for i, mic_name in enumerate(mics):
                marker = " ← (default)" if i == sr.Microphone().device_index else ""
                print(f"   {i}: {mic_name}{marker}")
        except Exception as e:
            print(f"   Error listing microphones: {e}")
        
        print("\n🎤 Speak something now (you have 5 seconds)...")
        print("   Try saying: 'Hello orbit, can you hear me?'")
        
        # Short test
        old_timeout = self.timeout
        self.timeout = 5
        
        text = self.listen()
        
        self.timeout = old_timeout
        
        if text:
            print(f"\n✅ SUCCESS! Heard: '{text}'")
            print("   Your microphone is working correctly!")
            return True
        else:
            print("\n❌ FAILED: Could not detect speech")
            print("\n🔧 Troubleshooting tips:")
            print("   1. Check microphone is plugged in")
            print("   2. Check system sound settings")
            print("   3. Try speaking louder")
            print("   4. Check microphone permissions")
            print("   5. Close other apps using microphone")
            return False
    
    def adjust_sensitivity(self, energy_threshold: int = None):
        """Adjust microphone sensitivity"""
        if energy_threshold:
            self.recognizer.energy_threshold = energy_threshold
            print(f"🔧 Energy threshold set to: {energy_threshold}")
        else:
            print("🔧 Auto-adjusting sensitivity...")
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"✅ New energy threshold: {self.recognizer.energy_threshold}")
            except Exception as e:
                print(f"❌ Adjustment failed: {e}")