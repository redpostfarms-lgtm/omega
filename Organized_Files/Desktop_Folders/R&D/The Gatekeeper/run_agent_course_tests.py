#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# SIMPLIFIED RUNNER - Avoids I/O issues
# Run course tests and games

import json
import math
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
TEST_DIR = GATE / 'agent_drone_tests'
TEST_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR = GATE / 'agent_drone_builds'

def load_agent_builds():
    """Load agent build specifications."""
    agents = {}
    for agent_name in ['Alpha', 'Beta', 'Gamma', 'Delta']:
        build_file = BUILD_DIR / f"{agent_name}_drone_build.json"
        if build_file.exists():
            with open(build_file, 'r', encoding='utf-8') as f:
                agents[agent_name] = json.load(f)
    return agents

def test_speed_course(agent_name: str, build: Dict) -> Dict:
    """Test speed course - 200m straight line."""
    perf = build.get('performance', {})
    max_speed = perf.get('max_speed_ms', 5.0)
    twr = perf.get('thrust_to_weight_ratio', 2.0)
    
    course_length = 200.0
    acceleration = (twr - 1) * 9.8
    if acceleration < 0:
        acceleration = 2.0
    
    time_to_max = max_speed / acceleration if acceleration > 0 else 5.0
    distance_to_max = 0.5 * acceleration * (time_to_max ** 2)
    
    if distance_to_max >= course_length:
        time_seconds = math.sqrt((2 * course_length) / acceleration)
    else:
        time_at_max = (course_length - distance_to_max) / max_speed
        time_seconds = time_to_max + time_at_max
    
    design_dir = build.get('design_direction', '')
    if 'speed' in design_dir.lower():
        time_seconds *= 0.95
    elif 'payload' in design_dir.lower():
        time_seconds *= 1.15
    
    baseline_time = 30.0
    score = (baseline_time / time_seconds) * 100 if time_seconds > 0 else 0
    score = min(score, 150.0)
    
    return {
        'agent_name': agent_name,
        'course_type': 'speed',
        'time_seconds': round(time_seconds, 2),
        'score': round(score, 1),
        'details': {
            'course_length_m': course_length,
            'max_speed_ms': max_speed,
            'acceleration_ms2': acceleration
        }
    }

def test_agility_course(agent_name: str, build: Dict) -> Dict:
    """Test agility course - 10-gate slalom."""
    perf = build.get('performance', {})
    agility_score = perf.get('agility_score', 0.7)
    max_speed = perf.get('max_speed_ms', 5.0)
    
    num_gates = 10
    gate_spacing = 50.0
    total_distance = num_gates * gate_spacing
    
    base_speed = max_speed * agility_score
    base_time = total_distance / base_speed
    
    turn_penalty = (1.0 - agility_score) * 2.0
    total_turn_time = turn_penalty * num_gates
    
    hit_probability = (1.0 - agility_score) * 0.3
    expected_hits = hit_probability * num_gates
    hit_penalty = expected_hits * 5.0
    
    time_seconds = base_time + total_turn_time + hit_penalty
    
    baseline_time = 60.0
    score = (baseline_time / time_seconds) * 100 if time_seconds > 0 else 0
    score = min(score, 150.0)
    
    return {
        'agent_name': agent_name,
        'course_type': 'agility',
        'time_seconds': round(time_seconds, 2),
        'score': round(score, 1),
        'details': {
            'num_gates': num_gates,
            'agility_score': agility_score,
            'expected_gate_hits': round(expected_hits, 1)
        }
    }

def test_endurance_course(agent_name: str, build: Dict) -> Dict:
    """Test endurance course - maximum flight time."""
    perf = build.get('performance', {})
    flight_time = perf.get('flight_time_minutes', 2.0)
    
    design_dir = build.get('design_direction', '')
    if 'endurance' in design_dir.lower():
        flight_time *= 1.1
    elif 'speed' in design_dir.lower():
        flight_time *= 0.85
    
    time_seconds = flight_time * 60.0
    
    baseline_time = 180.0
    score = (time_seconds / baseline_time) * 100 if baseline_time > 0 else 0
    score = min(score, 200.0)
    
    return {
        'agent_name': agent_name,
        'course_type': 'endurance',
        'time_seconds': round(time_seconds, 0),
        'score': round(score, 1),
        'details': {
            'flight_time_minutes': round(flight_time, 2),
            'battery': build.get('components', {}).get('battery', '')
        }
    }

def run_all_course_tests():
    """Run all agents through all courses."""
    print("=" * 60)
    print("DRONE COURSE TESTING")
    print("Speed, Agility, Endurance")
    print("=" * 60)
    
    agents = load_agent_builds()
    results = {}
    
    for agent_name, build in agents.items():
        print(f"\n{'='*60}")
        print(f"TESTING {agent_name}")
        print(f"{'='*60}")
        
        # Speed
        print(f"\n[{agent_name}] SPEED COURSE TEST")
        speed_result = test_speed_course(agent_name, build)
        print(f"Time: {speed_result['time_seconds']:.2f}s | Score: {speed_result['score']:.1f} pts")
        
        # Agility
        print(f"\n[{agent_name}] AGILITY COURSE TEST")
        agility_result = test_agility_course(agent_name, build)
        print(f"Time: {agility_result['time_seconds']:.2f}s | Score: {agility_result['score']:.1f} pts")
        
        # Endurance
        print(f"\n[{agent_name}] ENDURANCE COURSE TEST")
        endurance_result = test_endurance_course(agent_name, build)
        minutes = endurance_result['time_seconds'] / 60.0
        print(f"Time: {minutes:.2f} min | Score: {endurance_result['score']:.1f} pts")
        
        results[agent_name] = {
            'speed': speed_result,
            'agility': agility_result,
            'endurance': endurance_result
        }
    
    # Summary
    print("\n" + "=" * 60)
    print("COURSE TEST SUMMARY")
    print("=" * 60)
    
    print("\nSPEED COURSE (200m):")
    speed_sorted = sorted(results.items(), key=lambda x: x[1]['speed']['time_seconds'])
    for i, (name, r) in enumerate(speed_sorted, 1):
        print(f"{i}. {name}: {r['speed']['time_seconds']:.2f}s ({r['speed']['score']:.1f} pts)")
    
    print("\nAGILITY COURSE (10-gate slalom):")
    agility_sorted = sorted(results.items(), key=lambda x: x[1]['agility']['time_seconds'])
    for i, (name, r) in enumerate(agility_sorted, 1):
        print(f"{i}. {name}: {r['agility']['time_seconds']:.2f}s ({r['agility']['score']:.1f} pts)")
    
    print("\nENDURANCE COURSE (max flight time):")
    endurance_sorted = sorted(results.items(), key=lambda x: x[1]['endurance']['time_seconds'], reverse=True)
    for i, (name, r) in enumerate(endurance_sorted, 1):
        minutes = r['endurance']['time_seconds'] / 60.0
        print(f"{i}. {name}: {minutes:.2f} min ({r['endurance']['score']:.1f} pts)")
    
    print("\nOVERALL SCORES:")
    overall = {}
    for name, r in results.items():
        total = r['speed']['score'] + r['agility']['score'] + r['endurance']['score']
        overall[name] = total
    for i, (name, score) in enumerate(sorted(overall.items(), key=lambda x: x[1], reverse=True), 1):
        print(f"{i}. {name}: {score:.1f} total points")
    
    # Save
    results_file = TEST_DIR / 'course_test_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Results saved to {results_file}")
    
    return results

def run_games_after_tests():
    """Run 2 games of each type after course tests."""
    print("\n" + "=" * 60)
    print("GAME SESSION - AFTER COURSE TESTS")
    print("2 games of each type")
    print("=" * 60)
    
    # Import here to avoid I/O issues during import
    try:
        from drone_game_sandbox import GameSandbox
        sandbox = GameSandbox(arena_size=(50.0, 50.0, 20.0))
        sandbox.create_agents(count=4, load_custom_drones=True)
        
        game_results = {}
        
        # Tag - 2 games
        print("\n" + "=" * 60)
        print("TAG GAME - 2 GAMES")
        print("=" * 60)
        tag_results = []
        for i in range(2):
            print(f"\n--- Tag Game {i+1}/2 ---")
            result = sandbox._play_single_tag_game(duration=60.0)
            tag_results.append(result)
            time.sleep(0.2)
        game_results['tag'] = tag_results
        sandbox._print_tag_summary(tag_results)
        
        # Hide and Seek - 2 games
        print("\n" + "=" * 60)
        print("HIDE AND SEEK - 2 GAMES")
        print("=" * 60)
        hide_seek_results = []
        for i in range(2):
            print(f"\n--- Hide and Seek Game {i+1}/2 ---")
            result = sandbox._play_single_hide_and_seek_game(hiding_time=30.0, seeking_time=120.0)
            hide_seek_results.append(result)
            time.sleep(0.2)
        game_results['hide_and_seek'] = hide_seek_results
        sandbox._print_hide_and_seek_summary(hide_seek_results)
        
        # Dodgeball - 2 games
        print("\n" + "=" * 60)
        print("DODGEBALL - 2 GAMES")
        print("=" * 60)
        dodgeball_results = []
        for i in range(2):
            print(f"\n--- Dodgeball Game {i+1}/2 ---")
            result = sandbox._play_single_dodgeball_game(duration=120.0)
            dodgeball_results.append(result)
            time.sleep(0.2)
        game_results['dodgeball'] = dodgeball_results
        sandbox._print_dodgeball_summary(dodgeball_results)
        
        # Save game results
        game_file = TEST_DIR / 'game_results.json'
        with open(game_file, 'w', encoding='utf-8') as f:
            json.dump(game_results, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Game results saved to {game_file}")
        
    except Exception as e:
        print(f"[WARNING] Game execution error: {e}")
        print("[INFO] Course tests completed successfully")

def main():
    """Main entry point."""
    print("=" * 60)
    print("AGENT DRONE COURSE TESTER & GAME RUNNER")
    print("=" * 60)
    print("\nThe doors of knowledge opens.")
    print("Testing agents through courses, then playing games...\n")
    
    # Step 1: Run course tests
    course_results = run_all_course_tests()
    
    # Step 2: Run games
    run_games_after_tests()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nAll course tests and games completed!")
    print(f"Results saved to: {TEST_DIR}")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
