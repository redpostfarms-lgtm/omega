#!/usr/bin/env python3
"""
Omega Enhanced Web UI
=====================
Modern, feature-rich web interface for Omega Control Panel
Based on Control Panel UI Design specifications

Features:
- 1980s/90s sci-fi aesthetic with modern responsive design
- Real-time monitoring and controls
- Voice interaction support
- Audio visualization
- System status dashboard
- Dark theme with glowing elements
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

# Setup paths
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega_enhanced_ui_secret_2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Template with 1980s/90s Sci-Fi Aesthetic
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω OMEGA Control Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Header with Omega Logo */
        .header {
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border-bottom: 3px solid #ffd700;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
        }

        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
        }

        .omega-logo {
            width: 80px;
            height: 80px;
            filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5));
        }

        h1 {
            font-size: 3em;
            color: #ff0000;
            text-shadow: 0 0 20px rgba(255, 0, 0, 0.8), 0 0 40px rgba(255, 0, 0, 0.4);
            letter-spacing: 10px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        .subtitle {
            color: #ffd700;
            font-size: 1.2em;
            margin-top: 10px;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
        }

        /* Main Container */
        .container {
            max-width: 1600px;
            margin: 30px auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 20px;
        }

        /* Panel Base Style */
        .panel {
            background: rgba(10, 10, 20, 0.9);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }

        .panel-title {
            color: #00ffff;
            font-size: 1.3em;
            margin-bottom: 15px;
            text-transform: uppercase;
            border-bottom: 2px solid #00ffff;
            padding-bottom: 10px;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }

        /* Audio Visualizer Display */
        .audio-display {
            background: #000;
            border: 3px solid #ff0000;
            border-radius: 5px;
            height: 200px;
            margin-bottom: 20px;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            padding: 10px;
            box-shadow: inset 0 0 20px rgba(255, 0, 0, 0.3);
        }

        .audio-bar {
            width: 8px;
            background: linear-gradient(180deg, #ff0000 0%, #ff6600 50%, #ffff00 100%);
            border-radius: 2px;
            transition: height 0.1s ease;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        }

        /* Control Buttons - Sci-Fi Style */
        .control-buttons {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 20px 0;
        }

        .btn {
            padding: 15px 30px;
            font-size: 1.2em;
            font-weight: bold;
            text-transform: uppercase;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .btn:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s;
        }

        .btn:hover:before {
            left: 100%;
        }

        .btn-auto-cruise {
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
        }

        .btn-auto-cruise:hover {
            box-shadow: 0 0 30px rgba(255, 170, 0, 0.8);
            transform: scale(1.05);
        }

        .btn-auto-cruise.active {
            box-shadow: 0 0 40px rgba(255, 170, 0, 1);
            animation: glow-yellow 1s ease-in-out infinite;
        }

        .btn-normal-cruise {
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        .btn-normal-cruise:hover {
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.8);
            transform: scale(1.05);
        }

        .btn-normal-cruise.active {
            box-shadow: 0 0 40px rgba(0, 255, 0, 1);
            animation: glow-green 1s ease-in-out infinite;
        }

        .btn-pursuit {
            background: linear-gradient(135deg, #00aaff 0%, #0088ff 100%);
            color: #fff;
            box-shadow: 0 0 20px rgba(0, 170, 255, 0.5);
        }

        .btn-pursuit:hover {
            box-shadow: 0 0 30px rgba(0, 170, 255, 0.8);
            transform: scale(1.05);
        }

        .btn-pursuit.active {
            box-shadow: 0 0 40px rgba(0, 170, 255, 1);
            animation: glow-blue 1s ease-in-out infinite;
        }

        /* Glow Animations */
        @keyframes glow-yellow {
            0%, 100% { box-shadow: 0 0 40px rgba(255, 170, 0, 1); }
            50% { box-shadow: 0 0 60px rgba(255, 170, 0, 1), 0 0 80px rgba(255, 170, 0, 0.5); }
        }

        @keyframes glow-green {
            0%, 100% { box-shadow: 0 0 40px rgba(0, 255, 0, 1); }
            50% { box-shadow: 0 0 60px rgba(0, 255, 0, 1), 0 0 80px rgba(0, 255, 0, 0.5); }
        }

        @keyframes glow-blue {
            0%, 100% { box-shadow: 0 0 40px rgba(0, 170, 255, 1); }
            50% { box-shadow: 0 0 60px rgba(0, 170, 255, 1), 0 0 80px rgba(0, 170, 255, 0.5); }
        }

        /* Side Control Buttons */
        .side-controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }

        .side-btn {
            padding: 12px;
            font-size: 0.9em;
            font-weight: bold;
            border: 2px solid;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        .side-btn-pink {
            background: rgba(255, 20, 147, 0.2);
            border-color: #ff1493;
            color: #ff1493;
        }

        .side-btn-pink:hover {
            background: rgba(255, 20, 147, 0.4);
            box-shadow: 0 0 15px rgba(255, 20, 147, 0.5);
        }

        .side-btn-red {
            background: rgba(255, 0, 0, 0.2);
            border-color: #ff0000;
            color: #ff0000;
        }

        .side-btn-red:hover {
            background: rgba(255, 0, 0, 0.4);
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        }

        .side-btn-blue {
            background: rgba(0, 170, 255, 0.2);
            border-color: #00aaff;
            color: #00aaff;
        }

        .side-btn-blue:hover {
            background: rgba(0, 170, 255, 0.4);
            box-shadow: 0 0 15px rgba(0, 170, 255, 0.5);
        }

        /* Status Indicators */
        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }

        .status-item {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ffff;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
        }

        .status-label {
            font-size: 0.9em;
            color: #00ffff;
            margin-bottom: 8px;
        }

        .status-value {
            font-size: 1.5em;
            color: #00ff00;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }

        .status-value.warning {
            color: #ffaa00;
        }

        .status-value.error {
            color: #ff0000;
        }

        /* Console Output */
        .console {
            background: #000;
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-size: 0.9em;
            box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.1);
        }

        .console-line {
            color: #00ff00;
            margin-bottom: 5px;
            text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }

        .console-line.error {
            color: #ff0000;
        }

        .console-line.warning {
            color: #ffaa00;
        }

        .console-line.info {
            color: #00ffff;
        }

        /* Voice Control */
        .voice-control {
            margin-top: 20px;
            text-align: center;
        }

        .voice-btn {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: radial-gradient(circle, #ff0000 0%, #cc0000 100%);
            border: 4px solid #ffd700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-size: 2em;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        }

        .voice-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 40px rgba(255, 0, 0, 0.8);
        }

        .voice-btn.active {
            animation: voice-pulse 1s ease-in-out infinite;
            background: radial-gradient(circle, #00ff00 0%, #00cc00 100%);
        }

        @keyframes voice-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 1fr;
            }
        }

        /* Scan Lines Effect */
        body:before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 255, 0, 0.03) 0px,
                transparent 1px,
                transparent 2px,
                rgba(0, 255, 0, 0.03) 3px
            );
            pointer-events: none;
            z-index: 9999;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="logo-container">
            <img src="/images/omega_logo_red_gold_wreath.png" alt="Omega Logo" class="omega-logo">
            <div>
                <h1>Ω OMEGA</h1>
                <div class="subtitle">CONTROL PANEL SYSTEM</div>
            </div>
            <img src="/images/omega_logo_red_gold_wreath.png" alt="Omega Logo" class="omega-logo">
        </div>
    </div>

    <!-- Main Container -->
    <div class="container">
        <!-- Left Panel: System Status -->
        <div class="panel">
            <div class="panel-title">⚡ System Status</div>
            
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-label">CPU</div>
                    <div class="status-value" id="cpu-status">--</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Memory</div>
                    <div class="status-value" id="memory-status">--</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Disk</div>
                    <div class="status-value" id="disk-status">--</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Network</div>
                    <div class="status-value" id="network-status">ONLINE</div>
                </div>
            </div>

            <!-- Side Controls (Left) -->
            <div class="side-controls" style="margin-top: 30px;">
                <button class="side-btn side-btn-blue" onclick="handleSideControl('AIR')">AIR</button>
                <button class="side-btn side-btn-blue" onclick="handleSideControl('OIL')">OIL</button>
                <button class="side-btn side-btn-pink" onclick="handleSideControl('P1')">P1</button>
                <button class="side-btn side-btn-pink" onclick="handleSideControl('P2')">P2</button>
            </div>
        </div>

        <!-- Center Panel: Main Controls -->
        <div class="panel">
            <div class="panel-title">🎛️ Main Control Interface</div>
            
            <!-- Audio Visualizer -->
            <div class="audio-display" id="audio-display">
                <!-- Audio bars will be generated by JavaScript -->
            </div>

            <!-- Main Control Buttons -->
            <div class="control-buttons">
                <button class="btn btn-auto-cruise" id="btn-auto-cruise" onclick="handleMode('auto-cruise')">
                    🚀 AUTO CRUISE
                </button>
                <button class="btn btn-normal-cruise" id="btn-normal-cruise" onclick="handleMode('normal-cruise')">
                    ⚡ NORMAL CRUISE
                </button>
                <button class="btn btn-pursuit" id="btn-pursuit" onclick="handleMode('pursuit')">
                    🎯 PURSUIT MODE
                </button>
            </div>

            <!-- Voice Control -->
            <div class="voice-control">
                <div class="panel-title" style="font-size: 1em; margin-bottom: 10px;">Voice Control</div>
                <button class="voice-btn" id="voice-btn" onclick="toggleVoice()">
                    🎤
                </button>
                <div id="voice-status" style="margin-top: 10px; color: #00ffff;">Ready</div>
            </div>
        </div>

        <!-- Right Panel: Console & Controls -->
        <div class="panel">
            <div class="panel-title">📟 System Console</div>
            
            <!-- Console Output -->
            <div class="console" id="console">
                <div class="console-line info">[SYSTEM] Omega Control Panel initialized</div>
                <div class="console-line">[OK] All systems nominal</div>
                <div class="console-line info">[INFO] Awaiting commands...</div>
            </div>

            <!-- Side Controls (Right) -->
            <div class="side-controls">
                <button class="side-btn side-btn-blue" onclick="handleSideControl('S1')">S1</button>
                <button class="side-btn side-btn-blue" onclick="handleSideControl('S2')">S2</button>
                <button class="side-btn side-btn-red" onclick="handleSideControl('P3')">P3</button>
                <button class="side-btn side-btn-red" onclick="handleSideControl('P4')">P4</button>
            </div>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        // Initialize Socket.IO
        const socket = io();
        
        // Current mode
        let currentMode = null;
        let voiceActive = false;

        // Initialize audio visualizer bars
        const audioDisplay = document.getElementById('audio-display');
        const numBars = 30;
        for (let i = 0; i < numBars; i++) {
            const bar = document.createElement('div');
            bar.className = 'audio-bar';
            bar.style.height = '10px';
            audioDisplay.appendChild(bar);
        }

        // Animate audio visualizer
        function animateAudioBars() {
            const bars = document.querySelectorAll('.audio-bar');
            bars.forEach((bar, index) => {
                const randomHeight = Math.random() * 180 + 20;
                bar.style.height = randomHeight + 'px';
            });
        }

        // Start animation
        setInterval(animateAudioBars, 100);

        // Handle mode selection
        function handleMode(mode) {
            // Remove active class from all buttons
            document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            document.getElementById('btn-' + mode).classList.add('active');
            
            currentMode = mode;
            logConsole(`[MODE] ${mode.toUpperCase().replace('-', ' ')} activated`, 'info');
            
            // Emit to server
            socket.emit('mode_change', { mode: mode });
        }

        // Handle side controls
        function handleSideControl(control) {
            logConsole(`[CONTROL] ${control} activated`, 'warning');
            socket.emit('side_control', { control: control });
        }

        // Toggle voice control
        function toggleVoice() {
            const voiceBtn = document.getElementById('voice-btn');
            const voiceStatus = document.getElementById('voice-status');
            
            voiceActive = !voiceActive;
            
            if (voiceActive) {
                voiceBtn.classList.add('active');
                voiceStatus.textContent = 'Listening...';
                voiceStatus.style.color = '#00ff00';
                logConsole('[VOICE] Voice recognition activated', 'info');
                socket.emit('voice_control', { active: true });
            } else {
                voiceBtn.classList.remove('active');
                voiceStatus.textContent = 'Ready';
                voiceStatus.style.color = '#00ffff';
                logConsole('[VOICE] Voice recognition deactivated', 'info');
                socket.emit('voice_control', { active: false });
            }
        }

        // Log to console
        function logConsole(message, type = '') {
            const console = document.getElementById('console');
            const line = document.createElement('div');
            line.className = 'console-line ' + type;
            line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
            
            // Keep only last 50 lines
            const lines = console.querySelectorAll('.console-line');
            if (lines.length > 50) {
                lines[0].remove();
            }
        }

        // Update system status
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-status').textContent = data.cpu + '%';
                    document.getElementById('memory-status').textContent = data.memory + '%';
                    document.getElementById('disk-status').textContent = data.disk + '%';
                })
                .catch(error => console.error('Error fetching status:', error));
        }

        // Socket.IO event handlers
        socket.on('connect', () => {
            logConsole('[SOCKET] Connected to server', 'info');
        });

        socket.on('console_update', (data) => {
            logConsole(data.message, data.type || '');
        });

        socket.on('status_update', (data) => {
            if (data.cpu) document.getElementById('cpu-status').textContent = data.cpu + '%';
            if (data.memory) document.getElementById('memory-status').textContent = data.memory + '%';
            if (data.disk) document.getElementById('disk-status').textContent = data.disk + '%';
        });

        // Update status every 5 seconds
        setInterval(updateStatus, 5000);
        updateStatus();

        // Initialize
        logConsole('[INIT] Interface ready', 'info');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main UI page"""
    return HTML_TEMPLATE

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images"""
    return send_from_directory(IMAGES_DIR, filename)

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        return jsonify({
            'cpu': round(cpu, 1),
            'memory': round(memory, 1),
            'disk': round(disk, 1),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'error': str(e)
        })

@socketio.on('mode_change')
def handle_mode_change(data):
    """Handle mode change"""
    mode = data.get('mode')
    logger.info(f"Mode changed to: {mode}")
    emit('console_update', {
        'message': f'[SERVER] Mode changed to {mode.upper()}',
        'type': 'info'
    }, broadcast=True)

@socketio.on('side_control')
def handle_side_control(data):
    """Handle side control activation"""
    control = data.get('control')
    logger.info(f"Side control activated: {control}")
    emit('console_update', {
        'message': f'[SERVER] Control {control} processed',
        'type': 'warning'
    }, broadcast=True)

@socketio.on('voice_control')
def handle_voice_control(data):
    """Handle voice control toggle"""
    active = data.get('active')
    logger.info(f"Voice control: {'activated' if active else 'deactivated'}")
    emit('console_update', {
        'message': f'[SERVER] Voice recognition {"enabled" if active else "disabled"}',
        'type': 'info'
    }, broadcast=True)

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Omega Enhanced Web UI')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print(" " * 20 + "Ω OMEGA ENHANCED WEB UI")
    print("=" * 80)
    print(f"\n🚀 Starting server on http://{args.host}:{args.port}")
    print(f"🎛️  Access the control panel at: http://localhost:{args.port}")
    print("\n✅ Features:")
    print("   • 1980s/90s Sci-Fi Aesthetic")
    print("   • Real-time Audio Visualization")
    print("   • Voice Control Support")
    print("   • System Monitoring")
    print("   • WebSocket Communication")
    print("\n📝 Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    try:
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\n❌ Server error: {e}")

if __name__ == '__main__':
    main()
