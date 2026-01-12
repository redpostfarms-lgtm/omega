# Quick test of swarm
from agent_swarm_isolated import SwarmOrchestrator, GameType
import time

print("\n[Test] Starting swarm...")
swarm = SwarmOrchestrator()
swarm.start_swarm()

print("\n[Test] Letting agents learn for 15 seconds...")
time.sleep(15)

print("\n[Test] Summoning Go agent:")
print(swarm.summon_agent(GameType.GO))

print("\n[Test] Quick status:")
print(swarm.quick_status_all())

print("\n[Test] Stopping swarm...")
swarm.stop_swarm()

print("\n[Test] Done.")

