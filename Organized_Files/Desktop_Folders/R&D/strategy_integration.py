# -*- coding: utf-8 -*-
# STRATEGY INTEGRATION - Apply strategy core to games/MMORPGs/trading

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class StrategyApplicator:
    """Apply chess strategy core to other domains."""
    
    def __init__(self, strategy_core_path: str = "strategy_core.json"):
        """Initialize applicator."""
        self.core_path = Path(strategy_core_path)
        self.core_data = {}
        
        if self.core_path.exists():
            with open(self.core_path, 'r', encoding='utf-8') as f:
                self.core_data = json.load(f)
    
    def apply_to_war_game(self, game_state: Dict) -> Dict[str, Any]:
        """Apply strategy core to war game."""
        mapping = self.core_data.get('mappings', {}).get('chess_to_war', {})
        
        # Convert chess concepts to war game
        strategy = {
            'center_control': game_state.get('territory_control', 0.5),
            'tempo': game_state.get('initiative', 0.5),
            'material': game_state.get('resource_advantage', 0.0),
            'flanking_vectors': self._get_flanking_vectors(),
            'aggression_index': self._calculate_aggression(game_state)
        }
        
        return strategy
    
    def apply_to_mmorpg(self, raid_state: Dict) -> Dict[str, Any]:
        """Apply strategy core to MMORPG raid."""
        mapping = self.core_data.get('mappings', {}).get('chess_to_mmorpg', {})
        
        # Healer uses bishop pair logic
        healer_strategy = {
            'coverage': 'multiple_fronts',  # Bishop pair covers diagonals
            'positioning': 'flank_support',
            'threat_prioritization': 'fork_logic'  # Fork two mobs
        }
        
        # Rogue uses fork patterns
        rogue_strategy = {
            'target_selection': 'fork_two_mobs',
            'positioning': 'knight_pattern',
            'coordination': 'unit_coordination'
        }
        
        return {
            'healer': healer_strategy,
            'rogue': rogue_strategy,
            'tank': {'positioning': 'pawn_chain', 'aggro': 'tempo_control'}
        }
    
    def apply_to_trading(self, market_state: Dict) -> Dict[str, Any]:
        """Apply strategy core to trading algorithm."""
        mapping = self.core_data.get('mappings', {}).get('chess_to_trading', {})
        
        # Trading strategy from chess
        strategy = {
            'position_size': self._map_material(market_state),
            'entry_timing': self._map_tempo(market_state),
            'risk_management': self._map_endgame_pressure(market_state),
            'momentum': self._map_aggression_index(market_state)
        }
        
        return strategy
    
    def _get_flanking_vectors(self) -> List[Dict[str, float]]:
        """Get flanking vectors from openings."""
        openings = self.core_data.get('openings', [])
        return [op.get('flank_vector', [0.0, 0.0]) for op in openings]
    
    def _calculate_aggression(self, state: Dict) -> float:
        """Calculate aggression index from position."""
        vectors = self.core_data.get('vectors', {})
        tempo_vector = vectors.get('tempo_advantage', {})
        return tempo_vector.get('aggression_index', 0.5)
    
    def _map_material(self, state: Dict) -> float:
        """Map material advantage to position size."""
        vectors = self.core_data.get('vectors', {})
        material_vector = vectors.get('material_advantage', {})
        imbalance = material_vector.get('material_imbalance', 0.0)
        # Convert to position size multiplier
        return max(0.5, min(2.0, 1.0 + imbalance * 0.1))
    
    def _map_tempo(self, state: Dict) -> str:
        """Map tempo to entry timing."""
        vectors = self.core_data.get('vectors', {})
        tempo_vector = vectors.get('tempo_advantage', {})
        aggression = tempo_vector.get('aggression_index', 0.5)
        
        if aggression > 0.7:
            return 'aggressive_entry'
        elif aggression < 0.3:
            return 'defensive_entry'
        else:
            return 'balanced_entry'
    
    def _map_endgame_pressure(self, state: Dict) -> float:
        """Map endgame pressure to risk management."""
        vectors = self.core_data.get('vectors', {})
        endgame_vector = vectors.get('endgame_pressure', {})
        return endgame_vector.get('endgame_pressure', 0.5)
    
    def _map_aggression_index(self, state: Dict) -> float:
        """Map aggression index to momentum."""
        vectors = self.core_data.get('vectors', {})
        tempo_vector = vectors.get('tempo_advantage', {})
        return tempo_vector.get('aggression_index', 0.5)


# Example usage
if __name__ == '__main__':
    applicator = StrategyApplicator()
    
    # War game example
    war_state = {
        'territory_control': 0.7,
        'initiative': 0.6,
        'resource_advantage': 1.3
    }
    war_strategy = applicator.apply_to_war_game(war_state)
    print("[War Game] Strategy:", json.dumps(war_strategy, indent=2))
    
    # MMORPG example
    raid_state = {'party_size': 5}
    mmorpg_strategy = applicator.apply_to_mmorpg(raid_state)
    print("\n[MMORPG] Strategy:", json.dumps(mmorpg_strategy, indent=2))
    
    # Trading example
    market_state = {'volatility': 0.5}
    trading_strategy = applicator.apply_to_trading(market_state)
    print("\n[Trading] Strategy:", json.dumps(trading_strategy, indent=2))

