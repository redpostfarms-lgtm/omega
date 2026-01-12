# -*- coding: utf-8 -*-
# ELARA VISUAL CHECKERS - Interactive board window
# 800x800, dark walnut, gold trim, smooth animations

import sys
import math
import time
from typing import Optional, Tuple, Dict, List

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("ERROR: pygame required for visual board.")
    print("Install with: pip install pygame")
    sys.exit(1)

from elara_integrated_system import ElaraIntegratedSystem
from elara_difficulty_system import DifficultyLevel


class VisualCheckers:
    """Visual checkers board - 800x800, interactive."""
    
    def __init__(self, difficulty: DifficultyLevel = DifficultyLevel.BEGINNER):
        """Initialize visual checkers."""
        pygame.init()
        
        self.window_size = (800, 800)
        self.window = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Checkers - Beginner")
        
        # Colors
        self.bg_color = (45, 35, 25)  # Dark walnut
        self.gold_trim = (212, 175, 55)  # Gold
        self.board_light = (240, 217, 181)  # Light square
        self.board_dark = (181, 136, 99)  # Dark square
        self.red_piece = (200, 0, 0)
        self.black_piece = (50, 50, 50)
        self.red_king = (255, 100, 100)
        self.black_king = (100, 100, 100)
        self.selected = (255, 255, 0)
        self.legal_move = (0, 255, 0, 150)
        
        # Board
        self.board_start_x = 100
        self.board_start_y = 100
        self.square_size = 75
        self.board_size = 8
        
        # Game state
        self.board = self._init_board()
        self.selected_piece = None
        self.legal_moves = []
        self.current_turn = 1  # 1 = red, 2 = black
        self.difficulty = difficulty
        
        # System
        self.system = ElaraIntegratedSystem()
        self.system.difficulty.set_user_level("player", difficulty)
        
        # Banter engine
        from elara_banter_engine import BanterEngine, BanterTier
        self.banter_engine = BanterEngine()
        self.last_move_time = time.time()
        
        # Animation
        self.animating = None
        self.clock = pygame.time.Clock()
        self.running = True
        
        # New Game button
        self.new_game_button = pygame.Rect(600, 50, 150, 40)
        self.button_hovered = False
    
    def _init_board(self):
        """Initialize checkers board."""
        board = [[0 for _ in range(8)] for _ in range(8)]
        
        # Black pieces (top 3 rows)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 2
        
        # Red pieces (bottom 3 rows)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 1
        
        return board
    
    def draw_board(self):
        """Draw checkers board."""
        # Background
        self.window.fill(self.bg_color)
        
        # Gold trim
        border_width = 4
        pygame.draw.rect(self.window, self.gold_trim, (0, 0, self.window_size[0], border_width))
        pygame.draw.rect(self.window, self.gold_trim, (0, 0, border_width, self.window_size[1]))
        pygame.draw.rect(self.window, self.gold_trim, (self.window_size[0] - border_width, 0, border_width, self.window_size[1]))
        pygame.draw.rect(self.window, self.gold_trim, (0, self.window_size[1] - border_width, self.window_size[0], border_width))
        
        # Board squares
        for row in range(8):
            for col in range(8):
                x = self.board_start_x + col * self.square_size
                y = self.board_start_y + row * self.square_size
                
                # Square color
                is_light = (row + col) % 2 == 0
                color = self.board_light if is_light else self.board_dark
                
                # Breathing effect (subtle)
                breath = 1.0 + 0.02 * math.sin(time.time() * 2.0)
                color = tuple(min(255, int(c * breath)) for c in color)
                
                pygame.draw.rect(self.window, color, (x, y, self.square_size, self.square_size))
                
                # Highlight selected square
                if self.selected_piece == (row, col):
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill((*self.selected, 100))
                    self.window.blit(highlight, (x, y))
                
                # Highlight legal moves
                if (row, col) in self.legal_moves:
                    highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    highlight.fill(self.legal_move)
                    self.window.blit(highlight, (x, y))
        
        # Draw pieces
        self.draw_pieces()
        
        # Draw status
        self.draw_status()
    
    def draw_pieces(self):
        """Draw checkers pieces."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == 0:
                    continue
                
                x = self.board_start_x + col * self.square_size + self.square_size // 2
                y = self.board_start_y + row * self.square_size + self.square_size // 2
                
                # Piece color
                if piece == 1:  # Red
                    color = self.red_piece
                elif piece == 2:  # Black
                    color = self.black_piece
                elif piece == 3:  # Red King
                    color = self.red_king
                else:  # Black King
                    color = self.black_king
                
                # Draw piece
                radius = 28
                pygame.draw.circle(self.window, color, (x, y), radius)
                pygame.draw.circle(self.window, (255, 255, 255), (x, y), radius, 2)
                
                # King crown
                if piece == 3 or piece == 4:
                    crown_y = y - 10 - 3 * math.sin(time.time() * 3.0)
                    self._draw_crown(x, int(crown_y))
    
    def _draw_crown(self, x: int, y: int):
        """Draw floating crown for king."""
        points = [
            (x - 12, y),
            (x - 8, y - 8),
            (x - 4, y - 4),
            (x, y - 12),
            (x + 4, y - 4),
            (x + 8, y - 8),
            (x + 12, y)
        ]
        pygame.draw.polygon(self.window, (255, 215, 0), points)
    
    def draw_status(self):
        """Draw game status."""
        font = pygame.font.Font(None, 36)
        
        # Turn indicator
        turn_text = "Red's Turn" if self.current_turn == 1 else "Black's Turn (AI)"
        color = self.red_piece if self.current_turn == 1 else self.black_piece
        text = font.render(turn_text, True, color)
        self.window.blit(text, (50, 50))
        
        # New Game button
        button_color = (100, 150, 100) if not self.button_hovered else (120, 180, 120)
        pygame.draw.rect(self.window, button_color, self.new_game_button)
        pygame.draw.rect(self.window, self.gold_trim, self.new_game_button, 2)
        
        button_font = pygame.font.Font(None, 28)
        button_text = button_font.render("New Game", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=self.new_game_button.center)
        self.window.blit(button_text, text_rect)
        
        # Difficulty
        diff_text = f"Level: {self.difficulty.value.title()}"
        text = font.render(diff_text, True, self.gold_trim)
        self.window.blit(text, (50, 720))
        
        # Instructions
        small_font = pygame.font.Font(None, 24)
        inst_text = "Click piece to select, click destination to move"
        text = small_font.render(inst_text, True, (200, 200, 200))
        self.window.blit(text, (50, 750))
        
        # Banter status
        if self.banter_engine.escalation_level > 0.5:
            esc_text = f"Banter Level: {'!' * int(self.banter_engine.escalation_level * 5)}"
            text = small_font.render(esc_text, True, (255, 100, 100))
            self.window.blit(text, (400, 720))
    
    def start_new_game(self):
        """Reset game to initial state."""
        self.board = self._init_board()
        self.selected_piece = None
        self.legal_moves = []
        self.current_turn = 1  # Red goes first
        self.last_move_time = time.time()
        self.banter_engine.escalation_level = 0.0  # Reset banter
        print("\n[System] New game started. Red's turn.")
    
    def pos_to_square(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board square."""
        x, y = pos
        col = (x - self.board_start_x) // self.square_size
        row = (y - self.board_start_y) // self.square_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click."""
        # Check if New Game button clicked
        if self.new_game_button.collidepoint(pos):
            self.start_new_game()
            return
        
        square = self.pos_to_square(pos)
        if not square:
            return
        
        row, col = square
        
        # If piece selected, try to move
        if self.selected_piece:
            if square in self.legal_moves:
                # Track move time for mood detection
                move_time = time.time() - self.last_move_time
                self.last_move_time = time.time()
                
                # Make move
                from_row, from_col = self.selected_piece
                self._make_move((from_row, from_col), (row, col))
                
                # Generate banter (AI response)
                from elara_banter_engine import BanterTier
                tier_map = {
                    DifficultyLevel.BEGINNER: BanterTier.BEGINNER,
                    DifficultyLevel.INTERMEDIATE: BanterTier.INTERMEDIATE,
                    DifficultyLevel.EXPERT: BanterTier.EXPERT,
                    DifficultyLevel.MASTER: BanterTier.MASTER
                }
                tier = tier_map.get(self.difficulty, BanterTier.BEGINNER)
                
                # Detect if this was a blunder
                context = "move"
                if len(self.legal_moves) > 1 and square == self.legal_moves[-1]:  # Bad move heuristic
                    context = "blunder"
                
                banter = self.banter_engine.auto_scale_banter(tier, move_time, context=context)
                print(f"\n[System] {banter}")
                
                # Switch turn
                self.current_turn = 2 if self.current_turn == 1 else 1
                
                # AI move (if black's turn)
                if self.current_turn == 2:
                    self._ai_move()
                
                self.selected_piece = None
                self.legal_moves = []
            elif self.board[row][col] and ((self.board[row][col] == 1 or self.board[row][col] == 3) and self.current_turn == 1):
                # Select different piece
                self.selected_piece = (row, col)
                self.legal_moves = self._get_legal_moves((row, col))
            else:
                # Deselect
                self.selected_piece = None
                self.legal_moves = []
        else:
            # Select piece
            piece = self.board[row][col]
            if piece and ((piece == 1 or piece == 3) and self.current_turn == 1):
                self.selected_piece = (row, col)
                self.legal_moves = self._get_legal_moves((row, col))
    
    def _get_legal_moves(self, square: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get legal moves for piece."""
        row, col = square
        piece = self.board[row][col]
        
        if not piece:
            return []
        
        legal_moves = []
        is_red = piece == 1 or piece == 3
        is_king = piece == 3 or piece == 4
        
        # Check for mandatory jumps first
        jump_moves = []
        
        directions = []
        if is_red or is_king:
            directions.append((-1, -1))
            directions.append((-1, 1))
        if not is_red or is_king:
            directions.append((1, -1))
            directions.append((1, 1))
        
        for dr, dc in directions:
            # Jump move
            jump_row, jump_col = row + 2*dr, col + 2*dc
            if 0 <= jump_row < 8 and 0 <= jump_col < 8:
                mid_row, mid_col = row + dr, col + dc
                if 0 <= mid_row < 8 and 0 <= mid_col < 8:
                    mid_piece = self.board[mid_row][mid_col]
                    if mid_piece and mid_piece != piece and self.board[jump_row][jump_col] == 0:
                        jump_moves.append((jump_row, jump_col))
        
        if jump_moves:
            return jump_moves
        
        # Regular moves
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if self.board[new_row][new_col] == 0:
                    legal_moves.append((new_row, new_col))
        
        return legal_moves
    
    def _make_move(self, from_sq: Tuple[int, int], to_sq: Tuple[int, int]):
        """Make a move."""
        from_row, from_col = from_sq
        to_row, to_col = to_sq
        
        piece = self.board[from_row][from_col]
        
        # Check for jump
        if abs(to_row - from_row) == 2:
            jump_row = (from_row + to_row) // 2
            jump_col = (from_col + to_col) // 2
            self.board[jump_row][jump_col] = 0
        
        # Move piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        
        # King promotion
        if piece == 1 and to_row == 0:
            self.board[to_row][to_col] = 3  # Red king
        elif piece == 2 and to_row == 7:
            self.board[to_row][to_col] = 4  # Black king
    
    def _ai_move(self):
        """AI makes a move (beginner level)."""
        import random
        time.sleep(0.5)  # AI thinking delay
        
        # Get all black pieces
        black_pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == 2 or piece == 4:
                    black_pieces.append((row, col))
        
        if not black_pieces:
            return
        
        # Beginner: Random moves, sometimes mistakes
        random.shuffle(black_pieces)
        for piece_sq in black_pieces:
            moves = self._get_legal_moves(piece_sq)
            if moves:
                # Sometimes choose bad move (beginner behavior)
                if random.random() < 0.3 and len(moves) > 1:
                    move = moves[-1]  # Last move (often worse)
                else:
                    move = random.choice(moves)
                
                self._make_move(piece_sq, move)
                
                # Generate banter
                from elara_banter_engine import BanterTier
                tier_map = {
                    DifficultyLevel.BEGINNER: BanterTier.BEGINNER,
                    DifficultyLevel.INTERMEDIATE: BanterTier.INTERMEDIATE,
                    DifficultyLevel.EXPERT: BanterTier.EXPERT,
                    DifficultyLevel.MASTER: BanterTier.MASTER
                }
                tier = tier_map.get(self.difficulty, BanterTier.BEGINNER)
                
                banter = self.banter_engine.generate_banter(tier, context="move")
                print(f"\n[System] {banter}")
                
                self.current_turn = 1  # Back to player
                return
    
    def run(self):
        """Main game loop."""
        print("\n" + "=" * 60)
        print("ELARA CHECKERS - Visual Board")
        print("=" * 60)
        print("\n[System] Board up. Ready. Click pieces to move.")
        print("[System] Beginner mode active.")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEMOTION:
                    # Update button hover state
                    self.button_hovered = self.new_game_button.collidepoint(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Draw
            self.draw_board()
            pygame.display.flip()
            
            # Maintain 60 FPS
            self.clock.tick(60)
        
        pygame.quit()
        print("[System] Game closed.")


if __name__ == '__main__':
    if not HAS_PYGAME:
        print("ERROR: pygame required. Install with: pip install pygame")
        sys.exit(1)
    
    game = VisualCheckers(difficulty=DifficultyLevel.BEGINNER)
    game.run()

