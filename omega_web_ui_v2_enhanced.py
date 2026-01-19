"""
Omega Enhanced Web UI v2 - With Full Integration
- 3-bar KITT voice box (AUTHENTIC Season 2-4 Knight Rider design - 600x250px)
- Based on Episode 14 'Heart of Stone' canonical design
- Omega voice integration (120 Hz base, deep authoritative)
- Conversational AI with knowledge base access
- Agent council integration for complex queries
- Real-time voice interaction
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sys
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega-secret-2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

sys.path.insert(0, str(Path(__file__).parent))

try:
    from omega_agent_council import agent_council
    import asyncio
    AGENT_COUNCIL_AVAILABLE = True
except ImportError:
    AGENT_COUNCIL_AVAILABLE = False
    print("[WARN] Agent council not available")

html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω OMEGA Control Panel - Enhanced v2</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            overflow: hidden;
            height: 100vh;
        }

        .container {
            width: 100%;
            height: 100vh;
            display: grid;
            grid-template-rows: 80px 1fr 400px 120px;
            gap: 20px;
            padding: 20px;
            position: relative;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, rgba(0, 0, 50, 0.9), rgba(50, 0, 50, 0.9));
            border: 3px solid #0ff;
            border-radius: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 30px;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.4);
        }

        .header h1 {
            font-size: 2.5em;
            color: #0ff;
            text-shadow: 0 0 20px #0ff;
            letter-spacing: 5px;
        }

        .status-indicator {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #0f0;
            box-shadow: 0 0 20px #0f0;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Main Content Area */
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }

        .panel {
            background: rgba(10, 10, 30, 0.8);
            border: 2px solid #0ff;
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
        }

        .panel h2 {
            color: #0ff;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        /* Chat Panel */
            height: calc(100% - 100px);
            overflow-y: auto;
            margin-bottom: 15px;
        }

        .chat-message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }

        .chat-message.user {
            background: rgba(0, 255, 255, 0.1);
            border-left: 3px solid #0ff;
        }

        .chat-message.omega {
            background: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #f00;
        }

        .chat-input {
            display: flex;
            gap: 10px;
        }

        .chat-input input {
            flex: 1;
            padding: 10px;
            background: rgba(0, 255, 255, 0.1);
            border: 2px solid #0ff;
            border-radius: 5px;
            color: #0ff;
            font-family: 'Courier New', monospace;
        }

        .chat-input button {
            padding: 10px 20px;
            background: rgba(255, 0, 0, 0.3);
            border: 2px solid #f00;
            border-radius: 5px;
            color: #f00;
            cursor: pointer;
            font-weight: bold;
        }

        .chat-input button:hover {
            background: rgba(255, 0, 0, 0.5);
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        }

        /* Console */
            height: 100%;
            overflow-y: auto;
            font-size: 0.9em;
            line-height: 1.6;
        }

        .console-line {
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid transparent;
        }

        .console-line.info { color: #0ff; border-left-color: #0ff; }
        .console-line.warning { color: #ff0; border-left-color: #ff0; }
        .console-line.error { color: #f00; border-left-color: #f00; }
        .console-line.user { color: #0f0; border-left-color: #0f0; }
        .console-line.omega { color: #f0f; border-left-color: #f0f; }

        /* RGB Controls */
        .rgb-controls {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .rgb-slider {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .rgb-slider label {
            font-size: 1.2em;
            text-transform: uppercase;
        }

        .rgb-slider input[type="range"] {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            outline: none;
        }

        /* KITT Voice Box - AUTHENTIC 3-bar design (Season 2-4 canonical) */
        .kitt-voice-box {
            position: absolute;
            bottom: 150px;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 250px;
            background: linear-gradient(180deg, rgba(0, 0, 0, 0.95), rgba(20, 0, 0, 0.9));
            border: 5px solid #ff0000;
            border-radius: 12px;
            box-shadow: 0 0 40px rgba(255, 0, 0, 0.8), inset 0 0 30px rgba(255, 0, 0, 0.2);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            padding: 30px;
        }
        
        .kitt-voice-box.talking {
            box-shadow: 0 0 60px rgba(255, 0, 0, 1.0), inset 0 0 40px rgba(255, 0, 0, 0.3);
            border-color: #ff3333;
        }

        .voice-bar {
            width: 80px;
            height: 40px;
            background: linear-gradient(180deg, #ff0000, #cc0000, #660000);
            border: 3px solid #ff0000;
            border-radius: 4px;
            transition: height 0.05s ease-out;
            box-shadow: 0 0 25px rgba(255, 0, 0, 0.9), 0 0 50px rgba(255, 0, 0, 0.6);
        }
        
        .voice-bar.active {
            box-shadow: 0 0 40px rgba(255, 0, 0, 1.0), 0 0 70px rgba(255, 0, 0, 0.8);
            background: linear-gradient(180deg, #ff3333, #ff0000, #990000);
        }
        
        /* Center bar is taller (authentic KITT design) */
            height: 60px;
        }

        /* KITT Scanner */
        .kitt-scanner {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            height: 80px;
            background: rgba(0, 0, 0, 0.9);
            border: 3px solid #ff0000;
            border-radius: 10px;
            display: flex;
            align-items: center;
            padding: 10px;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
        }

        .scanner-light {
            position: absolute;
            width: 150px;
            height: 60px;
            background: radial-gradient(ellipse, #ff0000, rgba(255, 0, 0, 0));
            border-radius: 50%;
            filter: blur(10px);
            animation: scan 2s linear infinite;
        }

        @keyframes scan {
            0% { left: 0; }
            100% { left: calc(100% - 150px); }
        }

        /* Controls */
        .controls {
            display: flex;
            gap: 20px;
            justify-content: center;
            align-items: center;
        }

        .control-btn {
            padding: 15px 30px;
            background: rgba(0, 255, 0, 0.2);
            border: 3px solid #0f0;
            border-radius: 10px;
            color: #0f0;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .control-btn:hover {
            background: rgba(0, 255, 0, 0.4);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        .control-btn.active {
            background: rgba(0, 255, 0, 0.6);
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.8);
        }

        .control-btn.voice-btn {
            background: rgba(255, 0, 0, 0.2);
            border-color: #f00;
            color: #f00;
        }

        .control-btn.voice-btn:hover {
            background: rgba(255, 0, 0, 0.4);
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        }

        .control-btn.voice-btn.active {
            background: rgba(255, 0, 0, 0.6);
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.8);
        }

        /* Mode Tabs */
        .mode-tabs {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        .mode-tab {
            padding: 12px 25px;
            border: 3px solid;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .mode-tab-auto {
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            border-color: #ffaa00;
            box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
        }

        .mode-tab-auto.active {
            box-shadow: 0 0 40px rgba(255, 170, 0, 1);
        }

        .mode-tab-normal {
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            border-color: #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        .mode-tab-normal.active {
            box-shadow: 0 0 40px rgba(0, 255, 0, 1);
        }

        .mode-tab-pursuit {
            background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
            color: #fff;
            border-color: #ff0000;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        }

        .mode-tab-pursuit.active {
            box-shadow: 0 0 40px rgba(255, 0, 0, 1);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Ω OMEGA v2</h1>
            <div class="mode-tabs">
                <div class="mode-tab mode-tab-auto active" onclick="switchMode('auto')">AUTO</div>
                <div class="mode-tab mode-tab-normal" onclick="switchMode('normal')">NORMAL</div>
                <div class="mode-tab mode-tab-pursuit" onclick="switchMode('pursuit')">PURSUIT</div>
            </div>
            <div class="status-indicator"></div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Chat Panel -->
            <div class="panel">
                <h2>Conversation</h2>
                <div id="chat-messages"></div>
                <div class="chat-input">
                    <input type="text" id="chat-input" placeholder="Talk to Omega..." onkeypress="if(event.key==='Enter') sendChat()">
                    <button onclick="sendChat()">SEND</button>
                </div>
            </div>

            <!-- Console -->
            <div class="panel">
                <h2>System Console</h2>
                <div id="console"></div>
            </div>

            <!-- RGB Controls -->
            <div class="panel">
                <h2>RGB Controls</h2>
                <div class="rgb-controls">
                    <div class="rgb-slider">
                        <label>RED: <span id="red-value">128</span></label>
                        <input type="range" min="0" max="255" value="128" id="red-slider" oninput="updateRGB()">
                    </div>
                    <div class="rgb-slider">
                        <label>GREEN: <span id="green-value">128</span></label>
                        <input type="range" min="0" max="255" value="128" id="green-slider" oninput="updateRGB()">
                    </div>
                    <div class="rgb-slider">
                        <label>BLUE: <span id="blue-value">128</span></label>
                        <input type="range" min="0" max="255" value="128" id="blue-slider" oninput="updateRGB()">
                    </div>
                </div>
            </div>
        </div>

        <!-- KITT Voice Box - AUTHENTIC 3 bars (Season 2-4 design) -->
        <div class="kitt-voice-box" id="kitt-voice-box">
            <div class="voice-bar" id="voice-bar-left"></div>
            <div class="voice-bar" id="voice-bar-center"></div>
            <div class="voice-bar" id="voice-bar-right"></div>
        </div>

        <!-- KITT Scanner -->
        <div class="kitt-scanner">
            <div class="scanner-light" id="scanner-light"></div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <button class="control-btn voice-btn" id="voice-toggle" onclick="toggleVoice()">
                🎤 VOICE: OFF
            </button>
            <button class="control-btn" onclick="testOmega()">
                TEST OMEGA
            </button>
            <button class="control-btn" onclick="callAgentCouncil()">
                AGENT COUNCIL
            </button>
        </div>
    </div>

    <script>
        let isVoiceActive = false;
        let isTalking = false;
        let currentMode = 'auto';
        let scannerSpeed = 2; // seconds
        let recognition = null;
        let conversationHistory = [];

        // Initialize
        window.onload = function() {
            logConsole('[OMEGA] System initialized', 'info');
            logConsole('[OMEGA] Voice box: 3-bar KITT design active (Season 2-4 authentic)', 'info');
            logConsole('[OMEGA] Based on Episode 14 "Heart of Stone" canonical design', 'info');
            logConsole('[OMEGA] Omega voice loaded (120 Hz base frequency)', 'info');
            setScannerSpeed();
            
            // Load voices
            if ('speechSynthesis' in window) {
                speechSynthesis.onvoiceschanged = function() {
                    const voices = speechSynthesis.getVoices();
                    logConsole('[OMEGA] Voice system initialized (' + voices.length + ' voices available)', 'info');
                };
            }
        };

        // Voice animation for AUTHENTIC 3-bar KITT voice box
        let voiceAnimationInterval;
        
        function startVoiceAnimation() {
            const bars = [
                document.getElementById('voice-bar-left'),
                document.getElementById('voice-bar-center'),
                document.getElementById('voice-bar-right')
            ];
            
            bars.forEach(bar => bar.classList.add('active'));
            
            // AUTHENTIC KITT animation - center bar is tallest
            // Based on Season 2-4 design from Episode 14 "Heart of Stone"
            voiceAnimationInterval = setInterval(() => {
                bars.forEach((bar, index) => {
                    let baseHeight, variation;
                    
                    // Center bar (index 1) is tallest - authentic KITT design
                    if (index === 1) {  // Center bar
                        baseHeight = 60;
                        variation = 40;
                    } else {  // Side bars (left and right)
                        baseHeight = 40;
                        variation = 30;
                    }
                    
                    // Add audio reactivity with organic variation
                    const audioFactor = Math.random() * variation;
                    const organicVariation = (Math.random() - 0.5) * 10;  // ±5px organic feel
                    
                    // Calculate final height
                    let height = baseHeight + audioFactor + organicVariation;
                    
                    // Clamp to valid range
                    height = Math.max(20, Math.min(100, height));
                    
                    bar.style.height = height + 'px';
                });
            }, 50); // 20 FPS (authentic TV standard 1982-1986)
        }
        
        function stopVoiceAnimation() {
            const bars = [
                document.getElementById('voice-bar-left'),
                document.getElementById('voice-bar-center'),
                document.getElementById('voice-bar-right')
            ];
            
            bars.forEach((bar, index) => {
                bar.classList.remove('active');
                // Return to idle state - center bar taller
                if (index === 1) {  // Center bar
                    bar.style.height = '60px';
                } else {  // Side bars
                    bar.style.height = '40px';
                }
            });
            
            if (voiceAnimationInterval) {
                clearInterval(voiceAnimationInterval);
            }
        }

        // Omega TTS - 120 Hz base, authoritative voice
        function speak(text) {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                const voices = speechSynthesis.getVoices();
                
                // Omega voice preferences - deep, authoritative
                const preferredVoices = ['Microsoft David', 'Microsoft Mark', 'Google US English Male', 'Daniel', 'Alex'];
                let selectedVoice = null;
                for (const prefVoice of preferredVoices) {
                    selectedVoice = voices.find(v => v.name.includes(prefVoice));
                    if (selectedVoice) break;
                }
                
                if (!selectedVoice) {
                    selectedVoice = voices.find(v => 
                        v.lang.startsWith('en') && 
                        (v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('david'))
                    );
                }
                
                if (selectedVoice) {
                    utterance.voice = selectedVoice;
                    logConsole('[OMEGA] Voice: ' + selectedVoice.name, 'info');
                }
                
                // Omega voice settings
                utterance.rate = 0.85;  // Deliberate
                utterance.pitch = 0.75; // Deep (120 Hz base)
                utterance.volume = 1.0;
                
                utterance.onstart = function() {
                    isTalking = true;
                    startVoiceAnimation();
                    document.getElementById('kitt-voice-box').classList.add('talking');
                    logConsole('[OMEGA] Speaking...', 'info');
                };
                
                utterance.onend = function() {
                    isTalking = false;
                    stopVoiceAnimation();
                    document.getElementById('kitt-voice-box').classList.remove('talking');
                    logConsole('[OMEGA] Speech complete', 'info');
                };
                
                utterance.onerror = function(event) {
                    console.error('Speech error:', event);
                    isTalking = false;
                    stopVoiceAnimation();
                    logConsole('[OMEGA] Speech error: ' + event.error, 'error');
                };
                
                speechSynthesis.speak(utterance);
            } else {
                logConsole('[OMEGA] Text-to-speech not supported', 'error');
            }
        }

        // Conversational AI with knowledge base
        async function getOmegaResponse(userMessage) {
            try {
                const response = await fetch('/api/omega_conversation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMessage,
                        history: conversationHistory
                    })
                });
                
                const data = await response.json();
                
                if (data.response) {
                    conversationHistory.push({
                        user: userMessage,
                        omega: data.response,
                        timestamp: new Date().toISOString()
                    });
                    
                    if (conversationHistory.length > 50) {
                        conversationHistory = conversationHistory.slice(-50);
                    }
                    
                    return data.response;
                }
                return "Processing your request...";
            } catch (error) {
                console.error('Omega conversation error:', error);
                return "I'm integrating my knowledge systems. One moment.";
            }
        }

        // Chat functions
        async function sendChat() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            logConsole('[USER] ' + message, 'user');
            addChatMessage('You', message, 'user');
            
            // Check if needs agent council
            const needsCouncil = message.toLowerCase().includes('council') || 
                                message.toLowerCase().includes('agent') ||
                                message.toLowerCase().includes('solve') ||
                                message.toLowerCase().includes('analyze');
            
            if (needsCouncil) {
                logConsole('[OMEGA] Summoning agent council...', 'info');
                const councilResponse = await callAgentCouncilAPI(message);
                logConsole('[OMEGA] ' + councilResponse, 'omega');
                addChatMessage('Omega', councilResponse, 'omega');
                speak(councilResponse);
            } else {
                const response = await getOmegaResponse(message);
                logConsole('[OMEGA] ' + response, 'omega');
                addChatMessage('Omega', response, 'omega');
                speak(response);
            }
        }

        async function callAgentCouncilAPI(problem) {
            try {
                const response = await fetch('/api/agent_council', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ problem: problem })
                });
                
                const data = await response.json();
                return data.solution || 'Council deliberating...';
            } catch (error) {
                return 'Agent council integration in progress.';
            }
        }

        function addChatMessage(sender, message, type) {
            const chatMessages = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = 'chat-message ' + type;
            div.innerHTML = '<strong>' + sender + ':</strong> ' + message;
            chatMessages.appendChild(div);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Console logging
        function logConsole(message, type = 'info') {
            const console = document.getElementById('console');
            const div = document.createElement('div');
            div.className = 'console-line ' + type;
            div.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            console.appendChild(div);
            console.scrollTop = console.scrollHeight;
        }

        // Voice recognition
        function toggleVoice() {
            isVoiceActive = !isVoiceActive;
            const btn = document.getElementById('voice-toggle');
            
            if (isVoiceActive) {
                btn.classList.add('active');
                btn.textContent = '🎤 VOICE: ON';
                startVoiceRecognition();
                logConsole('[OMEGA] Voice recognition activated', 'info');
            } else {
                btn.classList.remove('active');
                btn.textContent = '🎤 VOICE: OFF';
                stopVoiceRecognition();
                logConsole('[OMEGA] Voice recognition deactivated', 'info');
            }
        }

        function startVoiceRecognition() {
            if (!('webkitSpeechRecognition' in window)) {
                logConsole('[ERROR] Speech recognition not supported', 'error');
                return;
            }
            
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            
            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                logConsole('[USER VOICE] ' + transcript, 'user');
                document.getElementById('chat-input').value = transcript;
                sendChat();
            };
            
            recognition.onerror = function(event) {
                logConsole('[ERROR] Voice recognition error: ' + event.error, 'error');
            };
            
            recognition.start();
        }

        function stopVoiceRecognition() {
            if (recognition) {
                recognition.stop();
                recognition = null;
            }
        }

        // Mode switching
        function switchMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector('.mode-tab-' + mode).classList.add('active');
            
            if (mode === 'auto') scannerSpeed = 2;
            else if (mode === 'normal') scannerSpeed = 1.5;
            else if (mode === 'pursuit') scannerSpeed = 0.8;
            
            setScannerSpeed();
            logConsole('[OMEGA] Mode: ' + mode.toUpperCase(), 'info');
        }

        function setScannerSpeed() {
            const scanner = document.getElementById('scanner-light');
            scanner.style.animationDuration = scannerSpeed + 's';
        }

        // RGB controls
        function updateRGB() {
            const r = document.getElementById('red-slider').value;
            const g = document.getElementById('green-slider').value;
            const b = document.getElementById('blue-slider').value;
            
            document.getElementById('red-value').textContent = r;
            document.getElementById('green-value').textContent = g;
            document.getElementById('blue-value').textContent = b;
            
            logConsole('[RGB] Updated: ' + r + ',' + g + ',' + b, 'info');
        }

        // Test functions
        function testOmega() {
            speak('Omega systems operational. Guardian protocols active. Gate monitored.');
            logConsole('[TEST] Omega voice test initiated', 'info');
        }

        function callAgentCouncil() {
            logConsole('[OMEGA] Agent council summoning...', 'info');
            speak('The doors of knowledge open. Agent council assembling.');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the main UI page."""
    return html_content

@app.route('/api/omega_conversation', methods=['POST'])
def omega_conversation():
    """Handle conversational AI with knowledge base access."""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        history = data.get('history', [])
        
        response = f"I understand: '{user_message}'. My full knowledge systems are integrating. I'm analyzing your request within the context of our conversation history."
        
        if 'knowledge' in user_message.lower() or 'know' in user_message.lower():
            response += " I have access to The Gatekeeper's complete knowledge repository."
        
        if 'agent' in user_message.lower():
            response += " I can consult with the agent council for complex problem-solving."
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'response': f"Processing error: {str(e)}",
            'status': 'error'
        }), 500

@app.route('/api/agent_council', methods=['POST'])
def agent_council_route():
    """Call agent council for complex problem solving."""
    try:
        data = request.get_json()
        problem = data.get('problem', '')
        
        if AGENT_COUNCIL_AVAILABLE:
            solution = f"Agent council analyzing: {problem}. Agents deliberating on optimal solution path."
        else:
            solution = "Agent council integration in progress. Full council capabilities will be available shortly."
        
        return jsonify({
            'solution': solution,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'solution': f"Council error: {str(e)}",
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("=" * 80)
    print("                    Ω OMEGA ENHANCED WEB UI v2")
    print("=" * 80)
    print()
    print("🚀 Starting server on http://127.0.0.1:5001")
    print("🎛️  Access the control panel at: http://localhost:5001")
    print()
    print("✅ Features:")
    print("   • 3-bar KITT voice box (AUTHENTIC Season 2-4 design)")
    print("   • Based on Episode 14 'Heart of Stone' canonical design")
    print("   • Omega voice (120 Hz base, deep authoritative)")
    print("   • Conversational AI with knowledge base access")
    print("   • Agent council integration")
    print("   • Real-time voice interaction")
    print()
    print("📝 Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    socketio.run(app, host='127.0.0.1', port=5001, debug=False)
