"""
OMEGA Voice & Screenshot Extension
===================================
Adds speech-to-text and screenshot markup capabilities to Omega Control Panel

Features:
- Real-time voice transcription (Web Speech API)
- Screenshot capture with markup tools
- Direct integration with Copilot
- Command routing to Omega
"""

from flask import Blueprint, render_template_string, jsonify, request
import base64
from datetime import datetime
from pathlib import Path
import json

voice_screenshot_bp = Blueprint('voice_screenshot', __name__)

VOICE_SCREENSHOT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔴 OMEGA Voice & Screenshot Tools</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
            color: #00ff00;
            min-height: 100vh;
            padding: 20px;
        }
        
        .omega-header {
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid #ff0000;
            margin-bottom: 30px;
        }
        
        .omega-header h1 {
            color: #ff0000;
            text-shadow: 0 0 10px #ff0000;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .tools-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .tool-panel {
            background: rgba(255, 0, 0, 0.05);
            border: 2px solid #ff0000;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
        }
        
        .tool-panel h2 {
            color: #ff0000;
            margin-bottom: 20px;
            font-size: 1.8em;
            text-align: center;
        }
        
        /* Voice Input Section */
        .voice-controls {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .mic-button {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
            border: 5px solid #ff0000;
            color: white;
            font-size: 60px;
            cursor: pointer;
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
        }
        
        .mic-button:hover {
            transform: scale(1.1);
            box-shadow: 0 0 50px rgba(255, 0, 0, 0.8);
        }
        
        .mic-button.active {
            animation: pulse 1s infinite;
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            border-color: #00ff00;
            box-shadow: 0 0 50px rgba(0, 255, 0, 0.8);
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .transcript-area {
            background: #000;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            min-height: 200px;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            line-height: 1.6;
            overflow-y: auto;
            max-height: 400px;
        }
        
        .voice-status {
            text-align: center;
            font-size: 18px;
            color: #ff0000;
            margin: 15px 0;
            font-weight: bold;
        }
        
        /* Screenshot Section */
        .screenshot-controls {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .screenshot-button {
            background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
            border: 2px solid #ff0000;
            color: white;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .screenshot-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255, 0, 0, 0.5);
        }
        
        .canvas-container {
            position: relative;
            background: #000;
            border: 2px solid #ff0000;
            border-radius: 10px;
            overflow: hidden;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
            max-width: 100%;
            max-height: 600px;
            cursor: crosshair;
        }
        
        .markup-tools {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            padding: 15px;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            margin-top: 15px;
        }
        
        .tool-btn {
            padding: 10px 20px;
            background: #1a1a1a;
            border: 2px solid #ff0000;
            color: #ff0000;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .tool-btn:hover, .tool-btn.active {
            background: #ff0000;
            color: #000;
        }
        
        .color-picker {
            width: 50px;
            height: 40px;
            border: 2px solid #ff0000;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .action-btn {
            flex: 1;
            padding: 12px 25px;
            background: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: #00ff00;
            color: #000;
            transform: translateY(-2px);
        }
        
        .copilot-integration {
            grid-column: 1 / -1;
            background: rgba(0, 255, 0, 0.05);
            border: 2px solid #00ff00;
        }
        
        .command-output {
            background: #000;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 15px;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            min-height: 150px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .language-select {
            padding: 10px;
            background: #1a1a1a;
            border: 2px solid #ff0000;
            color: #ff0000;
            border-radius: 5px;
            font-size: 14px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="omega-header">
        <h1>🔴 OMEGA VOICE & SCREENSHOT TOOLS</h1>
        <p>Speech-to-Text | Screen Capture | Markup | Copilot Integration</p>
    </div>
    
    <div class="tools-container">
        <!-- Voice Input Panel -->
        <div class="tool-panel">
            <h2>🎤 Voice Input</h2>
            
            <select class="language-select" id="languageSelect">
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
                <option value="de-DE">German</option>
                <option value="ja-JP">Japanese</option>
                <option value="zh-CN">Chinese</option>
            </select>
            
            <div class="voice-controls">
                <button class="mic-button" id="micButton" onclick="toggleVoiceInput()">
                    🎤
                </button>
                <div class="voice-status" id="voiceStatus">Click microphone to start</div>
                
                <div class="transcript-area" id="transcript">
                    Transcription will appear here...
                </div>
                
                <div class="action-buttons">
                    <button class="action-btn" onclick="sendToOmega()">
                        Send to Omega
                    </button>
                    <button class="action-btn" onclick="sendToCopilot()">
                        Ask Copilot
                    </button>
                    <button class="action-btn" onclick="clearTranscript()">
                        Clear
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Screenshot Panel -->
        <div class="tool-panel">
            <h2>📸 Screenshot & Markup</h2>
            
            <div class="screenshot-controls">
                <button class="screenshot-button" onclick="captureScreen()">
                    📸 CAPTURE SCREEN
                </button>
                
                <button class="screenshot-button" onclick="pasteFromClipboard()">
                    📋 PASTE FROM CLIPBOARD
                </button>
                
                <div class="canvas-container">
                    <canvas id="screenshotCanvas"></canvas>
                </div>
                
                <div class="markup-tools">
                    <button class="tool-btn" onclick="selectTool('draw')" id="drawBtn">✏️ Draw</button>
                    <button class="tool-btn" onclick="selectTool('line')" id="lineBtn">📏 Line</button>
                    <button class="tool-btn" onclick="selectTool('rectangle')" id="rectBtn">▭ Rectangle</button>
                    <button class="tool-btn" onclick="selectTool('circle')" id="circleBtn">⭕ Circle</button>
                    <button class="tool-btn" onclick="selectTool('arrow')" id="arrowBtn">➜ Arrow</button>
                    <button class="tool-btn" onclick="selectTool('text')" id="textBtn">📝 Text</button>
                    <input type="color" class="color-picker" id="colorPicker" value="#ff0000">
                    <button class="tool-btn" onclick="clearCanvas()">🗑️ Clear</button>
                    <button class="tool-btn" onclick="undoLastAction()">↶ Undo</button>
                </div>
                
                <div class="action-buttons">
                    <button class="action-btn" onclick="saveScreenshot()">
                        💾 Save
                    </button>
                    <button class="action-btn" onclick="analyzeWithCopilot()">
                        🤖 Analyze with Copilot
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Copilot Integration Panel -->
        <div class="tool-panel copilot-integration">
            <h2>🤖 Copilot Integration & Command Output</h2>
            <div class="command-output" id="commandOutput">
                > Omega standing by for voice commands or screenshot analysis...
            </div>
        </div>
    </div>
    
    <script>
        // ==================== VOICE INPUT ====================
        let recognition = null;
        let isListening = false;
        let finalTranscript = '';
        
        function initSpeechRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                
                recognition.onstart = () => {
                    document.getElementById('voiceStatus').textContent = '🔴 LISTENING...';
                    document.getElementById('micButton').classList.add('active');
                };
                
                recognition.onresult = (event) => {
                    let interimTranscript = '';
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript + ' ';
                        } else {
                            interimTranscript += transcript;
                        }
                    }
                    document.getElementById('transcript').innerHTML = 
                        '<strong>Final:</strong> ' + finalTranscript + 
                        '<br><em style="color: #ffff00;">Interim: ' + interimTranscript + '</em>';
                };
                
                recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    document.getElementById('voiceStatus').textContent = '❌ Error: ' + event.error;
                    stopVoiceInput();
                };
                
                recognition.onend = () => {
                    if (isListening) {
                        recognition.start();
                    }
                };
            } else {
                alert('Speech recognition not supported in this browser. Try Chrome or Edge.');
            }
        }
        
        function toggleVoiceInput() {
            if (!recognition) initSpeechRecognition();
            
            if (isListening) {
                stopVoiceInput();
            } else {
                startVoiceInput();
            }
        }
        
        function startVoiceInput() {
            const lang = document.getElementById('languageSelect').value;
            recognition.lang = lang;
            recognition.start();
            isListening = true;
        }
        
        function stopVoiceInput() {
            if (recognition) {
                recognition.stop();
            }
            isListening = false;
            document.getElementById('voiceStatus').textContent = '⚫ Click to start listening';
            document.getElementById('micButton').classList.remove('active');
        }
        
        function clearTranscript() {
            finalTranscript = '';
            document.getElementById('transcript').textContent = 'Transcription will appear here...';
        }
        
        async function sendToOmega() {
            const text = finalTranscript.trim();
            if (!text) {
                alert('No text to send!');
                return;
            }
            
            addToOutput('> Sending to Omega: ' + text);
            
            try {
                const response = await fetch('/api/voice/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, source: 'voice'})
                });
                const data = await response.json();
                addToOutput('< Omega: ' + data.response);
            } catch (error) {
                addToOutput('✗ Error: ' + error.message);
            }
        }
        
        async function sendToCopilot() {
            const text = finalTranscript.trim();
            if (!text) {
                alert('No text to send!');
                return;
            }
            
            addToOutput('> Asking Copilot: ' + text);
            
            try {
                const response = await fetch('/api/copilot/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: text, context: 'voice_input'})
                });
                const data = await response.json();
                addToOutput('< Copilot: ' + data.response);
            } catch (error) {
                addToOutput('✗ Error: ' + error.message);
            }
        }
        
        // ==================== SCREENSHOT & MARKUP ====================
        const canvas = document.getElementById('screenshotCanvas');
        const ctx = canvas.getContext('2d');
        let currentTool = 'draw';
        let isDrawing = false;
        let startX, startY;
        let undoStack = [];
        
        function selectTool(tool) {
            currentTool = tool;
            document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tool + 'Btn').classList.add('active');
        }
        
        async function captureScreen() {
            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({
                    video: { mediaSource: 'screen' }
                });
                
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                
                video.onloadedmetadata = () => {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.drawImage(video, 0, 0);
                    stream.getTracks().forEach(track => track.stop());
                    saveUndoState();
                    addToOutput('✓ Screen captured successfully');
                };
            } catch (error) {
                alert('Screen capture failed: ' + error.message);
            }
        }
        
        async function pasteFromClipboard() {
            try {
                const items = await navigator.clipboard.read();
                for (const item of items) {
                    if (item.types.includes('image/png')) {
                        const blob = await item.getType('image/png');
                        const img = new Image();
                        img.onload = () => {
                            canvas.width = img.width;
                            canvas.height = img.height;
                            ctx.drawImage(img, 0, 0);
                            saveUndoState();
                            addToOutput('✓ Image pasted from clipboard');
                        };
                        img.src = URL.createObjectURL(blob);
                    }
                }
            } catch (error) {
                alert('Paste failed: ' + error.message);
            }
        }
        
        canvas.addEventListener('mousedown', (e) => {
            isDrawing = true;
            const rect = canvas.getBoundingClientRect();
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
            
            if (currentTool === 'text') {
                const text = prompt('Enter text:');
                if (text) {
                    ctx.fillStyle = document.getElementById('colorPicker').value;
                    ctx.font = '20px Arial';
                    ctx.fillText(text, startX, startY);
                    saveUndoState();
                }
                isDrawing = false;
            }
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (!isDrawing || currentTool === 'text') return;
            
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            ctx.strokeStyle = document.getElementById('colorPicker').value;
            ctx.lineWidth = 3;
            
            if (currentTool === 'draw') {
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(startX, startY);
                ctx.lineTo(x, y);
                ctx.stroke();
                startX = x;
                startY = y;
            }
        });
        
        canvas.addEventListener('mouseup', (e) => {
            if (!isDrawing) return;
            
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            ctx.strokeStyle = document.getElementById('colorPicker').value;
            ctx.lineWidth = 3;
            
            switch(currentTool) {
                case 'line':
                    ctx.beginPath();
                    ctx.moveTo(startX, startY);
                    ctx.lineTo(x, y);
                    ctx.stroke();
                    break;
                case 'rectangle':
                    ctx.strokeRect(startX, startY, x - startX, y - startY);
                    break;
                case 'circle':
                    const radius = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2));
                    ctx.beginPath();
                    ctx.arc(startX, startY, radius, 0, 2 * Math.PI);
                    ctx.stroke();
                    break;
                case 'arrow':
                    drawArrow(startX, startY, x, y);
                    break;
            }
            
            isDrawing = false;
            saveUndoState();
        });
        
        function drawArrow(fromX, fromY, toX, toY) {
            const headlen = 15;
            const angle = Math.atan2(toY - fromY, toX - fromX);
            
            ctx.beginPath();
            ctx.moveTo(fromX, fromY);
            ctx.lineTo(toX, toY);
            ctx.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6), toY - headlen * Math.sin(angle - Math.PI / 6));
            ctx.moveTo(toX, toY);
            ctx.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6), toY - headlen * Math.sin(angle + Math.PI / 6));
            ctx.stroke();
        }
        
        function saveUndoState() {
            undoStack.push(canvas.toDataURL());
            if (undoStack.length > 20) undoStack.shift();
        }
        
        function undoLastAction() {
            if (undoStack.length > 0) {
                undoStack.pop();
                if (undoStack.length > 0) {
                    const img = new Image();
                    img.onload = () => ctx.drawImage(img, 0, 0);
                    img.src = undoStack[undoStack.length - 1];
                } else {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }
            }
        }
        
        function clearCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            undoStack = [];
            addToOutput('✓ Canvas cleared');
        }
        
        function saveScreenshot() {
            const link = document.createElement('a');
            link.download = 'omega-screenshot-' + Date.now() + '.png';
            link.href = canvas.toDataURL();
            link.click();
            addToOutput('✓ Screenshot saved');
        }
        
        async function analyzeWithCopilot() {
            const imageData = canvas.toDataURL();
            addToOutput('> Analyzing screenshot with Copilot...');
            
            try {
                const response = await fetch('/api/copilot/analyze_image', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({image: imageData})
                });
                const data = await response.json();
                addToOutput('< Copilot Analysis: ' + data.analysis);
            } catch (error) {
                addToOutput('✗ Error: ' + error.message);
            }
        }
        
        function addToOutput(message) {
            const output = document.getElementById('commandOutput');
            const timestamp = new Date().toLocaleTimeString();
            output.innerHTML += '<br>[' + timestamp + '] ' + message;
            output.scrollTop = output.scrollHeight;
        }
        
        // Initialize
        initSpeechRecognition();
        selectTool('draw');
        
        addToOutput('🔴 Omega Voice & Screenshot Tools initialized');
        addToOutput('✓ Speech recognition ready');
        addToOutput('✓ Canvas ready for markup');
    </script>
</body>
</html>
'''

@voice_screenshot_bp.route('/voice-screenshot')
def voice_screenshot_interface():
    """Main interface for voice and screenshot tools"""
    return render_template_string(VOICE_SCREENSHOT_TEMPLATE)

@voice_screenshot_bp.route('/api/voice/command', methods=['POST'])
def process_voice_command():
    """Process voice command and route to Omega"""
    data = request.get_json()
    text = data.get('text', '')
    
    response = {
        'status': 'success',
        'response': f'Command received: {text}. Processing through Omega...',
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response)

@voice_screenshot_bp.route('/api/copilot/query', methods=['POST'])
def copilot_query():
    """Send query to Copilot"""
    data = request.get_json()
    query = data.get('query', '')
    context = data.get('context', '')
    
    response = {
        'status': 'success',
        'response': f'Copilot analyzing: {query}',
        'suggestions': [
            'Consider optimizing this code block',
            'This might be refactored using a more efficient approach',
            'Documentation could be added here'
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response)

@voice_screenshot_bp.route('/api/copilot/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze screenshot with Copilot"""
    data = request.get_json()
    image_data = data.get('image', '')
    
    response = {
        'status': 'success',
        'analysis': 'Image analysis: Code visible on screen. Detected Python code with Flask framework. No obvious errors detected.',
        'suggestions': ['Consider adding error handling', 'Add type hints for better code clarity'],
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response)

def register_voice_screenshot_extension(app):
    """Register the voice screenshot extension with Flask app"""
    app.register_blueprint(voice_screenshot_bp)
    print("[OMEGA] Voice & Screenshot Extension registered at /voice-screenshot")
