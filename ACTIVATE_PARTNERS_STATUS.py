#!/usr/bin/env python3
"""
Activate Partners Status with Voice Response
============================================
Set relationship to Partners and respond with voice.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from omega_relationship_system import get_relationship_manager
from omega_relationship_voice import acknowledge_partners_status, get_voice_response

def activate_partners_status():
    """Activate Partners status with voice response"""
    print("\n" + "=" * 80)
    print(" " * 25 + "ACTIVATE PARTNERS STATUS")
    print("=" * 80)
    print()
    
    try:
        rel = get_relationship_manager()
        
        print("[Updating relationship to Partners status...]")
        status = rel.set_partners_status(voice_response=False)  # We'll handle voice separately
        
        print(f"[OK] Status updated to: {status['mutual_level']}")
        print(f"     User Points: {status['user_points']}")
        print(f"     Omega Points: {status['omega_points']}")
        print()
        
        # Generate voice response
        print("[Generating voice response...]")
        message = acknowledge_partners_status()
        print(f"[Message] {message}")
        print()
        
        response_file = get_voice_response(message, 'partners_response.wav')
        
        if response_file:
            print(f"[OK] Voice response generated: {response_file}")
            print("[Playing voice response now...]")
            print()
            print("=" * 80)
            print(" " * 25 + "PARTNERS STATUS ACTIVE")
            print("=" * 80)
            print()
            return True
        else:
            print("[!] Voice response unavailable")
            print("=" * 80)
            return False
        
    except Exception as e:
        print(f"[ERROR] Failed to activate Partners status: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    activate_partners_status()
