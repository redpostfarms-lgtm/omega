# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA 70B - Voice Integration
# Integrates XTTS voice cloning with Omega 70B and existing Omega voice system

"""
Ω Omega 70B Voice Integration

Integrates:
- XTTS voice cloning server
- Omega 70B text generation
- Existing Omega voice system
- Voice response generation
"""

import sys
import io
import json
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

OMEGA_HOME = Path.home() / 'omega_70b'
OMEGA_VOICE_DIR = Path(r'D:\RPF_BRAIN\The Gatekeeper\omega_voice')
if not OMEGA_VOICE_DIR.exists():
    OMEGA_VOICE_DIR = Path.cwd() / 'The Gatekeeper' / 'omega_voice'

XTTS_SERVER_URL = "http://localhost:9999"
OMEGA_SERVER_URL = "http://localhost:8000"


def check_xtts_server() -> bool:
    """Check if XTTS server is running."""
    try:
        response = requests.get(f"{XTTS_SERVER_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def start_xtts_server(voice_file: Optional[Path] = None) -> bool:
    """Start XTTS voice cloning server."""
    print("=" * 80)
    print("STARTING XTTS VOICE SERVER")
    print("=" * 80)
    
    # Find voice file
    if voice_file is None:
        # Look for user voice recordings
        voice_candidates = [
            OMEGA_VOICE_DIR / 'user_voice_*.wav',
            OMEGA_VOICE_DIR / 'omega_primary_voice.wav',
            OMEGA_HOME / 'voice_samples' / '*.wav',
        ]
        
        for pattern in voice_candidates:
            matches = list(Path(pattern.parent).glob(pattern.name))
            if matches:
                voice_file = matches[0]
                break
    
    if voice_file and voice_file.exists():
        print(f"Using voice file: {voice_file.name}")
        cmd = [
            "xtts-api-server",
            "--model", "xtts",
            "--voice", str(voice_file),
            "--port", "9999"
        ]
    else:
        print("No voice file found. Using default voice.")
        cmd = [
            "xtts-api-server",
            "--model", "xtts",
            "--port", "9999"
        ]
    
    try:
        # Start server in background
        if sys.platform == 'win32':
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✓ XTTS server starting...")
        print("  URL: http://localhost:9999")
        return True
    except Exception as e:
        print(f"✗ Failed to start XTTS server: {e}")
        return False


def text_to_speech(text: str, output_file: Optional[Path] = None) -> Optional[Path]:
    """Convert text to speech using XTTS."""
    if not check_xtts_server():
        print("⚠ XTTS server not running. Starting...")
        if not start_xtts_server():
            return None
    
    try:
        response = requests.post(
            f"{XTTS_SERVER_URL}/tts",
            json={"text": text},
            timeout=30
        )
        
        if response.status_code == 200:
            if output_file is None:
                output_file = OMEGA_HOME / 'voice_output' / f"omega_response_{int(__import__('time').time())}.wav"
                output_file.parent.mkdir(parents=True, exist_ok=True)
            
            output_file.write_bytes(response.content)
            return output_file
        else:
            print(f"✗ TTS request failed: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"✗ TTS error: {e}")
        return None


def chat_with_voice(prompt: str, generate_audio: bool = True) -> Dict[str, Any]:
    """Chat with Omega 70B and optionally generate voice response."""
    # Get text response from Omega 70B
    try:
        response = requests.post(
            f"{OMEGA_SERVER_URL}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return {
                "error": f"Server error: {response.status_code}",
                "text": None,
                "audio": None
            }
        
        data = response.json()
        text_response = data["choices"][0]["message"]["content"]
        
        result = {
            "text": text_response,
            "audio": None
        }
        
        # Generate audio if requested
        if generate_audio:
            audio_file = text_to_speech(text_response)
            if audio_file:
                result["audio"] = str(audio_file)
        
        return result
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "Omega 70B server not running. Start with: python omega_70b_server.py",
            "text": None,
            "audio": None
        }
    except Exception as e:
        return {
            "error": str(e),
            "text": None,
            "audio": None
        }


def integrate_with_omega_voice():
    """Integrate with existing Omega voice system."""
    print("=" * 80)
    print("INTEGRATING WITH OMEGA VOICE SYSTEM")
    print("=" * 80)
    
    # Check existing Omega voice
    omega_voice_file = OMEGA_VOICE_DIR / 'omega_primary_voice.wav'
    if omega_voice_file.exists():
        print(f"✓ Found existing Omega voice: {omega_voice_file.name}")
        return omega_voice_file
    
    print("⚠ No existing Omega voice found.")
    print("  You can use XTTS to clone your voice, or use the existing voice system.")
    return None


def main():
    """Main voice integration workflow."""
    print("=" * 80)
    print("Ω OMEGA 70B - VOICE INTEGRATION")
    print("=" * 80)
    print()
    
    # Check XTTS server
    if check_xtts_server():
        print("✓ XTTS server is running")
    else:
        print("⚠ XTTS server not running")
        response = input("Start XTTS server? (y/n): ")
        if response.lower() == 'y':
            integrate_with_omega_voice()
            start_xtts_server()
    
    # Check Omega 70B server
    try:
        response = requests.get(f"{OMEGA_SERVER_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ Omega 70B server is running")
        else:
            print("⚠ Omega 70B server not responding")
    except Exception:
        print("⚠ Omega 70B server not running")
        print("  Start with: python omega_70b_server.py")
    
    print("\n" + "=" * 80)
    print("VOICE INTEGRATION READY")
    print("=" * 80)
    print("\nUsage:")
    print("  from omega_70b_voice_integration import chat_with_voice")
    print("  result = chat_with_voice('Hello Omega', generate_audio=True)")
    print("  print(result['text'])")
    print("  # Audio saved to:", result['audio'])


if __name__ == '__main__':
    main()

