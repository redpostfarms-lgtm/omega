# -*- coding: utf-8 -*-
# ELARA INTEGRATED SYSTEM
# Complete integration: Framework + Difficulty + Teaching + Adaptive Learning

from elara_framework import ElaraFramework, GameType, PlayerProfile
from elara_difficulty_system import DifficultySystem, DifficultyLevel
from elara_teaching_mode import TeachingMode, TeachingLevel
from elara_voice_command import VoiceCommandHandler
from elara_performance_optimizer import PerformanceOptimizer
from elara_chess_engine_optimized import OptimizedChessEngine
from elara_state_manager import StateManager, GameState
import time

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class ElaraIntegratedSystem:
    """
    Complete integrated system.
    
    Every move is a data point.
    Never peaks. Always evolves.
    Natural. Organic.
    """
    
    def __init__(self):
        """Initialize integrated system."""
        self.framework = ElaraFramework()
        self.difficulty = DifficultySystem()
        self.teaching = TeachingMode(TeachingLevel.NORMAL)
        self.voice_handler = VoiceCommandHandler()
        
        # Initialize game engine (for rendering/interaction)
        from elara_game_engine import ElaraGameEngine
        self.game_engine = ElaraGameEngine()
        self.game_engine.difficulty_system = self.difficulty
        
        # Connect systems
        self.framework.difficulty_system = self.difficulty
        self.framework.teaching_mode = self.teaching
        self.framework.game_engine = self.game_engine  # Allow framework to access engine
        
        # Performance optimizations
        self.performance_optimizer = PerformanceOptimizer(target_fps=60)
        self.chess_engine = OptimizedChessEngine(max_depth=6)
        self.state_manager = StateManager()
        
        # Connect to framework
        self.framework.performance_optimizer = self.performance_optimizer
        self.framework.chess_engine = self.chess_engine
        self.framework.state_manager = self.state_manager
        
        # Current state
        self.current_user = "default"
        self.game_active = False
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice command: 'let's play [game]'."""
        # Parse game command
        game_type, game_name, options = self.voice_handler.parse_command(command)
        
        if not game_type and not game_name:
            return False
        
        # Load board (0.3s)
        if game_type:
            if isinstance(game_type, GameType):
                game_enum = game_type
            else:
                game_enum = GameType[game_type.value.upper()]
        else:
            # Dynamic game
            self.framework.learn_new_game(game_name)
            return True
        
        self.framework.load_board_engine(game_enum)
        self.framework.build_visual_grid()
        self.framework.render_pieces()
        
        # Start game in engine (creates game module)
        # Only if pygame is available and engine initialized
        if HAS_PYGAME and hasattr(self.game_engine, 'window') and self.game_engine.window:
            self.game_engine.start_new_game(game_type=game_enum, color="white")
        else:
            # Create game module directly without pygame
            if game_enum == GameType.CHECKERS:
                from elara_checkers_game import ElaraCheckersGame
                difficulty = self.difficulty.get_active_level().value
                self.game_engine.checkers_module = ElaraCheckersGame(self.game_engine, difficulty_level=difficulty)
                self.game_engine.current_game = game_enum
        
        # Run silent tutorial (game-specific)
        self.framework.run_silent_tutorial(game_type=game_enum)
        
        # Enable mouse
        self.framework.enable_mouse_move()
        
        # Set player
        if self.current_user not in self.framework.player_profiles:
            self.framework.player_profiles[self.current_user] = PlayerProfile(name=self.current_user)
        self.framework.current_player = self.framework.player_profiles[self.current_user]
        
        # Set difficulty
        user_level = self.difficulty.get_user_level(self.current_user)
        self.difficulty.current_level = user_level
        
        self.game_active = True
        
        print(f"[System] Game ready. Level: {user_level.value}. Board in 0.3s.")
        return True
    
    def handle_move(self, move: str, square: str, stare_time: float, click_speed: float):
        """Handle player move with full tracking."""
        if not self.framework.current_player:
            return
        
        # Track move
        self.framework.current_player.moves.append(move)
        
        # Track micro-behavior
        wiggles = self.framework.track_cursor_wiggle((0, 0))  # Would use actual cursor pos
        if self.framework.current_player:
            self.framework.track_micro_behavior(square, "move", {
                'stare_time': stare_time,
                'click_speed': click_speed,
                'cursor_wiggles': wiggles,
                'hesitation_count': 0
            })
        
        # Record click time
        self.framework.click_times.append(time.time())
        
        # Teaching mode commentary
        self.teaching.record_move(move, "player")
        comment = self.teaching.generate_comment()
        if comment:
            self.teaching.whisper(comment)
        
        # Smack talk
        level = self.difficulty.get_active_level().value
        smack = self.framework.generate_smack_talk(level, move)
        print(f"[System] {smack}")
        
        # AI move (if solo) - would check mode switcher
        # For now, just demonstrate
        if self.game_active:
            ai_move = self.difficulty.select_move([move], {})  # Would use actual legal moves
            self.teaching.record_move(ai_move, "ai")
            print(f"[System] {ai_move}")
        
        # Analyze patterns
        self.framework.analyze_patterns()
        
        # Learn mid-game
        self.framework.learn_mid_game()
    
    def handle_difficulty_switch(self, command: str):
        """Handle difficulty switch: 'expert on', 'teach me'."""
        # Parse difficulty command
        diff_cmd = self.voice_handler.parse_difficulty_command(command)
        
        if diff_cmd == "teach_mode":
            self.difficulty.enable_teach_mode()
            print("[System] Teach mode: Dropped one tier. Explains every breath.")
            return True
        
        elif diff_cmd in ['beginner', 'intermediate', 'expert', 'master']:
            level = DifficultyLevel[diff_cmd.upper()]
            self.difficulty.switch_level_mid_game(level)
            print(f"[System] Switched to {diff_cmd}. Tightened.")
            return True
        
        return False
    
    def end_game(self, won: bool):
        """End game - track, analyze, evolve."""
        if not self.framework.current_player:
            return
        
        player = self.framework.current_player
        
        # Update stats
        player.games_played += 1
        if won:
            player.wins += 1
        else:
            player.losses += 1
        
        # Record history
        player.history.append({
            'won': won,
            'moves': len(player.moves),
            'blunders': len(player.blunders),
            'timestamp': time.time()
        })
        
        # Track in difficulty system
        move_count = len(player.moves)
        if player.micro_behaviors and move_count > 0:
            avg_move_time = sum(b.stare_time for b in player.micro_behaviors[-move_count:]) / move_count
        else:
            avg_move_time = 0.0
        self.difficulty.track_game_result(self.current_user, won, move_count, avg_move_time)
        
        # Analyze patterns
        self.framework.analyze_patterns()
        
        # Whisper history
        if player.patterns and 'feared_square' in player.patterns:
            feared = player.patterns['feared_square']
            print(f"[Whisper] You feared {feared} last time.")
        
        # Evolve
        self.framework.evolve()
        
        # Save
        self.framework.save_profiles()
        self.difficulty.save_profiles()
        
        print(f"[System] Game complete. Games: {player.games_played}. Wins: {player.wins}.")
        print("[System] Never peaks. Always learns. Natural. Organic.")


if __name__ == '__main__':
    print("=" * 60)
    print("ELARA INTEGRATED SYSTEM")
    print("=" * 60)
    
    system = ElaraIntegratedSystem()
    
    # Test voice command
    print("\n[Test] Voice Command")
    system.handle_voice_command("let's play chess")
    
    # Test move tracking
    print("\n[Test] Move Tracking")
    system.handle_move("e4", "e4", stare_time=2.5, click_speed=0.3)
    system.handle_move("e5", "e5", stare_time=1.8, click_speed=0.2)
    
    # Test difficulty switch
    print("\n[Test] Difficulty Switch")
    system.handle_difficulty_switch("expert on")
    
    # Test teach mode
    print("\n[Test] Teach Mode")
    system.handle_difficulty_switch("teach me")
    
    # Test end game
    print("\n[Test] End Game")
    system.end_game(won=False)
    
    print("\n[OK] Integrated system ready. Every move is a data point.")

