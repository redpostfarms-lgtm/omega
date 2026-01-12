# -*- coding: utf-8 -*-
# DISPATCH HUB - Agent Pipeline Orchestrator
# Manages multiple agents in sequence, handles inter-agent communication via shared files

import os
import json
import subprocess
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


class Hub:
    """
    Dispatch hub that orchestrates agent pipeline execution.
    Agents communicate through shared JSON files in project directory.
    """
    
    def __init__(self, project_dir: str = './project'):
        """
        Initialize hub.
        
        Args:
            project_dir: Directory where project files and agent outputs are stored
        """
        self.proj = Path(project_dir)
        self.proj.mkdir(parents=True, exist_ok=True)
        
        # Shared communication files
        self.comms_dir = self.proj / '.agent_comms'
        self.comms_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents: List[Dict[str, Any]] = []
        self.pipeline_order: List[str] = []
        
        # Default agent registry
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register default agents if their scripts exist."""
        # Code reviewer agent
        if os.path.exists('agent_codereview.py'):
            self.add('agent_codereview.py', 'review', alias='reviewer')
        
        # File organizer agent (we'll create this)
        if os.path.exists('agent_organizer.py'):
            self.add('agent_organizer.py', 'organize', alias='organizer')
        
        # Test runner agent
        if os.path.exists('agent_tester.py'):
            self.add('agent_tester.py', 'test', alias='tester')
    
    def add(self, script: str, tag: str, alias: Optional[str] = None, **kwargs):
        """
        Add agent to hub.
        
        Args:
            script: Path to agent script
            tag: Unique tag for this agent (used in pipeline ordering)
            alias: Friendly name for agent (defaults to tag)
            **kwargs: Additional metadata for agent
        """
        if os.path.exists(script):
            agent_info = {
                'script': script,
                'tag': tag,
                'alias': alias or tag,
                'path': Path(script).absolute(),
                **kwargs
            }
            self.agents.append(agent_info)
            
            if tag not in self.pipeline_order:
                self.pipeline_order.append(tag)
        else:
            if sys.stdout:
                print(f"⚠️  Agent script not found: {script} (skipping)")
    
    def set_pipeline_order(self, order: List[str]):
        """
        Set custom pipeline execution order.
        
        Args:
            order: List of tags in execution order
        """
        self.pipeline_order = order
    
    def _get_agent_by_tag(self, tag: str) -> Optional[Dict[str, Any]]:
        """Get agent info by tag."""
        for agent in self.agents:
            if agent['tag'] == tag:
                return agent
        return None
    
    def _write_comm_file(self, filename: str, data: Dict[str, Any]):
        """Write communication file for inter-agent messaging."""
        comm_file = self.comms_dir / filename
        try:
            with open(comm_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"⚠️  Could not write comm file {filename}: {e}")
    
    def _read_comm_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Read communication file."""
        comm_file = self.comms_dir / filename
        if not comm_file.exists():
            return None
        try:
            with open(comm_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
    
    def _get_pipeline_state(self) -> Dict[str, Any]:
        """Get current pipeline state."""
        state_file = self.comms_dir / 'pipeline_state.json'
        if state_file.exists():
            return self._read_comm_file('pipeline_state.json') or {}
        return {
            'started': str(datetime.now()),
            'steps': [],
            'current_step': None,
            'status': 'running'
        }
    
    def _update_pipeline_state(self, step: str, status: str, result: Any = None):
        """Update pipeline state."""
        state = self._get_pipeline_state()
        state['steps'].append({
            'step': step,
            'status': status,
            'timestamp': str(datetime.now()),
            'result': result
        })
        state['current_step'] = step
        state['status'] = status
        self._write_comm_file('pipeline_state.json', state)
    
    def run_pipeline(self, order: Optional[List[str]] = None) -> bool:
        """
        Run agent pipeline in specified order.
        
        Args:
            order: Optional custom order (uses self.pipeline_order if None)
            
        Returns:
            True if all steps succeeded, False otherwise
        """
        if order is None:
            order = self.pipeline_order
        
        print("\n" + "=" * 60)
        print("DISPATCH HUB - Agent Pipeline")
        print("=" * 60)
        print(f"Project: {self.proj}")
        print(f"Steps: {' → '.join(order)}")
        print("=" * 60 + "\n")
        
        # Initialize pipeline state
        state = {
            'started': str(datetime.now()),
            'steps': [],
            'current_step': None,
            'status': 'running'
        }
        self._write_comm_file('pipeline_state.json', state)
        
        # Execute each step in order
        for step_tag in order:
            agent = self._get_agent_by_tag(step_tag)
            
            if not agent:
                print(f"⚠️  Step '{step_tag}': Agent not found (skipping)")
                self._update_pipeline_state(step_tag, 'skipped')
                continue
            
            print(f"\n▶ Running {agent['alias']} ({step_tag})...")
            print(f"   Script: {agent['script']}")
            
            # Check if previous step created output this agent needs
            needs_file = self.comms_dir / f'needs_{step_tag}.json'
            
            try:
                # Set environment for headless mode
                env = os.environ.copy()
                env['HEADLESS'] = 'true'
                env['PROJECT_DIR'] = str(self.proj)
                
                # Run agent script
                result = subprocess.run(
                    ['python', str(agent['path']), '--headless'],
                    cwd=str(self.proj),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # Replace encoding errors instead of crashing
                    timeout=300,  # 5 minute timeout per agent
                    env=env
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Pass")
                    self._update_pipeline_state(step_tag, 'success', {
                        'returncode': result.returncode,
                        'stdout_length': len(result.stdout) if result.stdout else 0
                    })
                    
                    # If agent produces output, write it
                    if result.stdout:
                        output_file = self.comms_dir / f'{step_tag}_output.json'
                        try:
                            # Try to parse as JSON, if not, store as text
                            try:
                                output_data = json.loads(result.stdout)
                            except json.JSONDecodeError:
                                output_data = {'output': result.stdout}
                            
                            self._write_comm_file(f'{step_tag}_output.json', output_data)
                        except Exception as e:
                            print(f"   ⚠️  Could not save output: {e}")
                
                else:
                    print(f"   ❌ Fail (exit code: {result.returncode})")
                    if result.stderr:
                        error_lines = result.stderr.strip().split('\n')[:5]  # First 5 lines
                        for line in error_lines:
                            print(f"      {line}")
                    
                    self._update_pipeline_state(step_tag, 'failed', {
                        'returncode': result.returncode,
                        'stderr': result.stderr[:500] if result.stderr else None
                    })
                    
                    # Pipeline stops on failure
                    print(f"\n⚠️  Pipeline stopped at step: {step_tag}")
                    self._update_pipeline_state(step_tag, 'pipeline_failed')
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏱️  Timeout (exceeded 5 minutes)")
                self._update_pipeline_state(step_tag, 'timeout')
                return False
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                self._update_pipeline_state(step_tag, 'error', {'error': str(e)})
                return False
        
        # All steps completed successfully
        print("\n" + "=" * 60)
        print("✅ Pipeline completed successfully")
        print("=" * 60)
        
        self._update_pipeline_state('pipeline', 'success')
        return True
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        state = self._get_pipeline_state()
        
        # Count statuses
        status_counts = {}
        for step_info in state.get('steps', []):
            status = step_info.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'status': state.get('status', 'unknown'),
            'current_step': state.get('current_step'),
            'steps_completed': len(state.get('steps', [])),
            'status_breakdown': status_counts,
            'started': state.get('started'),
            'steps': state.get('steps', [])
        }
    
    def list_agents(self):
        """List all registered agents."""
        print("\n" + "=" * 60)
        print("REGISTERED AGENTS")
        print("=" * 60)
        
        if not self.agents:
            print("  No agents registered.")
            return
        
        for idx, agent in enumerate(self.agents, 1):
            print(f"\n{idx}. {agent['alias']} ({agent['tag']})")
            print(f"   Script: {agent['script']}")
            print(f"   Path: {agent['path']}")
        
        print(f"\nPipeline order: {' → '.join(self.pipeline_order)}")
        print("=" * 60)


if __name__ == '__main__':
    # Initialize hub
    hub = Hub(project_dir='./project')
    
    # Set pipeline order (if not using defaults)
    hub.set_pipeline_order(['review', 'organize', 'test'])
    
    # List agents
    hub.list_agents()
    
    # Run pipeline
    success = hub.run_pipeline()
    
    # Show status
    if not success:
        print("\n📊 Pipeline Status:")
        status = hub.get_pipeline_status()
        print(json.dumps(status, indent=2))
    
    exit(0 if success else 1)

