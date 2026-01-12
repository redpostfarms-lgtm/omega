# -*- coding: utf-8 -*-
# Test Elara enhanced systems

from elara_voice_command import VoiceCommandHandler
from elara_mode_switcher import ModeSwitcher, GameMode
from elara_teaching_mode import TeachingMode, TeachingLevel
from elara_dynamic_game_loader import DynamicGameLoader

print("=" * 60)
print("ELARA SYSTEMS TEST")
print("=" * 60)

# Test 1: Voice Command
print("\n[Test 1] Voice Command Handler")
handler = VoiceCommandHandler()
commands = [
    "let's play chess",
    "let's play checkers",
    "let's play shogi"
]

for cmd in commands:
    game_type, game_name, opts = handler.parse_command(cmd)
    response = handler.respond_to_command(game_type, game_name)
    print(f"  Command: {cmd}")
    print(f"  Response: {response}")

# Test 2: Mode Switcher
print("\n[Test 2] Mode Switcher")
switcher = ModeSwitcher()
print(f"  Initial: {switcher.get_mode_description()}")

switcher.switch_mode(GameMode.DUEL)
print(f"  After switch: {switcher.get_mode_description()}")

switcher.ai_step_back()
print(f"  AI stepped back: observing={switcher.observing_game}")

switcher.ai_take_turn()
print(f"  AI returned: can_move={switcher.can_ai_move()}")

# Test 3: Teaching Mode
print("\n[Test 3] Teaching Mode")
teacher = TeachingMode(TeachingLevel.NORMAL)
teacher.record_move("e4", "white")
teacher.record_move("e5", "black")
teacher.record_move("Nf3", "white")

comment = teacher.generate_comment()
if comment:
    print(f"  Comment: {comment.comment}")
    print(f"  Explanation: {comment.explanation}")

explanation = teacher.handle_user_response("why")
if explanation:
    print(f"  User asks 'why': {explanation}")

# Test 4: Dynamic Loader
print("\n[Test 4] Dynamic Game Loader")
loader = DynamicGameLoader()
config = loader.load_game("shogi")
print(f"  Game: {config['name']}")
print(f"  Board: {config['board_size']}")
print(f"  Pieces: {[p['name'] for p in config['pieces']]}")

print("\n[OK] All systems operational")

