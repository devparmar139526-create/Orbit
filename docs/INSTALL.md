# 📦 orbit Installation Guide

Complete step-by-step installation guide for all platforms.

## Table of Contents
- [Windows](#windows-installation)
- [macOS](#macos-installation)
- [Linux](#linux-installation)
- [Verification](#verify-installation)
- [Common Issues](#troubleshooting)

---

## Windows Installation

### Step 1: Install Python

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. **Important:** Check "Add Python to PATH" during installation
3. Verify installation:
```cmd
python --version
pip --version
```

### Step 2: Install Ollama

1. Download from [ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open Command Prompt and verify:
```cmd
ollama --version
```

4. Pull the AI model:
```cmd
ollama pull gemma2:2b
```

5. Start Ollama (keep this window open):
```cmd
ollama serve
```

### Step 3: Install orbit

1. Download or clone orbit:
```cmd
git clone <repository-url>
cd orbit
```

2. Create virtual environment:
```cmd
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```cmd
pip install -r requirements.txt
```

4. Run test:
```cmd
python test_orbit.py
```

5. Start orbit:
```cmd
python bin\orbit.py
```

---

## macOS Installation

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python

```bash
brew install python@3.11
python3 --version
```

### Step 3: Install Ollama

```bash
# Download from ollama.ai or use:
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version

# Pull model
ollama pull gemma2:2b

# Start server
ollama serve
```

### Step 4: Install PortAudio (for microphone)

```bash
brew install portaudio
```

### Step 5: Install orbit

```bash
# Clone repository
git clone <repository-url>
cd orbit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run test
python test_orbit.py

# Start orbit
python bin/orbit.py
```

---

## Linux Installation

### Step 1: Install Python and Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install portaudio19-dev python3-pyaudio
sudo apt install espeak  # For TTS
```

#### Fedora:
```bash
sudo dnf install python3 python3-pip python3-virtualenv
sudo dnf install portaudio-devel
sudo dnf install espeak
```

#### Arch:
```bash
sudo pacman -S python python-pip
sudo pacman -S portaudio
sudo pacman -S espeak
```

### Step 2: Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version

# Pull model
ollama pull gemma2:2b

# Start server
ollama serve
```

### Step 3: Install orbit

```bash
# Clone repository
git clone <repository-url>
cd orbit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Fix audio permissions (if needed)
sudo usermod -a -G audio $USER
# Log out and back in for changes to take effect

# Run test
python test_orbit.py

# Start orbit
python bin/orbit.py
```

---

## Verify Installation

Run the test script to verify everything is working:

```bash
python test_orbit.py
```

You should see:
```
✅ All imports successful
✅ Connected to Ollama
✅ Memory store working
✅ Wikipedia API working
✅ Weather API working
✅ TTS initialized successfully
✅ STT initialized successfully

🎉 All tests passed! orbit is ready to use.
```

---

## Troubleshooting

### Ollama Not Found

**Windows:**
```cmd
# Check if running
tasklist | findstr ollama

# Restart
ollama serve
```

**Linux/macOS:**
```bash
# Check if running
ps aux | grep ollama

# Start as service (Linux with systemd)
sudo systemctl start ollama

# Or run manually
ollama serve
```

### Model Not Found

```bash
# List installed models
ollama list

# Pull model
ollama pull gemma2:2b

# Alternative models
ollama pull llama2        # ~4GB
ollama pull mistral       # ~4GB
ollama pull gemma2:9b     # ~6GB (better quality)
```

### Microphone Issues

**Windows:**
- Check Privacy Settings → Microphone → Allow apps to access
- Test in Sound Settings

**Linux:**
```bash
# Test microphone
arecord -l

# Install ALSA utils
sudo apt install alsa-utils

# Test recording
arecord -d 5 test.wav
aplay test.wav
```

**macOS:**
- System Preferences → Security & Privacy → Microphone
- Grant permission to Terminal

### PyAudio Installation Fails

**Windows:**
```cmd
# Use precompiled wheel
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
# Install dev packages first
sudo apt install portaudio19-dev python3-dev
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

### Import Errors

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Or install individually
pip install requests SpeechRecognition pyttsx3 pyaudio
```

### TTS Not Working

**Linux:**
```bash
# Install espeak
sudo apt install espeak

# Test
espeak "Hello World"
```

**Windows/macOS:**
- Should work out of the box with pyttsx3
- Try restarting your terminal

### Permission Denied Errors

**Linux/macOS:**
```bash
# Make script executable
chmod +x bin/orbit.py

# Fix audio permissions
sudo usermod -a -G audio $USER
```

---

## Next Steps

After successful installation:

1. **Start orbit:**
   ```bash
   python bin/orbit.py
   ```

2. **Try voice mode:**
   ```bash
   python bin/orbit.py --voice
   ```

3. **Customize settings:**
   - Edit `Orbit_core/config/settings.py`
   - Create `.env` file from `.env.example`

4. **Add IoT devices:**
   - See README.md for IoT configuration examples

5. **Explore commands:**
   - "What's the weather?"
   - "Who is [person]?"
   - "Open Chrome"
   - "Remind me to [task] at [time]"

---

## System Requirements

### Minimum:
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4 GB (8 GB recommended)
- **Storage:** 10 GB free space
- **OS:** Windows 10+, macOS 10.15+, or Linux (any recent distro)

### Recommended for Voice Mode:
- **CPU:** Quad-core 2.5 GHz+
- **RAM:** 8 GB+
- **Microphone:** Any USB or built-in mic
- **Internet:** For Wikipedia and Weather APIs

### For Larger Models:
- **RAM:** 16 GB+ for gemma2:9b or llama2:13b
- **Storage:** 20 GB+ for multiple models

---

## Getting Help

If you encounter issues not covered here:

1. Check the [README.md](README.md) troubleshooting section
2. Run `python test_orbit.py` to diagnose
3. Check Ollama logs: `ollama logs`
4. Verify Python packages: `pip list`

**Common Commands:**
```bash
# Check Python version
python --version

# Check if Ollama is running
curl http://localhost:11434

# List Ollama models
ollama list

# Test microphone
python -c "from Orbit_core.stt.deep import SpeechRecognizer; SpeechRecognizer().test_microphone()"
```

Happy automating! 🚀