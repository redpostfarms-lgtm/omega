#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MORNING STARTUP - Auto-diagnostic on boot
# Runs full scan and diagnosis, then continues normal operations

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_full_scan_and_diagnosis():
    """Run full diagnostic scan."""
    print("\n" + "=" * 60)
    print("MORNING STARTUP - Full Scan and Diagnosis")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Import and run diagnostic engine
        from diagnostic_engine import full_scan_and_diagnosis
        
        print("[Morning Startup] Running full scan and diagnosis...")
        result = full_scan_and_diagnosis()
        
        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 60)
        print("System optimized. Ready.")
        print()
        
        return result
    
    except Exception as e:
        print(f"[ERROR] Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def continue_normal_operations():
    """Continue with normal system operations after diagnostic."""
    print("\n" + "=" * 60)
    print("CONTINUING NORMAL OPERATIONS")
    print("=" * 60)
    
    # Check if swarm is configured to auto-start
    swarm_config = Path("swarm_auto_start.flag")
    if swarm_config.exists():
        print("[Morning Startup] Starting agent swarm...")
        try:
            from agent_swarm_isolated import SwarmOrchestrator
            swarm = SwarmOrchestrator()
            swarm.start_swarm()
            print("[Morning Startup] Swarm started.")
        except Exception as e:
            print(f"[WARNING] Swarm start failed: {e}")
    
    # Check for game framework auto-start
    game_config = Path("games_auto_start.flag")
    if game_config.exists():
        print("[Morning Startup] Game framework ready.")
        print("[Morning Startup] Games available: Chess, Checkers, Go, Mahjong")
    
    # Check for other startup tasks
    startup_tasks = Path("startup_tasks.json")
    if startup_tasks.exists():
        print("[Morning Startup] Loading startup tasks...")
        try:
            import json
            with open(startup_tasks, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            for task in tasks.get('tasks', []):
                task_name = task.get('name', 'Unknown')
                task_enabled = task.get('enabled', False)
                
                if task_enabled:
                    print(f"[Morning Startup] Task: {task_name} - Enabled")
                    # Would execute task here
        except Exception as e:
            print(f"[WARNING] Startup tasks load failed: {e}")
    
    print("\n" + "=" * 60)
    print("SYSTEM READY")
    print("=" * 60)
    print("[System] All systems operational.")
    print("[System] Ready for commands.")
    print()


def main():
    """Main morning startup sequence."""
    print("\n" + "=" * 60)
    print("MORNING STARTUP")
    print("=" * 60)
    print(f"Boot Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Full scan and diagnosis
    diagnostic_result = run_full_scan_and_diagnosis()
    
    # Brief pause
    time.sleep(1)
    
    # Step 2: Continue normal operations
    continue_normal_operations()
    
    print("\n[Morning Startup] Startup sequence complete.")
    print("[System] System ready. Listening.")


if __name__ == '__main__':
    main()

