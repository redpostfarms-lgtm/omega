# -*- coding: utf-8 -*-
# ELARA PERFORMANCE OPTIMIZER
# Industry best practices: double buffering, sprite caching, dirty rectangles

import time
from typing import Dict, List, Tuple, Optional, Set
from collections import deque
import weakref

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class PerformanceOptimizer:
    """
    Performance optimization module.
    
    Features:
    - Double buffering for smooth rendering
    - Sprite caching
    - Dirty rectangle updates
    - Frame rate smoothing
    - Memory pooling
    """
    
    def __init__(self, target_fps: int = 60):
        """Initialize performance optimizer."""
        self.target_fps = target_fps
        self.frame_times = deque(maxlen=60)  # Last 60 frames
        self.avg_frame_time = 16.67  # 60 FPS = 16.67ms per frame
        
        # Dirty rectangle tracking
        self.dirty_rects: Set = set()
        self.full_redraw = False
        
        # Sprite cache
        self.sprite_cache: Dict[str, Any] = {}
        
        # Double buffering
        self.back_buffer = None
        self.front_buffer = None
        
        # Memory pool for frequently allocated objects
        self.rect_pool = []
        self.max_pool_size = 100
    
    def get_rect_from_pool(self, x: int, y: int, w: int, h: int):
        """Get rectangle from pool (reuse objects)."""
        if not HAS_PYGAME:
            return None
        if self.rect_pool:
            rect = self.rect_pool.pop()
            rect.x, rect.y, rect.w, rect.h = x, y, w, h
            return rect
        if HAS_PYGAME:
            return pygame.Rect(x, y, w, h)
        return None
    
    def return_rect_to_pool(self, rect):
        """Return rectangle to pool for reuse."""
        if len(self.rect_pool) < self.max_pool_size:
            self.rect_pool.append(rect)
    
    def mark_dirty(self, rect):
        """Mark rectangle as dirty (needs redraw)."""
        self.dirty_rects.add(rect)
    
    def clear_dirty(self):
        """Clear dirty rectangles."""
        for rect in self.dirty_rects:
            self.return_rect_to_pool(rect)
        self.dirty_rects.clear()
    
    def get_cached_sprite(self, key: str, generator):
        """Get sprite from cache or generate if not cached."""
        if key not in self.sprite_cache:
            self.sprite_cache[key] = generator()
        return self.sprite_cache[key]
    
    def update_frame_time(self, frame_time: float):
        """Update frame time and calculate average."""
        self.frame_times.append(frame_time)
        if len(self.frame_times) >= 10:
            self.avg_frame_time = sum(self.frame_times) / len(self.frame_times)
    
    def should_drop_frame(self) -> bool:
        """Check if should drop frame to maintain FPS."""
        return self.avg_frame_time > (1000.0 / self.target_fps * 1.1)  # 10% threshold
    
    def get_fps(self) -> float:
        """Get current FPS."""
        if self.avg_frame_time > 0:
            return 1000.0 / self.avg_frame_time
        return 0.0


class TranspositionTable:
    """
    Transposition table for chess engine optimization.
    
    Stores evaluated positions to avoid re-computation.
    """
    
    def __init__(self, max_size: int = 100000):
        """Initialize transposition table."""
        self.table: Dict[int, Dict] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get_hash(self, board_state: str) -> int:
        """Get hash for board state."""
        return hash(board_state)
    
    def lookup(self, board_state: str) -> Optional[Dict]:
        """Lookup position in table."""
        key = self.get_hash(board_state)
        if key in self.table:
            self.hits += 1
            return self.table[key]
        self.misses += 1
        return None
    
    def store(self, board_state: str, value: float, depth: int, move: str):
        """Store position in table."""
        if len(self.table) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.table))
            del self.table[oldest_key]
        
        key = self.get_hash(board_state)
        self.table[key] = {
            'value': value,
            'depth': depth,
            'move': move,
            'timestamp': time.time()
        }
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hits + self.misses
        if total > 0:
            return self.hits / total
        return 0.0


class MoveOrderer:
    """
    Move ordering for chess engine optimization.
    
    Orders moves to improve alpha-beta pruning efficiency.
    """
    
    @staticmethod
    def order_moves(moves: List[str], position: Dict) -> List[str]:
        """
        Order moves for best alpha-beta performance.
        
        Order: captures, checks, then quiet moves.
        """
        captures = []
        checks = []
        quiet = []
        
        for move in moves:
            if 'x' in move:  # Capture
                captures.append(move)
            elif '+' in move:  # Check
                checks.append(move)
            else:
                quiet.append(move)
        
        # Order captures by value (capture value heuristic)
        captures.sort(key=lambda m: MoveOrderer._capture_value(m), reverse=True)
        
        return captures + checks + quiet
    
    @staticmethod
    def _capture_value(move: str) -> int:
        """Estimate capture value (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)."""
        # Piece values
        piece_values = {'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'P': 1, 'K': 0}
        
        # Extract captured piece (simplified)
        if 'x' in move:
            parts = move.split('x')
            if len(parts) > 1:
                captured = parts[1][0].upper() if parts[1] else 'P'
                return piece_values.get(captured, 1)
        
        return 0


if __name__ == '__main__':
    print("=" * 60)
    print("ELARA PERFORMANCE OPTIMIZER")
    print("=" * 60)
    
    optimizer = PerformanceOptimizer(target_fps=60)
    
    # Test frame time tracking
    for i in range(10):
        optimizer.update_frame_time(16.0)  # 60 FPS
    
    print(f"Average frame time: {optimizer.avg_frame_time:.2f}ms")
    print(f"FPS: {optimizer.get_fps():.1f}")
    
    # Test transposition table
    tt = TranspositionTable()
    tt.store("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 0.5, 5, "e4")
    result = tt.lookup("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    print(f"Transposition table hit: {result is not None}")
    print(f"Hit rate: {tt.get_hit_rate():.1%}")
    
    # Test move ordering
    moves = ['e4', 'Nf3', 'Bxc4', 'Qh5+', 'Nxe5', 'd4']
    ordered = MoveOrderer.order_moves(moves, {})
    print(f"Ordered moves: {ordered}")
    
    print("\n[OK] Performance optimizer ready")

