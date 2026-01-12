# -*- coding: utf-8 -*-
# FILE ORGANIZER AGENT - Moves/organizes files based on review output
# Communicates with other agents via shared JSON files

import os
import json
import shutil
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


class FileOrganizer(Agent):
    """
    File organizer agent that moves/organizes files.
    Reads review output to determine what needs organizing.
    """
    
    def __init__(self, goal: str = "organize project files", config: Optional[AgentConfig] = None):
        """Initialize file organizer agent."""
        super().__init__(goal, config)
        self.comms_dir = Path('.agent_comms')
        self.comms_dir.mkdir(parents=True, exist_ok=True)
        self.files_moved = 0
    
    def _read_review_output(self) -> Optional[Dict[str, Any]]:
        """Read output from code reviewer agent."""
        review_file = self.comms_dir / 'review_output.json'
        if review_file.exists():
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                return None
        return None
    
    def run_task(self, source_dir: str = ".", target_dirs: Optional[Dict[str, str]] = None) -> bool:
        """
        Organize files based on review output or default rules.
        
        Args:
            source_dir: Directory to organize
            target_dirs: Dict mapping file patterns to target directories
        """
        def organize():
            # Check if reviewer found issues
            review_output = self._read_review_output()
            
            source = Path(source_dir)
            if not source.exists():
                raise FileNotFoundError(f"Source directory not found: {source_dir}")
            
            # Default organization rules
            if target_dirs is None:
                target_dirs = {
                    'scripts': './scripts',
                    'tests': './tests',
                    'docs': './docs',
                    'data': './data',
                    'config': './config'
                }
            
            moved_files = []
            
            # Organize Python files by type
            python_files = list(source.glob('*.py'))
            
            if not python_files:
                # No files to organize - still success
                self.history.append("No Python files found to organize")
                output = {
                    'agent': 'organizer',
                    'timestamp': str(datetime.now()),
                    'files_moved': 0,
                    'files': [],
                    'target_dirs': target_dirs,
                    'status': 'no_files'
                }
                
                self.comms_dir.mkdir(parents=True, exist_ok=True)
                output_file = self.comms_dir / 'organize_output.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2)
                
                self.log_run('organize', 'no files to move', True)
                print(json.dumps(output, indent=2))
                return True
            
            for file_path in python_files:
                # Skip self and agent files
                if file_path.name in ['agent_organizer.py', 'agent_codereview.py', 'agent_tester.py', 'agent_hub.py', 'agent_anonymous.py']:
                    continue
                
                target = None
                
                # Check file naming patterns
                if file_path.name.startswith('test_') or file_path.name.endswith('_test.py'):
                    target = Path(target_dirs.get('tests', './tests'))
                elif 'config' in file_path.name.lower() or 'settings' in file_path.name.lower():
                    target = Path(target_dirs.get('config', './config'))
                else:
                    target = Path(target_dirs.get('scripts', './scripts'))
                
                # Move file
                target.mkdir(parents=True, exist_ok=True)
                dest = target / file_path.name
                
                # Handle existing file
                if dest.exists():
                    # Add timestamp suffix
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    stem = file_path.stem
                    dest = target / f"{stem}_{timestamp}{file_path.suffix}"
                
                shutil.move(str(file_path), str(dest))
                moved_files.append({
                    'source': str(file_path),
                    'destination': str(dest),
                    'timestamp': str(datetime.now())
                })
                self.files_moved += 1
            
            # Write output for next agent
            output = {
                'agent': 'organizer',
                'timestamp': str(datetime.now()),
                'files_moved': len(moved_files),
                'files': moved_files,
                'target_dirs': target_dirs
            }
            
            # Save to comms directory
            self.comms_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.comms_dir / 'organize_output.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)
            
            self.history.append(f"Moved {len(moved_files)} files")
            self.log_run('organize', f'moved {len(moved_files)} files', True)
            
            # Output JSON for hub
            print(json.dumps(output, indent=2))
            
            return True
        
        return self.run_with_retry(organize)


if __name__ == '__main__':
    config = AgentConfig(verbose=False)  # Headless mode
    organizer = FileOrganizer(config=config)
    
    # Read project directory from environment or use default
    project_dir = os.environ.get('PROJECT_DIR', '.')
    
    success = organizer.run_task(source_dir=project_dir)
    exit(0 if success else 1)

