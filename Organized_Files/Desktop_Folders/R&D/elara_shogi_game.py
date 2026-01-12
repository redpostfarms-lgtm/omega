# -*- coding: utf-8 -*-
# ELARA SHOGI GAME - 9x9 board, Japanese pieces, drop mechanics

import math
import time
from typing import Dict, List, Optional, Tuple, Any

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class ElaraShogiGame:
    """
    Shogi game module - visual rendering with teaching support.
    
    Features:
    - 9x9 board rendering
    - Japanese piece rendering (kanji)
    - Piece promotion zones
    - Drop mechanics visualization
    - Teaching mode integration
    """
    
    def __init__(self, engine, config: Optional[Dict[str, Any]] = None):
        """Initialize shogi game."""
        self.engine = engine
        self.config = config or {}
        self.board_size = 9
        self.square_size = 60  # Smaller for 9x9 board
        self.board_start_x = 80
        self.board_start_y = 80
        
        # Board state: 0 = empty, piece codes for pieces
        # Piece codes: K=King, G=Gold, S=Silver, N=Knight, L=Lance, B=Bishop, R=Rook, P=Pawn
        # Uppercase = black (sente), lowercase = white (gote)
        # + prefix = promoted
        self.board = self._init_board()
        self.selected_piece = None
        self.legal_moves = []
        self.current_turn = 'sente'  # sente (black) or gote (white)
        self.move_count = 0
        
        # Piece hand (captured pieces)
        self.sente_hand: List[str] = []
        self.gote_hand: List[str] = []
        
        # Colors
        self.board_light = (240, 217, 181)
        self.board_dark = (181, 136, 99)
        self.selected_color = (255, 255, 0, 150)
        self.legal_move_color = (0, 255, 0, 100)
        
        # Piece colors
        self.sente_color = (50, 50, 50)  # Dark
        self.gote_color = (220, 220, 220)  # Light
    
    def _init_board(self) -> List[List[str]]:
        """Initialize shogi board with starting position."""
        board = [['' for _ in range(9)] for _ in range(9)]
        
        # Row 0 (sente back rank)
        board[0] = ['L', 'N', 'S', 'G', 'K', 'G', 'S', 'N', 'L']
        # Row 1 (sente)
        board[1] = ['', 'R', '', '', '', '', '', 'B', '']
        # Row 2 (sente pawns)
        board[2] = ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P']
        
        # Rows 3-5 are empty
        
        # Row 6 (gote pawns)
        board[6] = ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p']
        # Row 7 (gote)
        board[7] = ['', 'b', '', '', '', '', '', 'r', '']
        # Row 8 (gote back rank)
        board[8] = ['l', 'n', 's', 'g', 'k', 'g', 's', 'n', 'l']
        
        return board
    
    def draw(self):
        """Draw shogi board and pieces."""
        if not HAS_PYGAME or not self.engine.window:
            return
        
        self.draw_board()
        self.draw_pieces()
        self.draw_hands()
        self.draw_status()
    
    def draw_board(self):
        """Draw 9x9 shogi board."""
        if not HAS_PYGAME or not self.engine.window:
            return
        
        # Draw board squares
        for row in range(9):
            for col in range(9):
                x = self.board_start_x + col * self.square_size
                y = self.board_start_y + row * self.square_size
                
                # Alternating colors
                is_light = (row + col) % 2 == 0
                color = self.board_light if is_light else self.board_dark
                
                # Draw square
                pygame.draw.rect(self.engine.window, color,
                               (x, y, self.square_size, self.square_size))
                
                # Draw border
                pygame.draw.rect(self.engine.window, (100, 100, 100),
                               (x, y, self.square_size, self.square_size), 1)
                
                # Highlight selected square
                if self.selected_piece == (row, col):
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill(self.selected_color)
                    self.engine.window.blit(highlight, (x, y))
                
                # Highlight legal moves
                if (row, col) in self.legal_moves:
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill(self.legal_move_color)
                    self.engine.window.blit(highlight, (x, y))
        
        # Draw promotion zones (top 3 rows for gote, bottom 3 for sente)
        promotion_color = (255, 200, 200, 50)
        # Gote promotion zone (top 3 rows)
        for row in range(3):
            for col in range(9):
                x = self.board_start_x + col * self.square_size
                y = self.board_start_y + row * self.square_size
                highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                highlight.fill(promotion_color)
                self.engine.window.blit(highlight, (x, y))
        
        # Sente promotion zone (bottom 3 rows)
        for row in range(6, 9):
            for col in range(9):
                x = self.board_start_x + col * self.square_size
                y = self.board_start_y + row * self.square_size
                highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                highlight.fill(promotion_color)
                self.engine.window.blit(highlight, (x, y))
    
    def draw_pieces(self):
        """Draw shogi pieces on board."""
        if not HAS_PYGAME or not self.engine.window:
            return
        
        try:
            font = pygame.font.Font(None, 32)
        except:
            font = None
        
        piece_names = {
            'K': '王', 'k': '王',  # King
            'G': '金', 'g': '金',  # Gold
            'S': '銀', 's': '銀',  # Silver
            'N': '桂', 'n': '桂',  # Knight
            'L': '香', 'l': '香',  # Lance
            'B': '角', 'b': '角',  # Bishop
            'R': '飛', 'r': '飛',  # Rook
            'P': '歩', 'p': '歩',  # Pawn
            '+B': '馬', '+b': '馬',  # Promoted Bishop
            '+R': '龍', '+r': '龍',  # Promoted Rook
            '+S': '全', '+s': '全',  # Promoted Silver
            '+N': '圭', '+n': '圭',  # Promoted Knight
            '+L': '杏', '+l': '杏',  # Promoted Lance
            '+P': 'と', '+p': 'と',  # Promoted Pawn
        }
        
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if not piece:
                    continue
                
                x = self.board_start_x + col * self.square_size + self.square_size // 2
                y = self.board_start_y + row * self.square_size + self.square_size // 2
                
                # Determine piece color
                is_sente = piece.isupper() if piece else False
                piece_color = self.sente_color if is_sente else self.gote_color
                
                # Draw piece circle background
                pygame.draw.circle(self.engine.window, (255, 255, 255), (x, y), 24)
                pygame.draw.circle(self.engine.window, piece_color, (x, y), 24, 2)
                
                # Draw piece name (kanji)
                if font:
                    piece_name = piece_names.get(piece, piece)
                    try:
                        text = font.render(piece_name, True, piece_color)
                        text_rect = text.get_rect(center=(x, y))
                        self.engine.window.blit(text, text_rect)
                    except:
                        # Fallback to letter
                        text = font.render(piece, True, piece_color)
                        text_rect = text.get_rect(center=(x, y))
                        self.engine.window.blit(text, text_rect)
    
    def draw_hands(self):
        """Draw captured pieces in hand areas."""
        if not HAS_PYGAME or not self.engine.window:
            return
        
        # Draw sente hand (left side)
        hand_y = 650
        hand_x = 80
        if self.sente_hand:
            try:
                small_font = pygame.font.Font(None, 24)
                text = small_font.render(f"Sente Hand: {', '.join(self.sente_hand)}", True, (200, 200, 200))
                self.engine.window.blit(text, (hand_x, hand_y))
            except:
                pass
        
        # Draw gote hand (right side)
        if self.gote_hand:
            try:
                small_font = pygame.font.Font(None, 24)
                text = small_font.render(f"Gote Hand: {', '.join(self.gote_hand)}", True, (200, 200, 200))
                self.engine.window.blit(text, (hand_x, hand_y + 25))
            except:
                pass
    
    def draw_status(self):
        """Draw game status."""
        if not HAS_PYGAME or not self.engine.window:
            return
        
        try:
            font = pygame.font.Font(None, 28)
            turn_text = f"Turn: {self.current_turn.title()}"
            text = font.render(turn_text, True, (200, 200, 200))
            self.engine.window.blit(text, (600, 50))
            
            move_text = f"Move: {self.move_count}"
            text = font.render(move_text, True, (200, 200, 200))
            self.engine.window.blit(text, (600, 80))
        except:
            pass
    
    def update(self):
        """Update game state."""
        pass
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click."""
        square = self.pos_to_square(pos)
        if not square:
            return
        
        row, col = square
        
        # Handle piece selection/movement
        if self.selected_piece:
            if square in self.legal_moves:
                # Make move
                from_row, from_col = self.selected_piece
                self._make_move((from_row, from_col), (row, col))
                self.selected_piece = None
                self.legal_moves = []
            else:
                # Select different piece or deselect
                piece = self.board[row][col]
                if piece and ((piece.isupper() and self.current_turn == 'sente') or 
                             (piece.islower() and self.current_turn == 'gote')):
                    self.selected_piece = (row, col)
                    self.legal_moves = self._get_legal_moves((row, col))
                else:
                    self.selected_piece = None
                    self.legal_moves = []
        else:
            # Select piece
            piece = self.board[row][col]
            if piece:
                is_sente_piece = piece.isupper()
                if (is_sente_piece and self.current_turn == 'sente') or \
                   (not is_sente_piece and self.current_turn == 'gote'):
                    self.selected_piece = (row, col)
                    self.legal_moves = self._get_legal_moves((row, col))
    
    def pos_to_square(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board square."""
        x, y = pos
        col = (x - self.board_start_x) // self.square_size
        row = (y - self.board_start_y) // self.square_size
        
        if 0 <= row < 9 and 0 <= col < 9:
            return (row, col)
        return None
    
    def _get_legal_moves(self, square: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get legal moves for piece (simplified)."""
        row, col = square
        piece = self.board[row][col]
        
        if not piece:
            return []
        
        # Simplified: show all empty squares (full movement rules would be complex)
        moves = []
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == '':
                    moves.append((r, c))
        
        return moves[:10]  # Limit to first 10 for now
    
    def _make_move(self, from_sq: Tuple[int, int], to_sq: Tuple[int, int]):
        """Make a move."""
        from_row, from_col = from_sq
        to_row, to_col = to_sq
        
        piece = self.board[from_row][from_col]
        
        # Check for capture
        captured = self.board[to_row][to_col]
        if captured:
            # Add to hand (invert case)
            if captured.isupper():
                self.gote_hand.append(captured.lower())
            else:
                self.sente_hand.append(captured.upper())
        
        # Move piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        
        # Check for promotion (simplified - promote if entering promotion zone)
        if piece and piece not in ['K', 'k', 'G', 'g']:  # Kings and golds don't promote
            is_sente = piece.isupper()
            in_promotion_zone = (is_sente and to_row < 3) or (not is_sente and to_row >= 6)
            if in_promotion_zone and not piece.startswith('+'):
                # Auto-promote for simplicity
                self.board[to_row][to_col] = '+' + piece
        
        # Switch turn
        self.current_turn = 'gote' if self.current_turn == 'sente' else 'sente'
        self.move_count += 1

