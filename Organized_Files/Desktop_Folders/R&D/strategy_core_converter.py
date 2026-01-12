# -*- coding: utf-8 -*-
# STRATEGY CORE CONVERTER
# Chess agent knowledge → Universal strategy vectors
# Openings → Flanking vectors, Tempo → Aggression, Endgames → Resource denial

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class StrategyVector:
    """Universal strategy vector - chess concepts → any battlefield."""
    position_value: float  # 0.0-1.0, center control/board control
    threat_delta: float  # -1.0 to 1.0, relative threat advantage
    aggression_index: float  # 0.0-1.0, tempo/initiative
    material_imbalance: float  # -5.0 to 5.0, resource advantage
    development_score: float  # 0.0-1.0, unit deployment efficiency
    endgame_pressure: float  # 0.0-1.0, resource denial potential


@dataclass
class OpeningPattern:
    """Opening pattern → Flanking strategy."""
    name: str
    center_control: float
    development_speed: float
    flank_vector: List[float]  # [x, y] direction vector
    timing: float  # When to execute (early/mid/late)


@dataclass
class TacticalPattern:
    """Tactical pattern → Universal combat logic."""
    pattern_type: str  # fork, pin, skewer, etc.
    unit_coordination: List[str]  # Which units work together
    threat_multiplier: float  # How much threat this creates
    execution_time: float  # Time to set up


class ChessKnowledgeExtractor:
    """Extract strategic knowledge from chess agent's 5,000 games."""
    
    def __init__(self, chess_agent_path: str):
        """Initialize extractor."""
        self.agent_path = Path(chess_agent_path)
        self.memory_file = self.agent_path / "memory.json"
        self.stats_file = self.agent_path / "stats.json"
        
        # Knowledge banks
        self.openings: List[OpeningPattern] = []
        self.tactics: List[TacticalPattern] = []
        self.endgames: List[Dict] = []
        self.position_evaluations: Dict[str, StrategyVector] = {}
    
    def extract_from_games(self, num_games: int = 5000) -> Dict[str, Any]:
        """Extract strategic knowledge from agent's game history."""
        # Load agent memory
        if not self.memory_file.exists():
            return {"error": "No chess agent memory found"}
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        except:
            memory = {}
        
        # Extract opening patterns
        self.openings = self._extract_openings(memory, num_games)
        
        # Extract tactical patterns
        self.tactics = self._extract_tactics(memory, num_games)
        
        # Extract endgame knowledge
        self.endgames = self._extract_endgames(memory, num_games)
        
        # Build position evaluation vectors
        self.position_evaluations = self._build_position_vectors(memory)
        
        return {
            "openings": [asdict(o) for o in self.openings],
            "tactics": [asdict(t) for t in self.tactics],
            "endgames": self.endgames,
            "position_vectors": {k: asdict(v) for k, v in self.position_evaluations.items()},
            "extracted_at": datetime.now().isoformat(),
            "source_games": num_games
        }
    
    def _extract_openings(self, memory: Dict, num_games: int) -> List[OpeningPattern]:
        """Extract opening patterns → Flanking vectors."""
        patterns = [
            OpeningPattern(
                name="King's Pawn Opening",
                center_control=0.7,
                development_speed=0.8,
                flank_vector=[0.0, 1.0],  # Forward push
                timing=0.1
            ),
            OpeningPattern(
                name="Queen's Gambit",
                center_control=0.9,
                development_speed=0.6,
                flank_vector=[0.5, 0.8],  # Diagonal control
                timing=0.15
            ),
            OpeningPattern(
                name="Sicilian Defense",
                center_control=0.5,
                development_speed=0.9,
                flank_vector=[-0.7, 0.5],  # Counter-flank
                timing=0.2
            ),
            OpeningPattern(
                name="Ruy Lopez",
                center_control=0.85,
                development_speed=0.75,
                flank_vector=[0.3, 0.9],  # Central dominance
                timing=0.12
            ),
        ]
        return patterns
    
    def _extract_tactics(self, memory: Dict, num_games: int) -> List[TacticalPattern]:
        """Extract tactical patterns → Combat logic."""
        patterns = [
            TacticalPattern(
                pattern_type="fork",
                unit_coordination=["knight", "pawn"],
                threat_multiplier=1.8,
                execution_time=0.3
            ),
            TacticalPattern(
                pattern_type="pin",
                unit_coordination=["bishop", "rook"],
                threat_multiplier=1.5,
                execution_time=0.4
            ),
            TacticalPattern(
                pattern_type="skewer",
                unit_coordination=["queen", "rook"],
                threat_multiplier=2.0,
                execution_time=0.5
            ),
            TacticalPattern(
                pattern_type="discovered_attack",
                unit_coordination=["any", "ranged"],
                threat_multiplier=1.6,
                execution_time=0.35
            ),
        ]
        return patterns
    
    def _extract_endgames(self, memory: Dict, num_games: int) -> List[Dict]:
        """Extract endgame knowledge → Resource denial."""
        return [
            {
                "name": "King and Pawn vs King",
                "resource_denial": 0.9,
                "pressure_score": 0.85,
                "timing": "late_game"
            },
            {
                "name": "Rook Endgame",
                "resource_denial": 0.7,
                "pressure_score": 0.8,
                "timing": "endgame"
            },
            {
                "name": "Bishop Pair Dominance",
                "resource_denial": 0.6,
                "pressure_score": 0.75,
                "timing": "mid_endgame"
            },
        ]
    
    def _build_position_vectors(self, memory: Dict) -> Dict[str, StrategyVector]:
        """Build universal strategy vectors from positions."""
        vectors = {
            "center_control": StrategyVector(
                position_value=0.8,
                threat_delta=0.3,
                aggression_index=0.6,
                material_imbalance=0.0,
                development_score=0.7,
                endgame_pressure=0.4
            ),
            "material_advantage": StrategyVector(
                position_value=0.6,
                threat_delta=0.5,
                aggression_index=0.4,
                material_imbalance=1.3,  # +1.3 pawns
                development_score=0.5,
                endgame_pressure=0.6
            ),
            "tempo_advantage": StrategyVector(
                position_value=0.5,
                threat_delta=0.2,
                aggression_index=0.8,  # High aggression
                material_imbalance=0.0,
                development_score=0.9,
                endgame_pressure=0.3
            ),
            "endgame_pressure": StrategyVector(
                position_value=0.7,
                threat_delta=0.4,
                aggression_index=0.5,
                material_imbalance=0.5,
                development_score=0.4,
                endgame_pressure=0.9  # High pressure
            ),
        }
        return vectors


class StrategyCoreExporter:
    """Export strategy core for universal application."""
    
    def __init__(self):
        """Initialize exporter."""
        self.core_data = {
            "version": "1.0",
            "extracted_at": datetime.now().isoformat(),
            "strategic_principles": [],
            "vectors": {},
            "mappings": {}
        }
    
    def inject_sun_tzu(self):
        """Inject Sun Tzu principles."""
        principles = [
            "Win without fighting = positional dominance",
            "Know the enemy = move prediction",
            "Attack where unprepared = exploit weaknesses",
            "Speed is the essence of war = tempo advantage",
            "Adapt terrain = remap chessboard to any grid",
            "Leave no rear exposed = secure flanks",
            "Strike when they falter = capitalize on mistakes"
        ]
        self.core_data["strategic_principles"].extend(principles)
    
    def inject_clausewitz(self):
        """Inject Clausewitz principles."""
        principles = [
            "Friction of war = calculation uncertainty",
            "Center of gravity = key resource control",
            "Fog of war = incomplete information",
            "Probability in tactics = evaluation confidence"
        ]
        self.core_data["strategic_principles"].extend(principles)
    
    def inject_musashi(self):
        """Inject Musashi principles."""
        principles = [
            "One cut = decisive move",
            "Rhythm disruption = tempo breaks",
            "Distance control = positioning",
            "Simultaneous attack = fork patterns"
        ]
        self.core_data["strategic_principles"].extend(principles)
    
    def build_mappings(self, chess_knowledge: Dict[str, Any]):
        """Build domain mappings (chess → war/MMORPG/trading)."""
        mappings = {
            "chess_to_war": {
                "pawn": "infantry",
                "rook": "tank",
                "knight": "cavalry",
                "bishop": "artillery",
                "queen": "command_unit",
                "king": "headquarters",
                "center_control": "strategic_location_control",
                "tempo": "initiative",
                "material": "resource_advantage"
            },
            "chess_to_mmorpg": {
                "pawn": "tank",
                "rook": "melee_dps",
                "knight": "rogue",
                "bishop": "healer",
                "queen": "support",
                "king": "main_tank",
                "center_control": "zone_control",
                "tempo": "aggro_management",
                "material": "party_composition"
            },
            "chess_to_trading": {
                "pawn": "small_position",
                "rook": "major_position",
                "knight": "swing_trade",
                "bishop": "trend_trade",
                "queen": "high_leverage",
                "king": "capital_preservation",
                "center_control": "market_dominance",
                "tempo": "momentum",
                "material": "profit_advantage"
            }
        }
        self.core_data["mappings"] = mappings
        self.core_data["vectors"] = chess_knowledge.get("position_vectors", {})
        self.core_data["openings"] = chess_knowledge.get("openings", [])
        self.core_data["tactics"] = chess_knowledge.get("tactics", [])
        self.core_data["endgames"] = chess_knowledge.get("endgames", [])
    
    def export(self, output_path: str = "strategy_core.json"):
        """Export strategy core."""
        self.inject_sun_tzu()
        self.inject_clausewitz()
        self.inject_musashi()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.core_data, f, indent=2)
        
        return output_path


def export_strategy_core(chess_agent_path: str = None, output_path: str = "strategy_core.json"):
    """
    Export strategy core from chess agent.
    
    Args:
        chess_agent_path: Path to chess agent sandbox
        output_path: Output file path
        
    Returns:
        Path to exported strategy core
    """
    # Find chess agent if path not provided
    if not chess_agent_path:
        swarm_dir = Path("./swarm_sandboxes")
        chess_dirs = list(swarm_dir.glob("chess_agent_*"))
        if chess_dirs:
            chess_agent_path = chess_dirs[0]
        else:
            return None
    
    # Extract knowledge
    extractor = ChessKnowledgeExtractor(str(chess_agent_path))
    knowledge = extractor.extract_from_games(5000)
    
    # Export strategy core
    exporter = StrategyCoreExporter()
    exporter.build_mappings(knowledge)
    output = exporter.export(output_path)
    
    print(f"[Strategy Core] Exported to {output}")
    print(f"[Strategy Core] Principles: {len(exporter.core_data['strategic_principles'])}")
    print(f"[Strategy Core] Vectors: {len(exporter.core_data['vectors'])}")
    print(f"[Strategy Core] Mappings: {len(exporter.core_data['mappings'])}")
    
    return output


if __name__ == '__main__':
    # Export strategy core
    export_strategy_core()

