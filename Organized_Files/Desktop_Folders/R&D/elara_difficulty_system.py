# -*- coding: utf-8 -*-
# ELARA DIFFICULTY SYSTEM
# Four levels: Beginner, Intermediate, Expert, Master
# Locked in. Adaptive. Switch mid-game.

import json
import random
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime


class DifficultyLevel(Enum):
    """Difficulty levels - locked in, adaptive."""
    BEGINNER = "beginner"      # 10-year-old on Red Bull
    INTERMEDIATE = "intermediate"  # Solid, center control
    EXPERT = "expert"          # 2200 ELO, endgame master
    MASTER = "master"          # 2800+, sees 6 moves ahead


@dataclass
class PlayerProfile:
    """Player profile with difficulty tracking."""
    user_id: str
    current_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    average_move_time: float = 0.0
    improvement_trend: float = 0.0  # Positive = climbing
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class DifficultySystem:
    """
    Four-level difficulty system.
    
    Levels:
    - Beginner: 10-year-old on Red Bull, opens wide, leaves queens
    - Intermediate: Solid, center control, punishes first slip
    - Expert: 2200 ELO, no mercy, castles fast, sacs pretty
    - Master: 2800+, sees 6 moves ahead, you're studying
    """
    
    def __init__(self, profiles_file: str = "./.elara/player_profiles.json"):
        """Initialize difficulty system."""
        self.profiles_file = Path(profiles_file)
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.profiles: Dict[str, PlayerProfile] = {}
        self.current_user_id = "default"
        self.current_level = DifficultyLevel.INTERMEDIATE
        self.teach_mode_active = False  # "teach me" drops one tier
        self.level_switched_mid_game = False
        
        # Load profiles
        self.load_profiles()
    
    def get_user_level(self, user_id: str = None) -> DifficultyLevel:
        """Get user's current difficulty level."""
        if user_id is None:
            user_id = self.current_user_id
        
        if user_id in self.profiles:
            return self.profiles[user_id].current_level
        return DifficultyLevel.INTERMEDIATE  # Default
    
    def set_user_level(self, user_id: str, level: DifficultyLevel):
        """Set user's difficulty level (sticky per user)."""
        if user_id not in self.profiles:
            self.profiles[user_id] = PlayerProfile(user_id=user_id)
        
        self.profiles[user_id].current_level = level
        self.current_user_id = user_id
        self.current_level = level
        self.save_profiles()
        print(f"[Difficulty] {user_id}: Set to {level.value}")
    
    def switch_level_mid_game(self, new_level: DifficultyLevel):
        """Switch difficulty mid-game - boom, tightens."""
        old_level = self.current_level
        self.current_level = new_level
        self.level_switched_mid_game = True
        
        level_descriptions = {
            DifficultyLevel.BEGINNER: "plays like a 10-year-old on Red Bull",
            DifficultyLevel.INTERMEDIATE: "solid, center control",
            DifficultyLevel.EXPERT: "2200 ELO, no mercy",
            DifficultyLevel.MASTER: "2800+, sees 6 moves ahead"
        }
        
        print(f"[Difficulty] Switched mid-game: {old_level.value} -> {new_level.value}")
        print(f"[Difficulty] {level_descriptions[new_level]}. Tightened.")
    
    def enable_teach_mode(self):
        """Enable teach mode - drops one tier, explains everything."""
        if not self.teach_mode_active:
            # Drop one tier
            level_order = [
                DifficultyLevel.BEGINNER,
                DifficultyLevel.INTERMEDIATE,
                DifficultyLevel.EXPERT,
                DifficultyLevel.MASTER
            ]
            
            current_idx = level_order.index(self.current_level)
            if current_idx > 0:
                self.teach_mode_level = level_order[current_idx - 1]
                self.teach_mode_active = True
                print(f"[Difficulty] Teach mode: Dropped to {self.teach_mode_level.value}")
                print(f"[Difficulty] Explains every breath. One tier lower.")
                return True
        
        return False
    
    def disable_teach_mode(self):
        """Disable teach mode - returns to original level."""
        if self.teach_mode_active:
            self.teach_mode_active = False
            print(f"[Difficulty] Teach mode off. Back to {self.current_level.value}")
            return True
        return False
    
    def get_active_level(self) -> DifficultyLevel:
        """Get active difficulty level (teach mode may lower it)."""
        if self.teach_mode_active:
            return getattr(self, 'teach_mode_level', self.current_level)
        return self.current_level
    
    def get_move_strategy(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get move strategy based on current difficulty level.
        
        Returns:
            Strategy dict with move selection, depth, evaluation
        """
        active_level = self.get_active_level()
        
        strategies = {
            DifficultyLevel.BEGINNER: {
                'name': 'beginner',
                'description': '10-year-old on Red Bull',
                'mistake_probability': 0.3,  # 30% chance of blunder
                'forgets_en_passant': True,
                'leaves_queens': True,
                'opens_wide': True,
                'search_depth': 1,
                'evaluation_depth': 2,
                'planning': False,
                'style': 'chaotic'
            },
            DifficultyLevel.INTERMEDIATE: {
                'name': 'intermediate',
                'description': 'Solid, center control, pins',
                'mistake_probability': 0.1,  # 10% chance of mistake
                'punishes_first_slip': True,
                'uses_tactics': True,
                'center_control': True,
                'search_depth': 3,
                'evaluation_depth': 4,
                'planning': True,
                'style': 'positional'
            },
            DifficultyLevel.EXPERT: {
                'name': 'expert',
                'description': '2200 ELO, no mercy',
                'mistake_probability': 0.02,  # 2% chance
                'endgame_master': True,
                'castles_fast': True,
                'sacs_pretty': True,
                'clocks_every_second': True,
                'search_depth': 5,
                'evaluation_depth': 6,
                'planning': True,
                'style': 'aggressive'
            },
            DifficultyLevel.MASTER: {
                'name': 'master',
                'description': '2800+, sees 6 moves ahead',
                'mistake_probability': 0.001,  # 0.1% chance
                'sees_6_moves_ahead': True,
                'knows_openings': True,  # e4 → Ruy Lopez to Zaitsev
                'endgame_tablebase': True,
                'search_depth': 8,
                'evaluation_depth': 10,
                'planning': True,
                'style': 'perfect'
            }
        }
        
        return strategies.get(active_level, strategies[DifficultyLevel.INTERMEDIATE])
    
    def select_move(self, legal_moves: List[str], position: Dict[str, Any]) -> str:
        """
        Select move based on difficulty level.
        
        Args:
            legal_moves: List of legal moves
            position: Current position
            
        Returns:
            Selected move
        """
        strategy = self.get_move_strategy(position)
        active_level = self.get_active_level()
        
        if active_level == DifficultyLevel.BEGINNER:
            return self._beginner_move(legal_moves, strategy)
        elif active_level == DifficultyLevel.INTERMEDIATE:
            return self._intermediate_move(legal_moves, position, strategy)
        elif active_level == DifficultyLevel.EXPERT:
            return self._expert_move(legal_moves, position, strategy)
        else:  # MASTER
            return self._master_move(legal_moves, position, strategy)
    
    def _beginner_move(self, legal_moves: List[str], strategy: Dict[str, Any]) -> str:
        """Beginner: 10-year-old on Red Bull."""
        # Random mistakes
        if random.random() < strategy['mistake_probability']:
            # Blunder - random move
            return random.choice(legal_moves)
        
        # Opens wide (king's pawn, queen's pawn)
        opening_moves = ['e4', 'e3', 'd4', 'd3']
        opening_moves = [m for m in opening_moves if m in legal_moves]
        if opening_moves:
            return random.choice(opening_moves)
        
        # Random move
        return random.choice(legal_moves)
    
    def _intermediate_move(self, legal_moves: List[str], position: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """Intermediate: Solid, center control, punishes slips."""
        # Prefer center moves
        center_moves = [m for m in legal_moves if any(sq in m for sq in ['d4', 'd5', 'e4', 'e5'])]
        if center_moves:
            return random.choice(center_moves)
        
        # Develop pieces
        development_moves = [m for m in legal_moves if any(piece in m for piece in ['N', 'B'])]
        if development_moves:
            return random.choice(development_moves)
        
        return random.choice(legal_moves)
    
    def _expert_move(self, legal_moves: List[str], position: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """Expert: 2200 ELO, no mercy, castles fast, sacs pretty."""
        # Prefer fast development
        castling_moves = [m for m in legal_moves if m in ['O-O', 'O-O-O', 'e1g1', 'e1c1']]
        if castling_moves:
            return castling_moves[0]
        
        # Tactical moves (captures, checks)
        tactical_moves = [m for m in legal_moves if 'x' in m or '+' in m]
        if tactical_moves:
            return tactical_moves[0]
        
        # Aggressive center control
        center_moves = [m for m in legal_moves if any(sq in m for sq in ['d4', 'd5', 'e4', 'e5'])]
        if center_moves:
            return center_moves[0]
        
        return legal_moves[0] if legal_moves else ""
    
    def _master_move(self, legal_moves: List[str], position: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """Master: 2800+, sees 6 moves ahead, knows openings."""
        # Opening book (e4 → Ruy Lopez)
        if len(position.get('move_history', [])) < 5:
            opening = self._get_opening_move(position, legal_moves)
            if opening:
                return opening
        
        # Deep search (simplified - would use actual engine)
        # For now, prefer best evaluated moves
        best_moves = self._evaluate_moves(legal_moves, position, depth=6)
        if best_moves:
            return best_moves[0]
        
        return legal_moves[0] if legal_moves else ""
    
    def _get_opening_move(self, position: Dict[str, Any], legal_moves: List[str]) -> Optional[str]:
        """Get opening book move (e4 → Ruy Lopez to Zaitsev)."""
        move_history = position.get('move_history', [])
        
        if not move_history:
            # First move: e4
            if 'e4' in legal_moves:
                return 'e4'
        elif len(move_history) == 1 and move_history[0] == 'e4':
            # Ruy Lopez setup
            if 'Nf3' in legal_moves:
                return 'Nf3'
        elif len(move_history) == 2:
            # Continue development
            if 'Bb5' in legal_moves:  # Ruy Lopez
                return 'Bb5'
        
        return None
    
    def _evaluate_moves(self, legal_moves: List[str], position: Dict[str, Any], depth: int) -> List[str]:
        """Evaluate moves (simplified - would use actual engine)."""
        # Simplified evaluation - would use minimax/alpha-beta
        # For now, prefer moves that control center
        center_squares = ['d4', 'd5', 'e4', 'e5']
        scored_moves = []
        
        for move in legal_moves:
            score = 0
            # Center control bonus
            if any(sq in move for sq in center_squares):
                score += 10
            # Capture bonus
            if 'x' in move:
                score += 5
            # Check bonus
            if '+' in move:
                score += 15
            
            scored_moves.append((score, move))
        
        # Sort by score
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in scored_moves]
    
    def track_game_result(self, user_id: str, won: bool, moves: int, move_time: float):
        """Track game result to detect improvement."""
        if user_id not in self.profiles:
            self.profiles[user_id] = PlayerProfile(user_id=user_id)
        
        profile = self.profiles[user_id]
        profile.games_played += 1
        
        if won:
            profile.wins += 1
        else:
            profile.losses += 1
        
        # Update average move time
        profile.average_move_time = (
            profile.average_move_time * 0.9 + move_time * 0.1
        )
        
        # Detect improvement (simplified)
        win_rate = profile.wins / profile.games_played if profile.games_played > 0 else 0.5
        
        # If winning > 60% at current level, mark as climbing
        if win_rate > 0.6 and profile.games_played >= 5:
            profile.improvement_trend = 1.0
            print(f"[Difficulty] {user_id}: Climbing. Win rate: {win_rate:.1%}")
        
        self.save_profiles()
    
    def should_level_up(self, user_id: str) -> bool:
        """Check if user should level up (climbing)."""
        if user_id not in self.profiles:
            return False
        
        profile = self.profiles[user_id]
        
        # If winning consistently and playing well
        if profile.improvement_trend > 0.7:
            win_rate = profile.wins / profile.games_played if profile.games_played > 0 else 0
            if win_rate > 0.65 and profile.games_played >= 10:
                return True
        
        return False
    
    def load_profiles(self):
        """Load player profiles from file."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        level = DifficultyLevel(profile_data['current_level'])
                        self.profiles[user_id] = PlayerProfile(
                            user_id=user_id,
                            current_level=level,
                            games_played=profile_data.get('games_played', 0),
                            wins=profile_data.get('wins', 0),
                            losses=profile_data.get('losses', 0),
                            average_move_time=profile_data.get('average_move_time', 0.0),
                            improvement_trend=profile_data.get('improvement_trend', 0.0),
                            last_updated=profile_data.get('last_updated', '')
                        )
            except Exception as e:
                print(f"[Difficulty] Error loading profiles: {e}")
    
    def save_profiles(self):
        """Save player profiles to file."""
        data = {}
        for user_id, profile in self.profiles.items():
            data[user_id] = asdict(profile)
            data[user_id]['current_level'] = profile.current_level.value
        
        with open(self.profiles_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_user_summary(self, user_id: str = None) -> str:
        """Get user difficulty summary."""
        if user_id is None:
            user_id = self.current_user_id
        
        if user_id in self.profiles:
            profile = self.profiles[user_id]
            level = profile.current_level.value
            climbing = "Climbing." if profile.improvement_trend > 0.7 else ""
            return f"{user_id}: {level.title()}. {climbing}"
        
        return f"{user_id}: Intermediate. (default)"


if __name__ == '__main__':
    system = DifficultySystem()
    
    # Test levels
    user_id = "test_user"
    system.set_user_level(user_id, DifficultyLevel.INTERMEDIATE)
    print(f"\n{system.get_user_summary(user_id)}")
    
    # Test mid-game switch
    system.switch_level_mid_game(DifficultyLevel.EXPERT)
    
    # Test teach mode
    system.enable_teach_mode()
    strategy = system.get_move_strategy({})
    print(f"\nTeach mode strategy: {strategy['name']}")
    
    # Test move selection
    legal_moves = ['e4', 'e3', 'd4', 'Nf3']
    move = system.select_move(legal_moves, {'move_history': []})
    print(f"\nSelected move: {move}")
    
    print("\n[OK] Difficulty system ready")

