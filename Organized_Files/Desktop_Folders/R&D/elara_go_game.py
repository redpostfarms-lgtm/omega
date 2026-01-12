# -*- coding: utf-8 -*-
# ELARA GO GAME - Tactile stone placement, capture sounds
# Black stones matte, white stones glow faint

import math
from typing import Dict, List, Optional, Tuple, Any

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class ElaraGoGame:
    """
    Go game module for Elara engine.
    
    Features:
    - Tiles rise from grid
    - Black stones matte, white stones glow faint
    - Place sound like glass on stone
    - Captured stones clink into bowl
    - Tactile feedback
    """
    
    def __init__(self, engine):
        """Initialize Go game."""
        self.engine = engine
        self.board_size = 19  # Standard Go board
        self.square_size = 35
        self.board_start_x = 50
        self.board_start_y = 50
        
        # Board state (0 = empty, 1 = black, 2 = white)
        self.board = [[0 for _ in range(19)] for _ in range(19)]
        self.current_turn = 1  # 1 = black, 2 = white
        self.captured_black = 0
        self.captured_white = 0
        
        # Animation state
        self.placing_stone: Optional[Dict[str, Any]] = None
        self.captured_stones: List[Dict[str, Any]] = []
        self.bowl_position = (750, 400)  # Position for captured stones
    
    def draw_board(self):
        """Draw Go board with grid."""
        if not HAS_PYGAME:
            return
        
        # Draw board background
        board_rect = pygame.Rect(
            self.board_start_x - 20,
            self.board_start_y - 20,
            self.board_size * self.square_size + 40,
            self.board_size * self.square_size + 40
        )
        pygame.draw.rect(self.engine.window, (220, 179, 92), board_rect)  # Wooden board
        
        # Draw grid lines
        for i in range(19):
            x = self.board_start_x + i * self.square_size
            y = self.board_start_y + i * self.square_size
            
            # Vertical line
            pygame.draw.line(self.engine.window, (0, 0, 0),
                           (x, self.board_start_y),
                           (x, self.board_start_y + (self.board_size - 1) * self.square_size),
                           1)
            
            # Horizontal line
            pygame.draw.line(self.engine.window, (0, 0, 0),
                           (self.board_start_x, y),
                           (self.board_start_x + (self.board_size - 1) * self.square_size, y),
                           1)
        
        # Draw star points (hoshi)
        star_points = [(3, 3), (3, 9), (3, 15),
                      (9, 3), (9, 9), (9, 15),
                      (15, 3), (15, 9), (15, 15)]
        for row, col in star_points:
            x = self.board_start_x + col * self.square_size
            y = self.board_start_y + row * self.square_size
            pygame.draw.circle(self.engine.window, (0, 0, 0), (x, y), 3)
        
        self.draw_stones()
        self.draw_captured_bowl()
    
    def draw_stones(self):
        """Draw Go stones."""
        if not HAS_PYGAME:
            return
        
        for row in range(19):
            for col in range(19):
                stone = self.board[row][col]
                if stone:
                    x = self.board_start_x + col * self.square_size
                    y = self.board_start_y + row * self.square_size
                    
                    # Check if stone is being placed (rising animation)
                    if self.placing_stone and self.placing_stone['pos'] == (row, col):
                        # Rising animation
                        progress = self.placing_stone['progress']
                        offset_y = -15 * (1 - progress)
                        y += int(offset_y)
                    
                    # Draw stone
                    radius = 15
                    if stone == 1:  # Black - matte
                        pygame.draw.circle(self.engine.window, (30, 30, 30), (x, y), radius)
                        # Matte effect - darker edges
                        pygame.draw.circle(self.engine.window, (20, 20, 20), (x, y), radius, 2)
                    else:  # White - glow faint
                        # Glow effect
                        glow_radius = radius + 3
                        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, (255, 255, 255, 80),
                                         (glow_radius, glow_radius), glow_radius)
                        self.engine.window.blit(glow_surface, (x - glow_radius, y - glow_radius))
                        
                        # Stone
                        pygame.draw.circle(self.engine.window, (240, 240, 240), (x, y), radius)
                        pygame.draw.circle(self.engine.window, (255, 255, 255), (x, y), radius, 2)
    
    def draw_captured_bowl(self):
        """Draw bowl for captured stones."""
        if not HAS_PYGAME:
            return
        
        # Draw bowl (simplified)
        bowl_x, bowl_y = self.bowl_position
        pygame.draw.ellipse(self.engine.window, (139, 69, 19),
                          (bowl_x - 40, bowl_y - 20, 80, 40))
        
        # Draw captured stones in bowl
        for i, stone_info in enumerate(self.captured_stones[:10]):  # Show up to 10
            x = bowl_x - 30 + (i % 5) * 15
            y = bowl_y - 10 + (i // 5) * 15
            color = (30, 30, 30) if stone_info['color'] == 1 else (240, 240, 240)
            pygame.draw.circle(self.engine.window, color, (x, y), 5)
    
    def draw(self):
        """Draw complete game state."""
        self.draw_board()
    
    def update(self):
        """Update game state."""
        # Update placing animation
        if self.placing_stone:
            elapsed = pygame.time.get_ticks() - self.placing_stone['start_time']
            duration = 300  # 300ms rise
            self.placing_stone['progress'] = min(elapsed / duration, 1.0)
            
            if self.placing_stone['progress'] >= 1.0:
                # Play sound: glass on stone
                if self.engine.audio_enabled:
                    print("[Sound] Glass on stone.")
                self.placing_stone = None
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click to place stone."""
        intersection = self._pos_to_intersection(pos)
        if not intersection:
            return
        
        row, col = intersection
        
        # Check if intersection is empty
        if self.board[row][col] != 0:
            return
        
        # Place stone
        self.board[row][col] = self.current_turn
        
        # Start rising animation
        self.placing_stone = {
            'pos': (row, col),
            'start_time': pygame.time.get_ticks(),
            'progress': 0.0
        }
        
        # Check for captures
        captured = self._check_captures(row, col)
        if captured:
            for cap_row, cap_col in captured:
                # Animate captured stone to bowl
                self._capture_stone(cap_row, cap_col)
        
        # Switch turn
        self.current_turn = 2 if self.current_turn == 1 else 1
    
    def _pos_to_intersection(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen position to board intersection."""
        x, y = pos
        col = round((x - self.board_start_x) / self.square_size)
        row = round((y - self.board_start_y) / self.square_size)
        
        if 0 <= row < 19 and 0 <= col < 19:
            return (row, col)
        return None
    
    def _check_captures(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Check if placing stone captures opponent groups."""
        captured = []
        opponent = 2 if self.current_turn == 1 else 1
        
        # Check adjacent intersections
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            adj_row, adj_col = row + dr, col + dc
            if 0 <= adj_row < 19 and 0 <= adj_col < 19:
                if self.board[adj_row][adj_col] == opponent:
                    # Check if group has liberties
                    group = self._get_group(adj_row, adj_col)
                    if self._group_has_no_liberties(group):
                        captured.extend(group)
        
        return captured
    
    def _get_group(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all stones in a group."""
        color = self.board[row][col]
        if color == 0:
            return []
        
        group = []
        visited = set()
        stack = [(row, col)]
        
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            
            if self.board[r][c] == color:
                group.append((r, c))
                # Check adjacent
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 19 and 0 <= nc < 19 and (nr, nc) not in visited:
                        stack.append((nr, nc))
        
        return group
    
    def _group_has_no_liberties(self, group: List[Tuple[int, int]]) -> bool:
        """Check if group has no liberties."""
        for row, col in group:
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                adj_row, adj_col = row + dr, col + dc
                if 0 <= adj_row < 19 and 0 <= adj_col < 19:
                    if self.board[adj_row][adj_col] == 0:
                        return False
        return True
    
    def _capture_stone(self, row: int, col: int):
        """Capture stone with animation."""
        color = self.board[row][col]
        self.board[row][col] = 0
        
        # Update captured count
        if color == 1:
            self.captured_black += 1
        else:
            self.captured_white += 1
        
        # Animate to bowl
        start_pos = (
            self.board_start_x + col * self.square_size,
            self.board_start_y + row * self.square_size
        )
        
        self.captured_stones.append({
            'color': color,
            'start_pos': start_pos,
            'target_pos': self.bowl_position,
            'start_time': pygame.time.get_ticks(),
            'duration': 500
        })
        
        # Play sound: clink into bowl
        if self.engine.audio_enabled:
            print("[Sound] Clink into bowl.")
        
        print("[System] Captured stones clink into a bowl. All tactile.")

