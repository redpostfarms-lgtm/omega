# -*- coding: utf-8 -*-
# TEST RUNNER AGENT - Runs tests and reports results
# Communicates with other agents via shared JSON files

import os
import json
import subprocess
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import base Agent
import sys
from pathlib import Path

# Add parent directory to path for imports when running from project directory
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from agent_anonymous import Agent, AgentConfig
except ImportError:
    # Try relative import
    sys.path.insert(0, str(Path(__file__).parent))
    from agent_anonymous import Agent, AgentConfig

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


class TestRunner(Agent):
    """
    Test runner agent that validates cleaned code.
    Simple implementation: checks for ./clean directory and runs main.py
    """
    
    def __init__(self, goal: str = "validate build", config: Optional[AgentConfig] = None):
        """Initialize test runner agent."""
        super().__init__(goal, config)
        self.comms_dir = Path('.agent_comms')
        self.comms_dir.mkdir(parents=True, exist_ok=True)
    
    def run_task(self) -> bool:
        """
        Run tests on cleaned code.
        Looks for ./clean/main.py and runs it.
        """
        def run_tests():
            if not os.path.exists('./clean'):
                self.history.append("No fixed code yet")
                output = {
                    'agent': 'tester',
                    'timestamp': str(datetime.now()),
                    'status': 'no_clean_code',
                    'message': 'No fixed code yet'
                }
                self.comms_dir.mkdir(parents=True, exist_ok=True)
                output_file = self.comms_dir / 'test_output.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2)
                print(json.dumps(output, indent=2))
                return False
            
            try:
                subprocess.check_call(['python', './clean/main.py'])
                self.history.append("All tests green")
                self.log_run('run', 'passed', True)
                
                output = {
                    'agent': 'tester',
                    'timestamp': str(datetime.now()),
                    'status': 'success',
                    'message': 'All tests green'
                }
                self.comms_dir.mkdir(parents=True, exist_ok=True)
                output_file = self.comms_dir / 'test_output.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2)
                print(json.dumps(output, indent=2))
                
                return True
                
            except subprocess.CalledProcessError as e:
                self.history.append(f"Crash code {e.returncode}")
                self.log_run('run', 'fail', False, error=f"Exit code: {e.returncode}")
                
                output = {
                    'agent': 'tester',
                    'timestamp': str(datetime.now()),
                    'status': 'failed',
                    'returncode': e.returncode,
                    'message': f'Crash code {e.returncode}'
                }
                self.comms_dir.mkdir(parents=True, exist_ok=True)
                output_file = self.comms_dir / 'test_output.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2)
                print(json.dumps(output, indent=2))
                
                return False
                
            except FileNotFoundError:
                self.history.append("Test script missing - skipping")
                self.log_run('run', 'skipped', True)
                
                output = {
                    'agent': 'tester',
                    'timestamp': str(datetime.now()),
                    'status': 'skipped',
                    'message': 'Test script missing. Skipping.'
                }
                self.comms_dir.mkdir(parents=True, exist_ok=True)
                output_file = self.comms_dir / 'test_output.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2)
                print(json.dumps(output, indent=2))
                
                return True  # Skipping is OK
        
        return self.run_with_retry(run_tests)


if __name__ == '__main__':
    import sys
    
    # Check if running in headless mode (for hub)
    headless = '--headless' in sys.argv or os.environ.get('HEADLESS', '').lower() == 'true'
    
    config = AgentConfig(verbose=not headless)
    tester = TestRunner(goal="validate build", config=config)
    
    success = tester.run_task()
    exit(0 if success else 1)

