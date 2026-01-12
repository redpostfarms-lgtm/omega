#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# AGENT DRONE COURSE TESTER
# Test each agent's drone through speed, agility, and endurance courses
# Then play 2 games of each type (tag, hide and seek, dodgeball)

import json
import math
import random
import time
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Note: Windows console encoding handled by print statements
# Removed stdout/stderr wrapping to avoid conflicts

# Import from existing systems
try:
    from agent_drone_builder import AgentDroneBuilder, DesignDirection
    from drone_game_sandbox import GameSandbox, DroneAgent, Position3D, DroneState, NerfGun
except ImportError as e:
    print(f"[WARNING] Import error: {e}")
    print("[INFO] Running in standalone mode")
    # Define minimal classes if imports fail
    class GameSandbox:
        def __init__(self, *args, **kwargs):
            self.agents = []
        def create_agents(self, *args, **kwargs):
            pass
        def _play_single_tag_game(self, *args, **kwargs):
            return {'winner': 'Unknown'}
        def _play_single_hide_and_seek_game(self, *args, **kwargs):
            return {'winner': 'Unknown'}
        def _play_single_dodgeball_game(self, *args, **kwargs):
            return {'winner': 'Unknown'}

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
TEST_DIR = GATE / 'agent_drone_tests'
TEST_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class CourseResult:
    """Result from a course test."""
    agent_name: str
    course_type: str
    time_seconds: float
    score: float
    details: Dict

@dataclass
class AgentTestResults:
    """Complete test results for an agent."""
    agent_name: str
    speed_course: Optional[CourseResult] = None
    agility_course: Optional[CourseResult] = None
    endurance_course: Optional[CourseResult] = None
    game_results: Dict = None

class CourseTester:
    """Test drones through speed, agility, and endurance courses."""
    
    def __init__(self):
        """Initialize course tester."""
        self.builder = AgentDroneBuilder()
        self.builder.build_all_agent_drones()
        self.agents = {}
        self.test_results: Dict[str, AgentTestResults] = {}
        
        # Load agent builds
        build_dir = GATE / 'agent_drone_builds'
        for agent_name in ['Alpha', 'Beta', 'Gamma', 'Delta']:
            build_file = build_dir / f"{agent_name}_drone_build.json"
            if build_file.exists():
                with open(build_file, 'r', encoding='utf-8') as f:
                    self.agents[agent_name] = json.load(f)
                    self.test_results[agent_name] = AgentTestResults(agent_name=agent_name)
    
    def test_speed_course(self, agent_name: str) -> CourseResult:
        """Test agent through speed course - straight line race."""
        print(f"\n[{agent_name}] SPEED COURSE TEST")
        print("-" * 60)
        
        build = self.agents.get(agent_name)
        if not build:
            return None
        
        perf = build.get('performance', {})
        max_speed = perf.get('max_speed_ms', 5.0)  # m/s
        twr = perf.get('thrust_to_weight_ratio', 2.0)
        
        # Speed course: 200m straight line
        course_length = 200.0  # meters
        start_time = time.time()
        
        # Calculate time based on max speed and acceleration
        # Acceleration = (TWR - 1) * 9.8 m/s²
        acceleration = (twr - 1) * 9.8
        if acceleration < 0:
            acceleration = 2.0  # Minimum acceleration
        
        # Time to reach max speed: v = a*t, so t = v/a
        time_to_max_speed = max_speed / acceleration if acceleration > 0 else 5.0
        
        # Distance to reach max speed: d = 0.5 * a * t²
        distance_to_max = 0.5 * acceleration * (time_to_max_speed ** 2)
        
        if distance_to_max >= course_length:
            # Never reaches max speed
            time_seconds = math.sqrt((2 * course_length) / acceleration)
        else:
            # Reaches max speed, then continues at max speed
            time_at_max = (course_length - distance_to_max) / max_speed
            time_seconds = time_to_max_speed + time_at_max
        
        # Add some variation based on design
        design_dir = build.get('design_direction', '')
        if 'speed' in design_dir.lower():
            time_seconds *= 0.95  # 5% faster for speed-focused
        elif 'payload' in design_dir.lower():
            time_seconds *= 1.15  # 15% slower for heavy drones
        
        # Score: 100 points for fastest, scaled by time
        # Baseline: 30 seconds for 200m = 100 points
        baseline_time = 30.0
        score = (baseline_time / time_seconds) * 100 if time_seconds > 0 else 0
        score = min(score, 150.0)  # Cap at 150
        
        details = {
            'course_length_m': course_length,
            'max_speed_ms': max_speed,
            'acceleration_ms2': acceleration,
            'time_to_max_speed': time_to_max_speed,
            'distance_to_max_speed': distance_to_max
        }
        
        print(f"Course: 200m straight line")
        print(f"Time: {time_seconds:.2f} seconds")
        print(f"Average Speed: {course_length/time_seconds:.2f} m/s")
        print(f"Score: {score:.1f} points")
        
        return CourseResult(
            agent_name=agent_name,
            course_type='speed',
            time_seconds=time_seconds,
            score=score,
            details=details
        )
    
    def test_agility_course(self, agent_name: str) -> CourseResult:
        """Test agent through agility course - obstacle slalom."""
        print(f"\n[{agent_name}] AGILITY COURSE TEST")
        print("-" * 60)
        
        build = self.agents.get(agent_name)
        if not build:
            return None
        
        perf = build.get('performance', {})
        agility_score = perf.get('agility_score', 0.7)
        max_speed = perf.get('max_speed_ms', 5.0)
        twr = perf.get('thrust_to_weight_ratio', 2.0)
        
        # Agility course: Slalom through 10 gates (50m spacing, 5m wide gates)
        num_gates = 10
        gate_spacing = 50.0  # meters
        gate_width = 5.0  # meters
        total_distance = num_gates * gate_spacing
        
        # Base time calculation
        # Agility affects turning speed and precision
        base_speed = max_speed * agility_score  # Effective speed in turns
        base_time = total_distance / base_speed
        
        # Add penalty for each gate (turning time)
        turn_penalty = (1.0 - agility_score) * 2.0  # seconds per gate
        total_turn_time = turn_penalty * num_gates
        
        # Gate hit penalty (lower agility = more likely to hit)
        hit_probability = (1.0 - agility_score) * 0.3
        expected_hits = hit_probability * num_gates
        hit_penalty = expected_hits * 5.0  # 5 seconds per hit
        
        time_seconds = base_time + total_turn_time + hit_penalty
        
        # Score: 100 points for best agility, scaled
        # Baseline: 60 seconds = 100 points
        baseline_time = 60.0
        score = (baseline_time / time_seconds) * 100 if time_seconds > 0 else 0
        score = min(score, 150.0)  # Cap at 150
        
        details = {
            'num_gates': num_gates,
            'gate_spacing_m': gate_spacing,
            'gate_width_m': gate_width,
            'agility_score': agility_score,
            'effective_speed_ms': base_speed,
            'expected_gate_hits': expected_hits,
            'turn_penalty_per_gate': turn_penalty
        }
        
        print(f"Course: 10-gate slalom (500m total)")
        print(f"Time: {time_seconds:.2f} seconds")
        print(f"Agility Score: {agility_score:.2f}")
        print(f"Expected Gate Hits: {expected_hits:.1f}")
        print(f"Score: {score:.1f} points")
        
        return CourseResult(
            agent_name=agent_name,
            course_type='agility',
            time_seconds=time_seconds,
            score=score,
            details=details
        )
    
    def test_endurance_course(self, agent_name: str) -> CourseResult:
        """Test agent through endurance course - maximum flight time."""
        print(f"\n[{agent_name}] ENDURANCE COURSE TEST")
        print("-" * 60)
        
        build = self.agents.get(agent_name)
        if not build:
            return None
        
        perf = build.get('performance', {})
        flight_time = perf.get('flight_time_minutes', 2.0)
        total_weight = perf.get('total_weight_grams', 1000.0)
        battery_capacity = build.get('components', {}).get('battery', '')
        
        # Endurance course: Hover test until battery depletion
        # Flight time is already calculated, but adjust for efficiency
        design_dir = build.get('design_direction', '')
        if 'endurance' in design_dir.lower():
            flight_time *= 1.1  # 10% longer for endurance-focused
        elif 'speed' in design_dir.lower():
            flight_time *= 0.85  # 15% shorter for speed-focused (higher power draw)
        
        # Convert to seconds
        time_seconds = flight_time * 60.0
        
        # Score: 100 points for longest flight, scaled
        # Baseline: 3 minutes = 100 points
        baseline_time = 180.0  # 3 minutes in seconds
        score = (time_seconds / baseline_time) * 100 if baseline_time > 0 else 0
        score = min(score, 200.0)  # Cap at 200
        
        details = {
            'flight_time_minutes': flight_time,
            'flight_time_seconds': time_seconds,
            'total_weight_grams': total_weight,
            'battery': battery_capacity,
            'efficiency_factor': 1.0 if 'endurance' in design_dir.lower() else 0.9
        }
        
        print(f"Course: Maximum hover time")
        print(f"Flight Time: {flight_time:.2f} minutes ({time_seconds:.0f} seconds)")
        print(f"Battery: {battery_capacity}")
        print(f"Score: {score:.1f} points")
        
        return CourseResult(
            agent_name=agent_name,
            course_type='endurance',
            time_seconds=time_seconds,
            score=score,
            details=details
        )
    
    def run_all_course_tests(self):
        """Run all agents through all courses."""
        print("=" * 60)
        print("DRONE COURSE TESTING")
        print("Speed, Agility, Endurance")
        print("=" * 60)
        
        for agent_name in self.agents.keys():
            print(f"\n{'='*60}")
            print(f"TESTING {agent_name}")
            print(f"{'='*60}")
            
            # Speed course
            speed_result = self.test_speed_course(agent_name)
            if speed_result:
                self.test_results[agent_name].speed_course = speed_result
            
            # Agility course
            agility_result = self.test_agility_course(agent_name)
            if agility_result:
                self.test_results[agent_name].agility_course = agility_result
            
            # Endurance course
            endurance_result = self.test_endurance_course(agent_name)
            if endurance_result:
                self.test_results[agent_name].endurance_course = endurance_result
        
        # Print summary
        self.print_course_summary()
        
        # Save results
        self.save_test_results()
    
    def print_course_summary(self):
        """Print summary of all course tests."""
        print("\n" + "=" * 60)
        print("COURSE TEST SUMMARY")
        print("=" * 60)
        
        # Speed course results
        print("\nSPEED COURSE (200m straight line):")
        print("-" * 60)
        speed_results = [(name, r.speed_course) for name, r in self.test_results.items() if r.speed_course]
        speed_results.sort(key=lambda x: x[1].time_seconds if x[1] else 999)
        for i, (name, result) in enumerate(speed_results, 1):
            print(f"{i}. {name}: {result.time_seconds:.2f}s ({result.score:.1f} pts)")
        
        # Agility course results
        print("\nAGILITY COURSE (10-gate slalom):")
        print("-" * 60)
        agility_results = [(name, r.agility_course) for name, r in self.test_results.items() if r.agility_course]
        agility_results.sort(key=lambda x: x[1].time_seconds if x[1] else 999)
        for i, (name, result) in enumerate(agility_results, 1):
            print(f"{i}. {name}: {result.time_seconds:.2f}s ({result.score:.1f} pts)")
        
        # Endurance course results
        print("\nENDURANCE COURSE (maximum flight time):")
        print("-" * 60)
        endurance_results = [(name, r.endurance_course) for name, r in self.test_results.items() if r.endurance_course]
        endurance_results.sort(key=lambda x: x[1].time_seconds if x[1] else 0, reverse=True)
        for i, (name, result) in enumerate(endurance_results, 1):
            minutes = result.time_seconds / 60.0
            print(f"{i}. {name}: {minutes:.2f} min ({result.score:.1f} pts)")
        
        # Overall scores
        print("\nOVERALL COURSE SCORES:")
        print("-" * 60)
        overall_scores = {}
        for name, results in self.test_results.items():
            total_score = 0.0
            if results.speed_course:
                total_score += results.speed_course.score
            if results.agility_course:
                total_score += results.agility_course.score
            if results.endurance_course:
                total_score += results.endurance_course.score
            overall_scores[name] = total_score
        
        sorted_overall = sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)
        for i, (name, score) in enumerate(sorted_overall, 1):
            print(f"{i}. {name}: {score:.1f} total points")
    
    def save_test_results(self):
        """Save test results to file."""
        results_file = TEST_DIR / 'course_test_results.json'
        
        results_data = {}
        for name, results in self.test_results.items():
            results_data[name] = {
                'speed_course': asdict(results.speed_course) if results.speed_course else None,
                'agility_course': asdict(results.agility_course) if results.agility_course else None,
                'endurance_course': asdict(results.endurance_course) if results.endurance_course else None
            }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Test results saved to {results_file}")

class GameRunner:
    """Run games after course tests."""
    
    def __init__(self, course_tester: CourseTester):
        """Initialize game runner with course test results."""
        self.course_tester = course_tester
        self.sandbox = GameSandbox(arena_size=(50.0, 50.0, 20.0))
        self.game_results: Dict[str, List[Dict]] = {}
    
    def run_games(self, games_per_type: int = 2):
        """Run games after course tests."""
        print("\n" + "=" * 60)
        print("GAME SESSION - AFTER COURSE TESTS")
        print(f"Playing {games_per_type} games of each type")
        print("=" * 60)
        
        # Create agents with their custom drones
        self.sandbox.create_agents(count=4, load_custom_drones=True)
        
        # Apply course test performance bonuses
        self.apply_course_bonuses()
        
        # Play Tag - 2 games
        print("\n" + "=" * 60)
        print("TAG GAME - 2 GAMES")
        print("=" * 60)
        tag_results = []
        for i in range(games_per_type):
            print(f"\n--- Tag Game {i+1}/{games_per_type} ---")
            result = self.sandbox._play_single_tag_game(duration=60.0)
            tag_results.append(result)
            time.sleep(0.3)
        self.game_results['tag'] = tag_results
        
        # Play Hide and Seek - 2 games
        print("\n" + "=" * 60)
        print("HIDE AND SEEK - 2 GAMES")
        print("=" * 60)
        hide_seek_results = []
        for i in range(games_per_type):
            print(f"\n--- Hide and Seek Game {i+1}/{games_per_type} ---")
            result = self.sandbox._play_single_hide_and_seek_game(hiding_time=30.0, seeking_time=120.0)
            hide_seek_results.append(result)
            time.sleep(0.3)
        self.game_results['hide_and_seek'] = hide_seek_results
        
        # Play Dodgeball - 2 games
        print("\n" + "=" * 60)
        print("DODGEBALL - 2 GAMES")
        print("=" * 60)
        dodgeball_results = []
        for i in range(games_per_type):
            print(f"\n--- Dodgeball Game {i+1}/{games_per_type} ---")
            result = self.sandbox._play_single_dodgeball_game(duration=120.0)
            dodgeball_results.append(result)
            time.sleep(0.3)
        self.game_results['dodgeball'] = dodgeball_results
        
        # Print game summary
        self.print_game_summary()
        
        # Save game results
        self.save_game_results()
    
    def apply_course_bonuses(self):
        """Apply performance bonuses based on course test results."""
        for agent in self.sandbox.agents:
            agent_name = agent.name
            test_results = self.course_tester.test_results.get(agent_name)
            
            if not test_results:
                continue
            
            # Speed bonus affects max_speed
            if test_results.speed_course:
                speed_bonus = test_results.speed_course.score / 100.0
                agent.max_speed *= (1.0 + speed_bonus * 0.1)  # Up to 10% boost
            
            # Agility bonus affects evasiveness
            if test_results.agility_course:
                agility_bonus = test_results.agility_course.score / 100.0
                agent.strategy['evasiveness'] = min(1.0, agent.strategy.get('evasiveness', 0.7) + agility_bonus * 0.2)
            
            # Endurance bonus affects battery life
            if test_results.endurance_course:
                endurance_bonus = test_results.endurance_course.score / 100.0
                agent.battery = min(100.0, agent.battery * (1.0 + endurance_bonus * 0.1))
    
    def print_game_summary(self):
        """Print summary of game results."""
        print("\n" + "=" * 60)
        print("GAME RESULTS SUMMARY")
        print("=" * 60)
        
        # Tag results
        print("\nTAG GAME RESULTS:")
        print("-" * 60)
        tag_wins = {}
        for result in self.game_results.get('tag', []):
            winner = result.get('winner', 'Unknown')
            tag_wins[winner] = tag_wins.get(winner, 0) + 1
        for agent_name, wins in sorted(tag_wins.items(), key=lambda x: x[1], reverse=True):
            print(f"{agent_name}: {wins} wins")
        
        # Hide and Seek results
        print("\nHIDE AND SEEK RESULTS:")
        print("-" * 60)
        hide_seek_wins = {}
        for result in self.game_results.get('hide_and_seek', []):
            winner = result.get('winner', 'Unknown')
            if isinstance(winner, str) and 'Hiders' in winner:
                # Hiders won
                for agent in self.sandbox.agents:
                    if agent.name not in hide_seek_wins:
                        hide_seek_wins[agent.name] = 0
            else:
                # Seeker won
                seeker = result.get('seeker', 'Unknown')
                hide_seek_wins[seeker] = hide_seek_wins.get(seeker, 0) + 1
        for agent_name, wins in sorted(hide_seek_wins.items(), key=lambda x: x[1], reverse=True):
            print(f"{agent_name}: {wins} wins")
        
        # Dodgeball results
        print("\nDODGEBALL RESULTS:")
        print("-" * 60)
        dodgeball_wins = {}
        for result in self.game_results.get('dodgeball', []):
            winner = result.get('winner', 'Unknown')
            dodgeball_wins[winner] = dodgeball_wins.get(winner, 0) + 1
        for agent_name, wins in sorted(dodgeball_wins.items(), key=lambda x: x[1], reverse=True):
            print(f"{agent_name}: {wins} wins")
        
        # Overall game performance
        print("\nOVERALL GAME PERFORMANCE:")
        print("-" * 60)
        overall_wins = {}
        for agent in self.sandbox.agents:
            overall_wins[agent.name] = (
                tag_wins.get(agent.name, 0) +
                hide_seek_wins.get(agent.name, 0) +
                dodgeball_wins.get(agent.name, 0)
            )
        for agent_name, wins in sorted(overall_wins.items(), key=lambda x: x[1], reverse=True):
            print(f"{agent_name}: {wins} total wins")
    
    def save_game_results(self):
        """Save game results to file."""
        results_file = TEST_DIR / 'game_results.json'
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.game_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Game results saved to {results_file}")

def main():
    """Main entry point."""
    try:
        print("=" * 60)
        print("AGENT DRONE COURSE TESTER & GAME RUNNER")
        print("=" * 60)
        print("\nThe doors of knowledge opens.")
        print("Testing agents through courses, then playing games...\n")
        
        # Step 1: Run course tests
        tester = CourseTester()
        tester.run_all_course_tests()
        
        # Step 2: Run games
        runner = GameRunner(tester)
        runner.run_games(games_per_type=2)
        
        print("\n" + "=" * 60)
        print("COMPLETE")
        print("=" * 60)
        print("\nAll course tests and games completed!")
        print(f"Results saved to: {TEST_DIR}")
    except (ValueError, IOError, OSError) as e:
        if 'closed file' in str(e).lower():
            # Handle closed file errors gracefully
            print(f"Warning: File I/O error occurred: {e}")
            sys.exit(1)
        else:
            raise
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
