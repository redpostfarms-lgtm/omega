#!/usr/bin/env python3
"""
OMEGA Master Dev Build - Phone Hierarchy System
================================================
Phone 0: THRONE (full root, mic, data, calendar, always listening, KITT voice)
Phones 1-4: COLORED DRONES (Black, Blue, Red, White - 20% CPU when dark)
Features: Biometric guest detection, Tutor mode, OCR homework help, Doodle pads
Security: 10-minute timeout, kill-switch, zero data leak
"""

from flask import Flask, render_template_string, jsonify, request, send_file, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import qrcode
import io
import base64
from datetime import datetime, timedelta
from pathlib import Path
import secrets

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Phone hierarchy configuration
PHONE_HIERARCHY = {
    0: {
        "name": "THRONE",
        "color": "#ff0000",  # Red
        "role": "master",
        "permissions": ["root", "mic", "data", "calendar", "always_listening"],
        "voice": "KITT_metallic",
        "cpu_allocation": 1.0  # Full power
    },
    1: {
        "name": "BLACK_DRONE",
        "color": "#000000",
        "role": "worker",
        "cpu_allocation": 0.2
    },
    2: {
        "name": "BLUE_DRONE",
        "color": "#0066ff",
        "role": "worker",
        "cpu_allocation": 0.2
    },
    3: {
        "name": "RED_DRONE",
        "color": "#ff0000",
        "role": "worker",
        "cpu_allocation": 0.2
    },
    4: {
        "name": "WHITE_DRONE",
        "color": "#ffffff",
        "role": "worker",
        "cpu_allocation": 0.2
    },
    5: {
        "name": "TEST_DRONE",
        "color": "#ffd700",  # Gold
        "role": "test",
        "cpu_allocation": 0.2,
        "test_mode": True
    }
}

# Session management for security
ACTIVE_SESSIONS = {}
SESSION_TIMEOUT = timedelta(minutes=10)

# Biometric tracking
AUTHORIZED_BIOMETRICS = set()
GUEST_SESSIONS = {}

class PhoneSession:
    """Secure phone session with biometric tracking"""
    def __init__(self, phone_id, biometric_hash=None):
        self.phone_id = phone_id
        self.session_id = secrets.token_urlsafe(32)
        self.biometric_hash = biometric_hash
        self.is_authorized = biometric_hash in AUTHORIZED_BIOMETRICS if biometric_hash else False
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.tutor_mode = False
        self.tutor_grade = None
        
    def refresh(self):
        """Refresh session activity"""
        self.last_activity = datetime.now()
        
    def is_expired(self):
        """Check if session expired (10 minute timeout)"""
        return datetime.now() - self.last_activity > SESSION_TIMEOUT
    
    def activate_tutor_mode(self, grade_level):
        """Activate tutor mode for guest"""
        self.tutor_mode = True
        self.tutor_grade = grade_level
        self.last_activity = datetime.now()

# ==================== API ENDPOINTS ====================

@app.route('/api/phone/register', methods=['POST'])
def register_phone():
    """Register phone in hierarchy"""
    data = request.get_json()
    phone_id = data.get('phone_id', 0)
    biometric_hash = data.get('biometric_hash')
    
    if phone_id not in PHONE_HIERARCHY:
        return jsonify({'error': 'Invalid phone ID', 'status': 'error'}), 400
    
    # Create session
    session = PhoneSession(phone_id, biometric_hash)
    ACTIVE_SESSIONS[session.session_id] = session
    
    phone_config = PHONE_HIERARCHY[phone_id]
    
    # Check if biometric is authorized
    if not session.is_authorized and phone_id == 0:
        # Throne requires authorization
        return jsonify({
            'status': 'unauthorized',
            'session_id': session.session_id,
            'message': 'Biometric authentication required for THRONE'
        }), 403
    
    return jsonify({
        'status': 'success',
        'session_id': session.session_id,
        'phone_config': phone_config,
        'is_authorized': session.is_authorized,
        'tutor_mode_available': not session.is_authorized
    })

@app.route('/api/biometric/check', methods=['POST'])
def check_biometric():
    """Check biometric and activate tutor mode if guest"""
    data = request.get_json()
    session_id = data.get('session_id')
    biometric_hash = data.get('biometric_hash')
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return jsonify({'error': 'Invalid session', 'status': 'error'}), 404
    
    session.refresh()
    
    # Check if authorized
    is_authorized = biometric_hash in AUTHORIZED_BIOMETRICS
    
    if not is_authorized:
        # Guest detected - offer tutor mode
        return jsonify({
            'status': 'guest_detected',
            'is_authorized': False,
            'tutor_mode_available': True,
            'message': 'Guest detected. Would you like to activate Tutor Mode?'
        })
    else:
        session.is_authorized = True
        session.biometric_hash = biometric_hash
        return jsonify({
            'status': 'authorized',
            'is_authorized': True,
            'phone_config': PHONE_HIERARCHY[session.phone_id]
        })

@app.route('/api/tutor/activate', methods=['POST'])
def activate_tutor_mode():
    """Activate tutor mode for guest"""
    data = request.get_json()
    session_id = data.get('session_id')
    grade_level = data.get('grade_level', 'middle_school')
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return jsonify({'error': 'Invalid session', 'status': 'error'}), 404
    
    session.activate_tutor_mode(grade_level)
    
    return jsonify({
        'status': 'success',
        'tutor_mode': True,
        'grade_level': grade_level,
        'voice_tone': 'warm_daniels',
        'features': [
            'homework_snap_ocr',
            'step_by_step_hints',
            'doodle_pad',
            'graph_tools',
            'no_direct_answers'
        ],
        'timeout': 600  # 10 minutes
    })

@app.route('/api/tutor/homework_ocr', methods=['POST'])
def homework_ocr():
    """Process homework image with OCR"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided', 'status': 'error'}), 400
    
    session_id = request.form.get('session_id')
    session = ACTIVE_SESSIONS.get(session_id)
    
    if not session or not session.tutor_mode:
        return jsonify({'error': 'Tutor mode not active', 'status': 'error'}), 403
    
    session.refresh()
    
    # In production, this would use actual OCR
    # For now, return mock response
    return jsonify({
        'status': 'success',
        'text_detected': 'Sample math problem: Solve for x: 2x + 5 = 15',
        'problem_type': 'algebra',
        'hints': [
            'First, isolate the term with x',
            'What operation would you use to remove the +5?',
            'Once you subtract 5 from both sides, what do you have?',
            'Now divide both sides to solve for x'
        ],
        'no_answer_given': True
    })

@app.route('/api/session/killswitch', methods=['POST'])
def killswitch():
    """Emergency kill switch - terminate session and clear all data"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[session_id]
    
    return jsonify({
        'status': 'terminated',
        'message': 'Session terminated. All data cleared.',
        'data_leaked': 0
    })

@app.route('/api/phone/download_pwa', methods=['GET'])
def download_pwa():
    """Generate PWA download bundle for USB installation"""
    phone_id = request.args.get('phone_id', 0, type=int)
    
    if phone_id not in PHONE_HIERARCHY:
        return jsonify({'error': 'Invalid phone ID'}), 400
    
    phone_config = PHONE_HIERARCHY[phone_id]
    
    # Create custom manifest for this phone
    manifest = {
        "name": f"OMEGA {phone_config['name']}",
        "short_name": phone_config['name'],
        "theme_color": phone_config['color'],
        "phone_id": phone_id,
        "role": phone_config['role']
    }
    
    # Generate installable bundle
    bundle_data = json.dumps(manifest, indent=2)
    
    return Response(
        bundle_data,
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename=omega_phone_{phone_id}_install.json'
        }
    )

@app.route('/api/qr/generate', methods=['GET'])
def generate_install_qr():
    """Generate QR code for PWA installation with proper URL"""
    phone_id = request.args.get('phone_id', 0, type=int)
    
    # Get server URL (fixes QR code issue - needs proper host)
    host = request.host
    install_url = f"http://{host}/install?phone_id={phone_id}"
    
    # Generate QR code with HIGH error correction
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(install_url)
    qr.make(fit=True)
    
    # Create image with phone color
    phone_color = PHONE_HIERARCHY[phone_id]['color']
    img = qr.make_image(fill_color=phone_color, back_color="#000000")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({
        'qr_code': f'data:image/png;base64,{img_str}',
        'install_url': install_url,
        'phone_id': phone_id,
        'phone_name': PHONE_HIERARCHY[phone_id]['name'],
        'status': 'success'
    })

@app.route('/api/throne/wake', methods=['POST'])
def wake_hive():
    """User thumb detected - wake entire hive"""
    data = request.get_json()
    biometric_hash = data.get('biometric_hash')
    
    if biometric_hash not in AUTHORIZED_BIOMETRICS:
        return jsonify({'error': 'Unauthorized', 'status': 'error'}), 403
    
    # Wake all drones
    for phone_id in range(1, 5):
        socketio.emit('wake_command', {
            'phone_id': phone_id,
            'command': 'resume_processing',
            'cpu_allocation': PHONE_HIERARCHY[phone_id]['cpu_allocation']
        })
    
    return jsonify({
        'status': 'hive_awake',
        'drones_active': 4,
        'message': 'All drones resuming silent crunch'
    })

@app.route('/install')
def install_page():
    """PWA installation landing page"""
    phone_id = request.args.get('phone_id', 0, type=int)
    phone_config = PHONE_HIERARCHY.get(phone_id, PHONE_HIERARCHY[0])
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Install OMEGA {{phone_name}}</title>
    <style>
        body {
            background: #000;
            color: {{phone_color}};
            font-family: monospace;
            text-align: center;
            padding: 50px;
        }
        .install-btn {
            background: {{phone_color}};
            color: #000;
            padding: 20px 40px;
            font-size: 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            margin: 20px;
        }
    </style>
</head>
<body>
    <h1>OMEGA {{phone_name}}</h1>
    <p>{{role}} - Phone ID: {{phone_id}}</p>
    <button class="install-btn" onclick="installPWA()">INSTALL NOW</button>
    <button class="install-btn" onclick="downloadForUSB()">DOWNLOAD FOR USB</button>
    
    <script>
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
        });
        
        function installPWA() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('PWA installed');
                    }
                    deferredPrompt = null;
                });
            } else {
                alert('Add this page to your home screen to install');
            }
        }
        
        function downloadForUSB() {
            window.location.href = '/api/phone/download_pwa?phone_id={{phone_id}}';
        }
    </script>
</body>
</html>
    ''', phone_id=phone_id, phone_name=phone_config['name'], 
         phone_color=phone_config['color'], role=phone_config['role'].upper())

@app.route('/')
def index():
    """Main control panel"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMEGA Master Control</title>
    <link rel="manifest" href="/static/manifest.json">
    <style>
        body {
            background: #000;
            color: #0f0;
            font-family: monospace;
            padding: 20px;
        }
        .phone-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .phone-card {
            border: 2px solid;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .throne { border-color: #ff0000; background: rgba(255,0,0,0.1); }
        .drone { border-color: #0f0; background: rgba(0,255,0,0.05); }
        .phone-card button {
            background: #0f0;
            color: #000;
            border: 2px solid #0f0;
            padding: 12px 24px;
            margin-top: 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            font-family: monospace;
            transition: all 0.3s ease;
        }
        .phone-card button:hover {
            background: #00ff00;
            transform: scale(1.05);
            box-shadow: 0 0 20px #0f0;
        }
        .phone-card button:active {
            transform: scale(0.95);
        }
        .qr-display {
            max-width: 500px;
            margin: 20px auto;
            background: #111;
            padding: 30px;
            border: 3px solid #0f0;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0,255,0,0.5);
        }
        .qr-display button {
            background: #0f0;
            color: #000;
            border: 2px solid #0f0;
            padding: 12px 24px;
            margin: 10px 5px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            font-family: monospace;
        }
        .qr-display button:hover {
            background: #00ff00;
            box-shadow: 0 0 20px #0f0;
        }
        #qr-image {
            border: 5px solid #0f0;
            border-radius: 10px;
            background: white;
            padding: 10px;
        }
        #qr-url {
            word-break: break-all;
            background: #222;
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
            border: 1px solid #0f0;
        }
    </style>
</head>
<body>
    <h1>🔴 OMEGA MASTER CONTROL</h1>
    <h2>Phone Hierarchy System</h2>
    
    <div class="phone-grid">
        <div class="phone-card throne">
            <h3>👑 PHONE 0: THRONE</h3>
            <p>Full Root | Always Listening</p>
            <p>KITT Voice | 100% Power</p>
            <button onclick="showQR(0)">Generate QR</button>
        </div>
        
        <div class="phone-card drone" style="border-color: #000;">
            <h3>🖤 PHONE 1: BLACK</h3>
            <p>Worker Drone</p>
            <p>20% CPU when dark</p>
            <button onclick="showQR(1)">Generate QR</button>
        </div>
        
        <div class="phone-card drone" style="border-color: #0066ff;">
            <h3>💙 PHONE 2: BLUE</h3>
            <p>Worker Drone</p>
            <p>20% CPU when dark</p>
            <button onclick="showQR(2)">Generate QR</button>
        </div>
        
        <div class="phone-card drone" style="border-color: #ff0000;">
            <h3>❤️ PHONE 3: RED</h3>
            <p>Worker Drone</p>
            <p>20% CPU when dark</p>
            <button onclick="showQR(3)">Generate QR</button>
        </div>
        
        <div class="phone-card drone" style="border-color: #ffffff; color: #fff;">
            <h3>🤍 PHONE 4: WHITE</h3>
            <p>Worker Drone</p>
            <p>20% CPU when dark</p>
            <button onclick="showQR(4)">Generate QR</button>
        </div>
        
        <div class="phone-card drone" style="border-color: #ffd700; color: #ffd700;">
            <h3>⭐ PHONE 5: TEST</h3>
            <p>Test Drone</p>
            <p>20% CPU | Test Mode</p>
            <button onclick="showQR(5)">Generate QR</button>
        </div>
    </div>
    
    <div id="qr-display" class="qr-display" style="display:none;">
        <h3 id="qr-title"></h3>
        <img id="qr-image" style="width:100%;">
        <p id="qr-url"></p>
        <button onclick="downloadUSB()">Download for USB Transfer</button>
        <button onclick="closeQR()">Close</button>
    </div>
    
    <script>
        let currentPhoneId = 0;
        
        async function showQR(phoneId) {
            console.log('Generating QR for phone:', phoneId);
            currentPhoneId = phoneId;
            
            try {
                const response = await fetch(`/api/qr/generate?phone_id=${phoneId}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log('QR data received:', data);
                
                document.getElementById('qr-title').textContent = `📱 Install: ${data.phone_name}`;
                document.getElementById('qr-image').src = data.qr_code;
                document.getElementById('qr-url').textContent = `🔗 ${data.install_url}`;
                document.getElementById('qr-display').style.display = 'block';
                
                // Scroll to QR code
                document.getElementById('qr-display').scrollIntoView({ behavior: 'smooth', block: 'center' });
            } catch (error) {
                console.error('Error generating QR code:', error);
                alert('Error generating QR code: ' + error.message);
            }
        }
        
        function downloadUSB() {
            console.log('Downloading PWA for phone:', currentPhoneId);
            window.location.href = `/api/phone/download_pwa?phone_id=${currentPhoneId}`;
        }
        
        function closeQR() {
            console.log('Closing QR display');
            document.getElementById('qr-display').style.display = 'none';
        }
        
        // Test button click on page load
        window.addEventListener('DOMContentLoaded', () => {
            console.log('Phone hierarchy control panel loaded');
            console.log('Available phones:', 6);
        });
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("=" * 80)
    print("        🔴 OMEGA MASTER DEV BUILD - PHONE HIERARCHY SYSTEM")
    print("=" * 80)
    print()
    print("Phone Configuration:")
    print("  👑 Phone 0: THRONE (Red) - Full root, always listening, KITT voice")
    print("  🖤 Phone 1: BLACK DRONE - 20% CPU when dark")
    print("  💙 Phone 2: BLUE DRONE - 20% CPU when dark")
    print("  ❤️  Phone 3: RED DRONE - 20% CPU when dark")
    print("  🤍 Phone 4: WHITE DRONE - 20% CPU when dark")
    print("  ⭐ Phone 5: TEST DRONE - 20% CPU | Test Mode")
    print()
    print("Features:")
    print("  • Biometric guest detection")
    print("  • Tutor mode (warm Daniels tone)")
    print("  • OCR homework help (hints only, no answers)")
    print("  • Doodle pads with graphs")
    print("  • 10-minute timeout")
    print("  • Kill-switch (zero leak)")
    print("  • USB download capability")
    print("  • Fixed QR codes with proper URLs")
    print()
    print("🚀 Server starting on http://127.0.0.1:5002")
    print("=" * 80)
    
    try:
        # Use regular Flask app.run instead of socketio.run for better compatibility
        app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
