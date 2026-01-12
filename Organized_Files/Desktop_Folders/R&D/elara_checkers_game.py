# -*- coding: utf-8 -*-
# ELARA CHECKERS GAME - Red-black squares, pop animations, king me

import math
from typing import Dict, List, Optional, Tuple, Any

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class ElaraCheckersGame:
    """
    Checkers game module.
    
    Features:
    - Red-black squares that breathe
    - Smooth piece dragging
    - Pop animations for double jumps
    - Camera follows smoothly
    - King me - crown floats on
    - Difficulty-based AI play
    """
    
    def __init__(self, engine, difficulty_level="beginner"):
        """Initialize checkers game."""
        self.engine = engine
        self.difficulty_level = difficulty_level
        self.board_size = 8
        self.square_size = 80
        self.board_start_x = 120  # Offset for smaller board
        self.board_start_y = 120
        
        # Board state (0 = empty, 1 = red, 2 = black, 3 = red king, 4 = black king)
        self.board = self._init_board()
        self.selected_piece = None
        self.legal_moves = []
        self.current_turn = 1  # 1 = red, 2 = black
        self.jumping = False
        self.move_count = 0
        
        # Animation state
        self.jump_animations: List[Dict[str, Any]] = []
        self.king_crowns: List[Dict[str, Any]] = []
    
    def _init_board(self) -> List[List[int]]:
        """Initialize checkers board."""
        board = [[0 for _ in range(8)] for _ in range(8)]
        
        # Place pieces (red on bottom, black on top)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 2  # Black pieces
        
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 1  # Red pieces
        
        return board
    
    def draw_board(self):
        """Draw checkers board with breathing squares."""
        if not HAS_PYGAME:
            return
        
        # Breathing effect (subtle color variation)
        time = pygame.time.get_ticks() / 1000.0
        breath_factor = 1.0 + 0.02 * math.sin(time * 2.0)
        
        for row in range(8):
            for col in range(8):
                x = self.board_start_x + col * self.square_size
                y = self.board_start_y + row * self.square_size
                
                # Red-black squares
                if (row + col) % 2 == 0:
                    color = (139, 69, 19)  # Dark brown/red
                else:
                    color = (255, 200, 200)  # Light red
                
                # Apply breathing effect
                color = tuple(int(c * breath_factor) for c in color)
                color = tuple(min(255, max(0, c)) for c in color)
                
                pygame.draw.rect(self.engine.window, color,
                               (x, y, self.square_size, self.square_size))
        
        self.draw_pieces()
    
    def draw_pieces(self):
        """Draw checkers pieces."""
        if not HAS_PYGAME:
            return
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    x = self.board_start_x + col * self.square_size + self.square_size // 2
                    y = self.board_start_y + row * self.square_size + self.square_size // 2
                    
                    # Piece colors
                    if piece == 1 or piece == 3:  # Red
                        color = (200, 0, 0)
                    else:  # Black
                        color = (50, 50, 50)
                    
                    # Draw piece
                    pygame.draw.circle(self.engine.window, color, (x, y), 30)
                    
                    # Draw crown for king
                    if piece == 3 or piece == 4:
                        # Crown floats on - animated
                        crown_y = y - 10 - 3 * math.sin(pygame.time.get_ticks() / 300.0)
                        self._draw_crown(x, int(crown_y))
    
    def _draw_crown(self, x: int, y: int):
        """Draw floating crown for king."""
        if not HAS_PYGAME:
            return
        
        # Draw crown (simplified)
        points = [
            (x - 15, y),
            (x - 10, y - 10),
            (x - 5, y - 5),
            (x, y - 15),
            (x + 5, y - 5),
            (x + 10, y - 10),
            (x + 15, y)
        ]
        pygame.draw.polygon(self.engine.window, (255, 215, 0), points)  # Gold
    
    def draw(self):
        """Draw complete game state."""
        self.draw_board()
    
    def update(self):
        """Update game state."""
        # Update jump animations
        self._update_jump_animations()
        
        # Update legal moves
        if self.selected_piece:
            self.legal_moves = self._get_legal_moves(self.selected_piece)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click."""
        square = self._pos_to_square(pos)
        if not square:
            return
        
        row, col = square
        
        # Select piece
        if not self.selected_piece:
            piece = self.board[row][col]
            if piece and ((piece == 1 or piece == 3) and self.current_turn == 1) or \
               ((piece == 2 or piece == 4) and self.current_turn == 2):
                self.selected_piece = (row, col)
                self.legal_moves = self._get_legal_moves((row, col))
        else:
            # Try to move
            if square in self.legal_moves:
                self._make_move(self.selected_piece, square)
                self.selected_piece = None
                self.legal_moves = []
            else:
                self.selected_piece = None
                self.legal_moves = []
    
    def _pos_to_square(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board square."""
        x, y = pos
        col = (x - self.board_start_x) // self.square_size
        row = (y - self.board_start_y) // self.square_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def _make_move(self, from_square: Tuple[int, int], to_square: Tuple[int, int]):
        """Make a move with pop animation for jumps."""
        from_row, from_col = from_square
        to_row, to_col = to_square
        
        piece = self.board[from_row][from_col]
        
        # Check for jump
        if abs(to_row - from_row) == 2:
            # Double jump - pop animation
            jump_row = (from_row + to_row) // 2
            jump_col = (from_col + to_col) // 2
            
            # Capture piece
            self.board[jump_row][jump_col] = 0
            
            # Add pop animation
            jump_pos = self._square_to_pos((jump_row, jump_col))
            self.jump_animations.append({
                'pos': jump_pos,
                'start_time': pygame.time.get_ticks(),
                'duration': 200
            })
        
        # Move piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        
        # Check for king promotion
        if piece == 1 and to_row == 0:
            self.board[to_row][to_col] = 3  # Red king
            # Crown floats on animation
            king_pos = self._square_to_pos(to_square)
            self.king_crowns.append({
                'pos': king_pos,
                'start_time': pygame.time.get_ticks(),
                'duration': 1000
            })
            print("[System] King me. Red checker leaps, crown floats on.")
        elif piece == 2 and to_row == 7:
            self.board[to_row][to_col] = 4  # Black king
        
        # Switch turn
        self.current_turn = 2 if self.current_turn == 1 else 1
    
    def _square_to_pos(self, square: Tuple[int, int]) -> Tuple[int, int]:
        """Convert board square to screen position."""
        row, col = square
        x = self.board_start_x + col * self.square_size + self.square_size // 2
        y = self.board_start_y + row * self.square_size + self.square_size // 2
        return (x, y)
    
    def _get_legal_moves(self, square: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get legal moves for piece."""
        row, col = square
        piece = self.board[row][col]
        
        if not piece:
            return []
        
        legal_moves = []
        
        # Direction based on piece type
        is_red = piece == 1 or piece == 3
        is_king = piece == 3 or piece == 4
        
        directions = []
        if is_red or is_king:
            directions.append((-1, -1))
            directions.append((-1, 1))
        if not is_red or is_king:
            directions.append((1, -1))
            directions.append((1, 1))
        
        # Check for mandatory jumps first
        jump_moves = []
        
        for dr, dc in directions:
            # Jump move
            jump_row, jump_col = row + 2*dr, col + 2*dc
            if 0 <= jump_row < 8 and 0 <= jump_col < 8:
                mid_row, mid_col = row + dr, col + dc
                if 0 <= mid_row < 8 and 0 <= mid_col < 8:
                    mid_piece = self.board[mid_row][mid_col]
                    if mid_piece and mid_piece != piece and self.board[jump_row][jump_col] == 0:
                        jump_moves.append((jump_row, jump_col))
        
        # If jumps available, only return jumps
        if jump_moves:
            return jump_moves
        
        # Regular moves
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if self.board[new_row][new_col] == 0:
                    legal_moves.append((new_row, new_col))
        
        return legal_moves
    
    def get_ai_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get AI move based on difficulty level.
        
        Returns:
            ((from_row, from_col), (to_row, to_col)) or None
        """
        import random
        
        # Get all pieces for current player
        ai_pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and ((piece == 2 or piece == 4) and self.current_turn == 2) or \
                   ((piece == 1 or piece == 3) and self.current_turn == 1):
                    ai_pieces.append((row, col))
        
        if not ai_pieces:
            return None
        
        # Beginner: Random moves, sometimes misses jumps, leaves pieces
        if self.difficulty_level == "beginner":
            # 30% chance of making a bad move
            if random.random() < 0.3:
                # Random piece, might not have moves
                random.shuffle(ai_pieces)
                for piece_sq in ai_pieces:
                    moves = self._get_legal_moves(piece_sq)
                    if moves:
                        # Sometimes choose a bad move (not the best)
                        if len(moves) > 1 and random.random() < 0.4:
                            return (piece_sq, moves[-1])  # Last move (often worse)
                        return (piece_sq, random.choice(moves))
            else:
                # Normal beginner play
                random.shuffle(ai_pieces)
                for piece_sq in ai_pieces:
                    moves = self._get_legal_moves(piece_sq)
                    if moves:
                        return (piece_sq, random.choice(moves))
        
        # Intermediate: Better moves, prioritizes jumps
        elif self.difficulty_level == "intermediate":
            # Look for jumps first
            for piece_sq in ai_pieces:
                moves = self._get_legal_moves(piece_sq)
                jump_moves = [m for m in moves if abs(m[0] - piece_sq[0]) == 2]
                if jump_moves:
                    return (piece_sq, jump_moves[0])
            
            # Regular moves
            for piece_sq in ai_pieces:
                moves = self._get_legal_moves(piece_sq)
                if moves:
                    # Prefer forward moves
                    forward_moves = [m for m in moves if (self.current_turn == 1 and m[0] < piece_sq[0]) or 
                                    (self.current_turn == 2 and m[0] > piece_sq[0])]
                    if forward_moves:
                        return (piece_sq, forward_moves[0])
                    return (piece_sq, moves[0])
        
        # Expert/Master: Would implement minimax here
        else:
            # For now, best available move
            best_move = None
            best_score = -float('inf')
            
            for piece_sq in ai_pieces:
                moves = self._get_legal_moves(piece_sq)
                for move in moves:
                    score = self._evaluate_move(piece_sq, move)
                    if score > best_score:
                        best_score = score
                        best_move = (piece_sq, move)
            
            return best_move
        
        return None
    
    def _evaluate_move(self, from_sq: Tuple[int, int], to_sq: Tuple[int, int]) -> float:
        """Evaluate move quality."""
        score = 0.0
        
        # Jump bonus
        if abs(to_sq[0] - from_sq[0]) == 2:
            score += 10.0
        
        # King promotion bonus
        if to_sq[0] == 0 or to_sq[0] == 7:
            score += 5.0
        
        # Center control
        if 2 <= to_sq[0] <= 5 and 2 <= to_sq[1] <= 5:
            score += 1.0
        
        return score
    
    def _update_jump_animations(self):
        """Update jump pop animations."""
        if not HAS_PYGAME:
            return
        
        current_time = pygame.time.get_ticks()
        to_remove = []
        
        for i, anim in enumerate(self.jump_animations):
            elapsed = current_time - anim['start_time']
            if elapsed > anim['duration']:
                to_remove.append(i)
            else:
                # Draw pop effect
                progress = elapsed / anim['duration']
                size = int(20 * (1 - progress))
                pygame.draw.circle(self.engine.window, (255, 100, 100),
                                 anim['pos'], size)
        
        for i in reversed(to_remove):
            self.jump_animations.pop(i)

