# -*- coding: utf-8 -*-
# SWARM CONTROL - Command interface for isolated agents
# Summon agents. Check status. Clean interface.

import sys
from agent_swarm_isolated import SwarmOrchestrator, GameType


def main():
    """Command-line interface for swarm control."""
    print("\n" + "=" * 60)
    print("ELARA SWARM CONTROL")
    print("=" * 60)
    print("\n4 Isolated Agents:")
    print("  1. Chess")
    print("  2. Checkers")
    print("  3. Mahjong")
    print("  4. Go")
    print("\nCommands:")
    print("  start     - Start all agents learning")
    print("  stop      - Stop all agents")
    print("  status    - Quick status of all")
    print("  chess     - Summon chess agent")
    print("  checkers  - Summon checkers agent")
    print("  mahjong   - Summon mahjong agent")
    print("  go        - Summon go agent")
    print("  all       - Summon all agents")
    print("  exit      - Exit")
    print("=" * 60 + "\n")
    
    swarm = SwarmOrchestrator()
    swarm.start_swarm()
    
    while True:
        try:
            cmd = input("Swarm> ").strip().lower()
            
            if cmd == "exit" or cmd == "quit":
                swarm.stop_swarm()
                print("\n[Swarm] Stopped. Clean.\n")
                break
            
            elif cmd == "start":
                swarm.start_swarm()
                print("[Swarm] All agents started.\n")
            
            elif cmd == "stop":
                swarm.stop_swarm()
                print("[Swarm] All agents stopped.\n")
            
            elif cmd == "status":
                print(swarm.quick_status_all())
            
            elif cmd == "chess":
                print(swarm.summon_agent(GameType.CHESS))
            
            elif cmd == "checkers":
                print(swarm.summon_agent(GameType.CHECKERS))
            
            elif cmd == "mahjong":
                print(swarm.summon_agent(GameType.MAHJONG))
            
            elif cmd == "go":
                print(swarm.summon_agent(GameType.GO))
            
            elif cmd == "all":
                print(swarm.summon_all())
            
            else:
                print(f"[ERROR] Unknown command: {cmd}\n")
        
        except KeyboardInterrupt:
            print("\n[Swarm] Stopping...")
            swarm.stop_swarm()
            print("[Swarm] Stopped. Clean.\n")
            break
        except Exception as e:
            print(f"[ERROR] {e}\n")


if __name__ == '__main__':
    main()

