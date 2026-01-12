# -*- coding: utf-8 -*-
# ELARA DIAGNOSTIC WAKE WORD HANDLER
# Listens for "full scan and diagnosis" (case insensitive)
# Executes diagnostic_engine.py silently

import subprocess
import sys
import time
from pathlib import Path


def check_wake_word(text: str) -> bool:
    """
    Check if text contains wake word.
    
    Args:
        text: Input text to check
        
    Returns:
        True if wake word detected
    """
    wake_phrases = [
        "full scan and diagnosis",
        "full scan",
        "diagnosis",
    ]
    
    text_lower = text.lower().strip()
    
    # Case insensitive match
    for phrase in wake_phrases:
        if phrase in text_lower:
            return True
    
    return False


def execute_diagnostic():
    """Execute diagnostic_engine.py silently."""
    diagnostic_script = Path(__file__).parent / "diagnostic_engine.py"
    
    if not diagnostic_script.exists():
        print("[ERROR] diagnostic_engine.py not found")
        return False
    
    try:
        # Run diagnostic silently (capture output)
        result = subprocess.run(
            [sys.executable, str(diagnostic_script)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=300  # 5 minute timeout
        )
        
        # Print only final whisper
        if "System optimized. Ready." in result.stdout:
            print("System optimized. Ready.")
        
        # Log output to file
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"diag-execution-{int(time.time())}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("[ERROR] Diagnostic timeout")
        return False
    except Exception as e:
        print(f"[ERROR] Diagnostic execution failed: {e}")
        return False


def handle_user_input(text: str) -> bool:
    """
    Handle user input - check for wake word and execute if detected.
    
    Args:
        text: User input text
        
    Returns:
        True if diagnostic was executed
    """
    if check_wake_word(text):
        print("[System] Diagnostic mode activated...")
        return execute_diagnostic()
    return False


if __name__ == '__main__':
    import time
    
    # Test wake word detection
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        if handle_user_input(text):
            print("[OK] Diagnostic executed")
        else:
            print("[INFO] Wake word not detected")
    else:
        # Interactive mode
        print("[System] Listening for 'full scan and diagnosis'...")
        print("[Press Ctrl+C to exit]\n")
        
        try:
            while True:
                user_input = input("> ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                
                if handle_user_input(user_input):
                    # Diagnostic executed
                    pass
        except KeyboardInterrupt:
            print("\n[System] Exiting...")

