# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Chess Game Replay System
# Logs saved forever. Replay like watching a security tape.

import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

GAMES = Path(r'D:\RPF_BRAIN\The Gatekeeper\games')
GAMES.mkdir(parents=True, exist_ok=True)
LOG_FILE = GAMES / 'ai_game.log'

def print_board_from_state(board_state: List[List[str]]) -> None:
    """
    Print chess board from board state.
    
    Args:
        board_state: 2D list representing the chess board
    """
    print("\n" + "=" * 50)
    print("   a b c d e f g h")
    print("  " + "-" * 17)
    for i, row in enumerate(board_state):
        rank = 8 - i
        row_str = ' '.join(p if p != '.' else ' ' for p in row)
        print(f"{rank}| {row_str}")
    print("=" * 50)

def replay_full_game() -> None:
    """
    Replay entire last AI vs AI game - clean, timestamped, no lag.
    
    Loads and replays the complete game from the log file.
    """
    if not LOG_FILE.exists():
        print("=" * 70)
        print("CHESS REPLAY - No games logged yet")
        print("=" * 70)
        print("\nNo AI vs AI games have been played yet.")
        print("Play an AI vs AI game first, then replay it.\n")
        return
    
    print("=" * 70)
    print("CHESS REPLAY - Full Game")
    print("=" * 70)
    print(f"\nLoading log: {LOG_FILE}")
    print("Playing back line by line. No lag. Like watching a security tape.\n")
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("Log file is empty.")
            return
        
        # Parse log entries
        entries = []
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("=== GAME START ==="):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {
                    'type': 'game_start',
                    'timestamp': line.split(' | ')[1] if ' | ' in line else ''
                }
            elif line.startswith("Move #"):
                if current_entry:
                    entries.append(current_entry)
                parts = line.split(' | ')
                current_entry = {
                    'type': 'move',
                    'move_num': parts[0].split('#')[1].split(' ')[0] if '#' in parts[0] else '',
                    'timestamp': parts[1] if len(parts) > 1 else '',
                    'player': parts[2] if len(parts) > 2 else '',
                    'move': parts[3] if len(parts) > 3 else ''
                }
            elif line.startswith("Board State:"):
                current_entry['board_state'] = []
            elif line.startswith("[") and 'board_state' in current_entry:
                # Parse board row
                row_str = line.strip('[]')
                row = [c if c != ' ' else '.' for c in row_str.split(', ')]
                current_entry['board_state'].append(row)
        
        if current_entry:
            entries.append(current_entry)
        
        # Replay entries
        move_count = 0
        for entry in entries:
            if entry['type'] == 'game_start':
                print(f"\n{'='*70}")
                print(f"GAME STARTED | {entry.get('timestamp', 'Unknown time')}")
                print(f"{'='*70}")
            elif entry['type'] == 'move':
                move_count += 1
                print(f"\n[Move #{move_count}] {entry.get('player', 'Unknown')} | {entry.get('move', '')}")
                print(f"Timestamp: {entry.get('timestamp', 'Unknown')}")
                
                if 'board_state' in entry and entry['board_state']:
                    print_board_from_state(entry['board_state'])
                
                # Fast playback - minimal delay
                time.sleep(0.1)
        
        print(f"\n{'='*70}")
        print(f"REPLAY COMPLETE - {move_count} moves replayed")
        print(f"{'='*70}\n")
        
    except (IOError, OSError) as e:
        print(f"  ❌ File I/O error: {e}")
    except (ValueError, KeyError) as e:
        print(f"  ❌ Data parsing error: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error replaying game: {e}")
        import traceback
        traceback.print_exc()

def replay_last_n_moves(n: int = 10) -> None:
    """
    Replay last N moves - scrolls them, shows evolution.
    
    Args:
        n: Number of moves to replay (default: 10)
    """
    if not LOG_FILE.exists():
        print("=" * 70)
        print("CHESS REPLAY - No games logged yet")
        print("=" * 70)
        print("\nNo AI vs AI games have been played yet.")
        return
    
    print("=" * 70)
    print(f"CHESS REPLAY - Last {n} Moves")
    print("=" * 70)
    print(f"\nLoading last {n} moves from log...")
    print("Showing evolution. AI learns. You learn too.\n")
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("Log file is empty.")
            return
        
        # Parse last N move entries
        entries = []
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Move #"):
                if current_entry:
                    entries.append(current_entry)
                parts = line.split(' | ')
                current_entry = {
                    'type': 'move',
                    'move_num': parts[0].split('#')[1].split(' ')[0] if '#' in parts[0] else '',
                    'timestamp': parts[1] if len(parts) > 1 else '',
                    'player': parts[2] if len(parts) > 2 else '',
                    'move': parts[3] if len(parts) > 3 else ''
                }
            elif line.startswith("Board State:"):
                current_entry['board_state'] = []
            elif line.startswith("[") and 'board_state' in current_entry:
                row_str = line.strip('[]')
                row = [c if c != ' ' else '.' for c in row_str.split(', ')]
                current_entry['board_state'].append(row)
        
        if current_entry:
            entries.append(current_entry)
        
        # Get last N moves
        move_entries = [e for e in entries if e.get('type') == 'move']
        last_n = move_entries[-n:] if len(move_entries) > n else move_entries
        
        print(f"Found {len(move_entries)} total moves. Showing last {len(last_n)}:\n")
        
        # Replay last N
        for i, entry in enumerate(last_n, 1):
            move_num = entry.get('move_num', str(len(move_entries) - len(last_n) + i))
            print(f"\n[Move #{move_num}] {entry.get('player', 'Unknown')} | {entry.get('move', '')}")
            print(f"Timestamp: {entry.get('timestamp', 'Unknown')}")
            
            if 'board_state' in entry and entry['board_state']:
                print_board_from_state(entry['board_state'])
            
            # Fast scroll
            time.sleep(0.08)
        
        print(f"\n{'='*70}")
        print(f"LAST {len(last_n)} MOVES COMPLETE")
        print(f"{'='*70}\n")
        
    except (IOError, OSError) as e:
        print(f"  ❌ File I/O error: {e}")
    except (ValueError, KeyError) as e:
        print(f"  ❌ Data parsing error: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error replaying moves: {e}")
        import traceback
        traceback.print_exc()

def main() -> None:
    """
    Main entry point - parse command line arguments.
    
    Supports:
    - 'full' or 'all': Replay full game
    - 'last N': Replay last N moves
    - Default: Replay full game
    """
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "full" or cmd == "all":
            replay_full_game()
        elif cmd.startswith("last"):
            # Extract number if present
            try:
                n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            except:
                n = 10
            replay_last_n_moves(n)
        else:
            # Default: full replay
            replay_full_game()
    else:
        # Default: full replay
        replay_full_game()

if __name__ == '__main__':
    main()

