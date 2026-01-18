"""
OMEGA PWA - Flask Development Server
=====================================
Run this to serve the PWA locally for testing.

Usage:
    python server.py

Then open http://localhost:5000 in your browser.
For mobile testing, use ngrok: ngrok http 5000
"""

from flask import Flask, send_from_directory, send_file
import os

app = Flask(__name__, static_folder='.')

# Serve index.html at root
@app.route('/')
def index():
    return send_file('index.html')

# Serve manifest.json
@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

# Serve service worker
@app.route('/sw.js')
def service_worker():
    response = send_file('sw.js', mimetype='application/javascript')
    # Service workers need this header to work at root scope
    response.headers['Service-Worker-Allowed'] = '/'
    return response

# Serve static files (icons, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# Serve icons
@app.route('/icons/<path:filename>')
def icons(filename):
    return send_from_directory('icons', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    OMEGA PWA Server                          ║
╠══════════════════════════════════════════════════════════════╣
║  Local:    http://localhost:{port}                            ║
║                                                              ║
║  For mobile testing with HTTPS (required for PWA):           ║
║  1. Install ngrok: https://ngrok.com                         ║
║  2. Run: ngrok http {port}                                    ║
║  3. Use the https:// URL from ngrok                          ║
║                                                              ║
║  Press Ctrl+C to stop the server                             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
