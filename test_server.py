#!/usr/bin/env python3
"""Minimal test server to debug the crash"""
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Test - If you see this, Flask is working</h1>"

@app.route('/test')
def test():
    return "<h1>Route Test</h1><p>Flask routes are working correctly</p>"

if __name__ == '__main__':
    print("Starting minimal test server on port 5003...")
    app.run(host='0.0.0.0', port=5003, debug=False)
