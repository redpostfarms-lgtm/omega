# -*- coding: utf-8 -*-
# ELARA MODE SWITCHER
# Solo, Duel, Co-op - switch mid-game, no reset

from enum import Enum
from typing import Optional, Dict, Any, List, Callable


class GameMode(Enum):
    """Game modes."""
    SOLO = "solo"  # User vs AI
    DUEL = "duel"  # 2 humans, hot-seat
    COOP = "coop"  # User + AI vs friend


class ModeSwitcher:
    """
    Mode switcher - switch between Solo, Duel, Co-op mid-game.
    
    Features:
    - Switch on the fly, mid-game
    - No reset, pieces wait
    - Clock pauses
    - AI steps back, watches, learns
    - "Elara, take my turn" to bring AI back
    """
    
    def __init__(self):
        """Initialize mode switcher."""
        self.current_mode = GameMode.SOLO
        self.previous_mode: Optional[GameMode] = None
        self.ai_active = True
        self.clock_paused = False
        self.observing_game = False  # AI watching/learning
    
    def switch_mode(self, new_mode: GameMode) -> bool:
        """
        Switch game mode mid-game.
        
        Args:
            new_mode: Mode to switch to
            
        Returns:
            True if switch successful
        """
        if new_mode == self.current_mode:
            return False
        
        self.previous_mode = self.current_mode
        self.current_mode = new_mode
        
        # Handle mode transition
        if new_mode == GameMode.SOLO:
            # Solo: AI active
            self.ai_active = True
            self.observing_game = False
            print("[Mode] Switched to Solo: You vs. me.")
        
        elif new_mode == GameMode.DUEL:
            # Duel: No AI, hot-seat
            self.ai_active = False
            self.observing_game = False
            self.clock_paused = True
            print("[Mode] Switched to Duel: Two humans, board hot-seats—no AI.")
        
        elif new_mode == GameMode.COOP:
            # Co-op: User + AI vs friend
            self.ai_active = True
            self.observing_game = False
            print("[Mode] Switched to Co-op: You + me vs. friend. AI plays your side, silent unless asked.")
        
        return True
    
    def pause_game(self):
        """Pause game (pieces wait, clock pauses)."""
        self.clock_paused = True
        print("[Mode] Game paused. Pieces wait. Clock pauses.")
    
    def resume_game(self):
        """Resume game."""
        self.clock_paused = False
        print("[Mode] Game resumed.")
    
    def ai_step_back(self):
        """AI steps back, watches, learns."""
        if self.ai_active:
            self.ai_active = False
            self.observing_game = True
            print("[Mode] AI stepped back. Watching. Learning. Wants back in? Say 'Elara, take my turn'.")
    
    def ai_take_turn(self) -> bool:
        """
        Bring AI back into game.
        
        Returns:
            True if AI can take turn
        """
        if self.current_mode in [GameMode.SOLO, GameMode.COOP]:
            self.ai_active = True
            self.observing_game = False
            print("[Mode] Elara slides in. No drama. No lag. Just another player. Human or ghost.")
            return True
        return False
    
    def can_ai_move(self) -> bool:
        """Check if AI can make a move."""
        return self.ai_active and not self.clock_paused
    
    def get_mode_description(self) -> str:
        """Get current mode description."""
        descriptions = {
            GameMode.SOLO: "Solo: You vs. me",
            GameMode.DUEL: "Duel: Two humans, hot-seat",
            GameMode.COOP: "Co-op: You + me vs. friend"
        }
        return descriptions.get(self.current_mode, "Unknown mode")


if __name__ == '__main__':
    switcher = ModeSwitcher()
    
    print(f"Current: {switcher.get_mode_description()}")
    
    # Switch to Duel
    switcher.switch_mode(GameMode.DUEL)
    print(f"Switched to: {switcher.get_mode_description()}")
    
    # AI step back
    switcher.ai_step_back()
    
    # AI take turn
    if switcher.ai_take_turn():
        print("AI can move now")

