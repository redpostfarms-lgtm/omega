# -*- coding: utf-8 -*-
# ELARA VOICE COMMAND HANDLER
# "let's play [game]" → instant board setup, smooth response

import re
import time
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from elara_game_engine import GameType


class VoiceCommandHandler:
    """
    Voice command handler for game start.
    
    Handles: "let's play chess" → board up, ready, your color?
    """
    
    def __init__(self):
        """Initialize voice command handler."""
        self.game_keywords = {
            'chess': GameType.CHESS,
            'checkers': GameType.CHECKERS,
            'go': GameType.GO,
            'mahjong': GameType.MAHJONG,
            'shogi': 'shogi',  # Dynamic game
            'hex': 'hex',
            'oware': 'oware',
        }
        
        # Difficulty keywords
        self.difficulty_keywords = {
            'beginner': 'beginner',
            'intermediate': 'intermediate',
            'expert': 'expert',
            'master': 'master'
        }
    
    def parse_command(self, command: str) -> Tuple[Optional[GameType], Optional[str], Dict[str, Any]]:
        """
        Parse voice command.
        
        Args:
            command: Voice command text
            
        Returns:
            (game_type, game_name, options)
        """
        command_lower = command.lower()
        
        # Match "let's play [game]"
        match = re.search(r"let'?s\s+play\s+(\w+)", command_lower)
        if not match:
            return None, None, {}
        
        game_name = match.group(1)
        
        # Check if known game
        if game_name in self.game_keywords:
            game_type = self.game_keywords[game_name]
            
            if isinstance(game_type, GameType):
                return game_type, game_name, {}
            else:
                # Dynamic game (shogi, hex, oware)
                return None, game_name, {'dynamic': True}
        
        return None, None, {}
    
    def parse_difficulty_command(self, command: str) -> Optional[str]:
        """
        Parse difficulty command.
        
        Args:
            command: Voice command (e.g., "expert on", "teach me")
            
        Returns:
            Difficulty level or special command
        """
        command_lower = command.lower()
        
        # "expert on" → switch to expert
        for level in self.difficulty_keywords.keys():
            if f"{level} on" in command_lower:
                return level
        
        # "teach me" → enable teach mode
        if "teach me" in command_lower:
            return "teach_mode"
        
        return None
    
    def respond_to_command(self, game_type: Optional[GameType], game_name: str) -> str:
        """
        Generate response to command.
        
        Returns:
            Response text
        """
        if game_type == GameType.CHESS:
            return "Board up. Ready. Your color? (queen's pawn, e2e4 tutorial)"
        elif game_type == GameType.CHECKERS:
            return "Board up. Ready. King me, red first, double-jump drill."
        elif game_type == GameType.GO:
            return "Board up. Ready. 19×19, komi 6.5, first move center."
        elif game_type == GameType.MAHJONG:
            return "Board up. Ready. Tile shuffle, dragon set, match three."
        elif game_name == 'shogi':
            return "Board up. Ready. Shogi rules loaded. Your color?"
        else:
            return f"Board up. Ready. {game_name.capitalize()} rules loaded. Let's play."


if __name__ == '__main__':
    handler = VoiceCommandHandler()
    
    # Test commands
    commands = [
        "let's play chess",
        "let's play checkers",
        "let's play go",
        "let's play mahjong",
        "let's play shogi"
    ]
    
    for cmd in commands:
        game_type, game_name, options = handler.parse_command(cmd)
        response = handler.respond_to_command(game_type, game_name)
        print(f"Command: {cmd}")
        print(f"Response: {response}\n")

