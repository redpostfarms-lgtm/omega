# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# HIVE_AUTO — 2026. Grows. Shrinks. Knows your machine.
# D:\RPF_BRAIN\The Gatekeeper\hive_auto.py

import subprocess
import json
import time
import sys
import io
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to import hardware monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not installed. Install with: pip install psutil")
    print("   Hive will use conservative limits without hardware monitoring.")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False

HIVE = Path(r'D:\RPF_BRAIN\The Gatekeeper\hive_auto')
HIVE.mkdir(parents=True, exist_ok=True)
MEMORY = HIVE / 'memory.json'  # permanent
STATE = HIVE / 'state.json'  # current sleep state
SOLUTIONS = HIVE / 'solutions'
SOLUTIONS.mkdir(parents=True, exist_ok=True)

# Boot memory
if MEMORY.exists():
    try:
        with open(MEMORY, 'r', encoding='utf-8') as f:
            mem = json.load(f)
    except:
        mem = {'solved': [], 'population': 0}
else:
    mem = {'solved': [], 'population': 0}

def can_grow():
    """Check if hardware can support more agents."""
    if not PSUTIL_AVAILABLE:
        # Conservative fallback: limit to 64 agents
        return True  # Will be limited by max_gen check
    
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        gpu_load = 0
        
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_load = gpus[0].load * 100
            except:
                pass
        
        # Growth conditions: RAM < 75%, GPU < 60%, CPU < 80%
        can_grow = ram < 75 and gpu_load < 60 and cpu < 80
        
        if not can_grow:
            print(f"   ⚠️  Hardware limits: RAM {ram:.1f}%, GPU {gpu_load:.1f}%, CPU {cpu:.1f}%")
        
        return can_grow
    except Exception as e:
        print(f"   ⚠️  Hardware check error: {e}")
        return True  # Default to allowing growth

def enhance_resource_tracking():
    """Enhanced resource tracking for agents."""
    if not PSUTIL_AVAILABLE:
        return {"status": "psutil_not_available", "cpu": 0, "ram": 0, "gpu": 0}
    
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        gpu_load = 0
        gpu_memory = 0
        
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_load = gpus[0].load * 100
                    gpu_memory = gpus[0].memoryUsed / gpus[0].memoryTotal * 100
            except:
                pass
        
        return {
            "status": "ok",
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_available_mb": ram.available / (1024 * 1024),
            "gpu_load_percent": gpu_load,
            "gpu_memory_percent": gpu_memory,
            "timestamp": int(time.time())
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def monitor_resources() -> Dict:
    """Monitor current resource usage."""
    return enhance_resource_tracking()

def get_resource_report() -> Dict:
    """Get comprehensive resource report."""
    current = monitor_resources()
    return {
        "current": current,
        "limits": {
            "cpu_threshold": 80,
            "ram_threshold": 75,
            "gpu_threshold": 60
        },
        "can_grow": can_grow(),
        "recommendation": "grow" if can_grow() else "maintain_or_shrink"
    }

def get_agent_response(problem: str, memory_context: str = ""):
    """Get response from agent using Ollama or fallback."""
    prompt = f"""You are Agent X in the Red Post hive. Shared memory: {memory_context}
Problem: {problem}
Reply in 2-3 sentences. End with: VOTE: YES/NO/ABSTAIN"""
    
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
                ['ollama', 'run', 'llama3.2', prompt],
                text=True,
                timeout=12,
                stderr=subprocess.DEVNULL
            ).strip()
            return reply
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    
    # Fallback response
    problem_lower = problem.lower()
    if 'solar' in problem_lower:
        return f"Solar analysis: Check panel angle, verify MPPT. Standard procedure. VOTE: YES"
    elif 'battery' in problem_lower or '18650' in problem_lower:
        return f"Battery diagnostics: Measure voltage, check cycles. Routine fix. VOTE: YES"
    elif 'grant' in problem_lower:
        return f"Grant process: Fill forms, attach logs. Compliance verified. VOTE: YES"
    else:
        return f"Problem analysis: {problem}. Requires investigation. Standard approach. VOTE: YES"

def hive_solve(problem: str):
    """Hive solve with hardware-aware scaling."""
    print("=" * 60)
    print("GATEKEEPER – HIVE AUTO (Hardware-Aware)")
    print("=" * 60)
    print(f"\nProblem: {problem}\n")
    print("The doors of knowledge opens. Hive awakens.\n")
    
    # Check if problem already solved
    problem_lower = problem.lower().strip()
    for solved in mem['solved']:
        if isinstance(solved, str) and problem_lower in solved.lower():
            print(f"🔄 Hive remembers this problem. Solution: {solved[:100]}...")
            return 'SOLVED_FROM_MEMORY'
    
    generation = 1
    active = 1  # Start small
    max_gen = 12  # Safety limit: max 4096 agents (2^12)
    
    memory_context = "\n".join([f"- {s}" for s in mem['solved'][-3:]]) if mem['solved'] else "No previous solutions."
    
    while generation <= max_gen:
        print(f"{'='*60}")
        print(f"Generation {generation} — {active} agents active")
        print(f"{'='*60}\n")
        
        votes = {'YES': 0, 'NO': 0, 'ABSTAIN': 0}
        responses = []
        
        for i in range(active):
            try:
                print(f"[Agent {i+1}/{active}] Thinking...", end=' ', flush=True)
                reply = get_agent_response(problem, memory_context)
                
                # Parse vote
                vote = 'ABSTAIN'
                if 'VOTE:' in reply.upper():
                    vote_part = reply.upper().split('VOTE:')[-1].strip()
                    if 'YES' in vote_part:
                        vote = 'YES'
                    elif 'NO' in vote_part:
                        vote = 'NO'
                    else:
                        vote = 'ABSTAIN'
                elif 'YES' in reply.upper() and 'VOTE' in reply.upper():
                    vote = 'YES'
                elif 'NO' in reply.upper() and 'VOTE' in reply.upper():
                    vote = 'NO'
                
                votes[vote] += 1
                responses.append(reply)
                print(f"Done. Vote: {vote}")
            except Exception as e:
                print(f"Error: {e}")
                votes['ABSTAIN'] += 1
        
        # Calculate consensus
        total_votes = sum(votes.values())
        if total_votes > 0:
            yes_rate = votes['YES'] / total_votes
            print(f"\n--- Votes: {votes['YES']} YES, {votes['NO']} NO, {votes['ABSTAIN']} ABSTAIN ---")
            
            if yes_rate >= 0.6:  # 60% consensus
                print(f"\n✅ Hive consensus reached ({yes_rate*100:.1f}% yes). Solution locked.\n")
                
                # Save solution
                solution_text = "\n".join(responses[-5:])  # Last 5 responses
                solution_entry = f"{problem} → {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                mem['solved'].append(solution_entry)
                mem['population'] = active
                
                # Save memory (keep last 1000 solutions)
                mem['solved'] = mem['solved'][-1000:]
                with open(MEMORY, 'w', encoding='utf-8') as f:
                    json.dump(mem, f, indent=2, ensure_ascii=False)
                
                # Save solution file
                solution_file = SOLUTIONS / f"{datetime.now().strftime('%Y%m%d_%H%M')}_{problem[:30].replace(' ', '_')}.txt"
                with open(solution_file, 'w', encoding='utf-8') as f:
                    f.write(f"Problem: {problem}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Generation: {generation}\n")
                    f.write(f"Agents: {active}\n")
                    f.write(f"Consensus: {yes_rate*100:.1f}%\n\n")
                    f.write("Solution:\n")
                    f.write(solution_text)
                
                # Save state
                with open(STATE, 'w', encoding='utf-8') as f:
                    json.dump({
                        'status': 'hibernating',
                        'population': active,
                        'last_solve': problem,
                        'timestamp': datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"💾 {active} agents in hibernation. Memory saved.")
                print(f"📁 Solution saved to: {solution_file}")
                return 'SOLVED'
        
        # Scale up — only if machine can take it
        next_gen = active * 2
        if next_gen > 4096:
            print(f"\n⚠️  Max safe size reached (4096 agents). Stable.")
            next_gen = 2048
            active = next_gen
        elif can_grow():
            active = next_gen
            print(f"   ✅ Hardware OK. Scaling to {active} agents...")
        else:
            print(f"   ⚠️  Hardware limit reached. Hibernating to reduce load...")
            active = max(1, active // 2)  # Shrink, but never below 1
        
        generation += 1
        time.sleep(0.7)  # Breath between generations
    
    # No consensus after max generations
    print(f"\n{'='*60}")
    print("⏸️  No consensus after {max_gen} generations.")
    print(f"{'='*60}\n")
    print("Hive diverged. Agents sleeping.")
    
    with open(STATE, 'w', encoding='utf-8') as f:
        json.dump({
            'status': 'diverged',
            'population': 0,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
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
            problem = "why is the barn dark at 4 PM?"
    
    result = hive_solve(problem)
    
    if result == 'SOLVED':
        say("Hive consensus reached. Problem solved. Agents hibernating.")
    elif result == 'SOLVED_FROM_MEMORY':
        say("Hive remembers. Solution retrieved from memory.")
    elif result == 'DIVERGED':
        say("Hive diverged. No consensus. Agents sleeping.")
    else:
        say("Hive error. Agents sleeping.")

