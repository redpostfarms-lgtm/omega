"""
GATE - Kit Voice Quick Play
Simple script to play Kit voice with KITT LED effects
"""

import os
import subprocess
import time
import sys

# Colors
R = '\033[91m'
C = '\033[96m'
Y = '\033[93m'
G = '\033[92m'
M = '\033[95m'
X = '\033[0m'
B = '\033[1m'

def led_sweep(duration=2.0):
    """Simple LED sweep animation"""
    bars = 20
    pos = 0
    direction = 1
    start = time.time()
    
    while time.time() - start < duration:
        line = ['░'] * bars
        if 0 <= pos < bars:
            line[pos] = f'{R}█{X}'
            if pos - 1 >= 0:
                line[pos - 1] = f'{M}▓{X}'
            if pos + 1 < bars:
                line[pos + 1] = f'{M}▓{X}'
        
        print(f'\r{C}║{X}{"".join(line)}{C}║{X}', end='', flush=True)
        
        pos += direction
        if pos >= bars - 1:
            direction = -1
        elif pos <= 0:
            direction = 1
        
        time.sleep(0.05)
    
    print(f'\n{G}✓ Ready{X}\n')

def play_kit():
    """Play Kit voice"""
    print(f'\n{C}{B}{"="*60}{X}')
    print(f'{C}{B}{"🎙️  GATE - KIT VOICE  🎙️":^60}{X}')
    print(f'{C}{B}{"="*60}{X}\n')
    
    # Check file
    if not os.path.exists('clip_0001.wav'):
        print(f'{R}✗ Kit voice file not found!{X}\n')
        return False
    
    size_mb = os.path.getsize('clip_0001.wav') / (1024 * 1024)
    print(f'{G}✓ Kit Voice Ready{X}')
    print(f'  File: clip_0001.wav')
    print(f'  Size: {size_mb:.2f} MB\n')
    
    # LED animation
    print(f'{Y}[Initializing Kit Voice]{X}')
    led_sweep(2.0)
    
    # Play voice
    print(f'{C}{B}[KIT SPEAKING]{X}')
    print(f'{C}► Playing Kit voice sample...{X}\n')
    
    try:
        abs_path = os.path.abspath('clip_0001.wav')
        result = subprocess.run(
            ['powershell', '-c', 
             f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()'],
            timeout=120,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f'{G}✓ Playback complete{X}\n')
            print(f'{Y}[Voice Output Complete]{X}')
            led_sweep(1.5)
            return True
        else:
            print(f'{R}✗ Playback failed{X}')
            if result.stderr:
                print(f'{Y}Error: {result.stderr[:200]}{X}')
            return False
    
    except Exception as e:
        print(f'{R}✗ Error: {e}{X}')
        return False

if __name__ == '__main__':
    play_kit()
    print(f'{C}{"="*60}{X}')
    print(f'{C}{B}KIT Voice System - Ready{X}')
    print(f'{C}{"="*60}{X}\n')
