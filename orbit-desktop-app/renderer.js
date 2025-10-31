// Electron IPC for window controls
const { ipcRenderer } = require('electron');

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const voiceVisualizer = document.getElementById('voice-visualizer');

// State
let isListening = false;
let recognition = null;
let systemLogs = [];
let conversations = [];
let currentConversationId = null;

// === INITIALIZATION === 
async function init() {
    setupEventListeners();
    setupWindowControls();
    checkServerStatus();
    await checkInternetConnection();
    initSpeechRecognition();
    initParticles();
    loadConversations();
    startLogPolling();
    
    // Auto-focus input
    userInput.focus();
    
    // Log initialization
    addLog('info', 'Admin dashboard initialized');
}

// Check internet connectivity for voice input
async function checkInternetConnection() {
    try {
        await fetch('https://www.google.com/generate_204', { 
            method: 'HEAD',
            mode: 'no-cors'
        });
        addLog('success', 'Internet connection: Available (voice input enabled)');
        return true;
    } catch (error) {
        addLog('warning', 'Internet connection: Offline (voice input will not work)');
        // Add warning message
        setTimeout(() => {
            const statusMsg = document.createElement('div');
            statusMsg.className = 'message-group system-message fade-in';
            statusMsg.innerHTML = `
                <div class="message-bubble glass-bubble" style="background: rgba(245, 158, 11, 0.2); border-color: rgba(245, 158, 11, 0.4);">
                    <div class="message-content">
                        <p>⚠️ <b>No Internet Connection Detected</b></p>
                        <p style="font-size: 13px;">Voice input requires internet (Google Speech API). Please use text input instead.</p>
                    </div>
                </div>
            `;
            chatMessages.appendChild(statusMsg);
        }, 2000);
        return false;
    }
}

// === WINDOW CONTROLS ===
function setupWindowControls() {
    document.getElementById('minimize-btn').addEventListener('click', () => {
        ipcRenderer.send('minimize-window');
    });
    
    document.getElementById('maximize-btn').addEventListener('click', () => {
        ipcRenderer.send('maximize-window');
    });
    
    document.getElementById('close-btn').addEventListener('click', () => {
        ipcRenderer.send('close-window');
    });
}

// === EVENT LISTENERS ===
function setupEventListeners() {
    sendBtn.addEventListener('click', handleSendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
    
    voiceBtn.addEventListener('click', toggleVoiceInput);
}

// === SERVER STATUS ===
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('connected', 'Connected to Orbit');
        } else {
            updateStatus('error', 'Server Error');
        }
    } catch (error) {
        updateStatus('error', 'Server Offline - Start api_server.py');
        console.error('Server check failed:', error);
    }
}

function updateStatus(state, message) {
    statusIndicator.className = `status-indicator glass-panel ${state}`;
    statusText.textContent = message;
}

// === MESSAGE HANDLING ===
async function handleSendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage('user', message);
    addLog('info', `User message: ${message.substring(0, 50)}...`);
    
    // Clear input
    userInput.value = '';
    userInput.focus();
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    // Animate background
    animateBackground();
    
    try {
        // Send to API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message }),
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.success) {
            addMessage('assistant', data.response);
            addLog('success', 'Received response from Orbit');
            
            // Refresh conversations to show new message
            setTimeout(() => loadConversations(), 1000);
        } else {
            addMessage('assistant', `Error: ${data.error}`);
            addLog('error', `API error: ${data.error}`);
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('assistant', 'Failed to connect to Orbit. Please ensure api_server.py is running.');
        addLog('error', `Connection error: ${error.message}`);
        console.error('API error:', error);
    }
}

function addMessage(sender, content, shouldScroll = true) {
    const messageGroup = document.createElement('div');
    messageGroup.className = `message-group ${sender}-message fade-in`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble glass-bubble';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Handle markdown-like formatting
    const formattedContent = content.replace(/\n/g, '<br>');
    messageContent.innerHTML = formattedContent;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    bubble.appendChild(messageContent);
    bubble.appendChild(timestamp);
    messageGroup.appendChild(bubble);
    chatMessages.appendChild(messageGroup);
    
    // Scroll to bottom
    if (shouldScroll) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group assistant-message fade-in';
    messageGroup.id = id;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble glass-bubble';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    bubble.appendChild(typingIndicator);
    messageGroup.appendChild(bubble);
    chatMessages.appendChild(messageGroup);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// === VOICE INPUT ===
function initSpeechRecognition() {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        voiceBtn.style.display = 'none';
        addLog('warning', 'Speech recognition not supported in browser');
        return;
    }
    
    try {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;
        
        recognition.onstart = () => {
            console.log('Speech recognition started');
            isListening = true;
            voiceBtn.classList.add('listening');
            voiceVisualizer.style.display = 'flex';
            updateStatus('listening', '🎤 Listening...');
            addLog('info', 'Voice input started - listening...');
        };
        
        recognition.onresult = (event) => {
            console.log('Speech recognition result:', event);
            const transcript = event.results[0][0].transcript;
            console.log('Transcript:', transcript);
            addLog('success', `Voice recognized: "${transcript}"`);
            userInput.value = transcript;
            
            // Auto-send the message
            setTimeout(() => {
                handleSendMessage();
            }, 100);
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error, event);
            addLog('error', `Voice recognition error: ${event.error}`);
            
            let errorMessage = 'Voice input error';
            let userMessage = '';
            
            switch(event.error) {
                case 'no-speech':
                    errorMessage = 'No speech detected';
                    userMessage = '⚠️ No speech was detected. Please try again and speak clearly.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Microphone not accessible';
                    userMessage = '⚠️ Cannot access microphone. Make sure no other app is using it.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone permission denied';
                    userMessage = '⚠️ Microphone permission denied. Check Windows Settings → Privacy & Security → Microphone.';
                    break;
                case 'network':
                    errorMessage = 'Network connection error';
                    userMessage = `⚠️ Cannot connect to speech recognition service.

This can happen if:
• Google's servers are unreachable
• Firewall is blocking the connection
• VPN is interfering
• DNS issues

Try:
• Type your message instead
• Restart your browser/app
• Check firewall settings
• Disable VPN temporarily`;
                    break;
                case 'service-not-allowed':
                    errorMessage = 'Speech service blocked';
                    userMessage = '⚠️ Speech recognition service is blocked. Please type your message instead.';
                    break;
                case 'aborted':
                    // User cancelled - don't show error
                    stopVoiceInput();
                    return;
                default:
                    errorMessage = `Speech error: ${event.error}`;
                    userMessage = `⚠️ Speech recognition error: ${event.error}. Please type your message instead.`;
            }
            
            stopVoiceInput();
            updateStatus('error', errorMessage);
            
            // Show detailed message to user only for important errors
            if (event.error !== 'no-speech') {
                addMessage('assistant', userMessage);
            }
            
            setTimeout(() => checkServerStatus(), 3000);
        };
        
        recognition.onend = () => {
            console.log('Speech recognition ended');
            addLog('info', 'Voice input ended');
            stopVoiceInput();
        };
        
        console.log('Speech recognition initialized successfully');
        addLog('success', 'Voice input ready (Web Speech API)');
        
    } catch (error) {
        console.error('Failed to initialize speech recognition:', error);
        addLog('error', `Voice init failed: ${error.message}`);
        voiceBtn.style.display = 'none';
    }
}

function toggleVoiceInput() {
    if (!recognition) {
        console.error('Speech recognition not available');
        addLog('error', 'Voice input not available');
        addMessage('assistant', '⚠️ Voice input is not available. Speech recognition failed to initialize.');
        return;
    }
    
    if (isListening) {
        console.log('Stopping voice input...');
        addLog('info', 'Stopping voice input');
        try {
            recognition.stop();
        } catch (error) {
            console.error('Error stopping recognition:', error);
            stopVoiceInput();
        }
    } else {
        console.log('Starting voice input...');
        addLog('info', 'Starting voice input...');
        try {
            recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
            addLog('error', `Failed to start: ${error.message}`);
            
            // Check if already running
            if (error.message && error.message.includes('already started')) {
                addMessage('assistant', '⚠️ Voice input is already listening. Speak now!');
            } else {
                addMessage('assistant', `⚠️ Could not start voice input: ${error.message}`);
            }
        }
    }
}

function stopVoiceInput() {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceVisualizer.style.display = 'none';
    checkServerStatus();
}

// === ADMIN DASHBOARD FUNCTIONS ===

// Load conversation history
async function loadConversations() {
    try {
        addLog('info', 'Loading conversation history...');
        const response = await fetch(`${API_BASE_URL}/memory/context`);
        const data = await response.json();
        
        if (data.success) {
            // Group messages into conversations
            conversations = groupMessagesIntoConversations(data.context);
            displayConversationList();
            addLog('success', `Loaded ${conversations.length} conversations`);
        } else {
            addLog('error', 'Failed to load conversations');
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
        addLog('error', `Conversation load error: ${error.message}`);
        document.getElementById('conversation-list').innerHTML = 
            '<p class="loading-text">Error loading conversations</p>';
    }
}

function groupMessagesIntoConversations(messages) {
    if (!messages || messages.length === 0) return [];
    
    const conversationGroups = [];
    let currentGroup = [];
    
    messages.forEach((msg, index) => {
        currentGroup.push(msg);
        
        // Create new conversation every 20 messages or at natural breaks
        if (currentGroup.length >= 20 || index === messages.length - 1) {
            conversationGroups.push({
                id: `conv-${conversationGroups.length}`,
                messages: [...currentGroup],
                timestamp: currentGroup[0].timestamp,
                preview: currentGroup[0].message.substring(0, 50)
            });
            currentGroup = [];
        }
    });
    
    return conversationGroups.reverse(); // Most recent first
}

function displayConversationList() {
    const listContainer = document.getElementById('conversation-list');
    
    if (conversations.length === 0) {
        listContainer.innerHTML = '<p class="loading-text">No conversations yet</p>';
        return;
    }
    
    listContainer.innerHTML = conversations.map((conv, index) => `
        <div class="conversation-item ${index === 0 ? 'active' : ''}" onclick="loadConversation('${conv.id}')">
            <div class="conversation-time">${formatTimestamp(conv.timestamp)}</div>
            <div class="conversation-preview">${conv.preview}...</div>
        </div>
    `).join('');
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'Unknown time';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

function loadConversation(conversationId) {
    const conversation = conversations.find(c => c.id === conversationId);
    if (!conversation) return;
    
    currentConversationId = conversationId;
    
    // Clear current chat
    chatMessages.innerHTML = '';
    
    // Display conversation messages
    conversation.messages.forEach(msg => {
        addMessage(msg.role === 'user' ? 'user' : 'assistant', msg.message, false);
    });
    
    // Update active state in list
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.conversation-item').classList.add('active');
    
    addLog('info', `Loaded conversation: ${conversationId}`);
}

function refreshConversations() {
    addLog('info', 'Refreshing conversations...');
    loadConversations();
    updateStatus('connecting', 'Refreshing...');
    setTimeout(() => checkServerStatus(), 1000);
}

async function clearAllMemory() {
    if (!confirm('⚠️ Clear all conversation memory? This cannot be undone!')) {
        return;
    }
    
    try {
        addLog('warning', 'Clearing all memory...');
        
        // Note: You'll need to implement this endpoint in api_server.py
        const response = await fetch(`${API_BASE_URL}/memory/clear`, {
            method: 'POST'
        });
        
        if (response.ok) {
            conversations = [];
            displayConversationList();
            chatMessages.innerHTML = `
                <div class="message-group system-message">
                    <div class="message-bubble glass-bubble">
                        <div class="message-content">
                            <h2>Memory Cleared 🗑️</h2>
                            <p>All conversation history has been deleted</p>
                        </div>
                    </div>
                </div>
            `;
            addLog('success', 'Memory cleared successfully');
        } else {
            addLog('error', 'Failed to clear memory');
        }
    } catch (error) {
        console.error('Error clearing memory:', error);
        addLog('error', `Clear memory error: ${error.message}`);
    }
}

// === SYSTEM LOGS ===

function addLog(level, message) {
    const log = {
        level: level,
        message: message,
        timestamp: new Date().toISOString()
    };
    
    systemLogs.unshift(log); // Add to beginning
    
    // Keep only last 1000 logs
    if (systemLogs.length > 1000) {
        systemLogs = systemLogs.slice(0, 1000);
    }
    
    console.log(`[${level.toUpperCase()}] ${message}`);
}

function showLogs() {
    const logsPanel = document.getElementById('logs-panel');
    const logsContent = document.getElementById('logs-content');
    
    logsPanel.style.display = 'flex';
    
    if (systemLogs.length === 0) {
        logsContent.innerHTML = '<p class="loading-text">No logs yet</p>';
        return;
    }
    
    logsContent.innerHTML = systemLogs.map(log => `
        <div class="log-entry ${log.level}">
            <div class="log-time">${new Date(log.timestamp).toLocaleString()}</div>
            <div class="log-message">${log.message}</div>
        </div>
    `).join('');
    
    addLog('info', 'Logs panel opened');
}

function closeLogs() {
    document.getElementById('logs-panel').style.display = 'none';
    addLog('info', 'Logs panel closed');
}

function exportLogs() {
    const logsText = systemLogs.map(log => 
        `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `orbit-logs-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    addLog('success', 'Logs exported successfully');
}

function startLogPolling() {
    // Poll for new conversations every 30 seconds
    setInterval(() => {
        loadConversations();
    }, 30000);
    
    addLog('info', 'Started background polling (30s interval)');
}

// === BACKGROUND ANIMATIONS ===
function animateBackground() {
    const orbs = document.querySelectorAll('.gradient-orb');
    orbs.forEach((orb, index) => {
        orb.style.animation = 'none';
        setTimeout(() => {
            orb.style.animation = `float ${15 + index * 3}s infinite ease-in-out`;
        }, 10);
    });
}

// === PARTICLE SYSTEM ===
function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 50;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        
        draw() {
            ctx.fillStyle = `rgba(147, 51, 234, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        // Draw connections
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 150) {
                    ctx.strokeStyle = `rgba(147, 51, 234, ${0.15 * (1 - distance / 150)})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    // Resize handler
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// === UTILITY FUNCTIONS ===
function speak(text) {
    // Text-to-speech (optional)
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        speechSynthesis.speak(utterance);
    }
}

// === MUSIC CONTROLS (Future Enhancement) ===
async function playMusic(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/music/play`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Music API error:', error);
        return { success: false, error: error.message };
    }
}

// === SCREENSHOT (Future Enhancement) ===
async function takeScreenshot() {
    try {
        const response = await fetch(`${API_BASE_URL}/screenshot`, {
            method: 'POST',
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Screenshot API error:', error);
        return { success: false, error: error.message };
    }
}

// === KEYBOARD SHORTCUTS ===
document.addEventListener('keydown', (e) => {
    // Ctrl+K or Cmd+K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        userInput.focus();
    }
    
    // Ctrl+L or Cmd+L to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }
    
    // Ctrl+Space to toggle voice
    if (e.ctrlKey && e.code === 'Space') {
        e.preventDefault();
        toggleVoiceInput();
    }
});

// === START APPLICATION ===
document.addEventListener('DOMContentLoaded', init);

// === EXPORTS FOR TESTING ===
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        quickAction,
        clearChat,
        playMusic,
        takeScreenshot,
    };
}
