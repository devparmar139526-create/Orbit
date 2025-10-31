# HiggsAudio TTS Setup Guide
## Microsoft Edge Neural TTS - Python 3.13 Compatible

## Overview
Orbit now supports **HiggsAudio** - a high-quality neural text-to-speech engine powered by **Microsoft Edge TTS**. This provides more natural, human-like voice synthesis compared to the default pyttsx3 engine.

### Why Edge TTS?
✅ **Python 3.13 Compatible** - Works with Python 3.7-3.13  
✅ **High-Quality Neural Voices** - Microsoft's own premium TTS  
✅ **300+ Voices** - In 100+ languages  
✅ **No GPU Required** - Fast CPU synthesis  
✅ **Free** - No API key or signup needed  
✅ **Offline Capable** - After initial voice download  

**Note:** Previously this used Coqui TTS, but Coqui only supports Python 3.9-3.11 ❌

## Features
- 🎤 **High-Quality Neural Voices** - Realistic, natural-sounding speech
- 🌍 **100+ Languages** - English, Spanish, French, German, Chinese, Japanese, Arabic, Hindi, and more
- 🎭 **300+ Unique Voices** - Multiple voices per language (male, female, different accents)
- 🔧 **Customizable** - Adjust speed, pitch, volume
- 🚀 **Async Operation** - Non-blocking speech synthesis
- 💾 **Save to File** - Export speech as MP3 files
- 🔁 **Fallback Support** - Automatically falls back to pyttsx3 if unavailable

## Installation

### Step 1: Install Edge TTS
```bash
pip install edge-tts
```

**Package size:** ~50KB (very lightweight!)

### Step 2: (Optional) Install Audio Playback
For better audio playback on Windows:
```bash
pip install playsound
```

That's it! No large model downloads, no GPU required.

## Configuration

### Option 1: Use Settings Object
Add to your `configs/phase2_config.json`:
```json
{
  "TTS_ENGINE": "higgs",
  "HIGGS_TTS_VOICE": "en-US-AriaNeural",
  "HIGGS_TTS_RATE": "+0%",
  "HIGGS_TTS_VOLUME": "+0%",
  "HIGGS_TTS_PITCH": "+0Hz"
}
```

### Option 2: Direct Initialization
```python
from Orbit_core.tts.dispatcher import TTSDispatcher

# Use HiggsAudio (Edge TTS)
tts = TTSDispatcher(engine_type="higgs")

# Or use pyttsx3 (default)
tts = TTSDispatcher(engine_type="pyttsx3")
```

## Usage Examples

### Basic Speech
```python
from Orbit_core.tts.higgs_audio_tts import HiggsAudioTTS

tts = HiggsAudioTTS()
tts.speak("Hello! This is HiggsAudio neural text-to-speech using Microsoft Edge.")
```

### Save to File
```python
tts = HiggsAudioTTS()
tts.save_to_file(
    "Welcome to Orbit AI Assistant!", 
    "output.mp3"
)
```

### Use Different Voices
```python
# Female voice (default)
tts = HiggsAudioTTS(voice="en-US-AriaNeural")
tts.speak("This is Aria, a natural female voice.")

# Male voice
tts = HiggsAudioTTS(voice="en-US-GuyNeural")
tts.speak("This is Guy, a natural male voice.")

# British accent
tts = HiggsAudioTTS(voice="en-GB-SoniaNeural")
tts.speak("This is Sonia with a British accent.")
```

### Adjust Speech Parameters
```python
# Faster speech
tts = HiggsAudioTTS()
tts.rate = "+50%"  # -50% to +100%
tts.speak("This is faster speech.")

# Lower pitch
tts.pitch = "-20Hz"  # -50Hz to +50Hz
tts.speak("This is lower pitch speech.")

# Louder volume
tts.volume = "+25%"  # -50% to +50%
tts.speak("This is louder speech.")
```

### Multi-Language Support
```python
# Spanish
tts = HiggsAudioTTS(voice="es-ES-ElviraNeural")
tts.speak("Hola, ¿cómo estás?")

# French
tts = HiggsAudioTTS(voice="fr-FR-DeniseNeural")
tts.speak("Bonjour, comment allez-vous?")

# Japanese
tts = HiggsAudioTTS(voice="ja-JP-NanamiNeural")
tts.speak("こんにちは、元気ですか？")

# Chinese
tts = HiggsAudioTTS(voice="zh-CN-XiaoxiaoNeural")
tts.speak("你好，你好吗？")

# Arabic
tts = HiggsAudioTTS(voice="ar-SA-ZariyahNeural")
tts.speak("مرحبا، كيف حالك؟")
```

### List Available Voices
```python
tts = HiggsAudioTTS()

# Get all English voices
voices = tts.get_voices_by_language('en-US')
for voice in voices[:5]:  # Show first 5
    print(voice)
```

### Switch Engines at Runtime
```python
from Orbit_core.tts.dispatcher import TTSDispatcher

tts = TTSDispatcher(engine_type="pyttsx3")
tts.speak("Using fast pyttsx3 engine")

# Switch to high-quality neural engine
tts.switch_engine("higgs")
tts.speak("Now using HiggsAudio neural engine with Microsoft Edge voices")
```

## Recommended Voices by Language

| Language | Female Voice | Male Voice |
|----------|-------------|------------|
| English (US) | `en-US-AriaNeural` | `en-US-GuyNeural` |
| English (UK) | `en-GB-SoniaNeural` | `en-GB-RyanNeural` |
| English (AU) | `en-AU-NatashaNeural` | `en-AU-WilliamNeural` |
| Spanish (ES) | `es-ES-ElviraNeural` | `es-ES-AlvaroNeural` |
| Spanish (MX) | `es-MX-DaliaNeural` | `es-MX-JorgeNeural` |
| French | `fr-FR-DeniseNeural` | `fr-FR-HenriNeural` |
| German | `de-DE-KatjaNeural` | `de-DE-ConradNeural` |
| Italian | `it-IT-ElsaNeural` | `it-IT-DiegoNeural` |
| Portuguese | `pt-BR-FranciscaNeural` | `pt-BR-AntonioNeural` |
| Russian | `ru-RU-SvetlanaNeural` | `ru-RU-DmitryNeural` |
| Japanese | `ja-JP-NanamiNeural` | `ja-JP-KeitaNeural` |
| Chinese | `zh-CN-XiaoxiaoNeural` | `zh-CN-YunxiNeural` |
| Korean | `ko-KR-SunHiNeural` | `ko-KR-InJoonNeural` |
| Arabic | `ar-SA-ZariyahNeural` | `ar-SA-HamedNeural` |
| Hindi | `hi-IN-SwaraNeural` | `hi-IN-MadhurNeural` |

## Voice Quality Examples

Try different voices to find your favorite:

```python
voices_to_test = [
    ("en-US-AriaNeural", "Aria - Friendly and conversational"),
    ("en-US-JennyNeural", "Jenny - Warm and expressive"),
    ("en-US-GuyNeural", "Guy - Professional male voice"),
    ("en-US-DavisNeural", "Davis - Deep authoritative male"),
    ("en-GB-SoniaNeural", "Sonia - British female"),
]

for voice, description in voices_to_test:
    print(f"\nTesting: {description}")
    tts = HiggsAudioTTS(voice=voice)
    tts.speak(f"Hello, I am {description.split('-')[0].strip()}")
    import time
    time.sleep(3)
```

## Performance Comparison

| Feature | pyttsx3 | HiggsAudio (Edge TTS) |
|---------|---------|----------------------|
| Voice Quality | Robotic | Natural/Human-like ✅ |
| Speed | Very Fast (~50ms) | Fast (~300ms) |
| Internet Required | No | Yes (first time only)* |
| CPU Usage | Low | Low-Moderate |
| Memory Usage | ~50MB | ~100MB |
| Languages | 3-5 | 100+ ✅ |
| Voices | 5-10 | 300+ ✅ |
| File Size | Small | Small (~50KB) ✅ |
| Python 3.13 | ✅ | ✅ |

\* Edge TTS caches voices locally after first download

## When to Use Each Engine

### Use **pyttsx3** when:
- Speed is absolutely critical (real-time responses)
- Running on very low-resource devices
- No internet connection available
- Voice quality is not important
- Quick testing/debugging

### Use **HiggsAudio (Edge TTS)** when:
- Voice quality matters (demos, production) ✅
- Need multi-language support ✅
- Want natural-sounding voices ✅
- Have internet connection (at least initially)
- Python 3.13 compatibility required ✅

## Troubleshooting

### Import Error: edge_tts module not found
```bash
pip install edge-tts
```

### Audio Playback Issues on Windows
Install playsound for better audio support:
```bash
pip install playsound
```

### No Sound Playing
- Check system volume
- Verify audio drivers are working
- Try different voice: some voices may fail on first attempt

### Slow First Speech
The first synthesis downloads the voice model (~5-10MB per voice). Subsequent calls are much faster as the voice is cached.

### Internet Connection Required
Edge TTS requires internet for the first synthesis of each voice. After that, voices are cached locally.

## Default Engine

By default, Orbit uses **pyttsx3** (fast, offline, lightweight).

To permanently switch to HiggsAudio:
1. Edit `configs/phase2_config.json`
2. Add: `"TTS_ENGINE": "higgs"`
3. Add: `"HIGGS_TTS_VOICE": "en-US-AriaNeural"` (optional)
4. Restart Orbit

## Installation Script

Quick setup script for HiggsAudio:

```bash
# Install edge-tts
pip install edge-tts

# Optional: Install audio player
pip install playsound

# Test installation
python -m Orbit_core.tts.higgs_audio_tts
```

Or use the demo function:
```python
from Orbit_core.tts.higgs_audio_tts import demo
demo()
```

## API Reference

### HiggsAudioTTS Class

#### Constructor
```python
HiggsAudioTTS(
    settings=None,              # Settings object
    voice: str = None,          # Voice name (e.g., "en-US-AriaNeural")
    language: str = None        # Language code (e.g., "en-US")
)
```

#### Methods

**speak(text: str)**
- Speak text using TTS (non-blocking)

**save_to_file(text: str, filename: str)**
- Save speech to MP3 file

**list_available_voices() -> List[str]**
- Get list of all available voices (300+)

**get_voices_by_language(language: str) -> List[str]**
- Get voices for a specific language

**stop()**
- Stop any currently playing audio

## Examples in Orbit

### Chat with High-Quality Voice
```bash
python orbit_api.py --config configs/phase2_config.json
```

Add to `configs/phase2_config.json`:
```json
{
  "TTS_ENGINE": "higgs",
  "ENABLE_TTS": true,
  "HIGGS_TTS_VOICE": "en-US-AriaNeural"
}
```

### API Server with HiggsAudio
```bash
python api_server.py
```

Voice responses will automatically use HiggsAudio if configured.

### Desktop App with Neural Voices
The Electron desktop app will automatically use HiggsAudio TTS if you have it configured in your settings.

## Voice Samples

Want to hear the voices before choosing? Use this script:

```python
from Orbit_core.tts.higgs_audio_tts import HiggsAudioTTS, RECOMMENDED_VOICES

# Test all recommended English voices
for voice in RECOMMENDED_VOICES['en-US']:
    print(f"\nTesting: {voice}")
    tts = HiggsAudioTTS(voice=voice)
    tts.speak(f"Hello, this is {voice}. I am one of the Microsoft Edge neural voices.")
    import time
    time.sleep(4)
```

## Additional Resources

- Edge TTS GitHub: https://github.com/rany2/edge-tts
- Edge TTS Documentation: https://github.com/rany2/edge-tts#usage
- Microsoft Edge TTS Voices: https://speech.microsoft.com/portal/voicegallery

## License

- **pyttsx3**: MPL-2.0 License (free for all use)
- **edge-tts**: GPL-3.0 License (free for all use)
- **Microsoft Edge TTS**: Free to use (Microsoft's service)

---

**Need Help?** Check the troubleshooting section or open an issue on GitHub.

**Python 3.13 Compatible** ✅ Unlike Coqui TTS, Edge TTS works perfectly with Python 3.13!
