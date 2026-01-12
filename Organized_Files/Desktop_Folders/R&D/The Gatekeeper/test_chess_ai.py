# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# TRADEMARK NOTICE: "Omega" and "Ω" are trademarks of Red Post Farms, LLC.
#
# Test Chess AI vs AI with visible output

import sys
import json
import random
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from game_hub_final import Chess

GAMES = Path(r'D:\RPF_BRAIN\The Gatekeeper\games')
GAMES.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 70)
    print("CHESS - AI vs AI")
    print("=" * 70)
    print("\nStarting new game...")
    print("AI (White) vs AI (Black)")
    print("=" * 70)
    
    # Create chess game
    game = Chess()
    game.players = ['ai', 'ai']
    
    # Log game start
    from datetime import datetime
    LOG_FILE = Path(r'D:\RPF_BRAIN\The Gatekeeper\games') / 'ai_game.log'
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"=== GAME START === | {timestamp}\n")
            f.write(f"{'='*70}\n\n")
    except:
        pass
    
    game.print_board()
    
    # Play game
    move_count = 0
    max_moves = 50  # Limit for demo
    invalid_move_count = 0
    max_invalid = 10  # Prevent infinite loops
    
    print("\n[Game] Starting AI vs AI match...\n")
    time.sleep(0.2)
    
    while move_count < max_moves and game.running:
        # AI turn
        if game.players[game.turn] == 'ai':
            ai_move = game.choose()
            
            if ai_move and ai_move != 'pass':
                player_name = "AI (White)" if game.turn == 0 else "AI (Black)"
                print(f"[{player_name}] Move {move_count + 1}: {ai_move}")
                
                move_success = False
                # Parse move format (e2e4 or e2->e4)
                if '->' in ai_move:
                    fr, to = ai_move.split('->')
                    move_success = game.move(fr, to)
                elif len(ai_move) >= 4:
                    # Format: e2e4 (4 chars)
                    move_success = game.move(ai_move[:2], ai_move[2:4])
                
                if move_success:
                    move_count += 1
                    invalid_move_count = 0  # Reset invalid counter
                    game.print_board()
                    game.save_state()
                    
                    # Faster for AI vs AI - reduced delay
                    time.sleep(0.15)
                else:
                    invalid_move_count += 1
                    if invalid_move_count >= max_invalid:
                        print(f"[Error] Too many invalid moves ({invalid_move_count}). Ending game.")
                        break
                    # Silently retry with different move
                    time.sleep(0.05)
            else:
                print("[Game] No valid moves available. Game over.")
                break
    
    print("\n" + "=" * 70)
    print(f"[Game] Completed {move_count} moves.")
    if invalid_move_count > 0:
        print(f"[Game] Had {invalid_move_count} invalid move attempts.")
    print("[Game] Moves learned and saved to memory.")
    print("=" * 70)
    
    # Save final state
    game.learn()
    game.save_state()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Game] Interrupted by user.")
    except Exception as e:
        print(f"\n[Error] {e}")
        import traceback
        traceback.print_exc()
