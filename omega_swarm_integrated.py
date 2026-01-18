#!/usr/bin/env python3
"""
OMEGA Swarm Integrated Server
Combines OMEGA Swarm UI with working backend and QR code features
Port 5002 | 6 Phones: Queen + 5 Drones (including TEST)
"""
from flask import Flask, render_template_string, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import json
import qrcode
import io
import base64
import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)

# 6-Phone Swarm Hierarchy
PHONE_HIERARCHY = {
    0: {"name": "QUEEN", "color": "#ffcc00", "role": "master", "label": "Queen Controller"},
    1: {"name": "BLACK_DRONE", "color": "#333333", "role": "worker", "label": "Drone 1 (Black)"},
    2: {"name": "BLUE_DRONE", "color": "#0088ff", "role": "worker", "label": "Drone 2 (Blue)"},
    3: {"name": "RED_DRONE", "color": "#ff0000", "role": "worker", "label": "Drone 3 (Red)"},
    4: {"name": "WHITE_DRONE", "color": "#ffffff", "role": "worker", "label": "Drone 4 (White)"},
    5: {"name": "TEST_DRONE", "color": "#ffd700", "role": "test", "label": "Drone 5 (TEST)", "test_mode": True}
}

# Load OMEGA Swarm HTML files
EXTRACTED_PATH = os.path.join(os.path.dirname(__file__), 'extracted_files_4')

def load_html_file(filename):
    """Load HTML file from extracted directory"""
    try:
        filepath = os.path.join(EXTRACTED_PATH, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Error loading {filename}: {e}")
        return None

# Load original OMEGA Swarm HTML
QUEEN_HTML = load_html_file('queen.html')
DRONE_HTML = load_html_file('drone.html')

@app.route('/api/qr/generate', methods=['GET', 'POST'])
def generate_qr():
    """Generate colored QR code for phone installation"""
    phone_id = int(request.args.get('phone_id', request.json.get('phone_id', 0) if request.is_json else 0))
    
    if phone_id not in PHONE_HIERARCHY:
        return jsonify({'error': 'Invalid phone ID'}), 400
    
    host = request.host
    
    # Queen gets queen.html, drones get drone.html
    if phone_id == 0:
        install_url = f"http://{host}/queen"
    else:
        install_url = f"http://{host}/drone?id={phone_id}"
    
    # Generate QR with phone color
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(install_url)
    qr.make(fit=True)
    
    phone_color = PHONE_HIERARCHY[phone_id]['color']
    img = qr.make_image(fill_color=phone_color, back_color="#000000")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({
        'qr_code': f'data:image/png;base64,{img_str}',
        'install_url': install_url,
        'phone_id': phone_id,
        'phone_name': PHONE_HIERARCHY[phone_id]['name'],
        'phone_label': PHONE_HIERARCHY[phone_id]['label'],
        'status': 'success'
    })

@app.route('/api/phone/download_pwa')
def download_pwa():
    """Download PWA installation bundle"""
    phone_id = int(request.args.get('phone_id', 0))
    
    if phone_id not in PHONE_HIERARCHY:
        return jsonify({'error': 'Invalid phone ID'}), 400
    
    phone_config = PHONE_HIERARCHY[phone_id]
    manifest = {
        "phone_id": phone_id,
        "config": phone_config,
        "server_url": f"http://{request.host}",
        "install_instructions": "Save this file and open on your phone"
    }
    
    bundle_data = json.dumps(manifest, indent=2)
    
    return Response(
        bundle_data,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=omega_swarm_phone_{phone_id}.json'}
    )

@app.route('/manifest.json')
def manifest():
    """PWA manifest for OMEGA Swarm"""
    return jsonify({
        "name": "OMEGA Swarm",
        "short_name": "OMEGA",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#ffcc00",
        "orientation": "portrait",
        "icons": []
    })

@app.route('/queen')
def queen_interface():
    """Queen controller interface"""
    if QUEEN_HTML:
        return QUEEN_HTML
    return "<h1>Error: queen.html not found</h1><p>Check extracted_files_4 directory</p>", 404

@app.route('/drone')
def drone_interface():
    """Drone worker interface"""
    drone_id = request.args.get('id', '1')
    
    if DRONE_HTML:
        # Inject drone ID into HTML
        html = DRONE_HTML.replace('data-drone="1"', f'data-drone="{drone_id}"')
        html = html.replace('id: 1,', f'id: {drone_id},')
        return html
    return "<h1>Error: drone.html not found</h1><p>Check extracted_files_4 directory</p>", 404

@app.route('/')
def index():
    """Main swarm control panel"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMEGA SWARM CONTROL</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(180deg, #0d0d0d 0%, #000 100%);
            color: #ffcc00;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        h1 {
            text-align: center;
            font-size: 42px;
            margin-bottom: 10px;
            text-shadow: 0 0 20px #ffcc00;
            letter-spacing: 4px;
        }
        h2 {
            text-align: center;
            font-size: 16px;
            margin-bottom: 40px;
            color: #888;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .swarm-status {
            max-width: 400px;
            margin: 0 auto 30px;
            padding: 20px;
            background: rgba(20, 20, 20, 0.9);
            border-radius: 15px;
            border: 2px solid #333;
            text-align: center;
        }
        .brain-tally {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        .brain-bar {
            width: 200px;
            height: 12px;
            background: #222;
            border-radius: 6px;
            overflow: hidden;
        }
        .brain-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff0000 0%, #ffcc00 100%);
            width: 20%;
            transition: width 0.3s ease;
            border-radius: 6px;
        }
        .phone-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .phone-card {
            border: 2px solid #333;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            background: rgba(20, 20, 20, 0.9);
            transition: all 0.3s ease;
        }
        .phone-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(255, 204, 0, 0.3);
        }
        .phone-card.queen {
            border-color: #ffcc00;
            background: rgba(255, 204, 0, 0.1);
        }
        .phone-card.queen h3::before { content: '♛ '; }
        .phone-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .phone-card h3 {
            font-size: 20px;
            margin-bottom: 10px;
            color: #ffcc00;
        }
        .phone-card p {
            margin: 8px 0;
            font-size: 14px;
            color: #888;
        }
        .phone-card button {
            background: #ffcc00;
            color: #000;
            border: none;
            padding: 12px 30px;
            margin-top: 15px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .phone-card button:hover {
            background: #ffd700;
            transform: scale(1.05);
            box-shadow: 0 0 20px #ffcc00;
        }
        .phone-card button:active {
            transform: scale(0.95);
        }
        #qr-display {
            display: none;
            max-width: 500px;
            margin: 40px auto;
            background: rgba(20, 20, 20, 0.98);
            padding: 40px;
            border: 3px solid #ffcc00;
            border-radius: 20px;
            box-shadow: 0 0 50px rgba(255, 204, 0, 0.5);
            position: relative;
        }
        #qr-display h3 {
            text-align: center;
            margin-bottom: 25px;
            font-size: 24px;
            color: #ffcc00;
            text-shadow: 0 0 10px #ffcc00;
        }
        #qr-image {
            width: 100%;
            max-width: 300px;
            border: 5px solid #ffcc00;
            border-radius: 15px;
            background: white;
            padding: 15px;
            display: block;
            margin: 0 auto 20px;
        }
        #qr-url {
            word-break: break-all;
            background: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #333;
            color: #888;
            font-size: 12px;
            font-family: monospace;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .button-group button {
            background: #ffcc00;
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            flex: 1;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .button-group button:hover {
            background: #ffd700;
            box-shadow: 0 0 20px #ffcc00;
        }
        .close-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            color: #888;
            font-size: 28px;
            cursor: pointer;
            padding: 5px 10px;
        }
        .close-btn:hover { color: #ffcc00; }
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #444;
            font-size: 12px;
            letter-spacing: 2px;
        }
    </style>
</head>
<body>
    <h1>⚡ OMEGA SWARM</h1>
    <h2>Distributed AI Control System</h2>
    
    <div class="swarm-status">
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">🧠 COLLECTIVE INTELLIGENCE</div>
        <div style="color: #888; font-size: 14px;">6 Nodes | Queen + 5 Drones</div>
        <div class="brain-tally">
            <span style="font-size: 12px; color: #888;">COMPUTE</span>
            <div class="brain-bar">
                <div class="brain-fill" id="brainFill"></div>
            </div>
            <span style="font-size: 14px; font-weight: bold;" id="brainPercent">20%</span>
        </div>
    </div>
    
    <div class="phone-grid">
        <div class="phone-card queen">
            <div class="phone-icon">📱</div>
            <h3>PHONE 0: QUEEN</h3>
            <p>Master Controller</p>
            <p>Full UI | Gold Theme</p>
            <p>Swarm Coordinator</p>
            <button onclick="showQR(0)">📲 Generate QR</button>
        </div>
        
        <div class="phone-card">
            <div class="phone-icon">📱</div>
            <h3>PHONE 1: BLACK DRONE</h3>
            <p>Background Worker</p>
            <p>Sipping Mode | 20% CPU</p>
            <p>Black Theme</p>
            <button onclick="showQR(1)">📲 Generate QR</button>
        </div>
        
        <div class="phone-card">
            <div class="phone-icon">📱</div>
            <h3>PHONE 2: BLUE DRONE</h3>
            <p>Background Worker</p>
            <p>Sipping Mode | 20% CPU</p>
            <p>Blue Theme</p>
            <button onclick="showQR(2)">📲 Generate QR</button>
        </div>
        
        <div class="phone-card">
            <div class="phone-icon">📱</div>
            <h3>PHONE 3: RED DRONE</h3>
            <p>Background Worker</p>
            <p>Sipping Mode | 20% CPU</p>
            <p>Red Theme</p>
            <button onclick="showQR(3)">📲 Generate QR</button>
        </div>
        
        <div class="phone-card">
            <div class="phone-icon">📱</div>
            <h3>PHONE 4: WHITE DRONE</h3>
            <p>Background Worker</p>
            <p>Sipping Mode | 20% CPU</p>
            <p>White Theme</p>
            <button onclick="showQR(4)">📲 Generate QR</button>
        </div>
        
        <div class="phone-card" style="border-color: #ffd700;">
            <div class="phone-icon">⭐</div>
            <h3>PHONE 5: TEST DRONE</h3>
            <p>Testing Mode</p>
            <p>Sipping Mode | 20% CPU</p>
            <p>Gold Theme | Test Features</p>
            <button onclick="showQR(5)">📲 Generate QR</button>
        </div>
    </div>
    
    <div id="qr-display">
        <button class="close-btn" onclick="closeQR()">&times;</button>
        <h3 id="qr-title"></h3>
        <img id="qr-image">
        <p id="qr-url"></p>
        <div class="button-group">
            <button onclick="downloadUSB()">💾 Download</button>
            <button onclick="openDirect()">🌐 Open Direct</button>
        </div>
    </div>
    
    <div class="footer">
        OMEGA SWARM v1.0 | Port 5002 | BroadcastChannel Enabled
    </div>
    
    <script>
        let currentPhoneId = 0;
        let currentInstallUrl = '';
        
        // Animate brain tally
        setInterval(() => {
            const percent = 20 + Math.floor(Math.random() * 10);
            document.getElementById('brainFill').style.width = percent + '%';
            document.getElementById('brainPercent').textContent = percent + '%';
        }, 2000);
        
        async function showQR(phoneId) {
            console.log('🎯 Generating QR for phone:', phoneId);
            currentPhoneId = phoneId;
            
            try {
                const response = await fetch(`/api/qr/generate?phone_id=${phoneId}`);
                const data = await response.json();
                
                currentInstallUrl = data.install_url;
                
                document.getElementById('qr-title').textContent = `📱 ${data.phone_label}`;
                document.getElementById('qr-image').src = data.qr_code;
                document.getElementById('qr-url').textContent = `🔗 ${data.install_url}`;
                document.getElementById('qr-display').style.display = 'block';
                
                document.getElementById('qr-display').scrollIntoView({ behavior: 'smooth', block: 'center' });
            } catch (error) {
                console.error('❌ Error generating QR:', error);
                alert('Error generating QR code: ' + error.message);
            }
        }
        
        function downloadUSB() {
            window.location.href = `/api/phone/download_pwa?phone_id=${currentPhoneId}`;
        }
        
        function openDirect() {
            window.open(currentInstallUrl, '_blank');
        }
        
        function closeQR() {
            document.getElementById('qr-display').style.display = 'none';
        }
        
        console.log('⚡ OMEGA SWARM Control Panel Initialized');
        console.log('📱 6 Phones Ready | Queen + 5 Drones');
    </script>
</body>
</html>
    ''')

@app.route('/manifest.json')
def queen_manifest():
    """Queen PWA manifest"""
    return jsonify({
        "name": "OMEGA Queen",
        "short_name": "Queen",
        "start_url": "/queen",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#ffcc00",
        "icons": []
    })

@app.route('/manifest-drone.json')
def drone_manifest():
    """Drone PWA manifest"""
    return jsonify({
        "name": "OMEGA Drone",
        "short_name": "Drone",
        "start_url": "/drone",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#ff0000",
        "icons": []
    })

@app.route('/sw.js')
def service_worker():
    """Service worker for PWA"""
    sw_code = '''
self.addEventListener('install', (e) => {
    console.log('[SW] Install');
    self.skipWaiting();
});

self.addEventListener('activate', (e) => {
    console.log('[SW] Activate');
    return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
    // Let all requests pass through
});
    '''
    return Response(sw_code, mimetype='application/javascript')

if __name__ == '__main__':
    print("=" * 80)
    print("⚡ OMEGA SWARM - INTEGRATED SERVER")
    print("=" * 80)
    print()
    print("🧠 Architecture:")
    print("   • Phone 0: Queen (Gold) - Master controller with full UI")
    print("   • Phones 1-4: Drones (Black, Blue, Red, White) - Background workers")
    print("   • Phone 5: TEST Drone (Gold) - Testing mode")
    print()
    print("✨ Features:")
    print("   • Sipping Mode: 20% CPU when screen off")
    print("   • Brain Tally: Aggregate compute power display")
    print("   • BroadcastChannel: Same-device communication")
    print("   • Color-coded QR codes")
    print("   • PWA support with service worker")
    print()
    print(f"🚀 Starting server on http://0.0.0.0:5002")
    print("=" * 80)
    print()
    
    # Check if HTML files exist
    if QUEEN_HTML:
        print("✅ Queen UI loaded successfully")
    else:
        print(f"⚠️  Queen UI not found at {EXTRACTED_PATH}")
    
    if DRONE_HTML:
        print("✅ Drone UI loaded successfully")
    else:
        print(f"⚠️  Drone UI not found at {EXTRACTED_PATH}")
    
    print()
    print("📱 Access control panel: http://127.0.0.1:5002")
    print("👑 Queen interface: http://127.0.0.1:5002/queen")
    print("🤖 Drone interface: http://127.0.0.1:5002/drone?id=1")
    print()
    print("=" * 80)
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=True, threaded=True)
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

