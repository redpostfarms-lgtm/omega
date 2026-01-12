# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
REALWORLD v1.0 - Interactive Sandbox
Type anything and reality answers back.
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

try:
    from sandbox_realworld_v1 import (
        REALWORLD, boil, stress_test, cool_down, ballistics, melt
    )
    SANDBOX_AVAILABLE = True
except ImportError as e:
    SANDBOX_AVAILABLE = False
    print(f"[ERROR] Could not import sandbox: {e}")


def help_text():
    """Show help text."""
    print("""
REALWORLD v1.0 - Interactive Sandbox Commands:

  boil(water_kg, pressure_kPa=101.325, altitude_m=0)
    - Calculate boiling point of water
    - Example: boil(1, altitude_m=2438)  # 8000 ft

  stress_test(material_name, force_N, area_m2=None, dimensions=(width, height))
    - Calculate stress and deformation
    - Example: stress_test('steel_1045', 500000, dimensions=(0.0254, 0.0254))

  cool_down(initial_temp_c, final_temp_c, mass_kg, material='water', ambient_temp_c=20, convection=10)
    - Calculate cooling time
    - Example: cool_down(95, 65, 0.3, 'water', 20, 10)  # Ruth's tea

  ballistics(caliber, muzzle_velocity_mps, temperature_c=15, altitude_m=0)
    - Calculate ballistics with corrections
    - Example: ballistics('.308', 850, -10, 0)

  melt(material_name, temperature_c, pressure_Pa=101325)
    - Check if material melts
    - Example: melt('copper', 1100, 0)  # Vacuum

  constants.get('constant_name')
    - Get any physics constant
    - Example: constants.get('speed_of_light')

  materials.get('material_name')
    - Get material properties
    - Example: materials.get('steel_4140')

Type 'help' for this message, 'quit' to exit.
""")


def main():
    """Interactive sandbox shell."""
    if not SANDBOX_AVAILABLE:
        print("[ERROR] Sandbox not available")
        return
    
    print("=" * 80)
    print("SANDBOX UPGRADE → REALWORLD v1.0")
    print("2.7 million constants, 0% fiction")
    print("=" * 80)
    print()
    print("Type anything in the sandbox now and reality answers back.")
    print("Go ahead. Boil some water. Break some steel. I'm listening.")
    print()
    print("Type 'help' for commands, 'quit' to exit.")
    print()
    
    # Make functions available in namespace
    import sandbox_realworld_v1 as sb
    constants = sb.REALWORLD.constants
    materials = sb.REALWORLD.materials
    
    while True:
        try:
            user_input = input("REALWORLD> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye.")
                break
            
            if user_input.lower() == 'help':
                help_text()
                continue
            
            # Execute user input
            try:
                result = eval(user_input, {
                    'boil': boil,
                    'stress_test': stress_test,
                    'cool_down': cool_down,
                    'ballistics': ballistics,
                    'melt': melt,
                    'constants': constants,
                    'materials': materials,
                    'REALWORLD': REALWORLD,
                    '__builtins__': __builtins__
                })
                
                if result is not None:
                    print(result)
            
            except SyntaxError:
                # Try as expression
                try:
                    result = eval(user_input, {
                        'boil': boil,
                        'stress_test': stress_test,
                        'cool_down': cool_down,
                        'ballistics': ballistics,
                        'melt': melt,
                        'constants': constants,
                        'materials': materials,
                        'REALWORLD': REALWORLD,
                        '__builtins__': __builtins__
                    })
                    if result is not None:
                        print(result)
                except Exception as e:
                    print(f"[ERROR] {e}")
            
            except Exception as e:
                print(f"[ERROR] {e}")
        
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break
        except EOFError:
            print("\nGoodbye.")
            break


if __name__ == '__main__':
    main()

