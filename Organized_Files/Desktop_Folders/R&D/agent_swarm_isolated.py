# -*- coding: utf-8 -*-
# ISOLATED AGENT SWARM
# 4 agents: Chess, Checkers, Mahjong, Go
# Zero shared memory. Zero cross-talk. Clean sandboxes.

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class GameType(Enum):
    """Game types for isolated agents."""
    CHESS = "chess"
    CHECKERS = "checkers"
    MAHJONG = "mahjong"
    GO = "go"


@dataclass
class AgentStats:
    """Agent statistics - isolated per agent."""
    name: str
    game_type: GameType
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    best_move_count: int = 9999
    last_achievement: str = ""
    last_report_time: float = 0.0
    learning_cycles: int = 0
    skill_level: float = 0.0  # 0.0 = beginner, 1.0 = master


class IsolatedAgent:
    """
    Isolated agent - no shared memory, no cross-talk.
    Breathes its own air. Grinds on its own timeline.
    """
    
    def __init__(self, game_type: GameType, agent_name: Optional[str] = None):
        """Initialize isolated agent."""
        self.game_type = game_type
        self.name = agent_name or f"{game_type.value}_agent_{int(time.time())}"
        
        # Isolated sandbox directory
        self.sandbox_dir = Path(f"./swarm_sandboxes/{self.name}")
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Isolated memory
        self.memory_file = self.sandbox_dir / "memory.json"
        self.stats_file = self.sandbox_dir / "stats.json"
        
        # Stats
        self.stats = AgentStats(
            name=self.name,
            game_type=game_type,
            last_report_time=time.time()
        )
        
        # Learning data (isolated)
        self.learning_log = []
        self.position_cache = {}  # Game-specific position evaluation
        
        # Load existing stats
        self._load_stats()
        
        # Learning thread (isolated)
        self.learning_active = False
        self.learning_thread = None
    
    def _load_stats(self):
        """Load stats from isolated sandbox."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stats.games_played = data.get('games_played', 0)
                    self.stats.wins = data.get('wins', 0)
                    self.stats.losses = data.get('losses', 0)
                    self.stats.draws = data.get('draws', 0)
                    self.stats.best_move_count = data.get('best_move_count', 9999)
                    self.stats.last_achievement = data.get('last_achievement', '')
                    self.stats.learning_cycles = data.get('learning_cycles', 0)
                    self.stats.skill_level = data.get('skill_level', 0.0)
            except Exception as e:
                print(f"[{self.name}] Failed to load stats: {e}")
    
    def _save_stats(self):
        """Save stats to isolated sandbox."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'games_played': self.stats.games_played,
                    'wins': self.stats.wins,
                    'losses': self.stats.losses,
                    'draws': self.stats.draws,
                    'best_move_count': self.stats.best_move_count,
                    'last_achievement': self.stats.last_achievement,
                    'learning_cycles': self.stats.learning_cycles,
                    'skill_level': self.stats.skill_level,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"[{self.name}] Failed to save stats: {e}")
    
    def learn_game(self, game_result: Dict[str, Any]):
        """
        Learn from game result - isolated learning.
        
        Args:
            game_result: {
                'won': bool,
                'move_count': int,
                'final_position': Any,
                'mistakes': List[str],
                'brilliant_moves': List[str]
            }
        """
        self.stats.games_played += 1
        
        if game_result.get('won'):
            self.stats.wins += 1
            if game_result.get('move_count', 9999) < self.stats.best_move_count:
                self.stats.best_move_count = game_result['move_count']
                self.stats.last_achievement = f"Beat engine in {game_result['move_count']} moves"
        else:
            self.stats.losses += 1
        
        # Update skill level (0.0 -> 1.0)
        if self.stats.games_played > 0:
            win_rate = self.stats.wins / self.stats.games_played
            self.stats.skill_level = min(1.0, win_rate * 0.7 + (self.stats.games_played / 1000) * 0.3)
        
        # Log learning (isolated)
        self.learning_log.append({
            'timestamp': time.time(),
            'result': game_result,
            'skill_level': self.stats.skill_level
        })
        
        # Keep last 1000 games
        if len(self.learning_log) > 1000:
            self.learning_log = self.learning_log[-1000:]
        
        # Increment learning cycles
        self.stats.learning_cycles += 1
        
        # Save stats
        self._save_stats()
    
    def start_learning_loop(self):
        """Start isolated learning loop - grinds independently."""
        if self.learning_active:
            return
        
        self.learning_active = True
        
        def _learn_loop():
            """Isolated learning thread."""
            while self.learning_active:
                try:
                    # Simulate game against engine
                    game_result = self._simulate_game()
                    
                    # Learn from result
                    self.learn_game(game_result)
                    
                    # Sleep (variable based on game type)
                    sleep_time = {
                        GameType.CHESS: 5.0,
                        GameType.CHECKERS: 3.0,
                        GameType.MAHJONG: 8.0,
                        GameType.GO: 10.0
                    }.get(self.game_type, 5.0)
                    
                    time.sleep(sleep_time)
                except Exception as e:
                    print(f"[{self.name}] Learning error: {e}")
                    time.sleep(1.0)
        
        self.learning_thread = threading.Thread(target=_learn_loop, daemon=True)
        self.learning_thread.start()
        print(f"[{self.name}] Learning loop started. Isolated. No cross-talk.")
    
    def _simulate_game(self) -> Dict[str, Any]:
        """Simulate game against engine - game-specific logic."""
        import random
        
        # Simulate game outcome based on current skill level
        # Skill level affects win probability
        win_probability = 0.3 + (self.stats.skill_level * 0.5)  # 30% base -> 80% max
        
        won = random.random() < win_probability
        
        # Move count based on game type and skill
        base_moves = {
            GameType.CHESS: 40,
            GameType.CHECKERS: 30,
            GameType.MAHJONG: 50,
            GameType.GO: 200
        }.get(self.game_type, 40)
        
        move_count = int(base_moves * (0.7 + random.random() * 0.6))
        
        # If won and skill high, fewer moves (better play)
        if won and self.stats.skill_level > 0.7:
            move_count = int(move_count * 0.7)
        
        return {
            'won': won,
            'move_count': move_count,
            'final_position': None,
            'mistakes': [] if won else ['Some mistake'],
            'brilliant_moves': ['Good move'] if won else []
        }
    
    def stop_learning(self):
        """Stop learning loop."""
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join(timeout=2.0)
        print(f"[{self.name}] Learning stopped.")
    
    def report(self) -> str:
        """Generate report - summon agent to report."""
        self.stats.last_report_time = time.time()
        
        win_rate = (self.stats.wins / self.stats.games_played * 100) if self.stats.games_played > 0 else 0.0
        
        report = f"\n[{self.name.upper()}] {self.game_type.value.upper()} AGENT REPORT"
        report += f"\n{'=' * 60}"
        report += f"\nGames Played: {self.stats.games_played}"
        report += f"\nWins: {self.stats.wins} | Losses: {self.stats.losses} | Draws: {self.stats.draws}"
        report += f"\nWin Rate: {win_rate:.1f}%"
        report += f"\nBest Win: {self.stats.best_move_count} moves"
        report += f"\nSkill Level: {self.stats.skill_level:.2f} ({'Beginner' if self.stats.skill_level < 0.3 else 'Intermediate' if self.stats.skill_level < 0.7 else 'Expert' if self.stats.skill_level < 0.9 else 'Master'})"
        report += f"\nLearning Cycles: {self.stats.learning_cycles}"
        
        if self.stats.last_achievement:
            report += f"\nLast Achievement: {self.stats.last_achievement}"
        
        report += f"\n{'=' * 60}\n"
        
        return report
    
    def quick_status(self) -> str:
        """Quick status - one-liner."""
        if self.stats.games_played == 0:
            return f"[{self.name}] Learning... ({self.stats.learning_cycles} cycles)"
        
        win_rate = (self.stats.wins / self.stats.games_played * 100) if self.stats.games_played > 0 else 0.0
        
        achievement = ""
        if self.stats.last_achievement:
            achievement = f" | {self.stats.last_achievement}"
        
        return f"[{self.name}] {self.stats.games_played} games, {win_rate:.0f}% win rate{achievement}"


class SwarmOrchestrator:
    """
    Swarm orchestrator - manages 4 isolated agents.
    No cross-talk. No shared memory. Clean summoning.
    """
    
    def __init__(self):
        """Initialize swarm."""
        self.agents: Dict[GameType, IsolatedAgent] = {}
        self.swarm_active = False
        
        # Initialize 4 agents
        print("\n" + "=" * 60)
        print("SPINNING 4-AGENT SWARM")
        print("=" * 60)
        
        for game_type in GameType:
            agent = IsolatedAgent(game_type)
            self.agents[game_type] = agent
            print(f"[OK] {agent.name} initialized in isolated sandbox: {agent.sandbox_dir}")
        
        print("\n[OK] All 4 agents isolated. No shared memory. No cross-talk.")
        print("=" * 60 + "\n")
    
    def start_swarm(self):
        """Start all agents learning independently."""
        if self.swarm_active:
            print("[Swarm] Already running.")
            return
        
        self.swarm_active = True
        
        for game_type, agent in self.agents.items():
            agent.start_learning_loop()
        
        print("[Swarm] All 4 agents grinding. Isolated. Silent.")
    
    def stop_swarm(self):
        """Stop all agents."""
        self.swarm_active = False
        
        for agent in self.agents.values():
            agent.stop_learning()
        
        print("[Swarm] All agents stopped.")
    
    def summon_agent(self, game_type: GameType) -> str:
        """Summon specific agent to report."""
        agent = self.agents.get(game_type)
        if not agent:
            return f"[ERROR] Agent for {game_type.value} not found."
        
        return agent.report()
    
    def summon_all(self) -> str:
        """Summon all agents to report."""
        report = "\n" + "=" * 60
        report += "\nSWARM STATUS - ALL AGENTS"
        report += "\n" + "=" * 60
        
        for game_type, agent in self.agents.items():
            report += agent.report()
        
        return report
    
    def quick_status_all(self) -> str:
        """Quick status of all agents."""
        status = "\n[Swarm] Quick Status:\n"
        for game_type, agent in self.agents.items():
            status += f"  {agent.quick_status()}\n"
        return status
    
    def get_agent(self, game_type: GameType) -> Optional[IsolatedAgent]:
        """Get specific agent."""
        return self.agents.get(game_type)


if __name__ == '__main__':
    # Create swarm
    swarm = SwarmOrchestrator()
    
    # Start learning
    swarm.start_swarm()
    
    # Let them grind for a bit
    print("\n[Swarm] Agents learning... (Ctrl+C to stop)")
    print("[Swarm] Use swarm.summon_agent(GameType.CHESS) to check status\n")
    
    try:
        # Example: Let them run for 30 seconds, then report
        time.sleep(30)
        
        # Summon individual agent
        print(swarm.summon_agent(GameType.CHESS))
        
        # Summon all
        print(swarm.summon_all())
        
        # Keep running
        while True:
            time.sleep(60)
            print(swarm.quick_status_all())
    except KeyboardInterrupt:
        print("\n[Swarm] Stopping...")
        swarm.stop_swarm()
        print("[Swarm] Stopped. Clean.")

