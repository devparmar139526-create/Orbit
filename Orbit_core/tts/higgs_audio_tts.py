"""
HiggsAudio TTS - High-quality neural text-to-speech
Uses Microsoft Edge TTS (edge-tts) for natural, human-like voice synthesis
Compatible with Python 3.7+ including Python 3.13
"""

import os
import sys
import asyncio
import threading
import tempfile
from typing import Optional, List
from pathlib import Path


class HiggsAudioTTS:
    """High-quality TTS using Microsoft Edge neural voices"""
    
    def __init__(self, settings=None, voice: str = None, language: str = None):
        self.settings = settings
        self.edge_tts = None
        self.tts_thread = None
        self.is_speaking = False
        self.first_speech = True  # Track first speech call for sync
        self.stop_requested = False  # Flag for interrupting TTS
        
        # Try to import edge-tts
        try:
            import edge_tts
            self.edge_tts = edge_tts
        except ImportError:
            print("[WARNING] edge-tts not installed. Install with: pip install edge-tts")
            # Fallback to pyttsx3
            try:
                from Orbit_core.tts.pyttsx_tts import PyTTSEngine
                self.fallback_engine = PyTTSEngine()
                self.using_fallback = True
                print("[OK] Using pyttsx3 as fallback")
            except Exception as e:
                print(f"[ERROR] Failed to initialize fallback TTS: {e}")
                self.using_fallback = False
            return
        
        self.using_fallback = False
        
        # Configuration
        if settings:
            self.voice = getattr(settings, 'HIGGS_TTS_VOICE', 'en-US-AriaNeural')
            self.language = getattr(settings, 'HIGGS_TTS_LANGUAGE', 'en-US')
            self.rate = getattr(settings, 'HIGGS_TTS_RATE', '+0%')
            self.volume = getattr(settings, 'HIGGS_TTS_VOLUME', '+0%')
            self.pitch = getattr(settings, 'HIGGS_TTS_PITCH', '+0Hz')
        else:
            self.voice = voice or 'en-US-AriaNeural'
            self.language = language or 'en-US'
            self.rate = '+0%'
            self.volume = '+0%'
            self.pitch = '+0Hz'
        
        print(f"[OK] HiggsAudio TTS initialized with voice: {self.voice}")
    
    def _get_event_loop(self):
        """Get or create an event loop for async operations"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def speak(self, text: str, wait: bool = True):
        """Speak text using Microsoft Edge TTS.
        
        Args:
            text: Text to speak
            wait: If True (default), wait until speaking is done before returning.
                  If False, speak in background and return immediately.
        """
        if self.using_fallback:
            self.fallback_engine.speak(text, wait=wait)
            return
        
        if not self.edge_tts:
            print("[WARNING] HiggsAudio TTS not available")
            return
        
        # Reset stop flag for new speech
        self.stop_requested = False
        
        # Fix for first speech - run synchronously to avoid threading issues  
        if self.first_speech:
            print("🔊 First HiggsAudio speech - running synchronously...")
            try:
                loop = self._get_event_loop()
                loop.run_until_complete(self._do_speak(text))
                self.first_speech = False
                print("✅ First HiggsAudio speech completed")
                return
            except Exception as e:
                print(f"⚠️  First HiggsAudio speech failed: {e}")
                self.first_speech = False
                # Fall through to threaded version
        
        self.tts_thread = threading.Thread(target=self._speak_async, args=(text,))
        self.tts_thread.daemon = False  # Non-daemon to ensure completion
        self.tts_thread.start()
        
        # Wait for speech to complete if requested
        if wait:
            # Wait indefinitely for TTS to complete (no timeout)
            # User can interrupt with "stop" command or Ctrl+C
            self.tts_thread.join()
            self.is_speaking = False
    
    def _speak_async(self, text: str):
        """Internal async speak method"""
        loop = self._get_event_loop()
        loop.run_until_complete(self._do_speak(text))
    
    async def _do_speak(self, text: str):
        """Actual async TTS synthesis and playback"""
        try:
            self.is_speaking = True
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            communicate = self.edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch
            )
            
            await communicate.save(tmp_path)
            self._play_audio(tmp_path)
            
            try:
                os.unlink(tmp_path)
            except:
                pass
            
        except Exception as e:
            print(f"[ERROR] HiggsAudio TTS error: {e}")
        finally:
            self.is_speaking = False
    
    def _play_audio(self, audio_path: str):
        """Play audio file using system player"""
        import time
        try:
            if sys.platform == "win32":
                # Use pygame for reliable Windows audio playback
                try:
                    import pygame
                    # Try different audio drivers for better compatibility
                    try:
                        pygame.mixer.quit()  # Quit any existing mixer
                    except:
                        pass
                    
                    # Initialize with specific settings for better compatibility
                    try:
                        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                    except pygame.error:
                        # Fallback to default initialization
                        try:
                            pygame.mixer.init()
                        except pygame.error as e:
                            print(f"⚠️  pygame audio init failed: {e}, using fallback...")
                            raise ImportError("pygame audio not available")
                    
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    # Wait for playback to complete or stop request
                    while pygame.mixer.music.get_busy():
                        if self.stop_requested:
                            pygame.mixer.music.stop()
                            pygame.mixer.quit()
                            print("⏹️  Audio stopped by user")
                            return
                        time.sleep(0.1)
                    pygame.mixer.quit()
                    print("✅ Audio playback completed (pygame)")
                except ImportError:
                    # Fallback: Use Windows Media Player command line
                    import subprocess
                    print("⚠️  pygame not found, using Windows Media Player...")
                    # Use PowerShell to play audio synchronously
                    ps_cmd = f'(New-Object Media.SoundPlayer "{audio_path}").PlaySync()'
                    subprocess.run(['powershell', '-Command', ps_cmd], check=False, timeout=30)
                    print("✅ Audio playback completed (WMP)")
            elif sys.platform == "darwin":
                os.system(f'afplay "{audio_path}"')
            else:
                os.system(f'mpg123 "{audio_path}" || ffplay -nodisp -autoexit "{audio_path}"')
        except Exception as e:
            print(f"[WARNING] Audio playback error: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """Stop current speech immediately"""
        self.stop_requested = True
        self.is_speaking = False
        print("🛑 TTS stop requested")
    
    def save_to_file(self, text: str, filename: str):
        """Save speech to audio file"""
        if self.using_fallback:
            print("[WARNING] save_to_file not supported with fallback engine")
            return
        
        if not self.edge_tts:
            print("[WARNING] HiggsAudio TTS not available")
            return
        
        loop = self._get_event_loop()
        loop.run_until_complete(self._save_to_file_async(text, filename))
    
    async def _save_to_file_async(self, text: str, filename: str):
        """Async save to file"""
        try:
            communicate = self.edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch
            )
            
            await communicate.save(filename)
            print(f"[OK] Audio saved to: {filename}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save audio: {e}")
    
    def stop(self):
        """Stop any currently playing audio"""
        self.is_speaking = False
    
    def list_available_voices(self) -> List[str]:
        """Get list of all available Edge TTS voices"""
        if not self.edge_tts:
            return []
        
        loop = self._get_event_loop()
        return loop.run_until_complete(self._list_voices_async())
    
    async def _list_voices_async(self) -> List[str]:
        """Async voice list retrieval"""
        try:
            voices = await self.edge_tts.VoicesManager.create()
            voice_list = []
            for voice in voices.voices:
                voice_list.append(f"{voice['Name']} ({voice['Locale']}) - {voice['Gender']}")
            return voice_list
        except Exception as e:
            print(f"[ERROR] Failed to list voices: {e}")
            return []
    
    def get_voices_by_language(self, language: str = None) -> List[str]:
        """Get voices for a specific language"""
        if not language:
            language = self.language
        
        all_voices = self.list_available_voices()
        return [v for v in all_voices if language in v]


# Recommended voices by language
RECOMMENDED_VOICES = {
    'en-US': ['en-US-AriaNeural', 'en-US-GuyNeural', 'en-US-JennyNeural'],
    'en-GB': ['en-GB-SoniaNeural', 'en-GB-RyanNeural'],
    'es-ES': ['es-ES-ElviraNeural', 'es-ES-AlvaroNeural'],
    'fr-FR': ['fr-FR-DeniseNeural', 'fr-FR-HenriNeural'],
    'de-DE': ['de-DE-KatjaNeural', 'de-DE-ConradNeural'],
    'ja-JP': ['ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'],
    'zh-CN': ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural'],
}
