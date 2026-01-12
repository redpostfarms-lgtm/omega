# -*- coding: utf-8 -*-
# ELARA STATE MANAGER
# Save/load game states, undo/redo, state compression

import json
import pickle
import gzip
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GameState:
    """Game state for save/load."""
    board: Dict
    move_history: List[str]
    current_turn: str
    game_type: str
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class StateManager:
    """
    State management system.
    
    Features:
    - Save/load game states
    - Undo/redo functionality
    - State compression
    - Auto-save
    """
    
    def __init__(self, save_dir: str = "./.elara/saves"):
        """Initialize state manager."""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Undo/redo stacks
        self.undo_stack: List[GameState] = []
        self.redo_stack: List[GameState] = []
        self.max_stack_size = 100
        
        # Auto-save
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes
    
    def save_state(self, state: GameState, filename: Optional[str] = None) -> str:
        """
        Save game state.
        
        Args:
            state: Game state to save
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.json.gz"
        
        filepath = self.save_dir / filename
        
        # Compress state
        state_dict = asdict(state)
        json_str = json.dumps(state_dict, indent=2)
        compressed = gzip.compress(json_str.encode('utf-8'))
        
        with open(filepath, 'wb') as f:
            f.write(compressed)
        
        return str(filepath)
    
    def load_state(self, filename: str) -> Optional[GameState]:
        """
        Load game state.
        
        Args:
            filename: Filename to load
            
        Returns:
            GameState or None if not found
        """
        filepath = self.save_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'rb') as f:
                compressed = f.read()
            
            # Decompress
            json_str = gzip.decompress(compressed).decode('utf-8')
            state_dict = json.loads(json_str)
            
            return GameState(**state_dict)
        except Exception as e:
            print(f"[StateManager] Error loading state: {e}")
            return None
    
    def push_state(self, state: GameState):
        """Push state to undo stack."""
        self.undo_stack.append(state)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new move made
        self.redo_stack.clear()
    
    def undo(self) -> Optional[GameState]:
        """Undo last move."""
        if not self.undo_stack:
            return None
        
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        
        if self.undo_stack:
            return self.undo_stack[-1]
        return None
    
    def redo(self) -> Optional[GameState]:
        """Redo last undone move."""
        if not self.redo_stack:
            return None
        
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        return state
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 1
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0


if __name__ == '__main__':
    manager = StateManager()
    
    # Test save/load
    state = GameState(
        board={},
        move_history=['e4', 'e5'],
        current_turn='white',
        game_type='chess',
        timestamp=time.time()
    )
    
    filepath = manager.save_state(state)
    print(f"Saved to: {filepath}")
    
    loaded = manager.load_state(Path(filepath).name)
    print(f"Loaded: {loaded is not None}")
    
    # Test undo/redo
    manager.push_state(state)
    state2 = GameState(board={}, move_history=['e4'], current_turn='black', 
                      game_type='chess', timestamp=time.time())
    manager.push_state(state2)
    
    print(f"Can undo: {manager.can_undo()}")
    undone = manager.undo()
    print(f"Undone: {undone is not None}")
    print(f"Can redo: {manager.can_redo()}")

