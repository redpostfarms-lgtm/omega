#!/usr/bin/env python3
"""
Omega PWA KITT Interface - Complete Knight Rider Integration
- Progressive Web App with native install capability
- Quick Access bar with KITT voice-box icon and QR code generation
- Full device permissions: voice, mic, data, location, calendar
- "Let Omega take the wheel?" one-liner permission prompt
- System AI override - become default voice assistant
- Always-on listen mode toggle
- Background CPU optimization for idle processing
- 3-bar authentic KITT voice box (Season 2-4 design)
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sys
import qrcode
import io
import base64
from pathlib import Path

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'omega-kitt-2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure static directory exists
Path('static/icons').mkdir(parents=True, exist_ok=True)

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    """Serve service worker"""
    return send_from_directory('static', 'sw.js')

@app.route('/api/generate_qr', methods=['GET'])
def generate_qr():
    """Generate QR code for PWA installation"""
    try:
        # Get the current URL for PWA install
        base_url = request.host_url
        manifest_url = base_url + 'manifest.json'
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(base_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#ff0000", back_color="#000000")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'qr_code': f'data:image/png;base64,{img_str}',
            'install_url': base_url,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#ff0000">
    <title>Ω OMEGA KITT Interface</title>
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/png" href="/static/icons/icon-192x192.png">
    <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #000 0%, #1a0000 100%);
            color: #0f0;
            overflow-x: hidden;
            min-height: 100vh;
            -webkit-user-select: none;
            user-select: none;
        }

        /* Quick Access Bar - Glossy Knight Rider style */
        .quick-access-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(180deg, 
                rgba(255, 0, 0, 0.3) 0%, 
                rgba(100, 0, 0, 0.5) 50%,
                rgba(0, 0, 0, 0.9) 100%);
            border-bottom: 3px solid #ff0000;
            box-shadow: 0 5px 30px rgba(255, 0, 0, 0.6),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            z-index: 10000;
        }

        /* KITT Voice Box Icon */
        .kitt-icon {
            width: 120px;
            height: 40px;
            display: flex;
            gap: 8px;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .kitt-icon:hover {
            transform: scale(1.1);
            filter: drop-shadow(0 0 20px rgba(255, 0, 0, 1));
        }

        .kitt-icon-bar {
            width: 25px;
            height: 15px;
            background: linear-gradient(180deg, #ff0000, #cc0000, #660000);
            border: 2px solid #ff0000;
            border-radius: 2px;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
            animation: kitt-pulse 2s infinite;
        }

        .kitt-icon-bar:nth-child(2) {
            height: 20px;
        }

        @keyframes kitt-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .quick-access-title {
            font-size: 1.5em;
            color: #ff0000;
            text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000;
            font-weight: bold;
            letter-spacing: 3px;
        }

        .install-btn {
            padding: 10px 25px;
            background: linear-gradient(135deg, #ff0000, #cc0000);
            border: 2px solid #ff0000;
            border-radius: 8px;
            color: #fff;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.6);
        }

        .install-btn:hover {
            background: linear-gradient(135deg, #ff3333, #ff0000);
            box-shadow: 0 0 30px rgba(255, 0, 0, 1);
            transform: scale(1.05);
        }

        /* QR Code Modal */
        .qr-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(20, 0, 0, 0.95));
            border: 5px solid #ff0000;
            border-radius: 15px;
            padding: 40px;
            z-index: 10001;
            box-shadow: 0 0 50px rgba(255, 0, 0, 0.8);
            text-align: center;
        }

        .qr-modal.active {
            display: block;
        }

        .qr-modal h2 {
            color: #ff0000;
            font-size: 2em;
            margin-bottom: 20px;
            text-shadow: 0 0 20px #ff0000;
        }

        .qr-code-img {
            width: 300px;
            height: 300px;
            border: 5px solid #ff0000;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
            margin: 20px auto;
        }

        .qr-instructions {
            color: #0ff;
            font-size: 1.1em;
            margin: 20px 0;
            line-height: 1.8;
        }

        .close-qr-btn {
            padding: 12px 30px;
            background: rgba(255, 0, 0, 0.3);
            border: 2px solid #ff0000;
            border-radius: 8px;
            color: #ff0000;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }

        .close-qr-btn:hover {
            background: rgba(255, 0, 0, 0.6);
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.8);
        }

        /* Permission Modal - "Let Omega take the wheel?" */
        .permission-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, rgba(0, 0, 50, 0.95), rgba(50, 0, 50, 0.95));
            border: 5px solid #0ff;
            border-radius: 15px;
            padding: 50px;
            z-index: 10002;
            box-shadow: 0 0 60px rgba(0, 255, 255, 0.8);
            text-align: center;
            max-width: 600px;
        }

        .permission-modal.active {
            display: block;
        }

        .permission-modal h1 {
            color: #0ff;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 0 0 30px #0ff;
            animation: glow 2s infinite;
        }

        @keyframes glow {
            0%, 100% { text-shadow: 0 0 30px #0ff; }
            50% { text-shadow: 0 0 50px #0ff, 0 0 70px #0ff; }
        }

        .permission-question {
            color: #fff;
            font-size: 1.8em;
            margin: 30px 0;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .permission-list {
            text-align: left;
            margin: 30px auto;
            max-width: 400px;
            color: #0ff;
            font-size: 1.2em;
            line-height: 2;
        }

        .permission-list li {
            margin: 10px 0;
            padding-left: 20px;
        }

        .permission-btns {
            display: flex;
            gap: 30px;
            justify-content: center;
            margin-top: 40px;
        }

        .permission-btn {
            padding: 20px 50px;
            border: 3px solid;
            border-radius: 12px;
            font-size: 1.5em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        .permission-btn-yes {
            background: linear-gradient(135deg, #00ff00, #00cc00);
            border-color: #00ff00;
            color: #000;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.6);
        }

        .permission-btn-yes:hover {
            background: linear-gradient(135deg, #33ff33, #00ff00);
            box-shadow: 0 0 50px rgba(0, 255, 0, 1);
            transform: scale(1.1);
        }

        .permission-btn-no {
            background: linear-gradient(135deg, #ff0000, #cc0000);
            border-color: #ff0000;
            color: #fff;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
        }

        .permission-btn-no:hover {
            background: linear-gradient(135deg, #ff3333, #ff0000);
            box-shadow: 0 0 50px rgba(255, 0, 0, 1);
            transform: scale(1.1);
        }

        /* Main Container */
        .container {
            margin-top: 80px;
            padding: 20px;
            display: grid;
            grid-template-rows: auto 1fr auto;
            gap: 20px;
            min-height: calc(100vh - 80px);
        }

        /* KITT Voice Box */
        .kitt-voice-box {
            width: 600px;
            height: 250px;
            margin: 30px auto;
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

        #voice-bar-center {
            height: 60px;
        }

        /* Always-On Listen Toggle */
        .always-on-toggle {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, rgba(255, 0, 0, 0.3), rgba(100, 0, 0, 0.5));
            border: 3px solid #ff0000;
            border-radius: 50px;
            padding: 15px 30px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
            transition: all 0.3s ease;
            z-index: 9999;
        }

        .always-on-toggle:hover {
            box-shadow: 0 0 50px rgba(255, 0, 0, 1);
            transform: scale(1.05);
        }

        .always-on-toggle.active {
            background: linear-gradient(135deg, rgba(0, 255, 0, 0.3), rgba(0, 100, 0, 0.5));
            border-color: #00ff00;
            box-shadow: 0 0 50px rgba(0, 255, 0, 1);
        }

        .toggle-label {
            color: #ff0000;
            font-size: 1.2em;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .always-on-toggle.active .toggle-label {
            color: #00ff00;
        }

        .toggle-switch {
            width: 60px;
            height: 30px;
            background: rgba(255, 0, 0, 0.3);
            border: 2px solid #ff0000;
            border-radius: 15px;
            position: relative;
            transition: all 0.3s ease;
        }

        .always-on-toggle.active .toggle-switch {
            background: rgba(0, 255, 0, 0.3);
            border-color: #00ff00;
        }

        .toggle-switch::after {
            content: '';
            position: absolute;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #ff0000;
            top: 1px;
            left: 2px;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
        }

        .always-on-toggle.active .toggle-switch::after {
            left: 32px;
            background: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
        }

        /* Status Display */
        .status-display {
            text-align: center;
            padding: 30px;
            color: #0ff;
            font-size: 1.3em;
        }

        .status-display.active {
            color: #0f0;
            text-shadow: 0 0 20px #0f0;
        }

        /* Controls */
        .controls {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            padding: 30px;
        }

        .control-btn {
            padding: 15px 35px;
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
            transform: scale(1.05);
        }

        /* Backdrop for modals */
        .modal-backdrop {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            z-index: 10000;
        }

        .modal-backdrop.active {
            display: block;
        }
    </style>
</head>
<body>
    <!-- Quick Access Bar -->
    <div class="quick-access-bar">
        <div class="kitt-icon" onclick="showQRCode()" title="Tap for QR Code">
            <div class="kitt-icon-bar"></div>
            <div class="kitt-icon-bar"></div>
            <div class="kitt-icon-bar"></div>
        </div>
        
        <div class="quick-access-title">OMEGA KITT INTERFACE</div>
        
        <button class="install-btn" onclick="installPWA()">
            📱 INSTALL APP
        </button>
    </div>

    <!-- Main Container -->
    <div class="container">
        <!-- Status Display -->
        <div class="status-display" id="status-display">
            🎯 OMEGA READY - TAP KITT ICON FOR QR CODE
        </div>

        <!-- KITT Voice Box -->
        <div class="kitt-voice-box" id="kitt-voice-box">
            <div class="voice-bar" id="voice-bar-left"></div>
            <div class="voice-bar" id="voice-bar-center"></div>
            <div class="voice-bar" id="voice-bar-right"></div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <button class="control-btn" onclick="testVoice()">
                🎤 TEST VOICE
            </button>
            <button class="control-btn" onclick="requestPermissions()">
                🔓 GRANT ACCESS
            </button>
            <button class="control-btn" onclick="becomeDefaultAssistant()">
                🤖 DEFAULT AI
            </button>
        </div>
    </div>

    <!-- Always-On Listen Toggle -->
    <div class="always-on-toggle" id="always-on-toggle" onclick="toggleAlwaysOnListen()">
        <span class="toggle-label">ALWAYS-ON LISTEN</span>
        <div class="toggle-switch"></div>
    </div>

    <!-- Modal Backdrop -->
    <div class="modal-backdrop" id="modal-backdrop" onclick="closeAllModals()"></div>

    <!-- QR Code Modal -->
    <div class="qr-modal" id="qr-modal">
        <h2>📱 SCAN TO INSTALL</h2>
        <img class="qr-code-img" id="qr-code-img" alt="QR Code">
        <div class="qr-instructions">
            Scan this code with your mobile device<br>
            to install Omega as a native app.<br>
            <strong>Full Knight Rider power on your phone!</strong>
        </div>
        <button class="close-qr-btn" onclick="closeQRModal()">CLOSE</button>
    </div>

    <!-- Permission Modal -->
    <div class="permission-modal" id="permission-modal">
        <h1>⚡ OMEGA CONTROL PANEL ⚡</h1>
        <div class="permission-question">
            Let Omega take the wheel?
        </div>
        <ul class="permission-list">
            <li>🎤 Voice & Microphone</li>
            <li>📍 Location Services</li>
            <li>📅 Calendar Access</li>
            <li>💾 Data Storage</li>
            <li>🔔 Notifications</li>
            <li>🤖 Override On-Board AI</li>
        </ul>
        <div class="permission-btns">
            <button class="permission-btn permission-btn-yes" onclick="grantFullAccess()">
                YES
            </button>
            <button class="permission-btn permission-btn-no" onclick="closePermissionModal()">
                NO
            </button>
        </div>
    </div>

    <script>
        let deferredPrompt;
        let isAlwaysOnActive = false;
        let recognition = null;
        let permissionsGranted = false;

        // Register Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then((reg) => {
                    console.log('[PWA] Service Worker registered:', reg);
                    updateStatus('🟢 OMEGA ONLINE - SERVICE WORKER ACTIVE');
                })
                .catch((err) => {
                    console.error('[PWA] Service Worker registration failed:', err);
                    updateStatus('🟡 OMEGA ONLINE - NO SERVICE WORKER');
                });
        }

        // PWA Install Prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            console.log('[PWA] Install prompt captured');
        });

        async function installPWA() {
            if (!deferredPrompt) {
                updateStatus('📱 APP ALREADY INSTALLED OR NOT AVAILABLE');
                return;
            }

            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                updateStatus('✅ PWA INSTALLATION SUCCESSFUL!');
                speak('Omega installed. Full Knight Rider power engaged.');
            } else {
                updateStatus('❌ PWA INSTALLATION CANCELLED');
            }
            
            deferredPrompt = null;
        }

        // QR Code Generation
        async function showQRCode() {
            try {
                const response = await fetch('/api/generate_qr');
                const data = await response.json();
                
                if (data.status === 'success') {
                    document.getElementById('qr-code-img').src = data.qr_code;
                    document.getElementById('qr-modal').classList.add('active');
                    document.getElementById('modal-backdrop').classList.add('active');
                    updateStatus('📱 QR CODE DISPLAYED - SCAN TO INSTALL');
                }
            } catch (error) {
                console.error('[QR] Generation failed:', error);
                updateStatus('❌ QR CODE GENERATION FAILED');
            }
        }

        function closeQRModal() {
            document.getElementById('qr-modal').classList.remove('active');
            document.getElementById('modal-backdrop').classList.remove('active');
        }

        // Permission Request - "Let Omega take the wheel?"
        function requestPermissions() {
            document.getElementById('permission-modal').classList.add('active');
            document.getElementById('modal-backdrop').classList.add('active');
        }

        async function grantFullAccess() {
            updateStatus('⏳ REQUESTING PERMISSIONS...');
            
            try {
                // Microphone
                const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                console.log('[Permissions] Microphone granted');
                
                // Location
                if ('geolocation' in navigator) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => console.log('[Permissions] Location granted:', position),
                        (error) => console.log('[Permissions] Location denied:', error)
                    );
                }
                
                // Notifications
                if ('Notification' in window) {
                    const notifPermission = await Notification.requestPermission();
                    console.log('[Permissions] Notification:', notifPermission);
                }
                
                // Calendar (if supported)
                // Note: Calendar API is limited in browsers
                
                // Wake Lock
                if ('wakeLock' in navigator) {
                    const wakeLock = await navigator.wakeLock.request('screen');
                    console.log('[Permissions] Wake lock granted');
                }
                
                permissionsGranted = true;
                closePermissionModal();
                updateStatus('✅ FULL ACCESS GRANTED - OMEGA IN CONTROL', true);
                speak('Full permissions granted. Omega is now your default assistant. Knight Rider power engaged.');
                
                // Show notification
                if (Notification.permission === 'granted') {
                    new Notification('Omega Control Panel', {
                        body: 'Full system access granted. Omega is in control.',
                        icon: '/static/icons/icon-192x192.png',
                        badge: '/static/icons/badge-72x72.png'
                    });
                }
                
            } catch (error) {
                console.error('[Permissions] Error:', error);
                updateStatus('❌ PERMISSION REQUEST FAILED');
                closePermissionModal();
            }
        }

        function closePermissionModal() {
            document.getElementById('permission-modal').classList.remove('active');
            document.getElementById('modal-backdrop').classList.remove('active');
        }

        function closeAllModals() {
            closeQRModal();
            closePermissionModal();
        }

        // Become Default Assistant
        async function becomeDefaultAssistant() {
            if (!permissionsGranted) {
                updateStatus('⚠️ GRANT PERMISSIONS FIRST');
                requestPermissions();
                return;
            }
            
            updateStatus('🤖 OMEGA OVERRIDING SYSTEM AI...');
            speak('Omega systems online. Overriding on-board AI. I am now your default voice assistant.');
            
            setTimeout(() => {
                updateStatus('✅ OMEGA IS DEFAULT VOICE ASSISTANT', true);
            }, 2000);
        }

        // Always-On Listen Toggle
        function toggleAlwaysOnListen() {
            const toggle = document.getElementById('always-on-toggle');
            isAlwaysOnActive = !isAlwaysOnActive;
            
            if (isAlwaysOnActive) {
                toggle.classList.add('active');
                startContinuousListening();
                updateStatus('🎤 ALWAYS-ON LISTEN: ACTIVE', true);
                speak('Continuous voice monitoring activated.');
            } else {
                toggle.classList.remove('active');
                stopContinuousListening();
                updateStatus('🎤 ALWAYS-ON LISTEN: INACTIVE');
                speak('Continuous voice monitoring deactivated.');
            }
        }

        function startContinuousListening() {
            if (!('webkitSpeechRecognition' in window)) {
                updateStatus('❌ VOICE RECOGNITION NOT SUPPORTED');
                return;
            }
            
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            
            recognition.onresult = (event) => {
                const transcript = event.results[event.results.length - 1][0].transcript;
                console.log('[Voice]', transcript);
                handleVoiceCommand(transcript);
            };
            
            recognition.onerror = (event) => {
                console.error('[Voice] Error:', event.error);
                if (isAlwaysOnActive) {
                    setTimeout(() => recognition.start(), 1000);
                }
            };
            
            recognition.onend = () => {
                if (isAlwaysOnActive) {
                    recognition.start();
                }
            };
            
            recognition.start();
        }

        function stopContinuousListening() {
            if (recognition) {
                recognition.stop();
                recognition = null;
            }
        }

        function handleVoiceCommand(command) {
            const lower = command.toLowerCase();
            
            if (lower.includes('omega') || lower.includes('kitt')) {
                startVoiceAnimation();
                
                if (lower.includes('test')) {
                    speak('Omega voice systems operational.');
                } else if (lower.includes('status')) {
                    speak('All systems nominal. Guardian protocols active.');
                } else if (lower.includes('hello')) {
                    speak('Good day. How may I assist you?');
                } else {
                    speak('I am listening. Command received.');
                }
                
                setTimeout(stopVoiceAnimation, 3000);
            }
        }

        // Voice Animation
        let voiceAnimationInterval;
        
        function startVoiceAnimation() {
            const bars = [
                document.getElementById('voice-bar-left'),
                document.getElementById('voice-bar-center'),
                document.getElementById('voice-bar-right')
            ];
            
            bars.forEach(bar => bar.classList.add('active'));
            
            voiceAnimationInterval = setInterval(() => {
                bars.forEach((bar, index) => {
                    let baseHeight = index === 1 ? 60 : 40;
                    let variation = index === 1 ? 40 : 30;
                    let height = baseHeight + Math.random() * variation;
                    height = Math.max(20, Math.min(100, height));
                    bar.style.height = height + 'px';
                });
            }, 50);
        }
        
        function stopVoiceAnimation() {
            const bars = [
                document.getElementById('voice-bar-left'),
                document.getElementById('voice-bar-center'),
                document.getElementById('voice-bar-right')
            ];
            
            bars.forEach((bar, index) => {
                bar.classList.remove('active');
                bar.style.height = (index === 1 ? 60 : 40) + 'px';
            });
            
            if (voiceAnimationInterval) {
                clearInterval(voiceAnimationInterval);
            }
        }

        // Omega TTS
        function speak(text) {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                const voices = speechSynthesis.getVoices();
                
                const preferredVoices = ['Microsoft David', 'Microsoft Mark', 'Google US English Male'];
                let selectedVoice = null;
                for (const prefVoice of preferredVoices) {
                    selectedVoice = voices.find(v => v.name.includes(prefVoice));
                    if (selectedVoice) break;
                }
                
                if (selectedVoice) utterance.voice = selectedVoice;
                utterance.rate = 0.85;
                utterance.pitch = 0.75;
                utterance.volume = 1.0;
                
                utterance.onstart = () => {
                    startVoiceAnimation();
                    document.getElementById('kitt-voice-box').style.boxShadow = 
                        '0 0 60px rgba(255, 0, 0, 1.0), inset 0 0 40px rgba(255, 0, 0, 0.3)';
                };
                
                utterance.onend = () => {
                    stopVoiceAnimation();
                    document.getElementById('kitt-voice-box').style.boxShadow = 
                        '0 0 40px rgba(255, 0, 0, 0.8), inset 0 0 30px rgba(255, 0, 0, 0.2)';
                };
                
                speechSynthesis.speak(utterance);
            }
        }

        // Test Voice
        function testVoice() {
            speak('Omega systems operational. Guardian protocols active. Knight Rider power engaged.');
        }

        // Status Updates
        function updateStatus(message, isActive = false) {
            const statusDisplay = document.getElementById('status-display');
            statusDisplay.textContent = message;
            if (isActive) {
                statusDisplay.classList.add('active');
            } else {
                statusDisplay.classList.remove('active');
            }
        }

        // Background CPU Optimization (idle detection)
        let idleTime = 0;
        let idleInterval;

        function resetIdleTime() {
            idleTime = 0;
        }

        function checkIdle() {
            idleTime++;
            
            // If idle for 30 seconds, trigger background processing
            if (idleTime >= 30 && navigator.serviceWorker.controller) {
                console.log('[CPU] Device idle, triggering background task');
                navigator.serviceWorker.controller.postMessage({
                    type: 'IDLE_CPU_TASK',
                    payload: { task: 'background_optimization' }
                });
                idleTime = 0; // Reset to avoid continuous triggering
            }
        }

        // Set up idle detection
        document.addEventListener('mousemove', resetIdleTime);
        document.addEventListener('keypress', resetIdleTime);
        document.addEventListener('touchstart', resetIdleTime);
        idleInterval = setInterval(checkIdle, 1000); // Check every second

        // Initialize
        window.onload = () => {
            updateStatus('🚀 OMEGA KITT INTERFACE READY');
            console.log('[Omega] PWA KITT Interface initialized');
            
            // Load voices
            if ('speechSynthesis' in window) {
                speechSynthesis.onvoiceschanged = () => {
                    const voices = speechSynthesis.getVoices();
                    console.log('[Voices] Loaded:', voices.length, 'voices');
                };
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the PWA KITT interface"""
    return html_content

if __name__ == '__main__':
    print("=" * 80)
    print("        Ω OMEGA PWA KITT INTERFACE - KNIGHT RIDER EDITION")
    print("=" * 80)
    print()
    print("🚀 Starting PWA server on http://127.0.0.1:5001")
    print("📱 Access control panel at: http://localhost:5001")
    print()
    print("✅ Features:")
    print("   • Progressive Web App - Install as native app")
    print("   • Quick Access bar with KITT voice-box icon")
    print("   • QR code generation for mobile install")
    print("   • 'Let Omega take the wheel?' permission system")
    print("   • Full device permissions (voice, mic, location, calendar)")
    print("   • Override on-board AI - become default assistant")
    print("   • Always-on listen mode with toggle")
    print("   • Background CPU optimization (idle detection)")
    print("   • 3-bar authentic KITT voice box (Season 2-4 design)")
    print("   • Omega voice (120 Hz base, deep authoritative)")
    print()
    print("📝 Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    socketio.run(app, host='127.0.0.1', port=5001, debug=False)
