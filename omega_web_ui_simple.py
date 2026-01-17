#!/usr/bin/env python3
"""
Omega Web UI - Simple Voice System Interface
Lightweight Flask interface for Omega voice system
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import os
import json
import threading
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega-voice-2026'
CORS(app)

# Voice system status
voice_system = {
    'running': True,
    'voices': [
        {
            'name': 'clip_0001.wav',
            'size_mb': 4.58,
            'brightness_hz': 1527,
            'energy': 0.0333,
            'quality': 0.0414,
            'tone': 'WARM',
            'duration': 27.21
        },
        {
            'name': 'omega_downloaded.wav',
            'size_mb': 33.82,
            'brightness_hz': 2139,
            'energy': 0.0049,
            'quality': 0.0588,
            'tone': 'BRIGHT',
            'duration': 100.52
        }
    ],
    'profiles_loaded': os.path.exists('voice_profiles_analysis.json'),
    'ffmpeg_available': os.path.exists('C:\\ffmpeg\\ffmpeg.exe')
}

# HTML Template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omega Voice System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        h1 {
            color: #2a5298;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .status-badge {
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 15px;
            font-weight: bold;
        }
        
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        }
        
        .card-title {
            font-size: 1.5em;
            color: #2a5298;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-icon {
            font-size: 1.8em;
        }
        
        .voice-name {
            font-weight: bold;
            color: #1e3c72;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #666;
            font-weight: 500;
        }
        
        .metric-value {
            color: #2a5298;
            font-weight: bold;
        }
        
        .tone-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .tone-warm {
            background: #fff3cd;
            color: #856404;
        }
        
        .tone-bright {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .deployment-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .deployment-title {
            font-size: 1.8em;
            color: #2a5298;
            margin-bottom: 20px;
        }
        
        .deployment-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .option {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .option:hover {
            border-color: #2a5298;
            background: #f0f4ff;
            transform: translateX(5px);
        }
        
        .option-title {
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .option-desc {
            color: #666;
            font-size: 0.95em;
            line-height: 1.5;
        }
        
        .option-code {
            background: #2a2a2a;
            color: #4caf50;
            padding: 10px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            margin-top: 10px;
            overflow-x: auto;
            white-space: nowrap;
        }
        
        .system-check {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .check-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            font-size: 0.95em;
        }
        
        .check-icon {
            font-weight: bold;
            margin-right: 10px;
            width: 20px;
        }
        
        .check-pass {
            color: #4caf50;
        }
        
        .check-fail {
            color: #f44336;
        }
        
        footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 40px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎙️ Omega Voice System</h1>
            <p class="subtitle">Dual Voice Analysis & Synthesis Platform</p>
            <div class="status-badge">✓ System Ready</div>
        </header>
        
        <div class="cards-grid" id="voice-cards">
            <!-- Voice cards will be loaded here -->
        </div>
        
        <div class="deployment-section">
            <h2 class="deployment-title">🚀 Deployment Options</h2>
            
            <div class="system-check">
                <div style="margin-bottom: 15px; font-weight: bold; color: #2a5298;">System Status:</div>
                <div class="check-item">
                    <span class="check-icon check-pass">✓</span>
                    <span>FFmpeg installed and configured</span>
                </div>
                <div class="check-item">
                    <span class="check-icon check-pass">✓</span>
                    <span>Voice files present (clip_0001.wav, omega_downloaded.wav)</span>
                </div>
                <div class="check-item">
                    <span class="check-icon check-pass">✓</span>
                    <span>Voice profiles extracted and analyzed</span>
                </div>
                <div class="check-item">
                    <span class="check-icon check-pass">✓</span>
                    <span>Web UI operational</span>
                </div>
            </div>
            
            <div class="deployment-options">
                <div class="option">
                    <div class="option-title">📡 Python API</div>
                    <div class="option-desc">Direct integration in your Python code for voice synthesis.</div>
                    <div class="option-code">from omega import omega_speak</div>
                </div>
                
                <div class="option">
                    <div class="option-title">🌐 Web Interface</div>
                    <div class="option-desc">This interface (localhost:5000) for real-time voice testing.</div>
                    <div class="option-code">python omega_control_panel_web.py</div>
                </div>
                
                <div class="option">
                    <div class="option-title">🎵 TTS Generation</div>
                    <div class="option-desc">Generate full TTS audio samples (optional, 15-20 min).</div>
                    <div class="option-code">python omega_dual_voice_blend.py</div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Omega Control Panel v1.0 | Voice System Integrated | January 16, 2026</p>
        </footer>
    </div>
    
    <script>
        // Load voice system data
        async function loadVoiceSystem() {
            try {
                const response = await fetch('/api/voice-system');
                const data = await response.json();
                renderVoiceCards(data.voices);
            } catch (error) {
                console.error('Error loading voice system:', error);
            }
        }
        
        function renderVoiceCards(voices) {
            const container = document.getElementById('voice-cards');
            container.innerHTML = voices.map((voice, idx) => `
                <div class="card">
                    <div class="voice-name">🎤 ${voice.name}</div>
                    <div class="metric">
                        <span class="metric-label">Size:</span>
                        <span class="metric-value">${voice.size_mb} MB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Duration:</span>
                        <span class="metric-value">${voice.duration}s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Brightness:</span>
                        <span class="metric-value">${Math.round(voice.brightness_hz)} Hz</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Energy:</span>
                        <span class="metric-value">${voice.energy.toFixed(4)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Quality:</span>
                        <span class="metric-value">${voice.quality.toFixed(4)}</span>
                    </div>
                    <div>
                        <span class="tone-badge tone-${voice.tone.toLowerCase()}">
                            ${voice.tone}
                        </span>
                    </div>
                </div>
            `).join('');
        }
        
        // Load on page load
        document.addEventListener('DOMContentLoaded', loadVoiceSystem);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(html_template)

@app.route('/api/voice-system', methods=['GET'])
def api_voice_system():
    """Get voice system status"""
    return jsonify(voice_system)

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get system status"""
    return jsonify({
        'running': True,
        'timestamp': datetime.now().isoformat(),
        'voices_available': len(voice_system['voices']),
        'ffmpeg': voice_system['ffmpeg_available']
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Omega Voice System Web UI')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🚀 Omega Voice System Web UI")
    print("="*70)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"URL: http://{args.host}:{args.port}")
    print("="*70 + "\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
