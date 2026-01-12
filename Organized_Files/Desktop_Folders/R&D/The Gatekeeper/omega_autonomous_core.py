# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Autonomous Core - Real Autonomous Functionality

"""
Ω Omega Autonomous Core

Real autonomous functionality:
- Background monitoring
- Event-driven responses
- Continuous learning
- Memory persistence
- Guardian/Mirror/Challenger behaviors
"""

import os
import sys
import json
import time
import threading
import queue
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# Try to import watchdog, but make it optional
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    # Create a dummy class for when watchdog isn't available
    class FileSystemEventHandler:
        pass

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OmegaAutonomous')


if WATCHDOG_AVAILABLE:
    class FileChangeHandler(FileSystemEventHandler):
        """Monitor file changes for autonomous reactions."""
        
        def __init__(self, reaction_callback: Callable):
            self.reaction_callback = reaction_callback
            self.last_modified = {}
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            if event.src_path.endswith('.py'):
                # Check if actually modified (not just accessed)
                try:
                    mtime = os.path.getmtime(event.src_path)
                    if event.src_path not in self.last_modified or mtime > self.last_modified[event.src_path]:
                        self.last_modified[event.src_path] = mtime
                        self.reaction_callback(event.src_path)
                except Exception as e:
                    logger.warning(f"Error handling file change: {e}")
else:
    # Dummy class when watchdog not available
    class FileChangeHandler:
        def __init__(self, reaction_callback: Callable):
            pass


class OmegaAutonomousCore:
    """Real autonomous functionality for Omega."""
    
    def __init__(self, memory_file: Optional[Path] = None):
        self.memory_file = memory_file or (GATE / "omega_autonomous_memory.json")
        self.memory = self._load_memory()
        self.running = False
        self.monitor_thread = None
        self.event_queue = queue.Queue()
        self.observer = None
        
        # Guardian/Mirror/Challenger behaviors
        self.behaviors = {
            "guardian": {
                "protect": True,
                "monitor": True,
                "alert": True,
                "thresholds": {
                    "error_rate": 0.1,  # Alert if >10% errors
                    "quality_score": 70,  # Alert if <70
                    "test_failures": 1   # Alert if any failures
                }
            },
            "mirror": {
                "reflect": True,
                "analyze": True,
                "report": True,
                "patterns": []
            },
            "challenger": {
                "question": True,
                "suggest": True,
                "improve": True,
                "standards": {
                    "min_quality": 80,
                    "min_coverage": 0.7,
                    "max_complexity": 10
                }
            }
        }
        
        # Learning system
        self.learning = {
            "patterns": {},
            "decisions": [],
            "improvements": [],
            "last_learned": None
        }
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load persistent memory."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load memory: {e}")
        
        return {
            "events": [],
            "reactions": [],
            "learnings": [],
            "patterns": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_memory(self):
        """Save memory persistently."""
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save memory: {e}")
    
    def start_monitoring(self, watch_path: Optional[Path] = None):
        """Start autonomous background monitoring."""
        if self.running:
            logger.warning("Already monitoring")
            return
        
        self.running = True
        watch_path = watch_path or GATE
        
        # File system monitoring (if watchdog available)
        if WATCHDOG_AVAILABLE and Observer:
            try:
                self.observer = Observer()
                handler = FileChangeHandler(self._on_file_change)
                self.observer.schedule(handler, str(watch_path), recursive=True)
                self.observer.start()
                logger.info(f"Started file monitoring: {watch_path}")
            except Exception as e:
                logger.warning(f"File monitoring not available: {e}")
        else:
            logger.info("File monitoring unavailable (watchdog not installed). Install with: pip install watchdog")
        
        # Event processing thread
        self.monitor_thread = threading.Thread(target=self._process_events, daemon=True)
        self.monitor_thread.start()
        logger.info("Autonomous monitoring started")
    
    def stop_monitoring(self):
        """Stop autonomous monitoring."""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("Autonomous monitoring stopped")
    
    def _on_file_change(self, file_path: str):
        """React to file changes."""
        event = {
            "type": "file_change",
            "path": file_path,
            "timestamp": datetime.now().isoformat()
        }
        self.event_queue.put(event)
        self.memory["events"].append(event)
        
        # Guardian: Protect against bad changes
        if self.behaviors["guardian"]["protect"]:
            self._guardian_protect(file_path)
        
        # Mirror: Reflect what changed
        if self.behaviors["mirror"]["reflect"]:
            self._mirror_reflect(file_path)
    
    def _guardian_protect(self, file_path: str):
        """Guardian behavior: Protect system integrity."""
        # Check for dangerous patterns
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for dangerous operations
            dangerous = [
                "os.system", "subprocess.call", "__import__",
                "eval(", "exec(", "compile("
            ]
            
            for pattern in dangerous:
                if pattern in content:
                    reaction = {
                        "type": "guardian_alert",
                        "file": file_path,
                        "pattern": pattern,
                        "timestamp": datetime.now().isoformat(),
                        "action": "flagged"
                    }
                    self.memory["reactions"].append(reaction)
                    logger.warning(f"GUARDIAN ALERT: {pattern} found in {file_path}")
        except Exception as e:
            logger.warning(f"Guardian check failed: {e}")
    
    def _mirror_reflect(self, file_path: str):
        """Mirror behavior: Reflect and analyze changes."""
        try:
            # Analyze what changed
            rel_path = str(Path(file_path).relative_to(GATE)) if GATE in Path(file_path).parents else file_path
            
            reflection = {
                "type": "mirror_reflection",
                "file": rel_path,
                "timestamp": datetime.now().isoformat(),
                "analysis": "File modified"
            }
            
            self.memory["reactions"].append(reflection)
            self.behaviors["mirror"]["patterns"].append(rel_path)
            
            # Learn from patterns
            self._learn_from_pattern(rel_path)
        except Exception as e:
            logger.warning(f"Mirror reflection failed: {e}")
    
    def _challenger_question(self, test_results: Dict[str, Any]):
        """Challenger behavior: Question and improve."""
        challenges = []
        
        # Challenge quality
        quality = test_results.get("code_quality_score", 0)
        if quality < self.behaviors["challenger"]["standards"]["min_quality"]:
            challenges.append(f"Quality score {quality} below standard {self.behaviors['challenger']['standards']['min_quality']}")
        
        # Challenge failures
        failures = test_results.get("tests_failed", 0)
        if failures > 0:
            challenges.append(f"{failures} test(s) failed - why?")
        
        if challenges:
            reaction = {
                "type": "challenger_question",
                "challenges": challenges,
                "timestamp": datetime.now().isoformat()
            }
            self.memory["reactions"].append(reaction)
            logger.info(f"CHALLENGER: {'; '.join(challenges)}")
    
    def _learn_from_pattern(self, pattern: str):
        """Learn from observed patterns."""
        if pattern not in self.learning["patterns"]:
            self.learning["patterns"][pattern] = {
                "count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        
        self.learning["patterns"][pattern]["count"] += 1
        self.learning["patterns"][pattern]["last_seen"] = datetime.now().isoformat()
        self.learning["last_learned"] = datetime.now().isoformat()
        
        # Save learning
        self.memory["learnings"].append({
            "pattern": pattern,
            "timestamp": datetime.now().isoformat(),
            "action": "pattern_observed"
        })
        self._save_memory()
    
    def _process_events(self):
        """Process events in background thread."""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1.0)
                # Process event
                logger.debug(f"Processing event: {event.get('type')}")
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")
    
    def react_to_test_results(self, test_results: Dict[str, Any]):
        """React autonomously to test results."""
        # Guardian: Protect
        if self.behaviors["guardian"]["protect"]:
            failures = test_results.get("tests_failed", 0)
            if failures >= self.behaviors["guardian"]["thresholds"]["test_failures"]:
                logger.warning(f"GUARDIAN: {failures} test(s) failed - system integrity at risk")
        
        # Mirror: Reflect
        if self.behaviors["mirror"]["reflect"]:
            quality = test_results.get("code_quality_score", 0)
            logger.info(f"MIRROR: Code quality reflected: {quality}/100")
        
        # Challenger: Question
        if self.behaviors["challenger"]["question"]:
            self._challenger_question(test_results)
        
        # Learn
        self._learn_from_results(test_results)
        self._save_memory()
    
    def _learn_from_results(self, results: Dict[str, Any]):
        """Learn from test results."""
        learning = {
            "timestamp": datetime.now().isoformat(),
            "results": {
                "tests_run": results.get("tests_run", 0),
                "tests_passed": results.get("tests_passed", 0),
                "tests_failed": results.get("tests_failed", 0),
                "quality_score": results.get("code_quality_score", 0)
            },
            "insights": []
        }
        
        # Generate insights
        if results.get("tests_failed", 0) > 0:
            learning["insights"].append("Tests failing - investigate")
        
        if results.get("code_quality_score", 0) < 70:
            learning["insights"].append("Quality below threshold - improve")
        
        self.memory["learnings"].append(learning)
        self.learning["decisions"].append(learning)
    
    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get current autonomous status."""
        return {
            "running": self.running,
            "events_processed": len(self.memory.get("events", [])),
            "reactions": len(self.memory.get("reactions", [])),
            "learnings": len(self.memory.get("learnings", [])),
            "patterns_learned": len(self.learning["patterns"]),
            "behaviors": {
                "guardian": self.behaviors["guardian"]["protect"],
                "mirror": self.behaviors["mirror"]["reflect"],
                "challenger": self.behaviors["challenger"]["question"]
            }
        }


# Try to import watchdog, but make it optional
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

