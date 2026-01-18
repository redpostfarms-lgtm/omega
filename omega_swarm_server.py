#!/usr/bin/env python3
"""
OMEGA Swarm Server - Stable Version
Serves OMEGA Swarm UI with working backend
Port 5002 | 6 Phones
"""
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import qrcode
import io
import base64
import secrets
import os
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)

# Register QR handler blueprint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'static', 'scripts'))
try:
    from qr_handler import qr
    app.register_blueprint(qr)
    print("✅ QR handler blueprint registered")
except ImportError as e:
    print(f"⚠️  QR handler blueprint not available: {e}")

# 6-Phone Hierarchy
PHONE_HIERARCHY = {
    0: {"name": "QUEEN", "color": "#ffcc00", "role": "master", "label": "Queen Controller"},
    1: {"name": "BLACK_DRONE", "color": "#333333", "role": "worker", "label": "Drone 1 (Black)"},
    2: {"name": "BLUE_DRONE", "color": "#0088ff", "role": "worker", "label": "Drone 2 (Blue)"},
    3: {"name": "RED_DRONE", "color": "#ff0000", "role": "worker", "label": "Drone 3 (Red)"},
    4: {"name": "WHITE_DRONE", "color": "#ffffff", "role": "worker", "label": "Drone 4 (White)"},
    5: {"name": "TEST_DRONE", "color": "#ffd700", "role": "test", "label": "Drone 5 (TEST)", "test_mode": True}
}

# Load HTML files at startup
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

# Load at module level
QUEEN_HTML = load_html_file('queen.html')
DRONE_HTML = load_html_file('drone.html')

@app.route('/manifest.json')
def manifest():
    """PWA manifest"""
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

@app.route('/api/qr/generate', methods=['GET', 'POST'])
def generate_qr():
    """Generate colored QR code"""
    try:
        phone_id = int(request.args.get('phone_id', request.json.get('phone_id', 0) if request.is_json else 0))
        
        if phone_id not in PHONE_HIERARCHY:
            return jsonify({'error': 'Invalid phone ID'}), 400
        
        # Use actual network IP instead of request.host
        host = "10.0.0.26:5002"
        
        if phone_id == 0:
            install_url = f"http://{host}/queen"
        else:
            install_url = f"http://{host}/drone?id={phone_id}"
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(install_url)
        qr.make(fit=True)
        
        phone_color = PHONE_HIERARCHY[phone_id]['color']
        img = qr.make_image(fill_color=phone_color, back_color="#000000")
        
        buffer = io.BytesIO()
        img.save(buffer, 'PNG')
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/queen')
def queen_interface():
    """Queen controller interface"""
    if QUEEN_HTML:
        return QUEEN_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}
    return "<h1>Error loading Queen interface</h1>", 500

@app.route('/drone')
def drone_interface():
    """Drone worker interface"""
    try:
        drone_id = request.args.get('id', '1')
        
        if DRONE_HTML:
            html = DRONE_HTML.replace('data-drone="1"', f'data-drone="{drone_id}"')
            html = html.replace('id: 1,', f'id: {drone_id},')
            return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        return "<h1>Error loading Drone interface</h1>", 500
    except Exception as e:
        return f"<h1>Error: {e}</h1>", 500

@app.route('/')
def index():
    """Control panel"""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMEGA SWARM CONTROL</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(180deg, #0d0d0d 0%, #000 100%);
            color: #ffcc00;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }}
        h1 {{
            text-align: center;
            font-size: 48px;
            margin-bottom: 10px;
            text-shadow: 0 0 20px #ffcc00;
            letter-spacing: 4px;
        }}
        h2 {{
            text-align: center;
            font-size: 16px;
            margin-bottom: 40px;
            color: #888;
            letter-spacing: 2px;
        }}
        .phone-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .phone-card {{
            border: 2px solid #333;
            border-radius: 15px;
            padding: 20px;
            background: rgba(20, 20, 20, 0.9);
            transition: all 0.3s ease;
        }}
        .phone-card:hover {{
            border-color: var(--phone-color);
            box-shadow: 0 0 20px var(--phone-color);
        }}
        .phone-name {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--phone-color);
        }}
        .phone-role {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        .qr-container {{
            background: #000;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            text-align: center;
        }}
        .qr-code {{
            width: 200px;
            height: 200px;
            margin: 0 auto;
        }}
        .btn {{
            width: 100%;
            padding: 12px;
            background: var(--phone-color);
            color: #000;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.2s;
        }}
        .btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(255,255,255,0.3);
        }}
        .links {{
            margin-top: 40px;
            text-align: center;
        }}
        .links a {{
            color: #ffcc00;
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border: 1px solid #ffcc00;
            border-radius: 5px;
            display: inline-block;
            transition: all 0.3s;
        }}
        .links a:hover {{
            background: #ffcc00;
            color: #000;
        }}
    </style>
</head>
<body>
    <h1>⚡ OMEGA SWARM</h1>
    <h2>6-Phone Distributed Intelligence Network</h2>
    
    <div class="phone-grid">
'''
    
    for phone_id, phone in PHONE_HIERARCHY.items():
        html += f'''
        <div class="phone-card" style="--phone-color: {phone['color']}">
            <div class="phone-name">{phone['label']}</div>
            <div class="phone-role">{phone['role']}</div>
            <div class="qr-container">
                <img class="qr-code" id="qr-{phone_id}" alt="QR Code">
            </div>
            <button class="btn" onclick="generateQR({phone_id})">Generate QR Code</button>
            <button class="btn" onclick="pullQr({phone_id})" style="margin-top:5px; opacity:0.8;">📱 Quick Scan</button>
        </div>
'''
    
    html += '''
    </div>
    
    <div class="links">
        <a href="/queen" target="_blank">👑 Open Queen Interface</a>
        <a href="/drone?id=1" target="_blank">🤖 Open Drone Interface</a>
    </div>
    
    <!-- QR Modal for individual drones -->
    <div id="qr-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:9999; padding:40px;">
        <div style="max-width:400px; margin:0 auto; text-align:center;">
            <h2 style="color:#ffcc00; margin-bottom:20px;">📱 Scan to Install</h2>
            <img id="qr-modal-img" style="width:100%; max-width:300px; border:4px solid #ffcc00; border-radius:10px; filter:drop-shadow(0 0 20px #ffcc00);">
            <p id="qr-modal-text" style="margin-top:20px; font-size:18px; color:#888;">Scan with your phone</p>
            <button onclick="closeQrModal()" style="margin-top:20px; padding:15px 40px; background:#ffcc00; color:#000; border:none; border-radius:8px; font-size:16px; font-weight:bold; cursor:pointer;">Close</button>
        </div>
    </div>
    
    <script>
        function pullQr(droneId) {
            // Use the new blueprint endpoint
            fetch(`/drone/${droneId}/qr`)
                .then(r => r.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    document.getElementById('qr-modal-img').src = url;
                    document.getElementById('qr-modal-text').innerText = `Drone ${droneId} - Scan to install`;
                    document.getElementById('qr-modal').style.display = 'block';
                })
                .catch(err => {
                    console.error('QR generation error:', err);
                    alert(`Error generating QR for Drone ${droneId}`);
                });
        }
        
        function closeQrModal() {
            document.getElementById('qr-modal').style.display = 'none';
        }
        
        async function generateQR(phoneId) {
            try {
                const response = await fetch(`/api/qr/generate?phone_id=${phoneId}`);
                const data = await response.json();
                document.getElementById(`qr-${phoneId}`).src = data.qr_code;
            } catch (error) {
                console.error('Error generating QR:', error);
                alert('Error generating QR code');
            }
        }
        
        // Auto-generate all QR codes on load
        window.addEventListener('load', () => {
'''
    
    for phone_id in PHONE_HIERARCHY.keys():
        html += f'            generateQR({phone_id});\n'
    
    html += '''
        });
    </script>
</body>
</html>
'''
    
    return html

if __name__ == '__main__':
    print("=" * 80)
    print("⚡ OMEGA SWARM SERVER")
    print("=" * 80)
    print()
    
    if QUEEN_HTML:
        print(f"✅ Queen UI loaded ({len(QUEEN_HTML)} bytes)")
    else:
        print("❌ Queen UI failed to load")
    
    if DRONE_HTML:
        print(f"✅ Drone UI loaded ({len(DRONE_HTML)} bytes)")
    else:
        print("❌ Drone UI failed to load")
    
    print()
    print("🚀 Starting server on http://0.0.0.0:5002")
    print()
    print("📱 Control Panel: http://127.0.0.1:5002")
    print("👑 Queen: http://127.0.0.1:5002/queen")
    print("🤖 Drone: http://127.0.0.1:5002/drone?id=1")
    print()
    print("=" * 80)
    print()
    
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
