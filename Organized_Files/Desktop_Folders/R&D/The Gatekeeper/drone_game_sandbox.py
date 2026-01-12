#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# DRONE GAME SANDBOX
# 4 agents playing tag, hide and seek, and dodgeball with nerf guns
# Deep learning from game mechanics and strategies

import json
import math
import random
import time
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
SANDBOX_DIR = GATE / 'drone_game_sandbox'
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

class GameType(Enum):
    """Game types for drone agents."""
    TAG = "tag"
    HIDE_AND_SEEK = "hide_and_seek"
    DODGEBALL = "dodgeball"

class DroneState(Enum):
    """Drone states during gameplay."""
    ACTIVE = "active"
    TAGGED = "tagged"
    HIDING = "hiding"
    SEEKING = "seeking"
    ELIMINATED = "eliminated"
    SAFE = "safe"

@dataclass
class Position3D:
    """3D position for drone."""
    x: float  # meters
    y: float  # meters
    z: float  # meters (altitude)
    
    def distance_to(self, other: 'Position3D') -> float:
        """Calculate 3D distance to another position."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def distance_2d(self, other: 'Position3D') -> float:
        """Calculate 2D distance (ignoring altitude)."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)

@dataclass
class NerfGun:
    """Nerf gun attachment for drone."""
    ammo: int = 20  # darts
    max_ammo: int = 20
    range_meters: float = 10.0  # effective range
    accuracy: float = 0.7  # hit probability at range
    reload_time: float = 2.0  # seconds
    fire_rate: float = 0.5  # seconds between shots
    last_shot_time: float = 0.0
    
    def can_fire(self, current_time: float) -> bool:
        """Check if gun can fire."""
        if self.ammo <= 0:
            return False
        if current_time - self.last_shot_time < self.fire_rate:
            return False
        return True
    
    def fire(self, target_pos: Position3D, shooter_pos: Position3D, current_time: float) -> Tuple[bool, float]:
        """Fire at target. Returns (hit, distance)."""
        if not self.can_fire(current_time):
            return False, 0.0
        
        distance = shooter_pos.distance_to(target_pos)
        if distance > self.range_meters:
            return False, distance
        
        # Accuracy decreases with distance
        distance_factor = 1.0 - (distance / self.range_meters)
        hit_probability = self.accuracy * distance_factor
        
        self.ammo -= 1
        self.last_shot_time = current_time
        
        hit = random.random() < hit_probability
        return hit, distance
    
    def reload(self):
        """Reload nerf gun."""
        self.ammo = self.max_ammo

@dataclass
class DroneAgent:
    """Drone agent for game sandbox."""
    agent_id: int
    name: str
    position: Position3D
    velocity: Position3D  # m/s in x, y, z
    max_speed: float = 5.0  # m/s
    battery: float = 100.0  # percent
    state: DroneState = DroneState.ACTIVE
    nerf_gun: NerfGun = None
    strategy: Dict = None
    stats: Dict = None
    
    def __post_init__(self):
        """Initialize after creation."""
        if self.nerf_gun is None:
            self.nerf_gun = NerfGun()
        if self.stats is None:
            self.stats = {
                'games_played': 0,
                'wins': 0,
                'losses': 0,
                'tags_made': 0,
                'tags_received': 0,
                'hits_made': 0,
                'hits_received': 0,
                'hiding_time': 0.0,
                'seeking_time': 0.0,
                'survival_time': 0.0
            }
        if self.strategy is None:
            self.strategy = {
                'aggressiveness': random.uniform(0.3, 0.7),
                'evasiveness': random.uniform(0.3, 0.7),
                'patience': random.uniform(0.3, 0.7),
                'cooperation': random.uniform(0.3, 0.7)
            }
    
    def move_toward(self, target: Position3D, dt: float):
        """Move toward target position."""
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        dz = target.z - self.position.z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 0.1:  # Already at target
            return
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
            dz /= distance
        
        # Apply max speed
        speed = min(self.max_speed, distance / dt)
        self.velocity.x = dx * speed
        self.velocity.y = dy * speed
        self.velocity.z = dz * speed
        
        # Update position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        self.position.z += self.velocity.z * dt
        
        # Consume battery
        self.battery -= 0.1 * dt
    
    def move_away_from(self, target: Position3D, dt: float):
        """Move away from target position."""
        dx = self.position.x - target.x
        dy = self.position.y - target.y
        dz = self.position.z - target.z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 0.1:
            # Too close, move randomly
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            dz = random.uniform(-0.5, 0.5)
        else:
            # Normalize direction
            dx /= distance
            dy /= distance
            dz /= distance
        
        # Apply max speed
        speed = self.max_speed * self.strategy['evasiveness']
        self.velocity.x = dx * speed
        self.velocity.y = dy * speed
        self.velocity.z = dz * speed
        
        # Update position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        self.position.z += self.velocity.z * dt
        
        # Consume battery
        self.battery -= 0.1 * dt

class GameSandbox:
    """Sandbox for drone games."""
    
    def __init__(self, arena_size: Tuple[float, float, float] = (50.0, 50.0, 20.0)):
        """Initialize game sandbox."""
        self.arena_size = arena_size  # (width, length, height) in meters
        self.agents: List[DroneAgent] = []
        self.game_type: Optional[GameType] = None
        self.game_active = False
        self.game_start_time = 0.0
        self.game_log: List[Dict] = []
        self.learning_data: Dict = {}
        
        # Arena boundaries
        self.arena_min = Position3D(0, 0, 2)  # Min altitude 2m
        self.arena_max = Position3D(arena_size[0], arena_size[1], arena_size[2])
        
        # Obstacles for hide and seek
        self.obstacles: List[Dict] = [
            {'pos': Position3D(10, 10, 0), 'size': (5, 5, 8)},
            {'pos': Position3D(30, 20, 0), 'size': (4, 4, 6)},
            {'pos': Position3D(15, 35, 0), 'size': (6, 6, 10)},
            {'pos': Position3D(40, 15, 0), 'size': (5, 5, 7)}
        ]
    
    def create_agents(self, count: int = 4, load_custom_drones: bool = True):
        """Create drone agents with their custom-built drones."""
        self.agents = []
        names = ["Alpha", "Beta", "Gamma", "Delta"]
        build_dir = GATE / 'agent_drone_builds'
        
        for i in range(count):
            # Random starting position
            pos = Position3D(
                random.uniform(5, self.arena_size[0] - 5),
                random.uniform(5, self.arena_size[1] - 5),
                random.uniform(3, 10)
            )
            
            agent_name = names[i] if i < len(names) else f"Drone{i+1}"
            agent = DroneAgent(
                agent_id=i,
                name=agent_name,
                position=pos,
                velocity=Position3D(0, 0, 0)
            )
            
            # Load custom drone build if available
            if load_custom_drones:
                build_file = build_dir / f"{agent_name}_drone_build.json"
                if build_file.exists():
                    try:
                        with open(build_file, 'r', encoding='utf-8') as f:
                            build_data = json.load(f)
                        
                        # Apply custom drone specifications
                        perf = build_data.get('performance', {})
                        agent.max_speed = perf.get('max_speed_ms', 5.0)
                        agent.strategy['aggressiveness'] = 0.7 if 'SPEED' in build_data.get('design_direction', '').upper() else 0.5
                        agent.strategy['evasiveness'] = perf.get('agility_score', 0.7)
                        agent.stats['drone_type'] = build_data.get('design_direction', 'standard')
                        agent.stats['custom_build'] = True
                        
                        print(f"[OK] {agent_name} loaded custom {build_data.get('design_direction', 'standard')} drone")
                    except Exception as e:
                        print(f"[WARNING] Failed to load custom drone for {agent_name}: {e}")
            
            self.agents.append(agent)
        
        print(f"[OK] Created {len(self.agents)} drone agents with custom builds")
    
    def learn_tag_rules(self):
        """Deep scrub and learn tag game rules."""
        rules = {
            'objective': 'One agent is "it" and must tag others by getting close enough',
            'tag_distance': 2.0,  # meters - close enough to tag
            'tag_method': 'physical proximity (no nerf gun needed)',
            'tagged_agent': 'becomes "it" and must tag someone else',
            'win_condition': 'last agent not tagged wins, or time limit',
            'strategy': {
                'it_agent': 'chase closest agent, use speed and positioning',
                'other_agents': 'evade "it", maintain distance, use obstacles',
                'teamwork': 'agents can coordinate to trap "it"'
            },
            'learning_points': [
                'Speed vs maneuverability trade-off',
                'Predictive positioning',
                'Energy management (battery)',
                'Arena awareness (boundaries)',
                'Multi-agent coordination'
            ]
        }
        
        self.learning_data['tag_rules'] = rules
        print("[LEARNED] Tag game rules and strategies")
        return rules
    
    def learn_hide_and_seek_rules(self):
        """Deep scrub and learn hide and seek rules."""
        rules = {
            'objective': 'Hiders hide, seeker finds and tags them',
            'phases': {
                'hiding_phase': 'Hiders have time to find hiding spots',
                'seeking_phase': 'Seeker searches for hiders',
                'tag_phase': 'Seeker tags hiders when found'
            },
            'tag_distance': 2.0,  # meters
            'hiding_time': 30.0,  # seconds for hiders to hide
            'win_condition': {
                'hiders': 'avoid being found until time limit',
                'seeker': 'find and tag all hiders'
            },
            'strategy': {
                'hiders': [
                    'Use obstacles for cover',
                    'Stay low to ground',
                    'Move slowly to avoid detection',
                    'Use shadows and blind spots',
                    'Coordinate with other hiders'
                ],
                'seeker': [
                    'Systematic search pattern',
                    'Check common hiding spots',
                    'Use altitude advantage',
                    'Listen for movement',
                    'Track multiple targets'
                ]
            },
            'learning_points': [
                'Spatial awareness',
                'Stealth movement',
                'Search patterns',
                'Environmental utilization',
                'Time management'
            ]
        }
        
        self.learning_data['hide_and_seek_rules'] = rules
        print("[LEARNED] Hide and seek game rules and strategies")
        return rules
    
    def learn_dodgeball_rules(self):
        """Deep scrub and learn dodgeball rules."""
        rules = {
            'objective': 'Eliminate opponents by hitting them with nerf darts',
            'nerf_gun': {
                'required': True,
                'range': 10.0,  # meters
                'accuracy': 0.7,
                'ammo': 20
            },
            'hit_detection': 'Nerf dart must hit target drone',
            'elimination': 'Hit drone is eliminated and removed from game',
            'win_condition': 'Last drone standing wins',
            'strategy': {
                'offensive': [
                    'Aim for center mass',
                    'Lead moving targets',
                    'Use cover while reloading',
                    'Coordinate with teammates',
                    'Manage ammo carefully'
                ],
                'defensive': [
                    'Constant movement',
                    'Unpredictable patterns',
                    'Use altitude changes',
                    'Stay near cover',
                    'Monitor all opponents'
                ]
            },
            'learning_points': [
                'Ballistic trajectory prediction',
                'Ammo management',
                'Reload timing',
                'Multi-target tracking',
                'Evasion patterns'
            ]
        }
        
        self.learning_data['dodgeball_rules'] = rules
        print("[LEARNED] Dodgeball game rules and strategies")
        return rules
    
    def play_tag(self, duration: float = 60.0, games: int = 16):
        """Play tag game - 16 games."""
        print("\n" + "=" * 60)
        print("DRONE TAG GAME - 16 GAMES")
        print("=" * 60)
        
        self.learn_tag_rules()
        rules = self.learning_data['tag_rules']
        
        game_results = []
        
        for game_num in range(1, games + 1):
            print(f"\n--- Game {game_num}/{games} ---")
            result = self._play_single_tag_game(duration)
            game_results.append(result)
            time.sleep(0.5)  # Brief pause between games
        
        # Summary
        self._print_tag_summary(game_results)
        return game_results
    
    def _play_single_tag_game(self, duration: float) -> Dict:
        """Play a single game of tag."""
        # Reset agents
        for agent in self.agents:
            agent.position = Position3D(
                random.uniform(5, self.arena_size[0] - 5),
                random.uniform(5, self.arena_size[1] - 5),
                random.uniform(3, 10)
            )
            agent.state = DroneState.ACTIVE
            agent.battery = 100.0
        
        # Randomly select "it"
        it_agent = random.choice(self.agents)
        it_agent.state = DroneState.TAGGED
        other_agents = [a for a in self.agents if a != it_agent]
        
        print(f"[TAG] {it_agent.name} is IT")
        
        start_time = time.time()
        dt = 0.1  # 100ms time step
        current_time = start_time
        
        game_log = []
        
        while current_time - start_time < duration:
            # "It" agent chases closest other agent
            if it_agent.state == DroneState.TAGGED:
                closest = min(other_agents, 
                            key=lambda a: it_agent.position.distance_to(a.position))
                it_agent.move_toward(closest.position, dt)
                
                # Check for tag
                distance = it_agent.position.distance_to(closest.position)
                if distance < 2.0:  # Tag distance
                    print(f"[TAG] {it_agent.name} tagged {closest.name}")
                    closest.stats['tags_received'] += 1
                    it_agent.stats['tags_made'] += 1
                    it_agent.state = DroneState.ACTIVE
                    closest.state = DroneState.TAGGED
                    it_agent, closest = closest, it_agent
                    other_agents = [a for a in self.agents if a != it_agent]
            
            # Other agents evade
            for agent in other_agents:
                if agent.state == DroneState.ACTIVE:
                    agent.move_away_from(it_agent.position, dt)
                    # Keep in bounds
                    agent.position.x = max(self.arena_min.x, min(self.arena_max.x, agent.position.x))
                    agent.position.y = max(self.arena_min.y, min(self.arena_max.y, agent.position.y))
                    agent.position.z = max(self.arena_min.z, min(self.arena_max.z, agent.position.z))
            
            current_time += dt
            time.sleep(0.01)  # Real-time simulation
        
        # Determine winner (agent who was "it" least or survived longest)
        winner = min(self.agents, key=lambda a: a.stats['tags_received'])
        winner.stats['wins'] += 1
        winner.stats['games_played'] += 1
        
        for agent in self.agents:
            if agent != winner:
                agent.stats['losses'] += 1
                agent.stats['games_played'] += 1
        
        return {
            'winner': winner.name,
            'duration': current_time - start_time,
            'tags_made': sum(a.stats['tags_made'] for a in self.agents),
            'final_it': it_agent.name
        }
    
    def play_hide_and_seek(self, hiding_time: float = 30.0, seeking_time: float = 120.0, games: int = 16):
        """Play hide and seek - 16 games."""
        print("\n" + "=" * 60)
        print("DRONE HIDE AND SEEK - 16 GAMES")
        print("=" * 60)
        
        self.learn_hide_and_seek_rules()
        rules = self.learning_data['hide_and_seek_rules']
        
        game_results = []
        
        for game_num in range(1, games + 1):
            print(f"\n--- Game {game_num}/{games} ---")
            result = self._play_single_hide_and_seek_game(hiding_time, seeking_time)
            game_results.append(result)
            time.sleep(0.5)
        
        self._print_hide_and_seek_summary(game_results)
        return game_results
    
    def _play_single_hide_and_seek_game(self, hiding_time: float, seeking_time: float) -> Dict:
        """Play a single game of hide and seek."""
        # Reset agents
        for agent in self.agents:
            agent.position = Position3D(
                random.uniform(5, self.arena_size[0] - 5),
                random.uniform(5, self.arena_size[1] - 5),
                random.uniform(3, 10)
            )
            agent.battery = 100.0
        
        # Randomly select seeker
        seeker = random.choice(self.agents)
        seeker.state = DroneState.SEEKING
        hiders = [a for a in self.agents if a != seeker]
        for hider in hiders:
            hider.state = DroneState.HIDING
        
        print(f"[HIDE & SEEK] {seeker.name} is SEEKER")
        print(f"[HIDE & SEEK] Hiders: {', '.join(h.name for h in hiders)}")
        
        # Phase 1: Hiding phase
        print(f"[HIDE & SEEK] Hiding phase ({hiding_time}s)...")
        start_time = time.time()
        dt = 0.1
        
        current_time = start_time
        while current_time - start_time < hiding_time:
            # Hiders move to hiding spots (behind obstacles)
            for hider in hiders:
                if hider.state == DroneState.HIDING:
                    # Find best hiding spot (behind obstacle)
                    best_spot = self._find_hiding_spot(hider.position)
                    hider.move_toward(best_spot, dt)
                    hider.stats['hiding_time'] += dt
                    # Keep in bounds
                    hider.position.x = max(self.arena_min.x, min(self.arena_max.x, hider.position.x))
                    hider.position.y = max(self.arena_min.y, min(self.arena_max.y, hider.position.y))
                    hider.position.z = max(self.arena_min.z, min(self.arena_max.z, hider.position.z))
            
            # Seeker waits (or moves to center)
            center = Position3D(self.arena_size[0]/2, self.arena_size[1]/2, 5)
            seeker.move_toward(center, dt)
            
            current_time += dt
            time.sleep(0.01)
        
        # Phase 2: Seeking phase
        print(f"[HIDE & SEEK] Seeking phase ({seeking_time}s)...")
        seek_start = current_time
        found_hiders = []
        
        while current_time - seek_start < seeking_time and len(found_hiders) < len(hiders):
            # Seeker searches systematically
            seeker.stats['seeking_time'] += dt
            closest_hider = min([h for h in hiders if h not in found_hiders],
                               key=lambda h: seeker.position.distance_to(h.position),
                               default=None)
            
            if closest_hider:
                seeker.move_toward(closest_hider.position, dt)
                distance = seeker.position.distance_to(closest_hider.position)
                
                if distance < 2.0:  # Found!
                    print(f"[HIDE & SEEK] {seeker.name} found {closest_hider.name}")
                    closest_hider.state = DroneState.TAGGED
                    found_hiders.append(closest_hider)
                    closest_hider.stats['tags_received'] += 1
                    seeker.stats['tags_made'] += 1
            
            # Hiders try to stay hidden (move slowly if seeker is far)
            for hider in hiders:
                if hider not in found_hiders:
                    distance_to_seeker = hider.position.distance_to(seeker.position)
                    if distance_to_seeker < 5.0:  # Seeker is close, try to evade
                        hider.move_away_from(seeker.position, dt * 0.5)  # Slow movement
                    hider.stats['hiding_time'] += dt
                    # Keep in bounds
                    hider.position.x = max(self.arena_min.x, min(self.arena_max.x, hider.position.x))
                    hider.position.y = max(self.arena_min.y, min(self.arena_max.y, hider.position.y))
                    hider.position.z = max(self.arena_min.z, min(self.arena_max.z, hider.position.z))
            
            current_time += dt
            time.sleep(0.01)
        
        # Determine winner
        if len(found_hiders) == len(hiders):
            # Seeker wins
            seeker.stats['wins'] += 1
            seeker.stats['games_played'] += 1
            for hider in hiders:
                hider.stats['losses'] += 1
                hider.stats['games_played'] += 1
            winner = seeker.name
        else:
            # Hiders win
            for hider in hiders:
                if hider not in found_hiders:
                    hider.stats['wins'] += 1
                hider.stats['games_played'] += 1
            seeker.stats['losses'] += 1
            seeker.stats['games_played'] += 1
            winner = f"Hiders ({len(hiders) - len(found_hiders)} remaining)"
        
        return {
            'winner': winner,
            'seeker': seeker.name,
            'found': len(found_hiders),
            'hidden': len(hiders) - len(found_hiders)
        }
    
    def _find_hiding_spot(self, current_pos: Position3D) -> Position3D:
        """Find a good hiding spot behind an obstacle."""
        if not self.obstacles:
            # No obstacles, hide at edge
            return Position3D(
                random.choice([5, self.arena_size[0] - 5]),
                random.choice([5, self.arena_size[1] - 5]),
                random.uniform(3, 8)
            )
        
        # Find closest obstacle
        closest_obstacle = min(self.obstacles,
                             key=lambda o: current_pos.distance_2d(o['pos']))
        
        # Hide behind obstacle (opposite side from center)
        center = Position3D(self.arena_size[0]/2, self.arena_size[1]/2, 0)
        dx = closest_obstacle['pos'].x - center.x
        dy = closest_obstacle['pos'].y - center.y
        
        # Position behind obstacle
        hide_pos = Position3D(
            closest_obstacle['pos'].x + dx * 0.5,
            closest_obstacle['pos'].y + dy * 0.5,
            random.uniform(3, 6)  # Low altitude
        )
        
        return hide_pos
    
    def play_dodgeball(self, duration: float = 120.0, games: int = 16):
        """Play dodgeball - 16 games."""
        print("\n" + "=" * 60)
        print("DRONE DODGEBALL - 16 GAMES")
        print("=" * 60)
        
        self.learn_dodgeball_rules()
        rules = self.learning_data['dodgeball_rules']
        
        game_results = []
        
        for game_num in range(1, games + 1):
            print(f"\n--- Game {game_num}/{games} ---")
            result = self._play_single_dodgeball_game(duration)
            game_results.append(result)
            time.sleep(0.5)
        
        self._print_dodgeball_summary(game_results)
        return game_results
    
    def _play_single_dodgeball_game(self, duration: float) -> Dict:
        """Play a single game of dodgeball."""
        # Reset agents
        for agent in self.agents:
            agent.position = Position3D(
                random.uniform(5, self.arena_size[0] - 5),
                random.uniform(5, self.arena_size[1] - 5),
                random.uniform(3, 10)
            )
            agent.state = DroneState.ACTIVE
            agent.battery = 100.0
            agent.nerf_gun.reload()
        
        print(f"[DODGEBALL] All agents active with nerf guns")
        
        start_time = time.time()
        dt = 0.1
        current_time = start_time
        
        active_agents = self.agents.copy()
        
        while current_time - start_time < duration and len(active_agents) > 1:
            for agent in active_agents:
                if agent.state == DroneState.ELIMINATED:
                    continue
                
                # Find closest opponent
                opponents = [a for a in active_agents if a != agent and a.state != DroneState.ELIMINATED]
                if not opponents:
                    break
                
                closest = min(opponents, key=lambda a: agent.position.distance_to(a.position))
                distance = agent.position.distance_to(closest.position)
                
                # Strategy: aggressive agents shoot, evasive agents dodge
                if agent.strategy['aggressiveness'] > 0.5 and distance < 15.0:
                    # Try to shoot
                    hit, shot_distance = agent.nerf_gun.fire(closest.position, agent.position, current_time)
                    if hit:
                        print(f"[DODGEBALL] {agent.name} hit {closest.name}")
                        closest.state = DroneState.ELIMINATED
                        active_agents.remove(closest)
                        agent.stats['hits_made'] += 1
                        closest.stats['hits_received'] += 1
                        closest.stats['survival_time'] = current_time - start_time
                
                # Evade if opponent is close or shooting
                if distance < 8.0 or agent.strategy['evasiveness'] > 0.5:
                    agent.move_away_from(closest.position, dt)
                else:
                    # Move toward opponent (if aggressive)
                    if agent.strategy['aggressiveness'] > 0.6:
                        agent.move_toward(closest.position, dt)
                
                # Reload if out of ammo
                if agent.nerf_gun.ammo == 0:
                    agent.nerf_gun.reload()
                
                # Keep in bounds
                agent.position.x = max(self.arena_min.x, min(self.arena_max.x, agent.position.x))
                agent.position.y = max(self.arena_min.y, min(self.arena_max.y, agent.position.y))
                agent.position.z = max(self.arena_min.z, min(self.arena_max.z, agent.position.z))
                
                agent.stats['survival_time'] = current_time - start_time
            
            current_time += dt
            time.sleep(0.01)
        
        # Determine winner
        winner = None
        for agent in active_agents:
            if agent.state != DroneState.ELIMINATED:
                winner = agent
                break
        
        if winner:
            winner.stats['wins'] += 1
            winner.stats['games_played'] += 1
            print(f"[DODGEBALL] Winner: {winner.name}")
        else:
            # Time limit reached, most survival time wins
            winner = max(self.agents, key=lambda a: a.stats['survival_time'])
            winner.stats['wins'] += 1
            winner.stats['games_played'] += 1
        
        for agent in self.agents:
            if agent != winner:
                agent.stats['losses'] += 1
                agent.stats['games_played'] += 1
        
        return {
            'winner': winner.name if winner else "Time Limit",
            'survivors': len([a for a in active_agents if a.state != DroneState.ELIMINATED]),
            'eliminations': len(self.agents) - len(active_agents)
        }
    
    def _print_tag_summary(self, results: List[Dict]):
        """Print tag game summary."""
        print("\n" + "=" * 60)
        print("TAG GAME SUMMARY - 16 GAMES")
        print("=" * 60)
        for agent in self.agents:
            print(f"{agent.name}: {agent.stats['wins']} wins, {agent.stats['tags_made']} tags made, {agent.stats['tags_received']} tags received")
    
    def _print_hide_and_seek_summary(self, results: List[Dict]):
        """Print hide and seek summary."""
        print("\n" + "=" * 60)
        print("HIDE AND SEEK SUMMARY - 16 GAMES")
        print("=" * 60)
        for agent in self.agents:
            print(f"{agent.name}: {agent.stats['wins']} wins, {agent.stats['tags_made']} finds, {agent.stats['hiding_time']:.1f}s hiding")
    
    def _print_dodgeball_summary(self, results: List[Dict]):
        """Print dodgeball summary."""
        print("\n" + "=" * 60)
        print("DODGEBALL SUMMARY - 16 GAMES")
        print("=" * 60)
        for agent in self.agents:
            print(f"{agent.name}: {agent.stats['wins']} wins, {agent.stats['hits_made']} hits made, {agent.stats['hits_received']} hits received")
    
    def save_learning_data(self):
        """Save learning data to file."""
        learning_file = SANDBOX_DIR / 'learning_data.json'
        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, indent=2, default=str)
        print(f"[OK] Learning data saved to {learning_file}")
    
    def save_stats(self):
        """Save agent statistics."""
        stats_file = SANDBOX_DIR / 'agent_stats.json'
        stats_data = {}
        for agent in self.agents:
            stats_data[agent.name] = agent.stats
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2)
        print(f"[OK] Stats saved to {stats_file}")

def main():
    """Main entry point."""
    print("=" * 60)
    print("DRONE GAME SANDBOX - 4 AGENTS")
    print("Tag, Hide and Seek, Dodgeball")
    print("=" * 60)
    print("\nThe doors of knowledge opens.")
    print("Initializing drone game sandbox...\n")
    
    sandbox = GameSandbox(arena_size=(50.0, 50.0, 20.0))
    sandbox.create_agents(count=4)
    
    # Play 16 games of each
    print("\n" + "=" * 60)
    print("STARTING GAME SESSION")
    print("=" * 60)
    
    # Tag - 16 games
    sandbox.play_tag(duration=60.0, games=16)
    
    # Hide and Seek - 16 games
    sandbox.play_hide_and_seek(hiding_time=30.0, seeking_time=120.0, games=16)
    
    # Dodgeball - 16 games
    sandbox.play_dodgeball(duration=120.0, games=16)
    
    # Save results
    sandbox.save_learning_data()
    sandbox.save_stats()
    
    print("\n" + "=" * 60)
    print("GAME SESSION COMPLETE")
    print("=" * 60)
    print("\nFinal Statistics:")
    for agent in sandbox.agents:
        print(f"\n{agent.name}:")
        print(f"  Games: {agent.stats['games_played']}")
        print(f"  Wins: {agent.stats['wins']}")
        print(f"  Losses: {agent.stats['losses']}")
        print(f"  Win Rate: {(agent.stats['wins']/max(agent.stats['games_played'],1)*100):.1f}%")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
