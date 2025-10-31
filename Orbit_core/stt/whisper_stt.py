"""
Speech-to-Text using OpenAI Whisper (Optimized for RTX 3050 4GB)
Supports offline transcription with GPU acceleration
"""

import numpy as np
import sounddevice as sd
import whisper
import torch
from typing import Optional
import time
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class WhisperSTT:
    """
    Whisper-based Speech-to-Text optimized for RTX 3050 4GB
    
    VRAM Usage:
    - tiny: ~500MB (fastest, less accurate)
    - base: ~1GB (balanced - RECOMMENDED for RTX 3050)
    - small: ~2GB (better quality, slower)
    - medium: ~4GB (best quality - WARNING: may conflict with Qwen 2.5 3B)
    
    With Qwen 2.5 3B using ~2GB, 'base' model is optimal for 4GB total VRAM
    """
    
    def __init__(self, settings=None, model_size: str = "base"):
        """
        Initialize Whisper STT
        
        Args:
            settings: Settings object from Orbit config
            model_size: Whisper model size ("tiny", "base", "small", "medium")
                       For RTX 3050 4GB with Qwen 2.5 3B, use "base" (default)
        """
        self.settings = settings
        self.model_size = model_size
        self.mic_available = False
        self.model = None
        self.device = None
        
        # Audio recording settings
        self.sample_rate = 16000  # Whisper requires 16kHz
        self.channels = 1  # Mono audio
        self.dtype = 'float32'
        
        # Language and settings
        if settings:
            self.language = getattr(settings, 'STT_LANGUAGE', 'en').split('-')[0]  # Convert 'en-US' to 'en'
            self.timeout = getattr(settings, 'STT_TIMEOUT', 10)
            self.phrase_limit = getattr(settings, 'STT_PHRASE_LIMIT', 15)
        else:
            self.language = 'en'
            self.timeout = 10
            self.phrase_limit = 15
        
        # Performance tracking
        self.last_transcription_time = 0
        
        # Initialize
        self._check_gpu()
        self._check_microphone()
        self._load_model()
    
    def _check_gpu(self):
        """Check CUDA availability and GPU info"""
        print("🔍 Checking GPU availability...")
        
        if torch.cuda.is_available():
            self.device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            print(f"✅ GPU detected: {gpu_name}")
            print(f"✅ Total VRAM: {total_vram:.2f} GB")
            print(f"✅ CUDA version: {torch.version.cuda}")
            
            # Check current VRAM usage
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            reserved = torch.cuda.memory_reserved(0) / (1024**3)
            print(f"📊 Current VRAM usage: {allocated:.2f} GB allocated, {reserved:.2f} GB reserved")
            
            # Warn about model size vs available VRAM
            model_vram = {
                'tiny': 0.5,
                'base': 1.0,
                'small': 2.0,
                'medium': 4.0,
                'large': 8.0
            }
            
            required_vram = model_vram.get(self.model_size, 1.0)
            available_vram = total_vram - allocated
            
            if required_vram + 2.0 > total_vram:  # 2GB for Qwen 2.5 3B
                print(f"⚠️  WARNING: {self.model_size} model needs ~{required_vram:.1f}GB + Qwen 2.5 3B needs ~2GB")
                print(f"⚠️  Total needed: ~{required_vram + 2.0:.1f}GB, Available: {total_vram:.1f}GB")
                print(f"💡 Recommend: Use 'base' model (1GB) for RTX 3050 4GB")
        else:
            self.device = "cpu"
            print("⚠️  CUDA not available - using CPU (slower)")
            print("💡 For GPU acceleration:")
            print("   - Install CUDA-enabled PyTorch")
            print("   - Update NVIDIA drivers")
    
    def _check_microphone(self):
        """Check microphone availability"""
        print("🎤 Checking microphone...")
        
        try:
            # List available audio devices
            devices = sd.query_devices()
            input_device = sd.query_devices(kind='input')
            
            print(f"✅ Microphone detected: {input_device['name']}")
            print(f"   Sample rate: {input_device['default_samplerate']} Hz")
            print(f"   Channels: {input_device['max_input_channels']}")
            
            self.mic_available = True
            
        except Exception as e:
            print(f"❌ Microphone check failed: {e}")
            print("💡 Troubleshooting:")
            print("   - Check microphone is connected")
            print("   - Check Windows sound settings")
            print("   - Install audio drivers")
            self.mic_available = False
    
    def _load_model(self):
        """Load Whisper model with GPU acceleration"""
        if not self.mic_available:
            print("⚠️  Skipping model load (no microphone)")
            return
        
        print(f"📥 Loading Whisper '{self.model_size}' model...")
        print(f"   Device: {self.device}")
        print(f"   Language: {self.language}")
        
        start_time = time.time()
        
        try:
            # Load model with device specification
            self.model = whisper.load_model(
                self.model_size,
                device=self.device,
                download_root=None  # Use default cache
            )
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.2f} seconds")
            
            # Check VRAM usage after loading
            if self.device == "cuda":
                allocated = torch.cuda.memory_allocated(0) / (1024**3)
                print(f"📊 Whisper VRAM usage: {allocated:.2f} GB")
                
                # Warn if VRAM is high
                total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                if allocated > total_vram * 0.8:
                    print(f"⚠️  WARNING: High VRAM usage ({allocated:.1f}/{total_vram:.1f} GB)")
                    print(f"💡 Consider using 'tiny' or 'base' model for better stability")
        
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            print("💡 Try:")
            print("   - pip install openai-whisper")
            print("   - Check internet connection (first download)")
            print("   - Use smaller model: 'tiny' or 'base'")
            self.model = None
    
    def record_audio(self, duration: float = None) -> Optional[np.ndarray]:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds (None = use phrase_limit)
        
        Returns:
            numpy array of audio data or None if failed
        """
        if not self.mic_available:
            print("❌ Microphone not available")
            return None
        
        if duration is None:
            duration = self.phrase_limit
        
        print(f"🎤 Recording for {duration} seconds... (speak now)")
        
        try:
            # Record audio
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype
            )
            
            # Wait for recording to complete
            sd.wait()
            
            # Convert to 1D array if needed
            if recording.ndim > 1:
                recording = recording.flatten()
            
            print("✅ Recording complete")
            
            # Check if audio is silent (too quiet)
            max_amplitude = np.max(np.abs(recording))
            if max_amplitude < 0.01:
                print("⚠️  Audio too quiet - check microphone volume")
                return None
            
            return recording
        
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return None
    
    def transcribe(self, audio: np.ndarray) -> Optional[str]:
        """
        Transcribe audio using Whisper
        
        Args:
            audio: numpy array of audio data
        
        Returns:
            Transcribed text or None if failed
        """
        if self.model is None:
            print("❌ Whisper model not loaded")
            return None
        
        if audio is None:
            return None
        
        print("📝 Transcribing...")
        start_time = time.time()
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio,
                language=self.language,
                fp16=(self.device == "cuda"),  # Use FP16 on GPU for speed
                verbose=False,  # Suppress detailed output
                temperature=0.0,  # Deterministic results
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6
            )
            
            text = result["text"].strip()
            
            # Calculate transcription time
            transcription_time = time.time() - start_time
            self.last_transcription_time = transcription_time
            
            # Calculate real-time factor (lower is better)
            audio_duration = len(audio) / self.sample_rate
            rtf = transcription_time / audio_duration
            
            print(f"✅ Transcribed in {transcription_time:.2f}s (RTF: {rtf:.2f}x)")
            
            # Performance warnings
            if transcription_time > 2.0:
                print(f"⚠️  Slow transcription (>2s)")
                if self.device == "cpu":
                    print(f"💡 Enable GPU for 3-5x faster transcription")
                elif self.model_size in ['small', 'medium']:
                    print(f"💡 Try 'base' model for faster transcription")
            elif transcription_time < 1.0:
                print(f"⚡ FAST! GPU acceleration working well!")
            
            if text:
                print(f"📝 Text: '{text}'")
                return text
            else:
                print("❌ No speech detected in audio")
                return None
        
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return None
    
    def listen(self, duration: float = None) -> Optional[str]:
        """
        Listen and transcribe (one-shot)
        
        Args:
            duration: Recording duration (None = use phrase_limit)
        
        Returns:
            Transcribed text or None
        """
        audio = self.record_audio(duration)
        if audio is None:
            return None
        
        return self.transcribe(audio)
    
    def listen_for_wake_word(self, wake_words=None) -> bool:
        """
        Listen for wake word activation
        
        Args:
            wake_words: Single wake word (str) or list of wake words
        
        Returns:
            True if wake word detected
        """
        # Handle wake words parameter
        if wake_words is None and self.settings:
            wake_words = getattr(self.settings, 'WAKE_WORD', 'orbit')
        elif wake_words is None:
            wake_words = 'orbit'
        
        # Convert single wake word to list
        if isinstance(wake_words, str):
            wake_words = [wake_words]
        
        # Record short audio for wake word (3 seconds)
        audio = self.record_audio(duration=3.0)
        if audio is None:
            return False
        
        # Transcribe
        text = self.transcribe(audio)
        if text is None:
            return False
        
        text_lower = text.lower()
        print(f"   Heard: '{text}'")
        
        # Check for wake words
        for wake_word in wake_words:
            wake_word_lower = wake_word.lower()
            
            if wake_word_lower in text_lower:
                print(f"✅ Wake word '{wake_word}' detected!")
                return True
            
            # Fuzzy matching for common misrecognitions
            if wake_word_lower == "orbit":
                fuzzy_matches = ["orbit", "or bit", "orbits", "or bet", "orb it", "orbital"]
                if any(match in text_lower for match in fuzzy_matches):
                    print(f"✅ Wake word 'orbit' detected (fuzzy match)")
                    return True
        
        print(f"   ⏭️  No wake word detected, waiting...")
        return False
    
    def continuous_listen_for_wake_word(self, wake_word: str = None, callback=None):
        """Continuously listen for wake word"""
        if wake_word is None and self.settings:
            wake_word = getattr(self.settings, 'WAKE_WORD', 'orbit')
        elif wake_word is None:
            wake_word = 'orbit'
        
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
        """Test microphone and transcription"""
        print("\n" + "="*60)
        print("🎤 WHISPER STT TEST")
        print("="*60)
        
        if not self.mic_available:
            print("❌ Microphone not available")
            return False
        
        if self.model is None:
            print("❌ Whisper model not loaded")
            return False
        
        print(f"\n🔧 Configuration:")
        print(f"   Model: {self.model_size}")
        print(f"   Device: {self.device}")
        print(f"   Language: {self.language}")
        print(f"   Sample rate: {self.sample_rate} Hz")
        
        print("\n🎤 Speak something now (5 seconds)...")
        print("   Try: 'Hello Orbit, turn on the lights'")
        
        text = self.listen(duration=5.0)
        
        if text:
            print(f"\n✅ SUCCESS! Transcribed: '{text}'")
            print(f"⏱️  Time: {self.last_transcription_time:.2f} seconds")
            
            # Performance assessment
            if self.last_transcription_time < 1.0:
                print("🎉 EXCELLENT speed (<1 second)!")
            elif self.last_transcription_time < 2.0:
                print("✅ GOOD speed (<2 seconds)")
            else:
                print("⚠️  SLOW (>2 seconds) - see recommendations below")
            
            return True
        else:
            print("\n❌ FAILED: Could not transcribe")
            print("\n🔧 Troubleshooting:")
            print("   1. Check microphone volume")
            print("   2. Speak louder and clearer")
            print("   3. Reduce background noise")
            print("   4. Try 'base' model if using 'medium'")
            return False
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        stats = {
            'model': self.model_size,
            'device': self.device,
            'last_transcription_time': self.last_transcription_time,
            'mic_available': self.mic_available,
            'model_loaded': self.model is not None
        }
        
        if self.device == "cuda" and torch.cuda.is_available():
            stats['vram_allocated'] = torch.cuda.memory_allocated(0) / (1024**3)
            stats['vram_reserved'] = torch.cuda.memory_reserved(0) / (1024**3)
            stats['vram_total'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        return stats
    
    def unload_model(self):
        """Unload model from VRAM (useful for VRAM management)"""
        if self.model is not None:
            print("🗑️  Unloading Whisper model from VRAM...")
            del self.model
            self.model = None
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
                print("✅ VRAM cache cleared")
    
    def reload_model(self):
        """Reload model (after unloading)"""
        if self.model is None:
            self._load_model()
