#!/usr/bin/env python3
"""
qr_handler.py — Drone QR endpoint with dynamic URL support
Blueprint for generating QR codes for OMEGA Swarm drones
"""
from flask import Blueprint, jsonify, request
import qrcode
from io import BytesIO
import socket

qr = Blueprint("qr", __name__)

def get_server_url():
    """Get the best available server URL (tunnel > network IP > localhost)"""
    # Check if running behind a tunnel (ngrok, localtunnel, etc.)
    # Priority: env var > network IP > localhost
    import os
    tunnel = os.environ.get('OMEGA_TUNNEL_URL')
    if tunnel:
        return tunnel
    
    # Get local network IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return f"http://{local_ip}:5002"
    except:
        return "http://localhost:5002"

@qr.route("/drone/<int:drone_id>/qr")
def drone_qr(drone_id):
    """Generate QR code for specific drone"""
    base_url = get_server_url()
    
    if drone_id == 0:
        install_url = f"{base_url}/queen"
    else:
        install_url = f"{base_url}/drone?id={drone_id}"
    
    # Generate QR code
    qr_img = qrcode.make(install_url, 
                         error_correction=qrcode.ERROR_CORRECT_H,
                         box_size=10,
                         border=4)
    
    # Convert to bytes
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io.getvalue(), 200, {
        'Content-Type': 'image/png',
        'Cache-Control': 'no-cache',
        'X-Install-URL': install_url
    }

@qr.route("/drone/<int:drone_id>/url")
def drone_url(drone_id):
    """Get the install URL for a drone"""
    base_url = get_server_url()
    
    if drone_id == 0:
        install_url = f"{base_url}/queen"
    else:
        install_url = f"{base_url}/drone?id={drone_id}"
    
    return jsonify({
        'drone_id': drone_id,
        'install_url': install_url,
        'server_url': base_url
    })
