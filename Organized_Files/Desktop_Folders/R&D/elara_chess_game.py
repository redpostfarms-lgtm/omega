# -*- coding: utf-8 -*-
# ELARA CHESS GAME - Smooth piece movement, silk physics
# Tooltips, check detection, legal move validation

import math
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class PieceType(Enum):
    """Chess piece types."""
    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"


class ElaraChessGame:
    """
    Chess game module for Elara engine.
    
    Features:
    - Smooth piece movement (e2 to e4 example)
    - Tooltip whispers (King in check, Legal? No)
    - Check detection
    - Legal move validation
    - Visual highlights
    """
    
    def __init__(self, engine, player_color: str = "white"):
        """Initialize chess game."""
        self.engine = engine
        self.player_color = player_color
        self.board_size = 8
        self.square_size = 80  # 800 / 10 (with margins)
        self.board_start_x = 80
        self.board_start_y = 80
        
        # Board state (FEN-like)
        self.board = self._init_board()
        self.selected_square = None
        self.legal_moves = []
        self.is_check = False
        self.check_square = None
        self.current_turn = "white"
        
        # Piece graphics (simplified - would load actual images)
        self.piece_sprites = {}
        self._init_piece_sprites()
    
    def _init_board(self) -> List[List[Optional[str]]]:
        """Initialize chess board."""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # White pieces
        board[7][0] = "R"  # Rook
        board[7][1] = "N"  # Knight
        board[7][2] = "B"  # Bishop
        board[7][3] = "Q"  # Queen
        board[7][4] = "K"  # King
        board[7][5] = "B"
        board[7][6] = "N"
        board[7][7] = "R"
        for i in range(8):
            board[6][i] = "P"  # Pawns
        
        # Black pieces
        board[0][0] = "r"
        board[0][1] = "n"
        board[0][2] = "b"
        board[0][3] = "q"
        board[0][4] = "k"
        board[0][5] = "b"
        board[0][6] = "n"
        board[0][7] = "r"
        for i in range(8):
            board[1][i] = "p"
        
        return board
    
    def _init_piece_sprites(self):
        """Initialize piece sprites (simplified)."""
        # Would load actual piece images
        # For now, use placeholder rectangles
        pass
    
    def draw_board(self):
        """Draw chess board."""
        if not HAS_PYGAME:
            return
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x = self.board_start_x + col * self.square_size
                y = self.board_start_y + row * self.square_size
                
                # Alternate colors
                is_light = (row + col) % 2 == 0
                color = self.engine.ui.board_color_light if is_light else self.engine.ui.board_color_dark
                
                pygame.draw.rect(self.engine.window, color, 
                               (x, y, self.square_size, self.square_size))
                
                # Highlight check square
                if self.is_check and (row, col) == self.check_square:
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill(self.engine.ui.check_highlight)
                    self.engine.window.blit(highlight, (x, y))
                
                # Highlight selected square
                if self.selected_square == (row, col):
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill(self.engine.ui.piece_highlight)
                    self.engine.window.blit(highlight, (x, y))
                
                # Highlight legal moves
                if (row, col) in self.legal_moves:
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill(self.engine.ui.move_highlight)
                    self.engine.window.blit(highlight, (x, y))
        
        # Draw pieces
        self.draw_pieces()
    
    def draw_pieces(self):
        """Draw chess pieces."""
        if not HAS_PYGAME:
            return
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    x = self.board_start_x + col * self.square_size + self.square_size // 2
                    y = self.board_start_y + row * self.square_size + self.square_size // 2
                    
                    # Check if piece is animating
                    animating = False
                    for anim in self.engine.animating_pieces:
                        if anim.get('piece') == piece and (row, col) == anim.get('square'):
                            animating = True
                            x, y = anim['current_pos']
                            break
                    
                    if not animating:
                        # Draw piece (simplified - would use actual sprite)
                        piece_color = (255, 255, 255) if piece.isupper() else (0, 0, 0)
                        piece_name = piece.upper()
                        
                        # Draw circle for piece
                        pygame.draw.circle(self.engine.window, piece_color, (int(x), int(y)), 30)
                        
                        # Draw piece letter
                        font = pygame.font.Font(None, 36)
                        text = font.render(piece_name, True, 
                                         (0, 0, 0) if piece.isupper() else (255, 255, 255))
                        text_rect = text.get_rect(center=(int(x), int(y)))
                        self.engine.window.blit(text, text_rect)
    
    def draw(self):
        """Draw complete game state."""
        self.draw_board()
    
    def update(self):
        """Update game state."""
        # Check for check
        self._detect_check()
        
        # Update legal moves
        if self.selected_square:
            self.legal_moves = self._get_legal_moves(self.selected_square)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on board."""
        square = self._pos_to_square(pos)
        if not square:
            return
        
        row, col = square
        
        # If no piece selected, select piece
        if not self.selected_square:
            piece = self.board[row][col]
            if piece and ((piece.isupper() and self.current_turn == "white") or 
                         (piece.islower() and self.current_turn == "black")):
                self.selected_square = (row, col)
                self.legal_moves = self._get_legal_moves((row, col))
        else:
            # Try to move
            if square in self.legal_moves:
                self._make_move(self.selected_square, square)
                self.selected_square = None
                self.legal_moves = []
                self.current_turn = "black" if self.current_turn == "white" else "white"
            elif self.board[row][col] and ((self.board[row][col].isupper() and self.current_turn == "white") or 
                                          (self.board[row][col].islower() and self.current_turn == "black")):
                # Select different piece
                self.selected_square = (row, col)
                self.legal_moves = self._get_legal_moves((row, col))
            else:
                # Deselect
                self.selected_square = None
                self.legal_moves = []
    
    def _pos_to_square(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board square."""
        x, y = pos
        col = (x - self.board_start_x) // self.square_size
        row = (y - self.board_start_y) // self.square_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def _square_to_pos(self, square: Tuple[int, int]) -> Tuple[int, int]:
        """Convert board square to screen position."""
        row, col = square
        x = self.board_start_x + col * self.square_size + self.square_size // 2
        y = self.board_start_y + row * self.square_size + self.square_size // 2
        return (x, y)
    
    def _make_move(self, from_square: Tuple[int, int], to_square: Tuple[int, int]):
        """Make a move with smooth animation."""
        from_row, from_col = from_square
        to_row, to_col = to_square
        
        piece = self.board[from_row][from_col]
        
        # Get screen positions
        from_pos = self._square_to_pos(from_square)
        to_pos = self._square_to_pos(to_square)
        
        # Animate piece movement - silk smooth
        self.engine.animate_piece_move(from_pos, to_pos, piece, duration=0.3)
        
        # Update board state
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Example: e2 to e4 movement
        if from_square == (6, 4) and to_square == (4, 4):
            print("[System] e2 to e4. Pieces slide like silk. No jump-cut.")
    
    def _get_legal_moves(self, square: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get legal moves for piece at square."""
        row, col = square
        piece = self.board[row][col]
        
        if not piece:
            return []
        
        legal_moves = []
        
        # Simplified legal move generation (would implement full rules)
        piece_type = piece.upper()
        
        if piece_type == "P":  # Pawn
            direction = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1
            
            # Forward move
            if 0 <= row + direction < 8 and not self.board[row + direction][col]:
                legal_moves.append((row + direction, col))
                
                # Double move from start
                if row == start_row and not self.board[row + 2*direction][col]:
                    legal_moves.append((row + 2*direction, col))
            
            # Capture diagonally
            for dc in [-1, 1]:
                if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                    target = self.board[row + direction][col + dc]
                    if target and ((piece.isupper() and target.islower()) or 
                                  (piece.islower() and target.isupper())):
                        legal_moves.append((row + direction, col + dc))
        
        # Would add other piece types...
        
        # Filter out moves that put own king in check
        filtered_moves = []
        for move in legal_moves:
            # Would check if move leaves king in check
            filtered_moves.append(move)
        
        return filtered_moves
    
    def _detect_check(self):
        """Detect if king is in check."""
        # Simplified check detection
        self.is_check = False
        self.check_square = None
        
        # Would implement full check detection
        # For now, placeholder
    
    def get_tooltip(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get tooltip text for position."""
        square = self._pos_to_square(pos)
        if not square:
            return None
        
        row, col = square
        
        # Check if square is legal move
        if self.selected_square and square in self.legal_moves:
            return "Legal move"
        
        # Check if king in check
        if self.is_check and square == self.check_square:
            return "King in check"
        
        # Check if illegal move
        if self.selected_square and square not in self.legal_moves and self.board[row][col]:
            return "Legal? No"
        
        return None
    
    def update(self):
        """Update game state."""
        self._detect_check()
        if self.selected_square:
            self.legal_moves = self._get_legal_moves(self.selected_square)

