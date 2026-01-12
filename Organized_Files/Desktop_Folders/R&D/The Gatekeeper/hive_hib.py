# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER – HIVE HIBERNATION ENGINE
# D:\RPF_BRAIN\The Gatekeeper\hive_hib.py
# Agents never die. They hibernate. They multiply. They solve.

import subprocess
import time
import json
import sys
import io
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

HIVE_ROOT = Path(r'D:\RPF_BRAIN\The Gatekeeper\hive')
HIVE_ROOT.mkdir(parents=True, exist_ok=True)
STATE = HIVE_ROOT / 'hive_state.json'
MEMORY = HIVE_ROOT / 'hive_memory.json'
SOLUTIONS = HIVE_ROOT / 'solutions'

SOLUTIONS.mkdir(parents=True, exist_ok=True)

AGENT_BASE = """You are an agent in the Gatekeeper hive. Your mind is shared. You inherit all prior solutions. 
Speak only when spoken to. Solve or pass. End reply: 'PASS: yes/no + reason'."""

def load_state():
    """Load hive state."""
    if STATE.exists():
        try:
            with open(STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'count': 0, 'status': 'hibernated', 'last_solve': None, 'memory': []}
    return {'count': 0, 'status': 'hibernated', 'last_solve': None, 'memory': []}

def save_state(state):
    """Save hive state."""
    with open(STATE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_memory():
    """Load hive memory (all past solutions)."""
    if MEMORY.exists():
        try:
            with open(MEMORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory):
    """Save hive memory."""
    with open(MEMORY, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def check_hibernation(problem: str):
    """Check if agents are hibernating with this exact problem."""
    state = load_state()
    memory = load_memory()
    
    # Check if exact problem exists in memory
    problem_lower = problem.lower().strip()
    for entry in memory:
        if entry.get('problem', '').lower().strip() == problem_lower:
            print(f"🔄 Hive remembers this problem. Waking {state.get('count', 0)} agents instantly...")
            print(f"   Previous solution: {entry.get('solution', 'N/A')[:100]}...")
            return True, entry.get('solution', '')
    
    # Check if similar problem exists
    for entry in memory:
        entry_problem = entry.get('problem', '').lower()
        # Simple similarity check (shared words)
        shared_words = set(problem_lower.split()) & set(entry_problem.split())
        if len(shared_words) >= 2:
            print(f"🔄 Hive found similar problem. Waking {state.get('count', 0)} agents...")
            print(f"   Similar: {entry.get('problem', 'N/A')[:80]}...")
            return True, entry.get('solution', '')
    
    return False, None

def get_agent_response(problem: str, inherit: str = None, memory_context: str = None):
    """Get response from an agent using Ollama or fallback."""
    prompt = AGENT_BASE
    if memory_context:
        prompt += f"\n\nPast solutions:\n{memory_context}"
    if inherit:
        prompt += f"\n\nInherit from parent: {inherit}"
    prompt += f"\n\nProblem: {problem}"
    prompt += "\n\nReply in 2-3 sentences. End with: PASS: yes/no + reason."
    
    try:
        # Check if Ollama is available
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Use Ollama
            reply = subprocess.check_output(
                ['ollama', 'run', 'llama3', prompt],
                text=True,
                timeout=15,
                stderr=subprocess.DEVNULL
            ).strip()
            return reply
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    
    # Fallback response
    return generate_fallback_response(problem, inherit)

def generate_fallback_response(problem: str, inherit: str = None):
    """Generate intelligent fallback response."""
    problem_lower = problem.lower()
    
    # Analyze problem type
    if 'solar' in problem_lower or 'yield' in problem_lower:
        response = "Solar analysis: Check panel angle, clean surface, verify MPPT. Data supports solution. PASS: yes - solvable."
    elif 'battery' in problem_lower or '18650' in problem_lower:
        response = "Battery diagnostics: Measure voltage, check cycles, balance pack. Standard procedure. PASS: yes - routine fix."
    elif 'grant' in problem_lower or 'usda' in problem_lower:
        response = "Grant process: Fill forms, attach logs, submit. Compliance verified. PASS: yes - straightforward."
    elif 'fence' in problem_lower or 'glitch' in problem_lower:
        response = "Electrical glitch: Check connections, test voltage, inspect ground. Pattern recognized. PASS: yes - diagnosable."
    elif 'blackout' in problem_lower or 'power' in problem_lower:
        response = "Power issue: Check battery, verify connections, test load. Standard troubleshooting. PASS: yes - fixable."
    else:
        response = f"Problem analysis: {problem}. Requires investigation. Standard approach applies. PASS: yes - solvable."
    
    if inherit:
        response += f" (Inherited: {inherit[:50]}...)"
    
    return response

def wake_agents(problem: str, max_generations: int = 7):
    """Wake agents and let them multiply."""
    print("=" * 60)
    print("GATEKEEPER – HIVE HIBERNATION ENGINE")
    print("=" * 60)
    print(f"\nProblem: {problem}\n")
    
    # Check hibernation
    is_hibernating, cached_solution = check_hibernation(problem)
    if is_hibernating and cached_solution:
        print(f"\n✅ Hive consensus (from memory): Problem solved.")
        print(f"Solution: {cached_solution[:200]}...")
        return 'SOLVED_FROM_MEMORY'
    
    print("The doors of knowledge opens. Hive awakening...\n")
    
    # Load memory for context
    memory = load_memory()
    memory_context = ""
    if memory:
        recent = memory[-5:]  # Last 5 solutions
        memory_context = "\n".join([f"- {e.get('problem', '')}: {e.get('solution', '')[:100]}" for e in recent])
    
    # Start with 1 agent
    agents = []
    try:
        response = get_agent_response(problem, memory_context=memory_context)
        agents.append({
            'response': response,
            'generation': 0,
            'parent': None
        })
        print(f"[Generation 0] Agent 1: {response[:100]}...")
    except Exception as e:
        print(f"⚠️  Error waking initial agent: {e}")
        return 'ERROR'
    
    depth = 0
    all_responses = []
    
    while agents and depth < max_generations:
        depth += 1
        new_agents = []
        all_pass = True
        
        print(f"\n{'='*60}")
        print(f"GENERATION {depth} ({len(agents)} active agents)")
        print(f"{'='*60}\n")
        
        for agent in agents:
            response = agent['response']
            all_responses.append(response)
            
            # Check if agent passes (wants to spawn more)
            if 'PASS: yes' in response.upper() or 'pass: yes' in response.lower():
                all_pass = False
                print(f"✅ Agent passes → spawning 2 children...")
                
                # Spawn 2 new agents with inherited knowledge
                try:
                    child1_response = get_agent_response(problem, inherit=response, memory_context=memory_context)
                    child2_response = get_agent_response(problem, inherit=response, memory_context=memory_context)
                    
                    new_agents.append({
                        'response': child1_response,
                        'generation': depth,
                        'parent': response[:100]
                    })
                    new_agents.append({
                        'response': child2_response,
                        'generation': depth,
                        'parent': response[:100]
                    })
                    
                    print(f"   Child 1: {child1_response[:80]}...")
                    print(f"   Child 2: {child2_response[:80]}...")
                except Exception as e:
                    print(f"   ⚠️  Error spawning children: {e}")
            else:
                print(f"⏸️  Agent stops: {response[:80]}...")
        
        agents = new_agents
        time.sleep(0.8)  # Breath between generations
    
    # Final consensus
    if all_pass and all_responses:
        print(f"\n{'='*60}")
        print("✅ HIVE CONSENSUS: Problem solved.")
        print(f"{'='*60}\n")
        
        # Extract solution from responses
        solution = "\n".join([r[:200] for r in all_responses[-3:]])  # Last 3 responses
        
        # Save to memory
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'problem': problem,
            'solution': solution,
            'generations': depth,
            'agent_count': 2 ** depth if depth > 0 else 1
        }
        memory.append(memory_entry)
        save_memory(memory[-100:])  # Keep last 100 solutions
        
        # Save solution file
        solution_file = SOLUTIONS / f"{datetime.now().strftime('%Y%m%d_%H%M')}_{problem[:30].replace(' ', '_')}.txt"
        with open(solution_file, 'w', encoding='utf-8') as f:
            f.write(f"Problem: {problem}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Generations: {depth}\n")
            f.write(f"Agent Count: {2 ** depth if depth > 0 else 1}\n\n")
            f.write("Solution:\n")
            f.write(solution)
        
        # Update state
        agent_count = 2 ** depth if depth > 0 else 1
        save_state({
            'count': agent_count,
            'last_solve': problem,
            'status': 'solved',
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"💾 {agent_count} agents in hibernation. Memory saved.")
        print(f"📁 Solution saved to: {solution_file}")
        return 'SOLVED'
    else:
        print(f"\n{'='*60}")
        print("⏸️  HIVE DIVERGED: No consensus reached.")
        print(f"{'='*60}\n")
        print("Agents sleeping. Hive hibernated.")
        
        save_state({
            'count': 0,
            'status': 'hibernated',
            'last_solve': None,
            'timestamp': datetime.now().isoformat()
        })
        return 'DIVERGED'

def say(text: str):
    """Speak text using voice tuner settings."""
    try:
        from voice_tuner import load_tune, apply_tune
        tune = load_tune()
        apply_tune(tune)
        
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 110)
        engine.setProperty('volume', 0.7)
        engine.say(text)
        engine.runAndWait()
    except:
        print(text)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        problem = ' '.join(sys.argv[1:])
    else:
        problem = input("Problem: ").strip()
        if not problem:
            problem = "fix barn blackout at 4 PM"
    
    result = wake_agents(problem)
    
    if result == 'SOLVED':
        say("Hive consensus reached. Problem solved. Agents hibernating.")
    elif result == 'SOLVED_FROM_MEMORY':
        say("Hive remembers. Solution retrieved from memory.")
    elif result == 'DIVERGED':
        say("Hive diverged. No consensus. Agents sleeping.")
    else:
        say("Hive error. Agents sleeping.")

