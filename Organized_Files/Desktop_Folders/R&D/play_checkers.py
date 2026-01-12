# -*- coding: utf-8 -*-
# PLAY CHECKERS - Beginner Level
# Game Framework

from elara_integrated_system import ElaraIntegratedSystem
from elara_game_engine import GameType
from elara_difficulty_system import DifficultyLevel

print("=" * 60)
print("ELARA GAME FRAMEWORK - Checkers (Beginner)")
print("=" * 60)

# Initialize system
system = ElaraIntegratedSystem()

# Set user
system.current_user = "player"

# Set difficulty to beginner
system.difficulty.set_user_level(system.current_user, DifficultyLevel.BEGINNER)
print(f"\n[Difficulty] {system.difficulty.get_user_summary(system.current_user)}")

# Load checkers game
print("\n[System] Loading checkers...")
system.handle_voice_command("let's play checkers")

# Start game
print("\n" + "=" * 60)
print("GAME READY")
print("=" * 60)
print("\n[System] Board up. Ready. King me, red first, double-jump drill.")
print("[System] Beginner mode: I play like a 10-year-old on Red Bull.")
print("[System] Opens wide, leaves pieces, forgets jumps sometimes.")
print("\n[Controls]")
print("  - Click pieces to select")
print("  - Click destination to move")
print("  - Say 'expert on' to switch difficulty mid-game")
print("  - Say 'teach me' for teaching mode")
print("\n[Game] Let's play!")

# Display initial board
from checkers_display import display_checkers_board

# Get board from game engine
if hasattr(system, 'game_engine') and system.game_engine.current_game == GameType.CHECKERS:
    if hasattr(system.game_engine, 'checkers_module') and system.game_engine.checkers_module:
        print("\n[Initial Board:]")
        display_checkers_board(system.game_engine.checkers_module.board)
    else:
        # Demo board if module not available
        demo_board = [[0 for _ in range(8)] for _ in range(8)]
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    demo_board[row][col] = 2
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    demo_board[row][col] = 1
        print("\n[Initial Board:]")
        display_checkers_board(demo_board)
else:
    # Demo board
    demo_board = [[0 for _ in range(8)] for _ in range(8)]
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 == 1:
                demo_board[row][col] = 2
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 == 1:
                demo_board[row][col] = 1
    print("\n[Initial Board:]")
    display_checkers_board(demo_board)

# Simulate a few moves to show the system working
print("\n[Example Game - Your Moves:]")
print("Your turn (Red) - Click a piece to select, then click destination")

# Show AI move capability
print("\n[Demo: AI Move (Black - Beginner)]")
if hasattr(system, 'game_engine') and hasattr(system.game_engine, 'checkers_module'):
    if system.game_engine.checkers_module:
        ai_move = system.game_engine.checkers_module.get_ai_move()
        if ai_move:
            from_sq, to_sq = ai_move
            print(f"[AI] Move: {from_sq} -> {to_sq}")
            print("[AI] 'Almost had it!' - Beginner smack talk")
            print("[AI] Playing like a 10-year-old on Red Bull...")
            print("[AI] Sometimes misses jumps, leaves pieces open.")
            
            # Show updated board
            system.game_engine.checkers_module._make_move(from_sq, to_sq)
            print("\n[Board After AI Move:]")
            display_checkers_board(system.game_engine.checkers_module.board)
else:
    print("[AI] 'Almost had it!' - Beginner smack talk")
    print("[AI] Playing like a 10-year-old on Red Bull...")
    print("[AI] Sometimes misses jumps, leaves pieces open.")

print("\n[Your turn (Red)] Make your move!")

print("\n[System] Game in progress. Every move is a data point.")
print("[System] Learning your patterns. Adapting. Never peaks.")

print("\n[OK] Checkers game ready. Beginner level. Enjoy!")

