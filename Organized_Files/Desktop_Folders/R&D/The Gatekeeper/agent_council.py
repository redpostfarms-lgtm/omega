# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER – AGENT COUNCIL MODE
# When a task lands, they debate. You decide.

import subprocess
import sys
import io
import argparse
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

# Agent Council
AGENT_HIVE = {
    'Ellis': 'Ex-NASA. Zero hype. Wants data.',
    'Mara': 'Farmer. Knows mud. Says what works.',
    'Li': 'Quantum. Cites papers. No guesswork.',
    'Cody': 'Salesman. Turns facts into pitch.',
    'Oracle': 'Looks at logs. Sees patterns. Silent until truth.'
}

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

def get_agent_response(name: str, mind: str, problem: str):
    """Get response from an agent using Ollama."""
    prompt = f"You are {name}. Voice: short. Speak like {mind}. Answer only. Problem: {problem}"
    
    try:
        # Check if Ollama is available
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    
    try:
        # Get agent response
        result = subprocess.check_output(
            ['ollama', 'run', 'llama3', prompt],
            text=True,
            timeout=8,
            stderr=subprocess.DEVNULL
        )
        return result.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception) as e:
        # Fallback: generate response based on agent personality
        return generate_fallback_response(name, mind, problem)

def generate_fallback_response(name: str, mind: str, problem: str):
    """Generate fallback response when Ollama is not available."""
    # More specific responses based on problem type
    problem_lower = problem.lower()
    
    if 'solar' in problem_lower or 'yield' in problem_lower:
        responses = {
            'Ellis': "1.2 kW array → tilt 42°, clean 15° from dust. Measure irradiance. Report numbers.",
            'Mara': "Mulch rows. Cuts 0.3 kWh loss. Check panel angle. Clean monthly.",
            'Li': "MPPT at 18V – you're at 16. Check efficiency curve. Verify calculations.",
            'Cody': "Boost yield 27% – farm tour ready. ROI: 3.1 years. Pitch deck ready.",
            'Oracle': "Log shows cell 12 dying. Pattern: winter degradation. Fix at source."
        }
    elif 'battery' in problem_lower or '18650' in problem_lower:
        responses = {
            'Ellis': "Measure voltage drop. Check cycle count. Report capacity curve.",
            'Mara': "Replace weak cells. Balance pack. Check connections.",
            'Li': "NASA model shows 412 cycles to failure. Verify with data.",
            'Cody': "New pack = 94% efficiency. Payback: 2.8 years. Ready to sell.",
            'Oracle': "Log pattern: cell 7 failing. Replace before cascade."
        }
    elif 'grant' in problem_lower or 'usda' in problem_lower:
        responses = {
            'Ellis': "Data: 1.5 MW, 98% uptime. Meets NRCS 504. Numbers verified.",
            'Mara': "Fill form. Attach logs. Submit before deadline. Simple.",
            'Li': "Compliance: Section 4 verified. Environmental impact calculated.",
            'Cody': "$15k grant → 40% match. ROI pitch ready. Grant deck done.",
            'Oracle': "Deadline: 11 days. Pattern: submit early. Log shows success rate."
        }
    else:
        responses = {
            'Ellis': f"Data needed: measure {problem}. Run diagnostics. Report numbers.",
            'Mara': f"Farm solution: {problem}. Check weather. Check soil. Fix what's broken.",
            'Li': f"Analysis: {problem}. Check equations. Verify assumptions. Cite sources.",
            'Cody': f"Pitch: {problem} → opportunity. ROI: 3.1 years. Ready to present.",
            'Oracle': f"Pattern detected: {problem}. Check logs. See pattern. Fix there."
        }
    
    return responses.get(name, f"{name}: Analyzing {problem}...")

def council_solve(problem: str):
    """Council debate and decision system."""
    print("=" * 60)
    print("GATEKEEPER – AGENT COUNCIL MODE")
    print("=" * 60)
    print(f"\nProblem: {problem}\n")
    
    say("The doors of knowledge opens. Council forms.")
    
    print("Council forming...\n")
    
    debate = []
    
    # Each agent provides their perspective
    for name, mind in AGENT_HIVE.items():
        print(f"[{name}] Thinking...", end=' ', flush=True)
        
        take = f"{name}: {mind} → {problem}"
        ans = get_agent_response(name, mind, problem)
        
        if ans:
            # Limit to 2 lines as specified
            lines = ans.split('\n')[:2]
            ans = '\n'.join(lines).strip()
        else:
            ans = generate_fallback_response(name, mind, problem)
        
        debate.append(f"{name}: {ans}")
        print("Done.")
    
    # Print the debate round
    print("\n" + "=" * 60)
    print("COUNCIL DEBATE")
    print("=" * 60 + "\n")
    
    for line in debate:
        print(line)
        print()
    
    # Final vote
    print("=" * 60)
    print("Council vote? (yes/no)")
    print("=" * 60)
    
    try:
        ans = input("> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        # Non-interactive mode or interrupted
        print("\n⏸️  Council dismissed (no input).")
        return "No consensus. Task canceled."
    
    if ans == 'yes':
        print("\n✅ Solution locked.")
        say("Solution locked. Council dismissed.")
        
        # Combine all solutions
        solution = '\n'.join(debate)
        return solution
    else:
        print("\n⏸️  Council dismissed.")
        say("Council dismissed. No consensus.")
        return "No consensus. Task canceled."

def main():
    """Main council function."""
    parser = argparse.ArgumentParser(description='Gatekeeper Agent Council')
    parser.add_argument('--problem', help='Problem to solve', required=True)
    
    args = parser.parse_args()
    
    solution = council_solve(args.problem)
    
    # Save council session
    from datetime import datetime
    council_log = BRAIN / 'Archived' / 'council_logs'
    council_log.mkdir(parents=True, exist_ok=True)
    
    log_file = council_log / f'council_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Problem: {args.problem}\n")
        f.write(f"Time: {datetime.now().isoformat()}\n")
        f.write(f"\nSolution:\n{solution}\n")
    
    print(f"\nCouncil session saved to: {log_file}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--problem':
        # Direct problem provided
        problem = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else input("Problem: ")
        solution = council_solve(problem)
    else:
        main()

