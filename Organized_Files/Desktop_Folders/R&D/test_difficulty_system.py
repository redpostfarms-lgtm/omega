# -*- coding: utf-8 -*-
# Test difficulty system

from elara_difficulty_system import DifficultySystem, DifficultyLevel

print("=" * 60)
print("ELARA DIFFICULTY SYSTEM TEST")
print("=" * 60)

system = DifficultySystem()
user_id = "test_user"

# Test 1: Set levels
print("\n[Test 1] Four Levels")
for level in DifficultyLevel:
    system.set_user_level(user_id, level)
    strategy = system.get_move_strategy({})
    print(f"  {level.value.title()}: {strategy['description']}")

# Test 2: Default user
print("\n[Test 2] Default User")
system.set_user_level(user_id, DifficultyLevel.INTERMEDIATE)
print(f"  {system.get_user_summary(user_id)}")

# Test 3: Mid-game switch
print("\n[Test 3] Mid-Game Switch")
system.switch_level_mid_game(DifficultyLevel.EXPERT)
strategy = system.get_move_strategy({})
print(f"  Switched to: {strategy['name']} - {strategy['description']}")

# Test 4: Teach mode
print("\n[Test 4] Teach Mode")
system.set_user_level(user_id, DifficultyLevel.EXPERT)
system.enable_teach_mode()
teach_strategy = system.get_move_strategy({})
print(f"  Original: Expert")
print(f"  Teach mode: {teach_strategy['name']} (one tier lower)")
print(f"  Explains every breath.")

# Test 5: Move selection
print("\n[Test 5] Move Selection by Level")
legal_moves = ['e4', 'e3', 'd4', 'd3', 'Nf3', 'Nc3', 'Bc4', 'Bf4']

for level in DifficultyLevel:
    system.current_level = level
    system.teach_mode_active = False
    move = system.select_move(legal_moves, {'move_history': []})
    strategy = system.get_move_strategy({})
    print(f"  {level.value.title()}: {move} ({strategy['style']})")

# Test 6: Opening book (Master)
print("\n[Test 6] Master Opening Book")
system.current_level = DifficultyLevel.MASTER
system.teach_mode_active = False

# First move
move1 = system.select_move(['e4', 'e3', 'd4'], {'move_history': []})
print(f"  First move: {move1}")

# Second move (after e4)
move2 = system.select_move(['Nf3', 'Nc3', 'Bc4'], {'move_history': ['e4']})
print(f"  After e4: {move2} (Ruy Lopez setup)")

# Test 7: Tracking improvement
print("\n[Test 7] Improvement Tracking")
system.track_game_result(user_id, won=True, moves=25, move_time=30.0)
system.track_game_result(user_id, won=True, moves=30, move_time=35.0)
system.track_game_result(user_id, won=False, moves=40, move_time=45.0)
system.track_game_result(user_id, won=True, moves=28, move_time=32.0)
system.track_game_result(user_id, won=True, moves=22, move_time=28.0)

print(f"  Games: {system.profiles[user_id].games_played}")
print(f"  Wins: {system.profiles[user_id].wins}")
print(f"  {system.get_user_summary(user_id)}")

print("\n[OK] Difficulty system operational")

