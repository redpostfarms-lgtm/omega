#!/usr/bin/env python3
"""
OMEGA Tunnel Setup
Configure ngrok or other tunneling service for external phone access
"""
import json
import subprocess
import os
import sys
from datetime import datetime

CONFIG_FILE = "tunnel_config.json"
NGROK_PATH = os.path.join(os.path.dirname(__file__), "ngrok.exe")

def load_config():
    """Load tunnel configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "ngrok": {
            "authtoken": "PASTE_YOUR_NGROK_TOKEN_HERE",
            "enabled": False,
            "region": "us"
        },
        "tunnel_url": None,
        "last_updated": None
    }

def save_config(config):
    """Save tunnel configuration"""
    config['last_updated'] = datetime.now().isoformat()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved to {CONFIG_FILE}")

def setup_ngrok_token(token):
    """Configure ngrok with authtoken"""
    if not os.path.exists(NGROK_PATH):
        print(f"❌ ngrok.exe not found at {NGROK_PATH}")
        return False
    
    try:
        result = subprocess.run([NGROK_PATH, "config", "add-authtoken", token], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok authtoken configured successfully")
            
            # Update config
            config = load_config()
            config['ngrok']['authtoken'] = token
            config['ngrok']['enabled'] = True
            save_config(config)
            return True
        else:
            print(f"❌ Failed to configure ngrok: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_tunnel(port=5002):
    """Start ngrok tunnel"""
    config = load_config()
    
    if not config['ngrok']['enabled']:
        print("❌ ngrok not enabled. Run setup first.")
        return None
    
    if not os.path.exists(NGROK_PATH):
        print(f"❌ ngrok.exe not found at {NGROK_PATH}")
        return None
    
    print(f"🚀 Starting ngrok tunnel on port {port}...")
    print("⏳ Getting public URL...")
    
    try:
        # Start ngrok in background
        proc = subprocess.Popen([NGROK_PATH, "http", str(port)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        
        # Wait a bit for ngrok to start
        import time
        time.sleep(3)
        
        # Get the public URL from ngrok API
        import requests
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            tunnels = response.json()
            if tunnels and 'tunnels' in tunnels and len(tunnels['tunnels']) > 0:
                public_url = tunnels['tunnels'][0]['public_url']
                print(f"✅ Tunnel active: {public_url}")
                
                # Save URL to config
                config['tunnel_url'] = public_url
                save_config(config)
                
                # Set environment variable for the server
                os.environ['OMEGA_TUNNEL_URL'] = public_url
                
                return public_url
        except:
            print("⚠️  Tunnel started but couldn't get URL automatically")
            print("📱 Check http://127.0.0.1:4040 for your ngrok URL")
            return None
            
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return None

def interactive_setup():
    """Interactive setup wizard"""
    print("=" * 60)
    print("⚡ OMEGA TUNNEL SETUP")
    print("=" * 60)
    print()
    print("This will configure ngrok for external phone access.")
    print()
    print("Steps:")
    print("1. Sign up at: https://dashboard.ngrok.com/signup")
    print("2. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Paste it below")
    print()
    
    token = input("Enter your ngrok authtoken (or 'skip' to do later): ").strip()
    
    if token.lower() == 'skip':
        print("\n✅ Skipped. You can run this script again later.")
        print(f"💡 Or edit {CONFIG_FILE} and add your token manually.")
        return
    
    if len(token) < 20:
        print("❌ Invalid token (too short). Try again.")
        return
    
    print("\n⚙️  Configuring ngrok...")
    if setup_ngrok_token(token):
        print("\n✅ Setup complete!")
        print("\n🚀 To start the tunnel, run:")
        print("   python setup_tunnel.py start")
        print("\n💡 Or set OMEGA_TUNNEL_URL environment variable manually")
    else:
        print("\n❌ Setup failed. Check the error above.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 5002
            start_tunnel(port)
            print("\n📱 Keep this terminal open while using the tunnel")
            print("⌨️  Press Ctrl+C to stop")
            
            try:
                # Keep running
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n✅ Tunnel stopped")
                
        elif command == "setup":
            if len(sys.argv) > 2:
                setup_ngrok_token(sys.argv[2])
            else:
                interactive_setup()
                
        elif command == "status":
            config = load_config()
            print("\n📊 Tunnel Status:")
            print(f"   Enabled: {config['ngrok']['enabled']}")
            print(f"   Token configured: {'Yes' if config['ngrok']['authtoken'] != 'PASTE_YOUR_NGROK_TOKEN_HERE' else 'No'}")
            print(f"   Last URL: {config['tunnel_url'] or 'None'}")
            print(f"   Last updated: {config['last_updated'] or 'Never'}")
            
        else:
            print("❌ Unknown command")
            print("\nUsage:")
            print("  python setup_tunnel.py setup          - Interactive setup")
            print("  python setup_tunnel.py setup <token>  - Setup with token")
            print("  python setup_tunnel.py start [port]   - Start tunnel (default: 5002)")
            print("  python setup_tunnel.py status         - Show status")
    else:
        interactive_setup()
