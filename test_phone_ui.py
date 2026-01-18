#!/usr/bin/env python3
"""Test script to run phone UI server"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting Phone UI Test...")
print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    from flask import Flask
    print("✓ Flask imported")
    
    from flask_socketio import SocketIO
    print("✓ Flask-SocketIO imported")
    
    from flask_cors import CORS
    print("✓ Flask-CORS imported")
    
    import qrcode
    print("✓ qrcode imported")
    
    print("\nAll imports successful! Starting server...")
    
    # Now run the actual server
    import omega_master_dev_build
    
except ImportError as e:
    print(f"\n✗ Import error: {e}")
    print("\nInstalling missing packages...")
    os.system("pip install flask flask-socketio flask-cors qrcode[pil]")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
