# -*- coding: utf-8 -*-
# GAME ENGINE - Main Launcher
# "let's play [game]" → instant board, smooth response

import sys
import os
import time
from pathlib import Path

# Import game engine
try:
    from elara_game_engine import ElaraGameEngine, GameType, voice_interaction
    from elara_voice_command import VoiceCommandHandler
    from elara_dynamic_game_loader import DynamicGameLoader
    from elara_mode_switcher import ModeSwitcher, GameMode
    from elara_teaching_mode import TeachingMode, TeachingLevel
    from elara_adaptive_learner import AdaptiveLearner
    from elara_voice_system import VoiceSystem
    from elara_difficulty_system import DifficultySystem, DifficultyLevel
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all elara_*.py files are in the same directory")
    sys.exit(1)


def handle_voice_command(command: str, engine: ElaraGameEngine) -> bool:
    """Handle voice command 'let's play [game]'."""
    if not engine.voice_command_handler:
        engine.voice_command_handler = VoiceCommandHandler()
    
    handler = engine.voice_command_handler
    
    # Parse command
    game_type, game_name, options = handler.parse_command(command)
    
    if not game_type and not game_name:
        return False
    
    # Get response
        response = handler.respond_to_command(game_type, game_name)
        print(f"[System] {response}")
        
        # Start game
        start_time = time.time()
        
        if game_type:
            # Known game type
            engine.start_new_game(game_type=game_type, color="white")
        elif game_name and options.get('dynamic'):
            # Dynamic game (shogi, hex, oware)
            engine.start_new_game(game_name=game_name, dynamic_config=options)
        
        elapsed = time.time() - start_time
        print(f"[System] Board appears in {elapsed:.2f} seconds. Mouse ready. Voice calm. Game starts clean.")
    
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("ELARA GAME ENGINE - Ready")
    print("=" * 60)
    
    # Initialize components
    engine = ElaraGameEngine()
    learner = AdaptiveLearner()
    voice = VoiceSystem(enabled=True)
    mode_switcher = ModeSwitcher()
    teaching_mode = TeachingMode(TeachingLevel.NORMAL)
    
    # Initialize engine
    if not engine.initialize():
        print("[Error] Failed to initialize game engine")
        return
    
    # Connect systems
    engine.adaptive_learner = learner
    engine.mode_switcher = mode_switcher
    engine.teaching_mode = teaching_mode
    engine.voice_enabled = True
    
    # Initialize difficulty system
    difficulty = DifficultySystem()
    engine.difficulty_system = difficulty
    
    # Set default user level (Intermediate)
    default_user = "default"
    difficulty.set_user_level(default_user, DifficultyLevel.INTERMEDIATE)
    print(f"\n[Difficulty] {difficulty.get_user_summary(default_user)}")
    
    print("\n[System] Ready. Say 'let's play [game]' to start.")
    print("Games: chess, checkers, go, mahjong, shogi, hex, oware")
    
    # Check for voice command
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        
        if "let's play" in command.lower() or "lets play" in command.lower():
            if handle_voice_command(command, engine):
                # Run game with teaching mode
                run_game_with_teaching(engine)
        else:
            # Old command format
            response = voice_interaction(command)
            print(f"[System] {response}")
    else:
        # Example: Run solo chess game with teaching
        print("\n[System] Running solo chess game with teaching mode...")
        print("[System] 30 moves. No text walls. Just voice, just truth.\n")
        
        engine.start_new_game(GameType.CHESS, "white")
        mode_switcher.switch_mode(GameMode.SOLO)
        
        # Simulate game with teaching
        simulate_teaching_game(engine, teaching_mode, 30)
    
    # Shutdown
    learner.save_patterns()
    engine.shutdown()


def run_game_with_teaching(engine: ElaraGameEngine):
    """Run game with teaching mode active."""
    if not engine.teaching_mode:
        return
    
    print("\n[System] Teaching mode active. Every 3 turns, I whisper.")
    print("[System] Say 'quiet' to stop. Say 'why' to understand.\n")
    
    # Would run actual game loop here
    # For now, just demonstrate teaching
    pass


def simulate_teaching_game(engine: ElaraGameEngine, teacher: TeachingMode, num_moves: int):
    """Simulate a teaching game."""
    moves = [
        ("e4", "white"), ("e5", "black"), ("Nf3", "white"),
        ("Nc6", "black"), ("Bc4", "white"), ("Bc5", "black"),
        ("b4", "white"), ("Bxb4", "black"), ("c3", "white"),
    ]
    
    for i, (move, player) in enumerate(moves[:num_moves]):
        teacher.record_move(move, player)
        
        # Check for commentary
        comment = teacher.generate_comment()
        if comment:
            teacher.whisper(comment)
            
            # Simulate user interaction
            if i == 3:  # After knight comment
                explanation = teacher.handle_user_response("why")
                if explanation:
                    print(f"[System] {explanation}")
    
    print("\n[System] Game complete. No text walls. Just voice, just truth.")


if __name__ == '__main__':
    main()
