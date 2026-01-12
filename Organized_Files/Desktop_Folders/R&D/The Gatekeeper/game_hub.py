# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.

# GAME HUB v1
# Chess, Shogi, Go – terminal, interactive, no GUI. Pure logic.

import os
import sys
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GAMES = Path(r'D:\RPF_BRAIN\The Gatekeeper\games')
GAMES.mkdir(parents=True, exist_ok=True)
STATE = GAMES / 'last_game.json'


class GameEngine:
    """Base game engine."""
    
    def __init__(self):
        self.board = self.reset_board()
        self.turn = 'white'
        self.history: List[Dict[str, Any]] = []
        self.running = True
    
    def reset_board(self):
        """Reset board to starting position."""
        raise NotImplementedError
    
    def move(self, fr: str, to: str) -> bool:
        """Make a move. Returns True if valid."""
        raise NotImplementedError
    
    def print_board(self):
        """Print board to terminal."""
        raise NotImplementedError
    
    def quit(self):
        """Quit game."""
        self.running = False
    
    def save(self):
        """Save game state."""
        game_state = {
            'type': self.__class__.__name__,
            'board': self.board,
            'turn': self.turn,
            'history': self.history
        }
        with open(STATE, 'w', encoding='utf-8') as f:
            json.dump(game_state, f, indent=2)
        print(f"[Saved] Game state saved to {STATE}")
    
    def load(self, state: Dict[str, Any]):
        """Load game state."""
        self.board = state.get('board', self.reset_board())
        self.turn = state.get('turn', 'white')
        self.history = state.get('history', [])
        print(f"[Loaded] {state.get('type', 'Game')} - Turn: {self.turn} - Moves: {len(self.history)}")


class Chess(GameEngine):
    """Chess game - terminal version."""
    
    def reset_board(self) -> List[List[str]]:
        """Initialize chess board."""
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Row 8 (black back rank)
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Row 7 (black pawns)
            ['' for _ in range(8)],  # Row 6
            ['' for _ in range(8)],  # Row 5
            ['' for _ in range(8)],  # Row 4
            ['' for _ in range(8)],  # Row 3
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # Row 2 (white pawns)
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']   # Row 1 (white back rank)
        ]
    
    def print_board(self):
        """Print chess board."""
        print("\n" + "=" * 40)
        print("   a b c d e f g h")
        print("  " + "-" * 17)
        for i, row in enumerate(self.board):
            rank = 8 - i
            row_str = ' '.join(p if p else '.' for p in row)
            print(f"{rank}| {row_str}")
        print("=" * 40)
        print(f"Turn: {self.turn.title()}")
        print(f"Moves: {len(self.history)}")
    
    def move(self, fr: str, to: str) -> bool:
        """Make a chess move."""
        try:
            # Parse squares (e.g., "e2" -> row=6, col=4)
            fr_col = ord(fr[0].lower()) - ord('a')
            fr_row = 8 - int(fr[1])
            to_col = ord(to[0].lower()) - ord('a')
            to_row = 8 - int(to[1])
            
            # Validate bounds
            if not (0 <= fr_row < 8 and 0 <= fr_col < 8 and 
                    0 <= to_row < 8 and 0 <= to_col < 8):
                print("[Error] Invalid square")
                return False
            
            piece = self.board[fr_row][fr_col]
            if not piece:
                print("[Error] No piece at source square")
                return False
            
            # Check turn (uppercase = white, lowercase = black)
            is_white = piece.isupper()
            if (is_white and self.turn != 'white') or (not is_white and self.turn != 'black'):
                print(f"[Error] Not {self.turn}'s turn")
                return False
            
            # Make move (simplified - no validation of move legality)
            captured = self.board[to_row][to_col]
            self.board[to_row][to_col] = piece
            self.board[fr_row][fr_col] = ''
            
            move_str = f"{fr}->{to}"
            if captured:
                move_str += f" (captures {captured})"
            
            print(f"[Chess] Move: {move_str}")
            self.history.append({'move': move_str, 'turn': self.turn})
            
            # Switch turn
            self.turn = 'black' if self.turn == 'white' else 'white'
            return True
            
        except (ValueError, IndexError) as e:
            print(f"[Error] Invalid move format: {e}")
            return False


class Shogi(GameEngine):
    """Shogi game - terminal version."""
    
    def reset_board(self) -> List[List[str]]:
        """Initialize shogi board (9x9)."""
        return [
            ['L', 'N', 'S', 'G', 'K', 'G', 'S', 'N', 'L'],  # Row 0 (sente back rank)
            ['', 'R', '', '', '', '', '', 'B', ''],           # Row 1
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],   # Row 2 (sente pawns)
            ['' for _ in range(9)],  # Row 3
            ['' for _ in range(9)],  # Row 4
            ['' for _ in range(9)],  # Row 5
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],   # Row 6 (gote pawns)
            ['', 'b', '', '', '', '', '', 'r', ''],           # Row 7
            ['l', 'n', 's', 'g', 'k', 'g', 's', 'n', 'l']    # Row 8 (gote back rank)
        ]
    
    def print_board(self):
        """Print shogi board."""
        print("\n" + "=" * 50)
        print("   9 8 7 6 5 4 3 2 1")
        print("  " + "-" * 18)
        for i, row in enumerate(self.board):
            rank = 9 - i
            row_str = ' '.join(p if p else '.' for p in row)
            print(f"{rank}| {row_str}")
        print("=" * 50)
        print(f"Turn: {self.turn.title()}")
        print(f"Moves: {len(self.history)}")
    
    def move(self, fr: str, to: str) -> bool:
        """Make a shogi move."""
        try:
            # Parse squares (e.g., "76" -> row=3, col=5 for 9x9)
            fr_col = 9 - int(fr[0])
            fr_row = int(fr[1]) - 1
            to_col = 9 - int(to[0])
            to_row = int(to[1]) - 1
            
            # Validate bounds
            if not (0 <= fr_row < 9 and 0 <= fr_col < 9 and 
                    0 <= to_row < 9 and 0 <= to_col < 9):
                print("[Error] Invalid square")
                return False
            
            piece = self.board[fr_row][fr_col]
            if not piece:
                print("[Error] No piece at source square")
                return False
            
            # Check turn (uppercase = sente, lowercase = gote)
            is_sente = piece.isupper()
            current_turn_is_sente = self.turn == 'white'  # white = sente for simplicity
            if (is_sente and not current_turn_is_sente) or (not is_sente and current_turn_is_sente):
                print(f"[Error] Not {self.turn}'s turn")
                return False
            
            # Make move
            captured = self.board[to_row][to_col]
            self.board[to_row][to_col] = piece
            self.board[fr_row][fr_col] = ''
            
            move_str = f"{fr}->{to}"
            if captured:
                move_str += f" (captures {captured})"
            
            print(f"[Shogi] Move: {move_str}")
            self.history.append({'move': move_str, 'turn': self.turn})
            
            # Switch turn
            self.turn = 'black' if self.turn == 'white' else 'white'
            return True
            
        except (ValueError, IndexError) as e:
            print(f"[Error] Invalid move format (use format like '76' for column 7, row 6): {e}")
            return False


class Go(GameEngine):
    """Go game - terminal version."""
    
    def reset_board(self) -> List[List[str]]:
        """Initialize Go board (19x19, empty)."""
        return [['' for _ in range(19)] for _ in range(19)]
    
    def print_board(self):
        """Print Go board."""
        print("\n" + "=" * 60)
        print("   ", end="")
        for i in range(19):
            print(f"{i+1:2}", end="")
        print()
        print("  " + "-" * 38)
        for i, row in enumerate(self.board):
            rank = 19 - i
            row_str = ' '.join(p if p else '.' for p in row)
            print(f"{rank:2}| {row_str}")
        print("=" * 60)
        print(f"Turn: {self.turn.title()}")
        print(f"Moves: {len(self.history)}")
    
    def move(self, fr: str, to: str) -> bool:
        """Make a Go move. 'fr' ignored, 'to' is intersection."""
        try:
            # Parse intersection (e.g., "D4" -> row, col)
            col = ord(to[0].upper()) - ord('A')
            row = 19 - int(to[1:]) if len(to) > 1 else 0
            
            # Alternative: numeric format "4,4"
            if ',' in to:
                col, row = map(int, to.split(','))
                row = 18 - row  # Flip row
            
            if not (0 <= row < 19 and 0 <= col < 19):
                print("[Error] Invalid intersection")
                return False
            
            if self.board[row][col]:
                print("[Error] Intersection already occupied")
                return False
            
            # Place stone
            stone = 'W' if self.turn == 'white' else 'B'
            self.board[row][col] = stone
            
            move_str = f"Place {stone} at {to}"
            print(f"[Go] {move_str}")
            self.history.append({'move': move_str, 'turn': self.turn})
            
            # Switch turn
            self.turn = 'black' if self.turn == 'white' else 'white'
            return True
            
        except (ValueError, IndexError) as e:
            print(f"[Error] Invalid move format (use format like 'D4' or '4,4'): {e}")
            return False


def load_last_game() -> Optional[GameEngine]:
    """Load last saved game."""
    if not STATE.exists():
        return None
    
    try:
        with open(STATE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        game_type = state.get('type', '')
        
        if game_type == 'Chess':
            game = Chess()
        elif game_type == 'Shogi':
            game = Shogi()
        elif game_type == 'Go':
            game = Go()
        else:
            return None
        
        game.load(state)
        return game
    except Exception as e:
        print(f"[Error] Failed to load game: {e}")
        return None


def main():
    """Main game hub."""
    print("=" * 60)
    print("GAME HUB v1")
    print("=" * 60)
    print("\nGames:")
    print("  1. Chess")
    print("  2. Shogi")
    print("  3. Go")
    print("\nCommands:")
    print("  n = new game")
    print("  q = quit")
    print("  save = save game state")
    print("  <move> = make move (e.g., 'e2 e4' for chess)")
    print("=" * 60)
    
    # Try to load last game
    game: Optional[GameEngine] = load_last_game()
    if game:
        print(f"\n[Loaded] Last game: {game.__class__.__name__}")
        print(f"         Turn: {game.turn} - Moves: {len(game.history)}")
        print("         Press Enter to continue...")
        input()
        game.print_board()
    else:
        print("\n[New] No saved game. Choose game (1, 2, or 3):")
        choice = input().strip()
        
        if choice == '1':
            game = Chess()
        elif choice == '2':
            game = Shogi()
        elif choice == '3':
            game = Go()
        else:
            print("[Error] Invalid choice")
            return
        
        game.print_board()
    
    # Main game loop
    while game.running:
        print("\n> ", end="")
        command = input().strip().lower()
        
        if command == 'q':
            game.quit()
            print("[Quit] Game ended")
        elif command == 'n':
            print("[New] Choose game (1=Chess, 2=Shogi, 3=Go):")
            choice = input().strip()
            if choice == '1':
                game = Chess()
            elif choice == '2':
                game = Shogi()
            elif choice == '3':
                game = Go()
            game.print_board()
        elif command == 'save':
            game.save()
        elif ' ' in command:
            # Move command (e.g., "e2 e4")
            parts = command.split()
            if len(parts) == 2:
                fr, to = parts
                if game.move(fr, to):
                    game.print_board()
                    game.save()  # Auto-save after each move
            else:
                print("[Error] Move format: <from> <to> (e.g., 'e2 e4')")
        else:
            print("[Error] Unknown command. Type 'q' to quit, 'n' for new game, 'save' to save")
    
    print("\n[Game Hub] Closed.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Game Hub] Interrupted. Goodbye.")
    except Exception as e:
        print(f"\n[Error] {e}")
        import traceback
        traceback.print_exc()

