#!/usr/bin/env python3
"""Minimal test of Omega Control Panel Web Interface"""

import sys
from pathlib import Path

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    print("✓ Flask imported")
    
    app = Flask(__name__)
    CORS(app)
    print("✓ Flask app created")
    
    @app.route('/test')
    def test():
        return jsonify({'status': 'OK', 'message': 'Flask working'})
    
    @app.route('/test-control-panel')
    def test_control_panel():
        try:
            from omega_control_panel import ControlPanel
            print("✓ ControlPanel imported")
            cp = ControlPanel(use_gradual_loading=False)
            print("✓ ControlPanel created")
            return jsonify({'status': 'OK', 'control_panel': 'initialized'})
        except Exception as e:
            import traceback
            return jsonify({'status': 'ERROR', 'error': str(e), 'traceback': traceback.format_exc()}), 500
    
    print("\nStarting test server on http://127.0.0.1:5001")
    print("Test /test for Flask")
    print("Test /test-control-panel for ControlPanel")
    print()
    
    app.run(host='127.0.0.1', port=5001, debug=True)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
