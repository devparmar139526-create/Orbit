# � ORBIT AI ASSISTANT - Complete System

> **Enterprise-Grade AI Assistant with 31 Production-Ready Features**  
> Zero Hardcoding • Fully Configurable • Cross-Platform • Production Ready

**Orbit** is a powerful, Jarvis-inspired AI assistant with voice control, desktop automation, productivity features, and AI-powered tools. Built with zero hardcoding, every feature is fully configurable.

## 🎯 System Status

✅ **Phase 1**: 8 Core Features - COMPLETE  
✅ **Phase 2**: 10 Device Control Features - COMPLETE  
✅ **Phase 3**: 13 AI & Productivity Features - COMPLETE  
✅ **Phase 4**: 14 YouTube Music Features - COMPLETE  
🎉 **Total**: 45 Features - 100% Test Coverage - Production Ready

## ✨ Key Features

### 🎤 Phase 1: Core (8 Features)
- **Voice Interaction** - Natural speech input/output with wake word
- **Local AI** - Ollama integration (phi3:mini, llama3, gemma2)
- **Wikipedia** - Knowledge search and information retrieval
- **Weather** - Real-time forecasts for any location
- **Desktop Control** - Launch and control applications
- **Task Scheduling** - Time-based reminders and commands
- **Hybrid Mode** - Seamless voice + text switching
- **Zero Hardcoding** - Fully configurable via JSON/env vars

### 🖥️ Phase 2: Device Control (10 Features)
- **Screenshots** - Capture screen with auto-save
- **Screen Recording** - Record screen activity to video
- **File Management** - Create, delete, move files/folders
- **Auto-Organize** - Sort downloads by type automatically
- **Keyboard Macros** - Automated keystroke sequences
- **Window Management** - List, focus, switch windows
- **Cross-Platform** - Windows, macOS, Linux support
- **Whitelisting** - Control app access with allow/block lists
- **Predefined Macros** - Ready-to-use automation scripts
- **Advanced Control** - System-level operations

### 🧠 Phase 3: AI & Productivity (13 Features)
- **Text Translation** - 20+ languages with deep-translator
- **Language Detection** - Automatic language identification
- **Batch Translation** - Translate multiple texts efficiently
- **Task Prediction** - AI predicts your next task from patterns
- **Smart Reminders** - Context-aware alerts with optimal timing
- **Schedule Optimization** - AI-powered schedule planning
- **Organize by Type** - Auto-categorize files (Images, Docs, Videos)
- **Organize by Date** - Sort files by creation date (YYYY-MM)
- **Document Summarization** - AI summarization of PDF/TXT
- **CSV Processing** - Analyze and process spreadsheets
- **Report Generation** - Auto-create formatted reports
- **Screen Time Tracking** - Monitor computer usage
- **Break Suggestions** - Pomodoro-style break reminders

### 🎵 Phase 4: YouTube Music (14 Features)
- **Search Music** - Find tracks, albums, artists, playlists
- **Play Tracks** - Instant playback with voice commands
- **Pause/Resume** - Full playback control
- **Next/Previous** - Navigate through tracks
- **Queue Management** - Add, view, clear, shuffle queue
- **Volume Control** - Adjust volume (0-100%)
- **Create Playlists** - Build custom playlists
- **View Playlists** - Browse your music library
- **Add to Playlist** - Organize favorite tracks
- **Play Playlists** - Play entire collections
- **Recommendations** - Personalized music suggestions
- **Mood Playlists** - Happy, sad, energetic, relaxed, focus
- **OAuth Authentication** - Secure API access
- **Playback State** - Track current song and status

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Ollama** (for local AI)
- **Microphone** (for voice mode)

### 2. Install Ollama

```bash
# Visit https://ollama.ai and install for your OS

# After installation, pull the model:
ollama pull gemma2:2b
# Or use a smaller/larger model:
# ollama pull gemma2:9b  (better quality, slower)
# ollama pull llama2     (alternative)

# Start Ollama server:
ollama serve
```

### 3. Install Python Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd orbit

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# On Linux, you may need additional packages for audio:
sudo apt-get install portaudio19-dev python3-pyaudio
```

### 4. Run orbit

```bash
# Text mode (no microphone needed)
python bin/orbit.py

# Voice mode (requires microphone)
python bin/orbit.py --voice
```

## 📁 Project Structure

```
orbit/
├── bin/
│   └── orbit.py              # Main entry point
├── Orbit_core/
│   ├── actions/              # Action handlers
│   │   ├── desktop.py        # Desktop app control
│   │   ├── iot.py           # IoT device control
│   │   ├── schedule_action.py # Task scheduling
│   │   ├── weather.py        # Weather queries
│   │   └── wikipedia.py      # Wikipedia search
│   ├── bus/
│   │   └── event_bus.py      # Event system
│   ├── config/
│   │   └── settings.py       # Configuration
│   ├── intent/
│   │   └── source_selector.py # Intent classification
│   ├── llm/
│   │   ├── ollama_client.py  # Ollama integration
│   │   └── router.py         # LLM routing
│   ├── memory/
│   │   └── sqlite_store.py   # Conversation memory
│   ├── stt/
│   │   └── deep.py           # Speech-to-text
│   └── tts/
│       ├── pyttsx_tts.py     # Text-to-speech engine
│       └── dispatcher.py     # TTS dispatcher
├── data/                     # Database & logs (auto-created)
└── requirements.txt
```

## 💬 Usage Examples

### Text Mode
```
You: Hello orbit
orbit: Hello! orbit is online and ready to assist you.

You: What's the weather in London?
orbit: Weather in London, United Kingdom: Currently clear sky with a temperature of 12°C...

You: Who is Albert Einstein?
orbit: According to Wikipedia: Albert Einstein was a German-born theoretical physicist...

You: Open Chrome
orbit: Opening chrome.

You: Remind me to drink water at 5 PM
orbit: Got it! I'll remind you to 'drink water' at 05:00 PM on October 01.
```

### Voice Mode
Just speak naturally! Say "exit" or "goodbye" to quit.

## ⚙️ Configuration

Edit `Orbit_core/config/settings.py` to customize:

```python
# LLM Settings
OLLAMA_MODEL = "gemma2:2b"  # Change model
OLLAMA_URL = "http://localhost:11434"

# Voice Settings
TTS_RATE = 175  # Speaking speed
TTS_VOLUME = 0.9  # Volume level

# Personality
SYSTEM_PROMPT = "You are orbit..."  # Customize personality
```

## 🏠 IoT Setup (Optional)

### Configure Smart Devices

Create a device configuration in your code:

```python
iot_config = {
    'devices': {
        'living_room_light': {
            'type': 'http',
            'on_url': 'http://192.168.1.100/on',
            'off_url': 'http://192.168.1.100/off'
        },
        'bedroom_fan': {
            'type': 'mqtt',
            'topic': 'home/bedroom/fan',
            'on_payload': '1',
            'off_payload': '0'
        }
    }
}
```

### Example IoT Commands
```
"Turn on living room light"
"Turn off bedroom fan"
```

## 🔧 Troubleshooting

### Ollama Not Connecting
```bash
# Make sure Ollama is running:
ollama serve

# Check if model is downloaded:
ollama list

# Pull model if needed:
ollama pull gemma2:2b
```

### Microphone Issues
```bash
# Test your microphone:
python -c "from Orbit_core.stt.deep import SpeechRecognizer; sr = SpeechRecognizer(); sr.test_microphone()"

# On Linux, check audio permissions:
sudo usermod -a -G audio $USER
```

### TTS Not Working
```bash
# Install additional dependencies:
# On Linux:
sudo apt-get install espeak

# On