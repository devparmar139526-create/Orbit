# 🌌 Orbit Desktop App

A stunning liquid glass desktop application for Orbit AI Assistant with voice input, animations, and beautiful UI.

## ✨ Features

- **Liquid Glass Design** - Purple-tinted glass morphism with blur effects
- **Voice Input** - Web Speech API for hands-free interaction
- **Animated Background** - Floating gradient orbs and particle system
- **Real-time Chat** - Beautiful chat bubbles with typing indicators
- **Quick Actions** - Sidebar shortcuts for common commands
- **Window Controls** - Custom frameless window with drag support
- **Dark Mode** - Stunning dark theme with glowing effects
- **Keyboard Shortcuts**:
  - `Ctrl+K` / `Cmd+K` - Focus input
  - `Ctrl+L` / `Cmd+L` - Clear chat
  - `Ctrl+Space` - Toggle voice input
  - `Enter` - Send message

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd orbit-desktop-app
npm install
```

### 2. Start the Backend API Server

Open a separate terminal and run:

```powershell
cd "c:\AAAA\Orbit Final"
.\.venv\Scripts\activate
python api_server.py
```

The API server will start on http://localhost:5000

### 3. Run the Desktop App

```bash
npm start
```

## 📦 Build Executable

### Windows

```bash
npm run build:win
```

Output: `dist/Orbit Setup.exe`

### macOS

```bash
npm run build:mac
```

Output: `dist/Orbit.dmg`

### Linux

```bash
npm run build:linux
```

Output: `dist/Orbit.AppImage`

## 🎨 UI Components

### Window Layout
```
┌─────────────────────────────────────────┐
│ [≡] Orbit AI Assistant      [─] [□] [×] │  ← Title Bar
├─────────────────────────────────────────┤
│         │                               │
│ Sidebar │      Chat Messages            │
│         │                               │
│ Actions │      [Voice Visualizer]       │
│         │                               │
│         │      User Input + Voice       │
└─────────────────────────────────────────┘
```

### Color Scheme
- **Primary Purple**: `#9333ea`
- **Secondary Purple**: `#c084fc`
- **Accent Purple**: `#a855f7`
- **Glass Background**: `rgba(255, 255, 255, 0.08)`
- **Text**: `rgba(255, 255, 255, 0.95)`

## 🔧 Configuration

### API Endpoint
Edit `renderer.js` to change the API URL:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Window Size
Edit `main.js`:

```javascript
const mainWindow = new BrowserWindow({
  width: 1200,  // Change width
  height: 800,  // Change height
  // ...
});
```

### Theme Colors
Edit CSS variables in `styles.css`:

```css
:root {
    --primary-purple: #9333ea;
    --secondary-purple: #c084fc;
    /* ... */
}
```

## 📁 Project Structure

```
orbit-desktop-app/
├── main.js           # Electron main process
├── renderer.js       # Frontend logic & API calls
├── index.html        # UI structure
├── styles.css        # Liquid glass styles
├── package.json      # Dependencies & build config
└── README.md         # This file
```

## 🎯 Usage

1. **Start Chatting**: Type in the input box or click the microphone icon
2. **Voice Input**: Click the microphone button and speak your command
3. **Quick Actions**: Use sidebar buttons for common tasks
4. **Clear Chat**: Click "Clear Chat" button or press `Ctrl+L`

### Example Commands

```
"Hello Orbit"
"Take a screenshot"
"What's the weather?"
"Play happy music"
"Search Wikipedia for Albert Einstein"
"Translate hello to Spanish"
"Set a reminder for 3pm"
```

## 🐛 Troubleshooting

### Server Offline Error
- Make sure `api_server.py` is running
- Check that Flask is installed: `pip install flask flask-cors`
- Verify the API is accessible at http://localhost:5000/api/health

### Voice Input Not Working
- Ensure microphone permissions are granted
- Chrome/Chromium required (Electron uses Chromium)
- Check browser console for errors (Ctrl+Shift+I)

### Window Not Transparent
- Update GPU drivers
- Try disabling hardware acceleration in `main.js`:
  ```javascript
  app.disableHardwareAcceleration();
  ```

## 🔮 Future Enhancements

- [ ] Music player controls in UI
- [ ] Screenshot preview gallery
- [ ] Settings panel for customization
- [ ] Multiple theme options (light mode)
- [ ] Chat history persistence
- [ ] System tray integration
- [ ] Hotkey to show/hide window
- [ ] Multi-language support
- [ ] Voice output (TTS)
- [ ] Animated avatar/assistant character

## 📄 License

Part of the Orbit AI Assistant project

## 🙏 Credits

- **Design**: Liquid glass morphism inspired by iOS/macOS
- **Framework**: Electron + Vanilla JavaScript
- **Backend**: Flask REST API with Orbit Core
- **Voice**: Web Speech API
- **Animations**: CSS3 + Canvas

---

**Made with 💜 by the Orbit Team**
