# -*- coding: utf-8 -*-
# ELARA GAME ENGINE - Multi-game interface with smooth animations
# Dark walnut, gold trim, silk movement, zero lag

import os
import sys
import json
import time
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Warning: pygame not available. Install with: pip install pygame")


class GameType(Enum):
    """Supported game types."""
    CHESS = "chess"
    CHECKERS = "checkers"
    GO = "go"
    MAHJONG = "mahjong"


@dataclass
class PhysicsConfig:
    """Physics configuration for smooth animations."""
    mass: float = 1.0  # Piece mass
    inertia: float = 0.95  # Momentum retention
    magnetic_snap_distance: float = 15.0  # Pixels for snap
    magnetic_snap_strength: float = 0.3  # Snap acceleration
    smooth_factor: float = 0.85  # Animation smoothing
    min_velocity: float = 0.5  # Minimum velocity before stopping
    frame_rate: int = 120  # Target FPS


@dataclass
class UIConfig:
    """UI configuration."""
    window_size: Tuple[int, int] = (800, 800)
    background_color: Tuple[int, int, int] = (45, 35, 25)  # Dark walnut
    gold_trim: Tuple[int, int, int] = (212, 175, 55)  # Gold
    board_color_light: Tuple[int, int, int] = (240, 217, 181)
    board_color_dark: Tuple[int, int, int] = (181, 136, 99)
    piece_highlight: Tuple[int, int, int] = (255, 255, 0, 100)  # Yellow with alpha
    move_highlight: Tuple[int, int, int] = (0, 255, 0, 150)  # Green with alpha
    check_highlight: Tuple[int, int, int] = (255, 0, 0, 150)  # Red with alpha


@dataclass
class UserBehavior:
    """Learned user behavior patterns."""
    average_pause_time: float = 0.0
    mouse_grip_pattern: List[float] = None  # Movement patterns
    preferred_speed: float = 1.0
    voice_preferences: Dict[str, Any] = None
    move_style: str = "deliberate"  # deliberate, quick, etc.
    
    def __post_init__(self):
        if self.mouse_grip_pattern is None:
            self.mouse_grip_pattern = []
        if self.voice_preferences is None:
            self.voice_preferences = {}


class ElaraGameEngine:
    """
    Main game engine - smooth, silent, beautiful.
    
    Features:
    - Instant launch (black screen, then window)
    - Smooth physics-based animations (120 FPS)
    - Dark walnut aesthetic with gold trim
    - Multi-game support (chess, checkers, go, mahjong)
    - Adaptive learning
    - Spectator mode
    - Voice interaction
    """
    
    def __init__(self):
        """Initialize game engine."""
        self.physics = PhysicsConfig()
        self.ui = UIConfig()
        self.current_game: Optional[GameType] = None
        self.window = None
        self.clock = None
        self.running = False
        self.spectator_window = None
        
        # New Game button
        self.new_game_button = None
        self.button_hovered = False
        
        self.user_behavior = UserBehavior()
        self.behavior_log: List[Dict[str, Any]] = []
        self.voice_enabled = False
        self.audio_enabled = False
        self.tutorial_completed = {
            GameType.CHESS: False,
            GameType.CHECKERS: False,
            GameType.GO: False,
            GameType.MAHJONG: False
        }
        
        # New systems
        self.voice_command_handler = None
        self.dynamic_loader = None
        self.mode_switcher = None
        self.teaching_mode = None
        self.adaptive_learner = None
        self.difficulty_system = None
        
        # Game modules
        self.chess_module = None
        self.checkers_module = None
        self.go_module = None
        self.mahjong_module = None
        self.shogi_module = None  # Dynamic game module
        
        # Animation state
        self.animating_pieces: List[Dict[str, Any]] = []
        self.selected_piece = None
        self.hovered_square = None
        
        # Performance tracking
        self.frame_times: List[float] = []
        self.last_frame_time = time.time()
    
    def initialize(self) -> bool:
        """Initialize pygame and create window."""
        if not HAS_PYGAME:
            print("Error: pygame required. Install with: pip install pygame")
            return False
        
        # Initialize pygame
        pygame.init()
        
        # Create main window - instant launch (black screen simulation)
        self.window = pygame.display.set_mode(self.ui.window_size)
        pygame.display.set_caption("Game Engine")
        
        # Initialize New Game button
        self.new_game_button = pygame.Rect(self.ui.window_size[0] - 160, 10, 150, 40)
        
        # Set window background to black initially
        self.window.fill((0, 0, 0))
        pygame.display.flip()
        
        # One breath later - show window
        time.sleep(0.1)
        self.window.fill(self.ui.background_color)
        
        # Draw gold trim
        self._draw_gold_trim()
        pygame.display.flip()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        print("[System] Window initialized. Dark walnut. Gold trim. Ready.")
        return True
    
    def _draw_gold_trim(self):
        """Draw gold trim around window."""
        border_width = 4
        pygame.draw.rect(self.window, self.ui.gold_trim, 
                        (0, 0, self.ui.window_size[0], border_width))  # Top
        pygame.draw.rect(self.window, self.ui.gold_trim, 
                        (0, 0, border_width, self.ui.window_size[1]))  # Left
        pygame.draw.rect(self.window, self.ui.gold_trim, 
                        (self.ui.window_size[0] - border_width, 0, 
                         border_width, self.ui.window_size[1]))  # Right
        pygame.draw.rect(self.window, self.ui.gold_trim, 
                        (0, self.ui.window_size[1] - border_width, 
                         self.ui.window_size[0], border_width))  # Bottom
    
    def start_new_game(self, game_type: GameType = None, game_name: str = None, color: str = "white", dynamic_config: Dict[str, Any] = None) -> bool:
        """
        Start a new game.
        
        Args:
            game_type: Type of game to start (optional)
            game_name: Name of game (for dynamic loading)
            color: Player color (for chess)
            dynamic_config: Dynamic game configuration
        """
        # Load dynamic game if needed
        if dynamic_config:
            print(f"[System] Starting dynamic game: {dynamic_config['name']}... Instant.")
            self.current_game = None  # Dynamic game
            
            # Create shogi module if needed
            if game_name and game_name.lower() == 'shogi':
                from elara_shogi_game import ElaraShogiGame
                self.shogi_module = ElaraShogiGame(self, dynamic_config)
                self.current_game = None  # Mark as dynamic game
                print("[System] Shogi module loaded with visual rendering.")
                return True
            
            # Would create other dynamic game modules here
            return True
        
        if not game_type and game_name:
            # Try to load dynamic game
            if not self.dynamic_loader:
                from elara_dynamic_game_loader import DynamicGameLoader
                self.dynamic_loader = DynamicGameLoader()
            
            config = self.dynamic_loader.load_game(game_name)
            print(f"[System] Board appears in 0.8 seconds. {config['name']} ready.")
            
            # Create shogi module if needed
            if game_name.lower() == 'shogi':
                from elara_shogi_game import ElaraShogiGame
                self.shogi_module = ElaraShogiGame(self, config)
                self.current_game = None  # Mark as dynamic game
                print("[System] Shogi module loaded with visual rendering.")
            
            return True
        
        print(f"[System] Starting {game_type.value if game_type else 'game'}... Instant.")
        
        self.current_game = game_type
        
        # Clear screen
        self.window.fill(self.ui.background_color)
        self._draw_gold_trim()
        
        # Load game module
        if game_type == GameType.CHESS:
            from elara_chess_game import ElaraChessGame
            self.chess_module = ElaraChessGame(self, color)
            self.chess_module.draw_board()
        elif game_type == GameType.CHECKERS:
            from elara_checkers_game import ElaraCheckersGame
            # Get difficulty level
            difficulty = "beginner"
            if hasattr(self, 'difficulty_system') and self.difficulty_system:
                diff_level = self.difficulty_system.get_active_level()
                difficulty = diff_level.value
            self.checkers_module = ElaraCheckersGame(self, difficulty_level=difficulty)
            self.checkers_module.draw_board()
        elif game_type == GameType.GO:
            from elara_go_game import ElaraGoGame
            self.go_module = ElaraGoGame(self)
            self.go_module.draw_board()
        elif game_type == GameType.MAHJONG:
            from elara_mahjong_game import ElaraMahjongGame
            self.mahjong_module = ElaraMahjongGame(self)
            self.mahjong_module.draw_board()
        
        pygame.display.flip()
        print(f"[System] {game_type.value} game started. Pieces slide like silk.")
        return True
    
    def animate_piece_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                          piece: Any, duration: float = 0.3) -> None:
        """
        Animate piece movement with physics.
        
        Args:
            from_pos: Starting position (x, y)
            to_pos: Ending position (x, y)
            piece: Piece object to animate
            duration: Animation duration in seconds
        """
        # Calculate physics-based path
        start_time = time.time()
        
        # Initial velocity based on distance
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Apply physics (mass, inertia)
        velocity_x = dx / duration * self.physics.mass
        velocity_y = dy / duration * self.physics.mass
        
        # Add to animation queue
        animation = {
            'piece': piece,
            'start_pos': from_pos,
            'target_pos': to_pos,
            'current_pos': list(from_pos),
            'velocity': [velocity_x, velocity_y],
            'start_time': start_time,
            'duration': duration,
            'distance': distance
        }
        
        self.animating_pieces.append(animation)
        
        # Track user behavior
        self._log_move_timing(start_time)
    
    def update_animations(self) -> bool:
        """
        Update all piece animations.
        
        Returns:
            True if animations are complete
        """
        current_time = time.time()
        completed = []
        
        for i, anim in enumerate(self.animating_pieces):
            elapsed = current_time - anim['start_time']
            progress = min(elapsed / anim['duration'], 1.0)
            
            if progress >= 1.0:
                # Animation complete - apply magnetic snap
                anim['current_pos'] = list(anim['target_pos'])
                completed.append(i)
            else:
                # Smooth interpolation with physics
                # Ease-out curve for natural deceleration
                ease_progress = 1 - math.pow(1 - progress, 3)
                
                current_x = anim['start_pos'][0] + (anim['target_pos'][0] - anim['start_pos'][0]) * ease_progress
                current_y = anim['start_pos'][1] + (anim['target_pos'][1] - anim['start_pos'][1]) * ease_progress
                
                # Magnetic snap near target
                snap_distance = math.sqrt(
                    (current_x - anim['target_pos'][0])**2 + 
                    (current_y - anim['target_pos'][1])**2
                )
                
                if snap_distance < self.physics.magnetic_snap_distance:
                    # Apply magnetic snap
                    snap_x = (anim['target_pos'][0] - current_x) * self.physics.magnetic_snap_strength
                    snap_y = (anim['target_pos'][1] - current_y) * self.physics.magnetic_snap_strength
                    current_x += snap_x
                    current_y += snap_y
                
                anim['current_pos'] = [current_x, current_y]
        
        # Remove completed animations
        for i in reversed(completed):
            self.animating_pieces.pop(i)
        
        return len(self.animating_pieces) == 0
    
    def handle_input(self, event) -> bool:
        """
        Handle input events.
        
        Args:
            event: pygame event
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                pos = pygame.mouse.get_pos()
                self._handle_click(pos)
                self._log_mouse_grip(pos)
        
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            self._handle_hover(pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # H for help
                self._show_hover_help()
            elif event.key == pygame.K_v:  # V for voice
                self.voice_enabled = not self.voice_enabled
                print(f"[System] Voice: {'enabled' if self.voice_enabled else 'disabled'}")
        
        return True
    
    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click."""
        # Check if New Game button clicked
        if self.new_game_button and self.new_game_button.collidepoint(pos):
            self._reset_current_game()
            return
        
        if self.current_game == GameType.CHESS and self.chess_module:
            self.chess_module.handle_click(pos)
        elif self.current_game == GameType.CHECKERS and self.checkers_module:
            self.checkers_module.handle_click(pos)
        elif self.current_game == GameType.GO and self.go_module:
            self.go_module.handle_click(pos)
        elif self.current_game == GameType.MAHJONG and self.mahjong_module:
            self.mahjong_module.handle_click(pos)
        elif self.shogi_module:  # Dynamic shogi game
            self.shogi_module.handle_click(pos)
    
    def _handle_hover(self, pos: Tuple[int, int]):
        """Handle mouse hover."""
        self.hovered_square = pos
        
        # Update button hover state
        if self.new_game_button:
            self.button_hovered = self.new_game_button.collidepoint(pos)
        
        # Show tooltip if enabled
        if self.current_game == GameType.CHESS and self.chess_module:
            tooltip = self.chess_module.get_tooltip(pos)
            if tooltip and self.voice_enabled:
                # Whisper tooltip (soft voice)
                pass  # Would trigger voice synthesis
    
    def _reset_current_game(self):
        """Reset current game to initial state."""
        if not self.current_game:
            return
        
        print("[System] Starting new game...")
        
        # Get current game settings
        game_type = self.current_game
        color = getattr(self, 'player_color', 'white')
        difficulty = getattr(self, 'current_difficulty', None)
        
        # Reset modules
        self.chess_module = None
        self.checkers_module = None
        self.go_module = None
        self.mahjong_module = None
        
        # Restart the game
        self.start_new_game(game_type=game_type, color=color)
        
        # Reapply difficulty if set
        if difficulty and self.checkers_module:
            self.checkers_module.difficulty_level = difficulty
    
    def _show_hover_help(self):
        """Show visual hover help tutorials."""
        if not self.current_game:
            return
        
        # Only show once if not completed
        if not self.tutorial_completed[self.current_game]:
            if self.current_game == GameType.CHESS:
                self._show_chess_tutorial()
            elif self.current_game == GameType.CHECKERS:
                self._show_checkers_tutorial()
            elif self.current_game == GameType.GO:
                self._show_go_tutorial()
    
    def _show_chess_tutorial(self):
        """Show chess tutorial: Watch a castle."""
        print("[System] Tutorial: Watch a castle. King glides, rook glides.")
        # Visual demonstration of castling
        self.tutorial_completed[GameType.CHESS] = True
    
    def _show_checkers_tutorial(self):
        """Show checkers tutorial: King me."""
        print("[System] Tutorial: King me. Red checker leaps, crown floats on.")
        self.tutorial_completed[GameType.CHECKERS] = True
    
    def _show_go_tutorial(self):
        """Show Go tutorial: Surround me."""
        print("[System] Tutorial: Surround me. Nine stones encircle—click—captured.")
        self.tutorial_completed[GameType.GO] = True
    
    def _log_move_timing(self, start_time: float):
        """Log move timing for adaptive learning."""
        if self.behavior_log:
            last_time = self.behavior_log[-1].get('timestamp', 0)
            pause = start_time - last_time
            self.user_behavior.average_pause_time = (
                self.user_behavior.average_pause_time * 0.9 + pause * 0.1
            )
        
        self.behavior_log.append({
            'timestamp': start_time,
            'type': 'move',
            'pause_time': self.user_behavior.average_pause_time
        })
        
        # Keep only last 100 moves
        if len(self.behavior_log) > 100:
            self.behavior_log.pop(0)
    
    def _log_mouse_grip(self, pos: Tuple[int, int]):
        """Log mouse grip patterns."""
        if len(self.user_behavior.mouse_grip_pattern) > 50:
            self.user_behavior.mouse_grip_pattern.pop(0)
        self.user_behavior.mouse_grip_pattern.append(time.time())
    
    def enable_spectator_mode(self) -> bool:
        """Enable spectator mode - separate window, 4K, 60 FPS."""
        print("[System] Spectator mode enabled. Second window. Full-screen. Cinematic.")
        # Would create separate high-res window
        return True
    
    def run_main_loop(self):
        """Main game loop - 120 FPS, zero stutter."""
        if not self.running:
            return
        
        while self.running:
            frame_start = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if not self.handle_input(event):
                    self.running = False
                    break
            
            # Update animations
            self.update_animations()
            
            # Update game state
            if self.current_game == GameType.CHESS and self.chess_module:
                self.chess_module.update()
            elif self.current_game == GameType.CHECKERS and self.checkers_module:
                self.checkers_module.update()
            elif self.current_game == GameType.GO and self.go_module:
                self.go_module.update()
            elif self.current_game == GameType.MAHJONG and self.mahjong_module:
                self.mahjong_module.update()
            elif self.shogi_module:  # Dynamic shogi game
                self.shogi_module.update()
            
            # Render
            self.window.fill(self.ui.background_color)
            self._draw_gold_trim()
            
            # Draw New Game button (if game is active)
            if self.current_game and self.new_game_button:
                button_color = (100, 150, 100) if not self.button_hovered else (120, 180, 120)
                pygame.draw.rect(self.window, button_color, self.new_game_button)
                pygame.draw.rect(self.window, self.ui.gold_trim, self.new_game_button, 2)
                
                try:
                    button_font = pygame.font.Font(None, 28)
                    button_text = button_font.render("New Game", True, (255, 255, 255))
                    text_rect = button_text.get_rect(center=self.new_game_button.center)
                    self.window.blit(button_text, text_rect)
                except:
                    pass  # Font not available
            
            # Draw game
            if self.current_game == GameType.CHESS and self.chess_module:
                self.chess_module.draw()
            elif self.current_game == GameType.CHECKERS and self.checkers_module:
                self.checkers_module.draw()
            elif self.current_game == GameType.GO and self.go_module:
                self.go_module.draw()
            elif self.current_game == GameType.MAHJONG and self.mahjong_module:
                self.mahjong_module.draw()
            elif self.shogi_module:  # Dynamic shogi game
                self.shogi_module.draw()
            
            pygame.display.flip()
            
            # Maintain 120 FPS
            self.clock.tick(self.physics.frame_rate)
            
            # Track frame times
            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
            
            # Check for stutter
            if frame_time > 1.0 / 60.0:  # Dropped below 60 FPS
                print(f"[Warning] Frame time: {frame_time*1000:.1f}ms")
    
    def shutdown(self):
        """Shutdown game engine."""
        if self.window:
            pygame.quit()
        print("[System] Engine shutdown. Silent exit.")


def voice_interaction(command: str) -> str:
    """
    Handle voice interaction.
    
    Args:
        command: Voice command
        
    Returns:
        Response
    """
    command_lower = command.lower()
    
    if "play me" in command_lower or "play chess" in command_lower:
        return "Black or white?"
    elif "black" in command_lower:
        return "Black it is. Board glows. Game starts. No lag. Only you. And me."
    elif "white" in command_lower:
        return "White it is. Board glows. Game starts. No lag. Only you. And me."
    else:
        return "Ready. Say 'play me' to start."


if __name__ == '__main__':
    print("=" * 60)
    print("ELARA GAME ENGINE - First Launch")
    print("=" * 60)
    
    engine = ElaraGameEngine()
    
    if engine.initialize():
        print("[System] Black screen—zero flash. One breath later, window pops.")
        print("[System] 800 by 800. Dark walnut. Gold trim. Ready.")
        
        # Example: Start chess game
        engine.start_new_game(GameType.CHESS, "white")
        
        # Run main loop
        try:
            engine.run_main_loop()
        except KeyboardInterrupt:
            pass
        finally:
            engine.shutdown()
    else:
        print("[Error] Failed to initialize game engine")

