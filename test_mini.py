#!/usr/bin/env python3
"""Minimal test - NO DEBUG MODE"""

import sys
from pathlib import Path

base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test')
def test():
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    print("✓ Starting server on http://127.0.0.1:5002")
    app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
