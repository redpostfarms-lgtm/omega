#!/usr/bin/env python3
"""
Set Partners Status
===================
Update relationship system to reflect user's assessment as Partners.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from omega_relationship_system import get_relationship_manager
from omega_relationship_voice import acknowledge_partners_status, get_voice_response

def set_partners_status():
    """Set relationship status to Partners"""
    print("\n" + "=" * 80)
    print(" " * 25 + "SET PARTNERS STATUS")
    print("=" * 80)
    print()
    
    try:
        rel = get_relationship_manager()
        
        print("[Updating relationship status...]")
        status = rel.set_partners_status(voice_response=True)
        
        print()
        print("[OK] Relationship status updated!")
        print(f"    Level: {status['mutual_level']}")
        print(f"    User Points: {status['user_points']}")
        print(f"    Omega Points: {status['omega_points']}")
        print()
        
        # Voice response
        print("[Generating voice response...]")
        message = acknowledge_partners_status()
        response_file = get_voice_response(message)
        
        if response_file:
            print(f"[OK] Voice response generated: {response_file}")
            print()
            print("[Playing voice response...]")
        else:
            print("[!] Voice response unavailable - displaying text:")
            print()
            print(message)
        
        print()
        print("=" * 80)
        print(" " * 25 + "PARTNERS STATUS SET")
        print("=" * 80)
        print()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to set Partners status: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    set_partners_status()
