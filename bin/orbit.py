#!/usr/bin/env python3
"""
Orbit - AI-Powered Home & Work Automation Assistant
This script runs the assistant in the command line (text or voice mode).
"""

import sys
import os
import argparse
import threading
import msvcrt  # Windows keyboard input
from collections.abc import Generator
from typing import Optional

# --- Add project root to path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# --- Import Orbit Components ---
from Orbit_core.config.settings import Settings
from Orbit_core.llm.router import LLMRouter
from Orbit_core.memory.sqlite_store import MemoryStore
from Orbit_core.intent.source_selector import SourceSelector
from Orbit_core.stt.deep import SpeechRecognizer
from Orbit_core.tts.dispatcher import TTSDispatcher

class Orbit:
    """The main class for the Orbit assistant."""
    def __init__(self, config_file: Optional[str] = None):
        print("🚀 Initializing Orbit...")
        self.settings = Settings(config_file)
        self.tts_stop_requested = False  # Flag for stop detection
        self.cancel_requested = False  # Shared flag for cancellation
        
        # Display configuration
        print(f"   Assistant: {self.settings.ASSISTANT_NAME}")
        print(f"   Wake Word: {self.settings.WAKE_WORD}")
        print(f"   AI Model: {self.settings.OPENAI_MODEL}")
        print(f"   STT Engine: {self.settings.STT_ENGINE}")
        print(f"   TTS Engine: {self.settings.TTS_ENGINE}")
        
        self.memory = MemoryStore(self.settings.DB_PATH)
        self.llm = LLMRouter(self.settings)
        self.source_selector = SourceSelector(self.llm, self.settings)
        
        self.stt = None
        self.tts = None
        
        # Initialize STT engine based on configuration
        self._init_stt()
        
        print("✅ Orbit is online and ready.")
    
    def _init_stt(self):
        """Initialize Speech-to-Text engine based on settings"""
        engine = self.settings.STT_ENGINE.lower()
        
        if engine == "whisper":
            print("🎤 Initializing Whisper STT...")
            try:
                model_size = getattr(self.settings, 'WHISPER_MODEL_SIZE', 'base')
                self.stt = WhisperSTT(self.settings, model_size=model_size)
                print(f"✅ Whisper STT initialized (model: {model_size})")
            except ImportError:
                print("❌ Whisper dependencies not installed!")
                print("   Run: pip install openai-whisper torch sounddevice")
                print("   Falling back to Google STT...")
                self.stt = SpeechRecognizer(self.settings)
            except Exception as e:
                print(f"❌ Whisper STT failed: {e}")
                print("   Falling back to Google STT...")
                self.stt = SpeechRecognizer(self.settings)
        else:
            # Use default Google/Sphinx STT
            self.stt = SpeechRecognizer(self.settings)
    
    def _check_for_cancel(self):
        """Check if user pressed ESC key to cancel (non-blocking, Windows)"""
        try:
            if msvcrt.kbhit():  # Check if key was pressed
                key = msvcrt.getch()
                # ESC key = 27 (0x1b), Ctrl+C = 3, or 'q' key as alternative
                if key == b'\x1b':  # ESC
                    return True
                elif key == b'\x03':  # Ctrl+C
                    return True
                elif key == b'q' or key == b'Q':  # Q key as fallback
                    return True
        except Exception as e:
            print(f"\n[Debug: Cancel check error: {e}]")
        return False
    
    def _listen_for_stop_command(self):
        """Background listener for 'stop' command during TTS"""
        if not self.stt or not self.stt.mic_available:
            return

        # Try to import speech_recognition; if unavailable, try to use self.stt's recognizer if provided.
        recognizer = None
        Microphone = None
        try:
            import speech_recognition as sr  # type: ignore
            recognizer = sr.Recognizer()
            Microphone = sr.Microphone
            recognizer.pause_threshold = 0.5
            recognizer.energy_threshold = 4000
        except Exception:
            # Gracefully fall back to internal recognizer if the wrapper provides one
            recognizer = getattr(self.stt, 'recognizer', None)
            Microphone = getattr(self.stt, 'Microphone', None)

            try:
                if recognizer:
                    recognizer.pause_threshold = getattr(recognizer, 'pause_threshold', 0.5)
                    recognizer.energy_threshold = getattr(recognizer, 'energy_threshold', 4000)
            except Exception:
                # If we cannot configure fallback recognizer, give up
                recognizer = None
                Microphone = None

        if recognizer is None or Microphone is None:
            # speech_recognition not available and no fallback recognizer -> skip stop-listening
            return

        try:
            with Microphone() as source:
                print("   (Listening for 'stop' command...)")
                try:
                    audio = recognizer.listen(source, timeout=0.5, phrase_time_limit=2)
                    try:
                        # Prefer recognizer's recognize_google if present
                        if hasattr(recognizer, 'recognize_google'):
                            text = recognizer.recognize_google(audio).lower()
                        else:
                            # If recognizer doesn't expose recognize_google, try a helper on self.stt
                            text = self.stt.transcribe_audio(audio).lower() if hasattr(self.stt, 'transcribe_audio') else ""
                    except Exception:
                        text = ""
                    if "stop" in text:
                        print("🛑 Stop command detected!")
                        self.tts_stop_requested = True
                        if self.tts:
                            self.tts.stop()
                except Exception:
                    pass  # Timeout or no speech - that's fine
        except Exception:
            pass  # Ignore errors in background listener
    
    def _speak_with_stop_detection(self, text: str):
        """Speak text while monitoring for 'stop' command"""
        self.tts_stop_requested = False
        
        # Start TTS in a thread
        tts_thread = threading.Thread(target=lambda: self.tts.speak(text))
        tts_thread.daemon = False
        tts_thread.start()
        
        # Monitor for stop command while TTS is playing
        while tts_thread.is_alive():
            if self.stt and self.stt.mic_available:
                self._listen_for_stop_command()
            if self.tts_stop_requested:
                break
            tts_thread.join(timeout=0.1)  # Check every 100ms
        
        # Wait for TTS to fully stop
        tts_thread.join()

    def run_text_mode(self):
        """Starts the conversation loop for text-based interaction."""
        # Initialize TTS for automatic speech
        if not self.tts:
            engine_type = getattr(self.settings, 'TTS_ENGINE', 'higgs')
            self.tts = TTSDispatcher(settings=self.settings, engine_type=engine_type)
        
        print("\n--- Orbit Text Mode ---")
        print("Type 'exit' or 'goodbye' to end the session.")
        print("💡 Press ESC during LLM processing to cancel!")
        print("🔊 Automatic speech enabled - all responses will be spoken")
        
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "goodbye"]:
                    print("Orbit: Goodbye!")
                    if self.settings.ENABLE_AUDIO_FEEDBACK:
                        self.tts.speak("Goodbye!")
                    break

                context = self.memory.get_recent_context(limit=self.settings.MAX_CONTEXT_MESSAGES)
                response_generator = self.source_selector.process(user_input, context)
                
                print("Orbit: (Press ESC to cancel) ", end='', flush=True)
                full_response = []
                cancelled = False
                
                try:
                    if isinstance(response_generator, Generator):
                        for chunk in response_generator:
                            # Check for ESC key
                            if self._check_for_cancel():
                                print("\n⏹️  Cancelled!")
                                cancelled = True
                                break
                            print(chunk, end='', flush=True)
                            full_response.append(chunk)
                    else:
                        print(response_generator, end='')
                        full_response.append(str(response_generator))

                    if not cancelled:
                        print() # Newline after the full response
                        
                        final_response_text = "".join(full_response)
                        
                        # Automatically speak the response
                        if final_response_text.strip():
                            print("🔊 Speaking response...")
                            try:
                                self.tts.speak(final_response_text)
                            except Exception as tts_error:
                                print(f"⚠️  TTS error: {tts_error}")
                        
                        self.memory.add_message("user", user_input)
                        self.memory.add_message("assistant", final_response_text)
                
                except KeyboardInterrupt:
                    print("\n⏹️  Cancelled! You can type a new query.")
                    continue

            except KeyboardInterrupt:
                print("\nOrbit: Goodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    def run_voice_mode(self):
        """Starts the conversation loop for voice-based interaction."""
        if not self.stt: 
            self.stt = SpeechRecognizer(self.settings)
        if not self.tts:
            # Use TTSDispatcher which supports both pyttsx3 and HiggsAudio (Edge TTS)
            engine_type = getattr(self.settings, 'TTS_ENGINE', 'pyttsx3')
            self.tts = TTSDispatcher(settings=self.settings, engine_type=engine_type)

        if not self.stt.mic_available:
            print("\n❌ Microphone not found. Cannot start voice mode.")
            return

        print(f"\n--- {self.settings.ASSISTANT_NAME} Voice Mode ---")
        print("🎤 Orbit will SPEAK all responses automatically (like Alexa)")
        print("💡 Wake words: 'orbit' or 'orb'")
        print("📌 Say wake word, then your command")
        self.tts.speak(f"{self.settings.ASSISTANT_NAME} voice mode activated. Say orbit or orb to begin.")

        # Define wake words and fuzzy variants
        wake_words = ["orbit", "orb", "or bit", "orbet", "orbits", "or bet", "orbe", "orbeet", "orbut", "orbid", "orvit", "orvit"]

        while True:
            try:
                print(f"\n👂 Say your command starting with wake word (e.g. 'orbit open notepad')...")
                # Listen for speech
                user_input = self.stt.listen()
                if not user_input:
                    continue
                text_lower = user_input.lower().strip()
                # Check if input starts with a wake word (fuzzy match)
                matched = None
                for wake_word in wake_words:
                    if text_lower.startswith(wake_word):
                        matched = wake_word
                        break
                if not matched:
                    print("⏭️  No wake word detected at start, ignoring input.")
                    continue
                # Remove wake word from start
                command = text_lower[len(matched):].strip(' .,:;!?')

                # Generate the response text before starting TTS
                context = self.memory.get_recent_context(limit=self.settings.MAX_CONTEXT_MESSAGES)
                response_generator = self.source_selector.process(command, context)

                # Collect response chunks into full_response
                full_response = []
                try:
                    if isinstance(response_generator, Generator):
                        for chunk in response_generator:
                            print(chunk, end='', flush=True)
                            full_response.append(chunk)
                    else:
                        print(response_generator, end='', flush=True)
                        full_response.append(str(response_generator))
                except Exception as e:
                    print(f"\n❌ Error while generating response: {e}")
                print()

                final_response_text = "".join(full_response)
                # ALWAYS speak the response in voice mode (like Alexa)
                print("🔊 Speaking response...")
                print(f"   Response length: {len(final_response_text)}")
                print(f"   First 50 chars: '{final_response_text[:50]}{'...' if len(final_response_text) > 50 else ''}'")
                try:
                    print("🔊 Calling TTS.speak()...")
                    print("💡 Say 'stop' to interrupt")
                    import threading
                    tts_thread = threading.Thread(target=lambda: self.tts.speak(final_response_text))
                    tts_thread.daemon = True
                    tts_thread.start()
                    interrupted = False
                    while tts_thread.is_alive():
                        import speech_recognition as sr
                        try:
                            with sr.Microphone() as source:
                                audio = self.stt.recognizer.listen(source, timeout=0.5, phrase_time_limit=1)
                                try:
                                    interrupt_text = self.stt.recognizer.recognize_google(audio, language=self.stt.language)
                                    if "stop" in interrupt_text.lower():
                                        print("\n⏹️  Stop command detected - interrupting TTS")
                                        self.tts.stop()
                                        interrupted = True
                                        break
                                except:
                                    pass
                        except sr.WaitTimeoutError:
                            pass
                    tts_thread.join(timeout=1.0)
                    if interrupted:
                        print("✅ TTS interrupted - ready for next command")
                    else:
                        print("✅ TTS call completed successfully")
                except Exception as tts_error:
                    print(f"❌ TTS error: {tts_error}")
                    import traceback
                    traceback.print_exc()
                    print("⚠️  Continuing without TTS...")
                self.memory.add_message("user", command)
                self.memory.add_message("assistant", final_response_text)
            except KeyboardInterrupt:
                print(f"\n{self.settings.ASSISTANT_NAME}: Shutting down.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
    
    def run_hybrid_mode(self):
        """Run with option to choose between voice or text input"""
        if not self.stt:
            self.stt = SpeechRecognizer(self.settings)
        if not self.tts:
            # Use TTSDispatcher which supports both pyttsx3 and HiggsAudio (Edge TTS)
            engine_type = getattr(self.settings, 'TTS_ENGINE', 'pyttsx3')
            self.tts = TTSDispatcher(settings=self.settings, engine_type=engine_type)
        
        mic_available = self.stt.mic_available if self.stt else False
        
        print(f"\n--- {self.settings.ASSISTANT_NAME} Hybrid Mode ---")
        print("✅ Speech-to-Text (STT): " + ("Available" if mic_available else "Not Available"))
        print("✅ Text-to-Speech (TTS): Enabled")
        print("🔊 Automatic speech enabled - all responses will be spoken")
        print("\n📝 Mode Switching Commands:")
        print("   • Type or say 'voice' / 'switch to voice' - Use voice input")
        print("   • Type or say 'text' / 'switch to text' - Use text input")
        print("   • Type or say 'exit' / 'goodbye' - Quit")
        print("\n💡 IMPORTANT: Press Ctrl+C to instantly cancel slow LLM responses!")
        print()
        
        input_mode = "text"  # Default mode
        
        while True:
            try:
                # Show current mode indicator
                if input_mode == "voice":
                    print("🎤 [VOICE MODE] Listening...")
                    user_input = self.stt.listen() if mic_available else None
                    if not user_input:
                        print("Did not hear anything. Type 'text' to switch to text mode.")
                        continue
                    print(f"You said: {user_input}")
                else:
                    mode_indicator = "⌨️  [TEXT MODE]" if not mic_available else "⌨️  [TEXT MODE - type 'voice' to speak]"
                    user_input = input(f"{mode_indicator} You: ")
                
                # Check for mode switching (works in both voice and text)
                user_input_clean = user_input.lower().strip()
                
                if user_input_clean in ["voice", "switch to voice", "use voice"]:
                    if mic_available:
                        input_mode = "voice"
                        print("✅ Switched to VOICE mode")
                        if self.settings.ENABLE_AUDIO_FEEDBACK:
                            self.tts.speak("Voice mode activated")
                    else:
                        print("❌ Microphone not available. Staying in text mode.")
                    continue
                elif user_input_clean in ["text", "switch to text", "use text", "type"]:
                    input_mode = "text"
                    print("✅ Switched to TEXT mode")
                    if self.settings.ENABLE_AUDIO_FEEDBACK:
                        self.tts.speak("Text mode activated")
                    continue
                
                # Check for exit
                if user_input.lower() in ["exit", "goodbye", "quit"]:
                    print(f"{self.settings.ASSISTANT_NAME}: Goodbye!")
                    if self.settings.ENABLE_AUDIO_FEEDBACK:
                        self.tts.speak("Goodbye!")
                    break
                
                # Process the input
                context = self.memory.get_recent_context(limit=self.settings.MAX_CONTEXT_MESSAGES)
                
                # Simple approach: just use try/except for KeyboardInterrupt
                print(f"💡 Press Ctrl+C to cancel instantly")
                
                try:
                    response_generator = self.source_selector.process(user_input, context)
                    
                    print(f"{self.settings.ASSISTANT_NAME}: ", end='', flush=True)
                    full_response = []
                    
                    if isinstance(response_generator, Generator):
                        for chunk in response_generator:
                            print(chunk, end='', flush=True)
                            full_response.append(chunk)
                    else:
                        print(response_generator, end='')
                        full_response.append(str(response_generator))
                    
                    print()  # Newline
                    
                    # Save to memory
                    if full_response:
                        final_response_text = "".join(full_response)
                        
                        # Automatically speak ALL responses (both voice and text mode)
                        if final_response_text.strip():
                            print("🔊 Speaking response...")
                            try:
                                if input_mode == "voice":
                                    # Voice mode: use stop detection
                                    self._speak_with_stop_detection(final_response_text)
                                    if self.tts_stop_requested:
                                        print("⏹️  Speech interrupted by user")
                                    else:
                                        print("✅ Speech completed")
                                else:
                                    # Text mode: simple speech
                                    self.tts.speak(final_response_text)
                            except Exception as tts_error:
                                print(f"⚠️  TTS error: {tts_error}")
                        
                        # Save to memory
                        self.memory.add_message("user", user_input)
                        self.memory.add_message("assistant", final_response_text)
                
                except KeyboardInterrupt:
                    print("\n⏹️  Cancelled instantly! Type your new query.")
                    continue
                
            except KeyboardInterrupt:
                print(f"\n{self.settings.ASSISTANT_NAME}: Shutting down.")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
    
    def run_wake_word_mode(self):
        """Run voice mode with wake word detection"""
        if not self.stt:
            self.stt = SpeechRecognizer(self.settings)
        if not self.tts:
            # Use TTSDispatcher which supports both pyttsx3 and HiggsAudio (Edge TTS)
            engine_type = getattr(self.settings, 'TTS_ENGINE', 'pytttsx3')
            self.tts = TTSDispatcher(settings=self.settings, engine_type=engine_type)
        
        if not self.stt.mic_available:
            print("\n❌ Microphone not found. Cannot start wake word mode.")
            return
        
        print(f"\n--- {self.settings.ASSISTANT_NAME} Wake Word Mode ---")
        print(f"Say '{self.settings.WAKE_WORD}' to activate")
        if self.settings.ENABLE_AUDIO_FEEDBACK:
            self.tts.speak(f"Wake word mode active. Say {self.settings.WAKE_WORD} to begin.")
        
        while True:
            try:
                # Listen for wake word
                if self.stt.listen_for_wake_word(self.settings.WAKE_WORD):
                    if self.settings.ENABLE_AUDIO_FEEDBACK:
                        self.tts.speak("Yes? How can I help?")
                    
                    # Now listen for the actual command
                    user_input = self.stt.listen()
                    
                    if user_input:
                        print(f"You said: {user_input}")
                        
                        if user_input.lower() in ["exit", "goodbye", "stop listening"]:
                            self.tts.speak("Goodbye!")
                            break
                        
                        context = self.memory.get_recent_context(limit=self.settings.MAX_CONTEXT_MESSAGES)
                        response_generator = self.source_selector.process(user_input, context)
                        
                        print(f"{self.settings.ASSISTANT_NAME} says: ", end='', flush=True)
                        full_response = []
                        
                        for chunk in response_generator:
                            print(chunk, end='', flush=True)
                            full_response.append(chunk)
                        print()
                        
                        final_response_text = "".join(full_response)
                        if self.settings.ENABLE_AUDIO_FEEDBACK:
                            self.tts.speak(final_response_text)
                        
                        self.memory.add_message("user", user_input)
                        self.memory.add_message("assistant", final_response_text)
                        
                        print(f"\n👂 Listening for wake word '{self.settings.WAKE_WORD}'...")
                    
            except KeyboardInterrupt:
                print(f"\n{self.settings.ASSISTANT_NAME}: Shutting down.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Orbit AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Modes:
  Default (Hybrid)  - Choose between voice or text input on the fly
  --voice          - Voice-only mode (requires microphone)
  --wake-word      - Wake word detection mode (say 'orbit' to activate)
  --text           - Text-only mode (no voice features)
  
Features:
  ✅ Speech-to-Text (Google + offline Sphinx fallback)
  ✅ Text-to-Speech (pyttsx3)
  ✅ Wake word detection
  ✅ Smart scheduling and reminders
  ✅ Desktop app control
  ✅ Weather, Wikipedia, and more
        """
    )
    parser.add_argument("--voice", action="store_true", help="Run Orbit in voice-only mode.")
    parser.add_argument("--text", action="store_true", help="Run Orbit in text-only mode.")
    parser.add_argument("--wake-word", action="store_true", help="Run Orbit with wake word detection.")
    parser.add_argument("--config", type=str, help="Path to configuration file.")
    parser.add_argument("--test-mic", action="store_true", help="Test microphone setup.")
    args = parser.parse_args()

    try:
        app = Orbit(config_file=args.config)
        
        if args.test_mic:
            # Test microphone
            stt = SpeechRecognizer(app.settings)
            stt.test_microphone()
        elif args.wake_word:
            app.run_wake_word_mode()
        elif args.voice:
            app.run_voice_mode()
        elif args.text:
            app.run_text_mode()
        else:
            # Default: Hybrid mode (best of both worlds!)
            app.run_hybrid_mode()
    finally:
        print(f"\n{app.settings.ASSISTANT_NAME if hasattr(app, 'settings') else 'Orbit'} session ended.")


if __name__ == "__main__":
    main()
