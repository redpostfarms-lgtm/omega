# -*- coding: utf-8 -*-
# ELARA MAHJONG GAME - Tiles stack like marble, drag match, collapse like water

import math
from typing import Dict, List, Optional, Tuple, Any
import random

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class ElaraMahjongGame:
    """
    Mahjong game module for Elara engine.
    
    Features:
    - Tiles stack like marble
    - Click, flip, reveal dragon
    - Drag match, boom - collapse
    - No explosion, just flow like water
    """
    
    def __init__(self, engine):
        """Initialize Mahjong game."""
        self.engine = engine
        self.tile_width = 60
        self.tile_height = 80
        self.tile_spacing = 5
        
        # Tile types (simplified)
        self.tile_types = ['dragon', 'circle', 'bamboo', 'character', 'wind']
        self.tiles: List[Dict[str, Any]] = []
        self.selected_tiles: List[int] = []
        self.matched_tiles: List[int] = []
        
        # Animation state
        self.flipping_tiles: List[Dict[str, Any]] = []
        self.collapsing_tiles: List[Dict[str, Any]] = []
        
        # Initialize tiles
        self._init_tiles()
    
    def _init_tiles(self):
        """Initialize Mahjong tiles."""
        # Create pairs of tiles
        tile_pairs = []
        for tile_type in self.tile_types:
            for value in range(1, 10):
                tile_pairs.append((tile_type, value))
                tile_pairs.append((tile_type, value))  # Pair
        
        # Shuffle and position
        random.shuffle(tile_pairs)
        
        # Create tile layout (pyramid shape)
        layout_rows = [
            [28, 29, 30, 31, 32, 33, 34, 35, 36],
            [19, 20, 21, 22, 23, 24, 25, 26, 27],
            [10, 11, 12, 13, 14, 15, 16, 17, 18],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ]
        
        row_y = 100
        for row_idx, row_layout in enumerate(layout_rows):
            row_x = 100 + (3 - row_idx) * 30  # Offset for pyramid
            for col_idx, tile_idx in enumerate(row_layout):
                if tile_idx < len(tile_pairs):
                    tile_type, value = tile_pairs[tile_idx]
                    x = row_x + col_idx * (self.tile_width + self.tile_spacing)
                    y = row_y
                    
                    self.tiles.append({
                        'type': tile_type,
                        'value': value,
                        'x': x,
                        'y': y,
                        'flipped': False,
                        'matched': False,
                        'z_index': row_idx
                    })
            
            row_y += self.tile_height + self.tile_spacing
    
    def draw_board(self):
        """Draw Mahjong tiles stacked like marble."""
        if not HAS_PYGAME:
            return
        
        # Sort by z-index for proper stacking
        sorted_tiles = sorted(self.tiles, key=lambda t: t['z_index'], reverse=True)
        
        for tile in sorted_tiles:
            if tile['matched']:
                continue
            
            x = tile['x']
            y = tile['y']
            
            # Check if flipping
            if tile in [ft['tile'] for ft in self.flipping_tiles]:
                flip_info = next(ft for ft in self.flipping_tiles if ft['tile'] == tile)
                progress = flip_info['progress']
                
                # 3D flip effect
                scale_x = abs(math.cos(progress * math.pi))
                x_offset = (self.tile_width - self.tile_width * scale_x) / 2
                x += int(x_offset)
            
            # Draw tile (marble-like)
            tile_rect = pygame.Rect(x, y, self.tile_width, self.tile_height)
            
            if tile['flipped']:
                # Draw tile face
                color = (255, 240, 220)  # Marble color
                pygame.draw.rect(self.engine.window, color, tile_rect)
                pygame.draw.rect(self.engine.window, (200, 180, 160), tile_rect, 2)
                
                # Draw tile symbol (simplified)
                if tile['type'] == 'dragon':
                    # Draw dragon symbol
                    font = pygame.font.Font(None, 36)
                    text = font.render("龍", True, (100, 0, 0))
                    text_rect = text.get_rect(center=(x + self.tile_width//2, y + self.tile_height//2))
                    self.engine.window.blit(text, text_rect)
                    print("[System] Click, flip, reveal dragon.")
            else:
                # Draw tile back (marble texture)
                # Gradient for marble effect
                for i in range(self.tile_height):
                    shade = 180 + int(20 * math.sin(i / 5))
                    pygame.draw.line(self.engine.window, (shade, shade, shade),
                                   (x, y + i), (x + self.tile_width, y + i))
            
            # Highlight if selected
            if tile in [self.tiles[i] for i in self.selected_tiles if i < len(self.tiles)]:
                highlight = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
                highlight.fill((255, 255, 0, 100))
                self.engine.window.blit(highlight, (x, y))
    
    def draw(self):
        """Draw complete game state."""
        self.draw_board()
        self._draw_collapsing_tiles()
    
    def _draw_collapsing_tiles(self):
        """Draw collapsing tile animations."""
        if not HAS_PYGAME:
            return
        
        for collapse in self.collapsing_tiles:
            progress = collapse['progress']
            tile = collapse['tile']
            
            # Flow like water - particles flow down
            x = tile['x']
            y = tile['y'] + int(100 * progress)  # Flow down
            
            # Opacity fade
            alpha = int(255 * (1 - progress))
            tile_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
            tile_surface.fill((255, 240, 220, alpha))
            self.engine.window.blit(tile_surface, (x, y))
    
    def update(self):
        """Update game state."""
        # Update flipping animations
        current_time = pygame.time.get_ticks()
        to_remove = []
        
        for i, flip in enumerate(self.flipping_tiles):
            elapsed = current_time - flip['start_time']
            duration = 400  # 400ms flip
            flip['progress'] = min(elapsed / duration, 1.0)
            
            if flip['progress'] >= 1.0:
                flip['tile']['flipped'] = True
                to_remove.append(i)
        
        for i in reversed(to_remove):
            self.flipping_tiles.pop(i)
        
        # Update collapsing animations
        to_remove = []
        for i, collapse in enumerate(self.collapsing_tiles):
            elapsed = current_time - collapse['start_time']
            duration = 600  # 600ms collapse
            collapse['progress'] = min(elapsed / duration, 1.0)
            
            if collapse['progress'] >= 1.0:
                collapse['tile']['matched'] = True
                to_remove.append(i)
        
        for i in reversed(to_remove):
            self.collapsing_tiles.pop(i)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click."""
        tile_idx = self._pos_to_tile(pos)
        if tile_idx is None:
            return
        
        tile = self.tiles[tile_idx]
        
        # Flip tile
        if not tile['flipped']:
            self.flipping_tiles.append({
                'tile': tile,
                'start_time': pygame.time.get_ticks(),
                'progress': 0.0
            })
        
        # Select tile for matching
        elif tile['flipped'] and not tile['matched']:
            if tile_idx not in self.selected_tiles:
                self.selected_tiles.append(tile_idx)
            
            # Check for match (2 selected)
            if len(self.selected_tiles) == 2:
                idx1, idx2 = self.selected_tiles
                tile1 = self.tiles[idx1]
                tile2 = self.tiles[idx2]
                
                if tile1['type'] == tile2['type'] and tile1['value'] == tile2['value']:
                    # Match! Collapse like water
                    self._match_tiles(idx1, idx2)
                else:
                    # No match
                    self.selected_tiles = []
    
    def _pos_to_tile(self, pos: Tuple[int, int]) -> Optional[int]:
        """Convert screen position to tile index."""
        x, y = pos
        
        # Check tiles from top to bottom (z-order)
        sorted_tiles = sorted(enumerate(self.tiles), 
                            key=lambda t: t[1]['z_index'], reverse=True)
        
        for idx, tile in sorted_tiles:
            if tile['matched']:
                continue
            
            tile_x = tile['x']
            tile_y = tile['y']
            
            if tile_x <= x <= tile_x + self.tile_width and \
               tile_y <= y <= tile_y + self.tile_height:
                return idx
        
        return None
    
    def _match_tiles(self, idx1: int, idx2: int):
        """Match two tiles - collapse like water."""
        tile1 = self.tiles[idx1]
        tile2 = self.tiles[idx2]
        
        # Start collapse animations
        self.collapsing_tiles.append({
            'tile': tile1,
            'start_time': pygame.time.get_ticks(),
            'progress': 0.0
        })
        self.collapsing_tiles.append({
            'tile': tile2,
            'start_time': pygame.time.get_ticks(),
            'progress': 0.0
        })
        
        self.selected_tiles = []
        print("[System] Drag match, boom—collapse. No explosion. Just flow like water.")

