# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.

# GAME HUB FINAL v3
# Solo AI vs AI, Human vs AI, Human vs Human
# All boards learn from every move. No graphics. Pure logic.

import os
import json
import random
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GAMES = Path(r'D:\RPF_BRAIN\The Gatekeeper\games')
GAMES.mkdir(parents=True, exist_ok=True)
LEARN = GAMES / 'learn.json'
STATE = GAMES / 'last_game.json'
LOG_FILE = GAMES / 'ai_game.log'


class Engine:
    """Base game engine with learning."""
    
    def __init__(self) -> None:
        """Initialize the game engine."""
        self.running = True
        self.mode = 'chess'
        self.players = ['human', 'human']  # p0, p1
        self.history: List[str] = []
        self.turn = 0
        self.board = []
        
        # Load learning memory
        if LEARN.exists():
            try:
                self.memory = json.loads(LEARN.read_text())
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"  ⚠️  Could not load learning memory: {e}")
                self.memory = {}
        else:
            self.memory = {}  # move → win count
    
    def choose(self) -> str:
        """AI move for non-human player."""
        if self.players[self.turn] == 'ai':
            moves = self.legal_moves()
            if not moves:
                return 'pass'
            
            # Use learned moves if available (prefer moves with higher win counts)
            scored_moves = []
            for move in moves:
                score = self.memory.get(move, 0)
                scored_moves.append((score, move))
            
            # Prefer learned winning moves, but add randomness
            scored_moves.sort(reverse=True)
            if scored_moves and random.random() < 0.7:  # 70% chance to pick best
                return scored_moves[0][1]
            else:
                return random.choice(moves)
        
        return ''
    
    def learn(self) -> None:
        """After game, count winning moves."""
        # For now, just increment all moves played (winner's moves get more later)
        for move in self.history:
            self.memory[move] = self.memory.get(move, 0) + 1
        
        with open(LEARN, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2)
        print("[Learned] Move patterns saved to memory.")
    
    def quit(self) -> None:
        """Quit game."""
        self.save_state()
        self.learn()
        self.running = False
    
    def save_state(self) -> None:
        """Save game state."""
        state = {
            'mode': self.mode,
            'players': self.players,
            'history': self.history,
            'turn': self.turn,
            'board': self.board
        }
        try:
            with open(STATE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            print(f"  ⚠️  Could not save game state: {e}")
        except Exception as e:
            print(f"  ⚠️  Unexpected error saving state: {e}")
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load game state."""
        self.mode = state.get('mode', 'chess')
        self.players = state.get('players', ['human', 'human'])
        self.history = state.get('history', [])
        self.turn = state.get('turn', 0)
        self.board = state.get('board', [])
    
    def parse_input(self, s: str) -> str:
        """Parse user input."""
        s = s.strip().lower()
        
        if s in ['q', 'quit', 'exit']:
            self.quit()
            return ''
        elif s == 'n':
            self.setup()
            return ''
        elif s == 'ai':
            # Toggle opponent
            self.players[1] = 'ai' if self.players[1] == 'human' else 'human'
            print(f"[Mode] Opponent now: {self.players[1].upper()}")
            return ''
        elif s == 'solo':
            self.mode = self.mode  # Keep current mode
            self.players = ['ai', 'ai']
            self.setup()
            print("[Mode] Solo AI vs AI")
            return ''
        elif s == 'shogi':
            return 'switch_shogi'
        elif s == 'go':
            return 'switch_go'
        elif s == 'chess':
            return 'switch_chess'
        elif s == 'done':
            # Commit to memory
            self.learn()
            print("[Done] Moves committed to memory.")
            return ''
        else:
            return s
    
    def legal_moves(self) -> List[str]:
        """Get legal moves (to be overridden)."""
        return []
    
    def setup(self) -> None:
        """Setup game (to be overridden)."""
        pass
    
    def print_board(self) -> None:
        """Print board (to be overridden)."""
        pass
    
    def move(self, fr: str, to: str) -> bool:
        """Make move (to be overridden)."""
        return False


class Chess(Engine):
    """Chess game."""
    
    def __init__(self) -> None:
        """Initialize chess game."""
        super().__init__()
        self.mode = 'chess'
        self.setup()
    
    def setup(self) -> None:
        """Initialize chess board."""
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Row 8 (black)
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Row 7
            ['.' for _ in range(8)],  # Row 6
            ['.' for _ in range(8)],  # Row 5
            ['.' for _ in range(8)],  # Row 4
            ['.' for _ in range(8)],  # Row 3
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # Row 2
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']   # Row 1 (white)
        ]
        self.turn = 0
        self.history = []
        self.print_board()
    
    def print_board(self) -> None:
        """Print chess board."""
        print("\n" + "=" * 50)
        print("   a b c d e f g h")
        print("  " + "-" * 17)
        for i, row in enumerate(self.board):
            rank = 8 - i
            row_str = ' '.join(p if p != '.' else ' ' for p in row)
            print(f"{rank}| {row_str}")
        print("=" * 50)
        player_names = {
            'human': 'Human',
            'ai': 'AI'
        }
        p0 = player_names.get(self.players[0], 'Human')
        p1 = player_names.get(self.players[1], 'Human')
        print(f"Turn: {'White' if self.turn == 0 else 'Black'} ({p0 if self.turn == 0 else p1})")
        print(f"Moves: {len(self.history)}")
    
    def legal_moves(self) -> List[str]:
        """Get legal moves - properly generate valid moves."""
        moves = []
        piece_chars = 'PNBRQK' if self.turn == 0 else 'pnbrqk'
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece in piece_chars:
                    # Convert board position to chess notation
                    square = f"{chr(97+col)}{8-row}"
                    
                    # Generate moves based on piece type
                    if piece.lower() == 'p':  # Pawn
                        if self.turn == 0:  # White (moves up, row decreases)
                            # Single move forward
                            if row > 0 and self.board[row-1][col] == '.':
                                target = f"{chr(97+col)}{8-(row-1)}"
                                moves.append(f"{square}{target}")
                            # Double move from starting position
                            if row == 6 and self.board[row-1][col] == '.' and self.board[row-2][col] == '.':
                                target = f"{chr(97+col)}{8-(row-2)}"
                                moves.append(f"{square}{target}")
                            # Capture diagonally left
                            if (row > 0 and col > 0 and self.board[row-1][col-1] != '.' and
                                self.board[row-1][col-1] not in 'PNBRQK.'):
                                target = f"{chr(97+col-1)}{8-(row-1)}"
                                moves.append(f"{square}{target}")
                            # Capture diagonally right
                            if (row > 0 and col < 7 and self.board[row-1][col+1] != '.' and
                                self.board[row-1][col+1] not in 'PNBRQK.'):
                                target = f"{chr(97+col+1)}{8-(row-1)}"
                                moves.append(f"{square}{target}")
                        else:  # Black (moves down, row increases)
                            # Single move forward
                            if row < 7 and self.board[row+1][col] == '.':
                                target = f"{chr(97+col)}{8-(row+1)}"
                                moves.append(f"{square}{target}")
                            # Double move from starting position
                            if row == 1 and self.board[row+1][col] == '.' and self.board[row+2][col] == '.':
                                target = f"{chr(97+col)}{8-(row+2)}"
                                moves.append(f"{square}{target}")
                            # Capture diagonally left
                            if (row < 7 and col > 0 and self.board[row+1][col-1] != '.' and
                                self.board[row+1][col-1] not in 'pnbrqk.'):
                                target = f"{chr(97+col-1)}{8-(row+1)}"
                                moves.append(f"{square}{target}")
                            # Capture diagonally right
                            if (row < 7 and col < 7 and self.board[row+1][col+1] != '.' and
                                self.board[row+1][col+1] not in 'pnbrqk.'):
                                target = f"{chr(97+col+1)}{8-(row+1)}"
                                moves.append(f"{square}{target}")
                    
                    elif piece.lower() == 'r':  # Rook
                        # Horizontal and vertical moves
                        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                            for i in range(1, 8):
                                new_row, new_col = row + dr*i, col + dc*i
                                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                                    break
                                target_piece = self.board[new_row][new_col]
                                if target_piece == '.':
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                                elif (self.turn == 0 and target_piece.islower()) or (self.turn == 1 and target_piece.isupper()):
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                                    break
                                else:
                                    break
                    
                    elif piece.lower() == 'n':  # Knight
                        for dr, dc in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < 8 and 0 <= new_col < 8:
                                target_piece = self.board[new_row][new_col]
                                if target_piece == '.' or ((self.turn == 0 and target_piece.islower()) or (self.turn == 1 and target_piece.isupper())):
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                    
                    elif piece.lower() == 'b':  # Bishop
                        # Diagonal moves
                        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                            for i in range(1, 8):
                                new_row, new_col = row + dr*i, col + dc*i
                                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                                    break
                                target_piece = self.board[new_row][new_col]
                                if target_piece == '.':
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                                elif (self.turn == 0 and target_piece.islower()) or (self.turn == 1 and target_piece.isupper()):
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                                    break
                                else:
                                    break
                    
                    elif piece.lower() == 'q':  # Queen
                        # Combines rook and bishop moves
                        for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                            for i in range(1, 8):
                                new_row, new_col = row + dr*i, col + dc*i
                                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                                    break
                                target_piece = self.board[new_row][new_col]
                                if target_piece == '.':
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                                elif (self.turn == 0 and target_piece.islower()) or (self.turn == 1 and target_piece.isupper()):
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
                                    break
                                else:
                                    break
                    
                    elif piece.lower() == 'k':  # King
                        # One square in any direction
                        for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < 8 and 0 <= new_col < 8:
                                target_piece = self.board[new_row][new_col]
                                if target_piece == '.' or ((self.turn == 0 and target_piece.islower()) or (self.turn == 1 and target_piece.isupper())):
                                    moves.append(f"{square}{chr(97+new_col)}{8-new_row}")
        
        return moves if moves else []
    
    def _log_move(self, move_str: str, move_num: int) -> None:
        """
        Log move to ai_game.log with timestamp and board state.
        
        Args:
            move_str: The move string (e.g., "e2->e4")
            move_num: The move number
        """
        if self.players != ['ai', 'ai']:
            return  # Only log AI vs AI games
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            player = "AI (White)" if self.turn == 0 else "AI (Black)"
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"Move #{move_num} | {timestamp} | {player} | {move_str}\n")
                f.write("Board State:\n")
                
                # Log board state row by row
                for row in self.board:
                    row_str = ', '.join(p if p != '.' else ' ' for p in row)
                    f.write(f"[{row_str}]\n")
                f.write("\n")
        except Exception as e:
            # Silent fail - don't interrupt game for logging issues
            pass
    
    def move(self, fr: str, to: str) -> bool:
        """Make chess move."""
        try:
            fr_col = ord(fr[0].lower()) - ord('a')
            fr_row = 8 - int(fr[1])
            to_col = ord(to[0].lower()) - ord('a')
            to_row = 8 - int(to[1])
            
            if not (0 <= fr_row < 8 and 0 <= fr_col < 8 and 
                    0 <= to_row < 8 and 0 <= to_col < 8):
                return False
            
            piece = self.board[fr_row][fr_col]
            if piece == '.':
                return False
            
            # Check turn
            is_white = piece.isupper()
            if (is_white and self.turn != 0) or (not is_white and self.turn != 1):
                return False
            
            # Make move
            self.board[to_row][to_col] = piece
            self.board[fr_row][fr_col] = '.'
            
            move_str = f"{fr}->{to}"
            self.history.append(move_str)
            
            # Log move before turn change
            move_num = len(self.history)
            self._log_move(move_str, move_num)
            
            self.turn = 1 - self.turn
            return True
            
        except (ValueError, IndexError):
            return False


class Shogi(Engine):
    """Shogi game."""
    
    def __init__(self) -> None:
        """Initialize shogi game."""
        super().__init__()
        self.mode = 'shogi'
        self.setup()
    
    def setup(self) -> None:
        """Initialize shogi board."""
        self.board = [
            ['L', 'N', 'S', 'G', 'K', 'G', 'S', 'N', 'L'],  # Row 0
            ['.', 'R', '.', '.', '.', '.', '.', 'B', '.'],   # Row 1
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],   # Row 2
            ['.' for _ in range(9)],  # Row 3
            ['.' for _ in range(9)],  # Row 4
            ['.' for _ in range(9)],  # Row 5
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],   # Row 6
            ['.', 'b', '.', '.', '.', '.', '.', 'r', '.'],   # Row 7
            ['l', 'n', 's', 'g', 'k', 'g', 's', 'n', 'l']   # Row 8
        ]
        self.turn = 0
        self.history = []
        self.print_board()
    
    def print_board(self) -> None:
        """Print shogi board."""
        print("\n" + "=" * 60)
        print("   9 8 7 6 5 4 3 2 1")
        print("  " + "-" * 18)
        for i, row in enumerate(self.board):
            rank = 9 - i
            row_str = ' '.join(p if p != '.' else ' ' for p in row)
            print(f"{rank}| {row_str}")
        print("=" * 60)
        player_names = {
            'human': 'Human',
            'ai': 'AI'
        }
        p0 = player_names.get(self.players[0], 'Human')
        p1 = player_names.get(self.players[1], 'Human')
        print(f"Turn: {'Sente' if self.turn == 0 else 'Gote'} ({p0 if self.turn == 0 else p1})")
        print(f"Moves: {len(self.history)}")
    
    def legal_moves(self) -> List[str]:
        """Get legal moves (simplified)."""
        moves = []
        piece_chars = 'PNBRQKGSL' if self.turn == 0 else 'pnbrqkgsl'
        
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece in piece_chars:
                    # Generate basic forward moves
                    if piece.lower() == 'p':  # Pawn
                        if self.turn == 0 and row > 0 and self.board[row-1][col] == '.':
                            moves.append(f"{9-col}{row+1}{9-col}{row}")
                        elif self.turn == 1 and row < 8 and self.board[row+1][col] == '.':
                            moves.append(f"{9-col}{row+1}{9-col}{row+2}")
        
        return moves if moves else ['76->75', '34->35']
    
    def move(self, move_str: str) -> bool:
        """
        Make shogi move (format: "76->75" or "765").
        
        Args:
            move_str: The move string
            
        Returns:
            True if move was successful, False otherwise
        """
        try:
            if '->' in move_str:
                fr, to = move_str.split('->')
            elif len(move_str) >= 4:
                fr = move_str[:2]
                to = move_str[2:4]
            else:
                return False
            
            fr_col = 9 - int(fr[0])
            fr_row = int(fr[1]) - 1
            to_col = 9 - int(to[0])
            to_row = int(to[1]) - 1
            
            if not (0 <= fr_row < 9 and 0 <= fr_col < 9 and 
                    0 <= to_row < 9 and 0 <= to_col < 9):
                return False
            
            piece = self.board[fr_row][fr_col]
            if piece == '.':
                return False
            
            # Make move
            self.board[to_row][to_col] = piece
            self.board[fr_row][fr_col] = '.'
            
            move_str_full = f"{fr}->{to}"
            self.history.append(move_str_full)
            self.turn = 1 - self.turn
            return True
            
        except (ValueError, IndexError):
            return False


class Go(Engine):
    """Go game."""
    
    def __init__(self) -> None:
        """Initialize Go game."""
        super().__init__()
        self.mode = 'go'
        self.setup()
    
    def setup(self) -> None:
        """Initialize Go board."""
        self.board = [['.' for _ in range(19)] for _ in range(19)]
        self.turn = 0
        self.history = []
        self.print_board()
    
    def print_board(self) -> None:
        """Print Go board."""
        print("\n" + "=" * 80)
        print("   ", end="")
        for i in range(19):
            print(f"{i+1:2}", end="")
        print()
        print("  " + "-" * 38)
        for i, row in enumerate(self.board):
            rank = 19 - i
            row_str = ' '.join(p if p != '.' else ' ' for p in row)
            print(f"{rank:2}| {row_str}")
        print("=" * 80)
        player_names = {
            'human': 'Human',
            'ai': 'AI'
        }
        p0 = player_names.get(self.players[0], 'Human')
        p1 = player_names.get(self.players[1], 'Human')
        print(f"Turn: {'Black' if self.turn == 0 else 'White'} ({p0 if self.turn == 0 else p1})")
        print(f"Moves: {len(self.history)}")
    
    def legal_moves(self) -> List[str]:
        """Get legal moves (all empty intersections)."""
        moves = []
        for row in range(19):
            for col in range(19):
                if self.board[row][col] == '.':
                    moves.append(f"{chr(65+col)}{19-row}")  # A1, B2, etc.
        return moves
    
    def move(self, pos: str) -> bool:
        """
        Make Go move.
        
        Args:
            pos: The position string (e.g., "A1")
            
        Returns:
            True if move was successful, False otherwise
        """
        try:
            col = ord(pos[0].upper()) - ord('A')
            row = 19 - int(pos[1:])
            
            if not (0 <= row < 19 and 0 <= col < 19):
                return False
            
            if self.board[row][col] != '.':
                return False
            
            # Place stone
            stone = 'B' if self.turn == 0 else 'W'
            self.board[row][col] = stone
            
            move_str = f"Place {stone} at {pos}"
            self.history.append(move_str)
            self.turn = 1 - self.turn
            return True
            
        except (ValueError, IndexError):
            return False


# ——————— RUN LOOP ————————

def main() -> None:
    """Main game loop."""
    # Check for command line arguments
    auto_solo = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '--solo' or sys.argv[1] == 'solo':
            auto_solo = True
    
    print("=" * 60)
    print("GAME HUB FINAL v3")
    print("=" * 60)
    print("\nModes:")
    print("  Human vs Human")
    print("  Human vs AI (toggle with 'ai')")
    print("  AI vs AI (type 'solo')")
    print("\nGames: chess, shogi, go")
    print("\nCommands:")
    print("  [move] - make move (e.g., 'e2e4' or 'e2 e4')")
    print("  n - new game")
    print("  ai - toggle AI opponent")
    print("  solo - AI vs AI mode")
    print("  chess/shogi/go - switch game")
    print("  done - commit moves to memory")
    print("  q - quit")
    print("=" * 60)
    
    # Load last game or start new
    game: Optional[Engine] = None
    
    if STATE.exists() and not auto_solo:
        try:
            s = json.loads(STATE.read_text())
            mode = s.get('mode', 'chess')
            
            if mode == 'chess':
                game = Chess()
            elif mode == 'shogi':
                game = Shogi()
            elif mode == 'go':
                game = Go()
            else:
                game = Chess()
            
            game.load_state(s)
            print(f"\n[Loaded] Last game: {game.mode}")
            print(f"         {game.players[0].upper()} vs {game.players[1].upper()}")
            if game.history:
                print(f"         Last moves: {', '.join(game.history[-3:])}")
            print("         Press Enter to continue...")
            input()
            game.print_board()
        except Exception as e:
            print(f"[Error] Failed to load: {e}")
            game = Chess()
            game.setup()
    else:
        game = Chess()
        game.setup()
        
        # Auto-start solo mode if requested
        if auto_solo:
            game.players = ['ai', 'ai']
            print("\n[Mode] AI vs AI - Solo mode activated")
            game.print_board()
    
    # Main loop
    move_count = 0
    max_moves = 200  # Prevent infinite loops in AI vs AI
    
    while game.running:
        # Limit AI vs AI games to prevent infinite loops
        if game.players == ['ai', 'ai'] and move_count >= max_moves:
            print(f"\n[Game] Reached {max_moves} moves. Ending AI vs AI game.")
            game.learn()
            game.quit()
            break
        
        # Human turn
        if game.players[game.turn] == 'human':
            print("\n> ", end="")
            try:
                cmd = input().strip()
            except (EOFError, KeyboardInterrupt):
                game.quit()
                break
            
            action = game.parse_input(cmd)
            
            if not action:
                continue
            
            # Handle game switching
            if action == 'switch_chess':
                game = Chess()
                game.players = ['human', 'human']
                game.setup()
                continue
            elif action == 'switch_shogi':
                game = Shogi()
                game.players = ['human', 'human']
                game.setup()
                continue
            elif action == 'switch_go':
                game = Go()
                game.players = ['human', 'human']
                game.setup()
                continue
            
            # Handle moves
            move_made = False
            
            if game.mode == 'chess':
                # Format: e2e4 or e2 e4
                if ' ' in action:
                    parts = action.split()
                    if len(parts) == 2:
                        move_made = game.move(parts[0], parts[1])
                elif len(action) == 4:
                    move_made = game.move(action[:2], action[2:])
            elif game.mode == 'shogi':
                # Format: 76->75 or 765
                move_made = game.move(action)
            elif game.mode == 'go':
                # Format: D4 or d4
                move_made = game.move(action)
            
            if move_made:
                game.print_board()
                game.save_state()
            elif action and action not in ['solo', 'ai', 'n', 'q']:
                print("[Error] Invalid move.")
        
        # AI turn
        if game.running and game.players[game.turn] == 'ai':
            import time
            time.sleep(0.5)  # Small delay so you can see moves
            
            ai_move = game.choose()
            if ai_move and ai_move != 'pass':
                player_name = "AI (White)" if game.turn == 0 else "AI (Black)"
                print(f"\n[{player_name}] Plays: {ai_move}")
                
                move_success = False
                if game.mode == 'chess':
                    if '->' in ai_move:
                        fr, to = ai_move.split('->')
                        move_success = game.move(fr, to)
                    elif len(ai_move) == 4:
                        move_success = game.move(ai_move[:2], ai_move[2:])
                elif game.mode == 'shogi':
                    move_success = game.move(ai_move)
                elif game.mode == 'go':
                    move_success = game.move(ai_move)
                
                if move_success:
                    move_count += 1
                    game.print_board()
                    game.save_state()
                    
                    # In AI vs AI mode, continue automatically
                    if game.players == ['ai', 'ai']:
                        continue
                else:
                    print("[AI] Invalid move, trying again...")
                    time.sleep(0.3)
    
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

