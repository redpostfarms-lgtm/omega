#!/usr/bin/env python3
"""
Simplified Phone UI Server - Standalone
"""
from flask import Flask, render_template_string, jsonify, request, Response
from flask_cors import CORS
import json
import qrcode
import io
import base64
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)

# Phone hierarchy
PHONE_HIERARCHY = {
    0: {"name": "THRONE", "color": "#ff0000", "role": "master"},
    1: {"name": "BLACK_DRONE", "color": "#000000", "role": "worker"},
    2: {"name": "BLUE_DRONE", "color": "#0066ff", "role": "worker"},
    3: {"name": "RED_DRONE", "color": "#ff0000", "role": "worker"},
    4: {"name": "WHITE_DRONE", "color": "#ffffff", "role": "worker"},
    5: {"name": "TEST_DRONE", "color": "#ffd700", "role": "test", "test_mode": True}
}

@app.route('/api/qr/generate')
def generate_qr():
    """Generate QR code"""
    phone_id = int(request.args.get('phone_id', 0))
    
    if phone_id not in PHONE_HIERARCHY:
        return jsonify({'error': 'Invalid phone ID'}), 400
    
    host = request.host
    install_url = f"http://{host}/install?phone_id={phone_id}"
    
    # Generate QR
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
        'status': 'success'
    })

@app.route('/api/phone/download_pwa')
def download_pwa():
    """Download PWA bundle"""
    phone_id = int(request.args.get('phone_id', 0))
    
    if phone_id not in PHONE_HIERARCHY:
        return jsonify({'error': 'Invalid phone ID'}), 400
    
    phone_config = PHONE_HIERARCHY[phone_id]
    manifest = {
        "phone_id": phone_id,
        "config": phone_config,
        "install_instructions": "Transfer this file to your phone and open it"
    }
    
    bundle_data = json.dumps(manifest, indent=2)
    
    return Response(
        bundle_data,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=omega_phone_{phone_id}_install.json'}
    )

@app.route('/')
def index():
    """Main control panel"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMEGA Phone Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        h1 { text-align: center; font-size: 32px; margin-bottom: 10px; text-shadow: 0 0 10px #0f0; }
        h2 { text-align: center; font-size: 18px; margin-bottom: 30px; }
        .phone-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .phone-card { border: 2px solid; padding: 20px; border-radius: 10px; text-align: center; background: rgba(0,255,0,0.05); }
        .phone-card h3 { font-size: 18px; margin-bottom: 10px; }
        .phone-card p { margin: 5px 0; font-size: 14px; }
        .phone-card button {
            background: #0f0; color: #000; border: 2px solid #0f0; padding: 12px 24px;
            margin-top: 15px; border-radius: 5px; cursor: pointer; font-weight: bold;
            font-size: 16px; font-family: monospace; transition: all 0.3s ease; width: 100%;
        }
        .phone-card button:hover { background: #00ff00; transform: scale(1.05); box-shadow: 0 0 20px #0f0; }
        .phone-card button:active { transform: scale(0.95); }
        .throne { border-color: #ff0000; background: rgba(255,0,0,0.1); }
        #qr-display {
            display: none; max-width: 500px; margin: 30px auto; background: #111;
            padding: 30px; border: 3px solid #0f0; border-radius: 15px; box-shadow: 0 0 30px rgba(0,255,0,0.5);
        }
        #qr-display h3 { text-align: center; margin-bottom: 20px; font-size: 24px; }
        #qr-image { width: 100%; border: 5px solid #0f0; border-radius: 10px; background: white; padding: 10px; }
        #qr-url { word-break: break-all; background: #222; padding: 10px; border-radius: 5px; margin: 15px 0; border: 1px solid #0f0; }
        #qr-display button {
            background: #0f0; color: #000; border: 2px solid #0f0; padding: 12px 24px;
            margin: 10px 5px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px;
        }
        #qr-display button:hover { background: #00ff00; box-shadow: 0 0 20px #0f0; }
    </style>
</head>
<body>
    <h1>🔴 OMEGA PHONE CONTROL</h1>
    <h2>Phone Hierarchy System</h2>
    
    <div class="phone-grid">
        <div class="phone-card throne">
            <h3>👑 PHONE 0: THRONE</h3>
            <p>Full Root | KITT Voice</p>
            <p>100% Power</p>
            <button onclick="showQR(0)">Generate QR</button>
        </div>
        
        <div class="phone-card">
            <h3>🖤 PHONE 1: BLACK</h3>
            <p>Worker Drone</p>
            <p>20% CPU</p>
            <button onclick="showQR(1)">Generate QR</button>
        </div>
        
        <div class="phone-card">
            <h3>💙 PHONE 2: BLUE</h3>
            <p>Worker Drone</p>
            <p>20% CPU</p>
            <button onclick="showQR(2)">Generate QR</button>
        </div>
        
        <div class="phone-card">
            <h3>❤️ PHONE 3: RED</h3>
            <p>Worker Drone</p>
            <p>20% CPU</p>
            <button onclick="showQR(3)">Generate QR</button>
        </div>
        
        <div class="phone-card">
            <h3>🤍 PHONE 4: WHITE</h3>
            <p>Worker Drone</p>
            <p>20% CPU</p>
            <button onclick="showQR(4)">Generate QR</button>
        </div>
        
        <div class="phone-card" style="border-color: #ffd700;">
            <h3>⭐ PHONE 5: TEST</h3>
            <p>Test Drone</p>
            <p>20% CPU | Test Mode</p>
            <button onclick="showQR(5)">Generate QR</button>
        </div>
    </div>
    
    <div id="qr-display">
        <h3 id="qr-title"></h3>
        <img id="qr-image">
        <p id="qr-url"></p>
        <button onclick="downloadUSB()">Download for USB</button>
        <button onclick="closeQR()">Close</button>
    </div>
    
    <script>
        let currentPhoneId = 0;
        
        async function showQR(phoneId) {
            console.log('Generating QR for phone:', phoneId);
            currentPhoneId = phoneId;
            
            try {
                const response = await fetch(`/api/qr/generate?phone_id=${phoneId}`);
                const data = await response.json();
                
                document.getElementById('qr-title').textContent = `📱 ${data.phone_name}`;
                document.getElementById('qr-image').src = data.qr_code;
                document.getElementById('qr-url').textContent = `🔗 ${data.install_url}`;
                document.getElementById('qr-display').style.display = 'block';
                
                document.getElementById('qr-display').scrollIntoView({ behavior: 'smooth', block: 'center' });
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        function downloadUSB() {
            window.location.href = `/api/phone/download_pwa?phone_id=${currentPhoneId}`;
        }
        
        function closeQR() {
            document.getElementById('qr-display').style.display = 'none';
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("=" * 80)
    print("🔴 OMEGA PHONE CONTROL - SIMPLIFIED SERVER")
    print("=" * 80)
    print()
    print("6 Phones: THRONE + 5 Drones (Black, Blue, Red, White, TEST)")
    print()
    print("🚀 Starting server on http://127.0.0.1:5002")
    print("=" * 80)
    print()
    
    app.run(host='127.0.0.1', port=5002, debug=False, threaded=True)
