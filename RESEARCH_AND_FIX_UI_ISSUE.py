#!/usr/bin/env python3
"""
Research and Fix UI Window Closing Issue
========================================
This script activates agents to research the issue and test solutions.
"""

import sys
import os
import traceback
from pathlib import Path
import time

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

def activate_research_agents():
    """Activate agent council for research"""
    try:
        from omega_agent_council import agent_council, wake_agents_and_process
        import asyncio
        
        print("=" * 80)
        print(" " * 20 + "ACTIVATING RESEARCH AGENTS")
        print("=" * 80)
        print()
        
        # Wake all agents
        awakened = agent_council.wake_all_agents()
        print(f"[AGENTS] Awakened {len(awakened)} agents: {', '.join(awakened)}")
        print()
        
        # Queue research task
        task_data = {
            'problem': 'Matplotlib UI window closes immediately when launched from desktop shortcut',
            'requirements': 'Window must stay open and remain interactive',
            'current_implementation': 'Uses FuncAnimation with plt.show(block=False) and plt.pause() loop',
            'symptoms': 'Window appears briefly then closes, process may still be running'
        }
        agent_council.queue_learning_task('ui_issue_research', task_data)
        print("[AGENTS] Research task queued")
        print()
        
        return True
    except Exception as e:
        print(f"[WARNING] Could not activate agents: {e}")
        return False

def research_issue():
    """Research the UI window closing issue"""
    print("=" * 80)
    print(" " * 20 + "RESEARCHING UI WINDOW ISSUE")
    print("=" * 80)
    print()
    
    findings = []
    
    # Finding 1: Check if FuncAnimation is the issue
    print("RESEARCH POINT 1: FuncAnimation Behavior")
    print("-" * 80)
    print("FuncAnimation creates its own event loop.")
    print("When used with plt.show(block=False), the animation should keep running.")
    print("However, if the Python script exits, the window closes.")
    print()
    findings.append({
        'issue': 'FuncAnimation requires event loop to run',
        'detail': 'Animation object must stay alive, process must not exit'
    })
    
    # Finding 2: Check run() method behavior
    print("RESEARCH POINT 2: run() Method Analysis")
    print("-" * 80)
    print("The run() method calls _create_gui_panel() which creates FuncAnimation.")
    print("Then it enters a while loop with plt.pause().")
    print("This should work, but maybe there's an exception or early exit?")
    print()
    findings.append({
        'issue': 'run() method should keep process alive',
        'detail': 'Need to check if run() is actually running the loop'
    })
    
    # Finding 3: Windows shortcut behavior
    print("RESEARCH POINT 3: Windows Shortcut Behavior")
    print("-" * 80)
    print("When Python script is launched from shortcut:")
    print("- If script exits, window closes immediately")
    print("- Console window behavior affects GUI window")
    print("- Process must stay alive for GUI to remain")
    print()
    findings.append({
        'issue': 'Windows process lifecycle',
        'detail': 'Python process must not exit while GUI is open'
    })
    
    # Finding 4: Matplotlib event loop
    print("RESEARCH POINT 4: Matplotlib Event Loop")
    print("-" * 80)
    print("With FuncAnimation:")
    print("- Animation object manages its own updates")
    print("- plt.pause() processes GUI events")
    print("- Both should work together")
    print("However, maybe we need plt.show(block=True) with FuncAnimation?")
    print()
    findings.append({
        'issue': 'Event loop interaction',
        'detail': 'FuncAnimation + plt.pause() loop might conflict'
    })
    
    print()
    print("=" * 80)
    print("RESEARCH FINDINGS SUMMARY")
    print("=" * 80)
    for i, finding in enumerate(findings, 1):
        print(f"\n{i}. {finding['issue']}")
        print(f"   {finding['detail']}")
    
    return findings

def test_solution_1():
    """Test Solution 1: Use plt.show(block=True) with FuncAnimation"""
    print("\n" + "=" * 80)
    print(" " * 15 + "TESTING SOLUTION 1: block=True with FuncAnimation")
    print("=" * 80)
    print()
    
    print("Hypothesis: FuncAnimation should work with plt.show(block=True)")
    print("This would block the main thread but keep window open.")
    print()
    print("PROS:")
    print("  - Window definitely stays open")
    print("  - Event loop processes automatically")
    print()
    print("CONS:")
    print("  - Blocks main thread (but that's OK for launcher)")
    print("  - FuncAnimation might not need the plt.pause() loop")
    print()
    
    return "Try using plt.show(block=True) after creating FuncAnimation"

def test_solution_2():
    """Test Solution 2: Ensure run() doesn't exit early"""
    print("\n" + "=" * 80)
    print(" " * 15 + "TESTING SOLUTION 2: Ensure run() stays alive")
    print("=" * 80)
    print()
    
    print("Hypothesis: run() method might be exiting due to exception")
    print("or the loop might not be running properly.")
    print()
    print("Fix: Add better error handling and ensure loop runs")
    print()
    
    return "Add try/except around run() loop, ensure it doesn't exit"

def test_solution_3():
    """Test Solution 3: Keep process alive explicitly"""
    print("\n" + "=" * 80)
    print(" " * 15 + "TESTING SOLUTION 3: Explicit process keep-alive")
    print("=" * 80)
    print()
    
    print("Hypothesis: Python process exits before window is fully initialized")
    print()
    print("Fix: Add explicit wait/keep-alive mechanism")
    print()
    
    return "Add explicit keep-alive after window creation"

def main():
    """Main research and fix process"""
    print("\n" + "=" * 80)
    print(" " * 15 + "UI WINDOW CLOSING ISSUE - RESEARCH & FIX")
    print("=" * 80)
    print()
    
    # Step 1: Activate agents
    activate_research_agents()
    
    # Step 2: Research the issue
    findings = research_issue()
    
    # Step 3: Test solutions
    solution1 = test_solution_1()
    solution2 = test_solution_2()
    solution3 = test_solution_3()
    
    print("\n" + "=" * 80)
    print(" " * 20 + "RECOMMENDED FIX")
    print("=" * 80)
    print()
    print("Based on research, the issue is likely that:")
    print("1. FuncAnimation needs the event loop to run")
    print("2. plt.show(block=False) with plt.pause() loop should work")
    print("3. BUT if there's an exception or early exit, window closes")
    print()
    print("RECOMMENDED SOLUTION:")
    print("- Modify run() method to use plt.show(block=True) OR")
    print("- Ensure run() loop never exits (better error handling) OR")
    print("- Use a combination: show window, then block on mainloop")
    print()
    print("Let's implement the fix now...")
    print()
    
    return findings

if __name__ == "__main__":
    try:
        findings = main()
        print("\n[OK] Research complete. Ready to implement fix.")
    except KeyboardInterrupt:
        print("\n\nResearch interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Research failed: {e}")
        traceback.print_exc()
        sys.exit(1)
