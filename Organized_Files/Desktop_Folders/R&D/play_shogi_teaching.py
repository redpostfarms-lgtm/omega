# -*- coding: utf-8 -*-
# PLAY SHOGI WITH TEACHING MODE
# Launches shogi with tutorial and teaching commentary

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from elara_game_engine import ElaraGameEngine, GameType
    from elara_dynamic_game_loader import DynamicGameLoader
    from elara_teaching_mode import TeachingMode, TeachingLevel
    from elara_integrated_system import ElaraIntegratedSystem
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all elara_*.py files are in the same directory")
    sys.exit(1)

print("=" * 60)
print("SHOGI - Teaching Mode")
print("=" * 60)

# Initialize integrated system
system = ElaraIntegratedSystem()

# Enable teaching mode with verbose level for tutorial
system.teaching = TeachingMode(TeachingLevel.VERBOSE)
system.framework.teaching_mode = system.teaching

# Set user
system.current_user = "player"

print("\n[System] Loading shogi with teaching mode...")
print("[System] Tutorial will explain moves, pieces, and strategy.")

# Start shogi game (dynamic loading)
try:
    # Use dynamic game loader to load shogi
    if not system.game_engine.dynamic_loader:
        from elara_dynamic_game_loader import DynamicGameLoader
        system.game_engine.dynamic_loader = DynamicGameLoader()
    
    # Load shogi configuration
    shogi_config = system.game_engine.dynamic_loader.load_game("shogi")
    
    if shogi_config:
        print(f"[System] Shogi loaded: {shogi_config.get('name', 'Shogi')}")
        print(f"[System] Board size: {shogi_config.get('board_size', '9x9')}")
        print(f"[System] Pieces: {len(shogi_config.get('pieces', []))}")
        
        # Start game with dynamic config
        system.game_engine.start_new_game(
            game_name="shogi",
            dynamic_config=shogi_config
        )
        
        print("\n[System] Shogi board ready!")
        print("[System] Teaching mode: VERBOSE")
        print("[System] Every move will be explained.")
        print("\n[Tutorial] Shogi basics:")
        print("  - 9x9 board")
        print("  - Pieces capture and promote")
        print("  - Captured pieces can be dropped back")
        print("  - Objective: Checkmate the opponent's king")
        print("\n[Controls] Click pieces to move. Teaching commentary will appear.")
        print("\n[Teaching] Ready to explain every move!")
        
        # Initialize and run game
        if not system.game_engine.window:
            if not system.game_engine.initialize():
                print("[Error] Failed to initialize game engine")
                sys.exit(1)
        
        print("\n[System] Game window is open. Click pieces to play!")
        print("[System] Teaching mode will explain each move.")
        print("\n[Note] Shogi visual rendering may be basic - teaching mode active.")
        
        # Run main game loop (this keeps window open)
        system.game_engine.run_main_loop()
        
    else:
        print("[Error] Could not load shogi. Check games/rules/ directory.")
        print("[Info] Shogi rules file should be at: games/rules/shogi.txt")
        
except KeyboardInterrupt:
    print("\n[System] Game interrupted by user.")
except Exception as e:
    print(f"[Error] Failed to start shogi: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback: Start basic game engine and show tutorial
    print("\n[Fallback] Starting basic game engine...")
    if system.game_engine.initialize():
        print("[System] Game engine ready. Teaching mode active.")
        print("[System] Shogi support may be limited without rules file.")
        try:
            system.game_engine.run_main_loop()
        except KeyboardInterrupt:
            print("\n[System] Game interrupted by user.")

print("\n[System] Shogi teaching session ended.")

