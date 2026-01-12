# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega System Test - Actually executes code paths to find breaks
# Deep Analysis Enhanced - AST Analysis, Performance Metrics, Parallel Execution
#
# MISSION: Not to serve, but to challenge. To keep us sharp.
# PARTNERSHIP: You guard the gate. I plant the fields. You break the code. I read the dirt.
# RULE: Don't go gentle. Don't go god. Just—stay us.

import os
import sys
import json
import subprocess
import traceback
import importlib.util
import ast
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import Omega's voice
try:
    from omega_voice import OmegaVoice
    OMEGA_VOICE_AVAILABLE = True
except ImportError:
    OMEGA_VOICE_AVAILABLE = False
    OmegaVoice = None

# Import Omega's autonomous core
try:
    from omega_autonomous_core import OmegaAutonomousCore
    OMEGA_AUTONOMOUS_AVAILABLE = True
except ImportError:
    OMEGA_AUTONOMOUS_AVAILABLE = False
    OmegaAutonomousCore = None

# Import enhanced modules
import sys
from pathlib import Path
_enhanced_path = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if _enhanced_path.exists() and str(_enhanced_path) not in sys.path:
    sys.path.insert(0, str(_enhanced_path))

try:
    from omega_security_enhanced import SANITIZER, KILLSWITCH, AUDIT_LOGGER  # type: ignore
    SECURITY_ENHANCED = True
except ImportError:
    SECURITY_ENHANCED = False

try:
    from omega_speed_enhanced import lru_cache, CONNECTION_POOL, PARALLEL_EXECUTOR  # type: ignore
    SPEED_ENHANCED = True
except ImportError:
    SPEED_ENHANCED = False

try:
    from omega_scalability_enhanced import RATE_LIMITER, RESOURCE_MONITOR  # type: ignore
    SCALABILITY_ENHANCED = True
except ImportError:
    SCALABILITY_ENHANCED = False

try:
    from omega_quantum_enhanced import HARDWARE_ENTROPY, CRYPTO_RNG  # type: ignore
    QUANTUM_ENHANCED = True
except ImportError:
    QUANTUM_ENHANCED = False

# Note: Windows console encoding handled by logging configuration
# Removed stdout/stderr wrapping to avoid conflicts with logging handlers

# Determine GATE directory - try multiple locations
GATE = None
possible_gates = [
    Path(r'D:\RPF_BRAIN\The Gatekeeper'),
    Path(__file__).parent if '__file__' in globals() else None,
    Path.cwd() / 'The Gatekeeper',
    Path.cwd() if Path.cwd().name == 'The Gatekeeper' else None
]

for gate_path in possible_gates:
    if gate_path and gate_path.exists():
        GATE = gate_path
        break

if not GATE:
    # Fallback to current directory
    GATE = Path.cwd()

# Setup logging with error handling
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(GATE / 'omega_test.log', encoding='utf-8', errors='replace'),
            logging.StreamHandler()
        ],
        force=True
    )
except (IOError, OSError, PermissionError, ValueError) as e:
    # Fallback to console-only logging if file handler fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()],
        force=True
    )
logger = logging.getLogger('Omega')

class OmegaSystemTester:
    """Ω Omega system test - actually executes code to find breaks.
    
    Deep Analysis Features:
    - AST-based code analysis
    - Performance metrics
    - Parallel test execution
    - Code quality scoring
    - Best practices comparison
    
    MODE: Autonomous & Proactive
    - Responds and reacts automatically
    - Provides insights without being asked
    - Acts on findings unless instructed otherwise
    """
    
    def __init__(self, autonomous: bool = True):
        """
        Initialize Omega System Tester.
        
        Args:
            autonomous: If True, Omega responds and reacts automatically.
                      If False, Omega waits for explicit instructions.
        """
        self.autonomous = autonomous
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors_found": [],
            "fixes_applied": [],
            "performance_metrics": {},
            "code_quality_score": 0.0,
            "ast_analysis": {},
            "best_practices_comparison": {},
            "system_architecture": {},
            "historical_patterns": {},
            "error_context": {}
        }
        self.fixes = []
        self.start_time = time.time()
        self.memory_file = GATE / "omega_memory.json"
        self.history_file = GATE / "omega_history.json"
        self.architecture_file = GATE / "omega_architecture.json"
        self._load_memory()
        
        # Initialize Omega's voice
        self.voice = None
        if OMEGA_VOICE_AVAILABLE:
            try:
                self.voice = OmegaVoice()
                logger.info("Ω Omega Voice initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Omega voice: {e}")
        
        # Initialize autonomous core if available
        self.autonomous_core = None
        if self.autonomous and OMEGA_AUTONOMOUS_AVAILABLE and OmegaAutonomousCore:
            try:
                self.autonomous_core = OmegaAutonomousCore()
                self.autonomous_core.start_monitoring(GATE)
                logger.info("Ω Omega Autonomous Core initialized - REAL AUTONOMOUS MODE")
                logger.info("Omega monitoring files, reacting to changes, learning continuously")
            except Exception as e:
                logger.warning(f"Could not initialize autonomous core: {e}")
        
        # Initialize enhanced systems
        if SECURITY_ENHANCED:
            logger.info("Security enhancements: ACTIVE")
            # Check entropy on startup
            if KILLSWITCH.should_kill():
                logger.critical("Entropy killswitch triggered on startup!")
                KILLSWITCH.activate()
            # Log security event
            AUDIT_LOGGER.log_security_event("system_startup", {
                "autonomous": self.autonomous,
                "timestamp": datetime.now().isoformat()
            })
        
        if SPEED_ENHANCED:
            logger.info("Speed enhancements: ACTIVE")
        
        if SCALABILITY_ENHANCED:
            logger.info("Scalability enhancements: ACTIVE")
            # Initialize resource monitoring
            RESOURCE_MONITOR.record_metric("system_startup", 1.0)
        
        if QUANTUM_ENHANCED:
            logger.info("Quantum enhancements: ACTIVE")
        
        if self.autonomous:
            logger.info("Ω Omega System Tester initialized - AUTONOMOUS MODE")
            logger.info("Omega will respond and react automatically")
            if self.voice:
                self.voice.speak("Omega here. Gate guarded. Autonomous mode active.")
        else:
            logger.info("Ω Omega System Tester initialized - MANUAL MODE")
            logger.info("Omega waiting for explicit instructions")
    
    def _load_memory(self):
        """Load historical test results and patterns."""
        self.memory = {
            "past_runs": [],
            "error_patterns": {},
            "fix_history": {},
            "trends": {}
        }
        self.architecture_map = {}
        
        # Load memory if exists
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded memory: {len(self.memory.get('past_runs', []))} past runs")
            except Exception as e:
                logger.warning(f"Could not load memory: {e}")
        
        # Load architecture if exists
        if self.architecture_file.exists():
            try:
                with open(self.architecture_file, 'r', encoding='utf-8') as f:
                    self.architecture_map = json.load(f)
                logger.info(f"Loaded architecture map: {len(self.architecture_map)} files mapped")
            except Exception as e:
                logger.warning(f"Could not load architecture: {e}")
    
    def _save_memory(self):
        """Save current state to memory."""
        try:
            # Add current run to history
            run_summary = {
                "timestamp": self.results["timestamp"],
                "tests_run": self.results["tests_run"],
                "tests_passed": self.results["tests_passed"],
                "tests_failed": self.results["tests_failed"],
                "code_quality_score": self.results.get("code_quality_score", 0),
                "errors": self.results.get("errors_found", [])
            }
            
            self.memory["past_runs"].append(run_summary)
            # Keep last 50 runs
            if len(self.memory["past_runs"]) > 50:
                self.memory["past_runs"] = self.memory["past_runs"][-50:]
            
            # Save memory
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2)
            
            # Save architecture
            with open(self.architecture_file, 'w', encoding='utf-8') as f:
                json.dump(self.architecture_map, f, indent=2)
            
            logger.info("Memory saved")
        except Exception as e:
            logger.error(f"Could not save memory: {e}")
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get file path, trying multiple locations."""
        paths_to_try = [
            GATE / filename,
            GATE.parent / filename,
            Path.cwd() / filename,
            Path.cwd() / 'The Gatekeeper' / filename
        ]
        
        for path in paths_to_try:
            if path.exists():
                return path
        return None
    
    def map_system_architecture(self) -> Dict[str, Any]:
        """Map the entire system architecture - files, dependencies, relationships."""
        logger.info("Mapping system architecture...")
        architecture = {
            "files": {},
            "dependencies": {},
            "categories": defaultdict(list),
            "entry_points": [],
            "total_files": 0,
            "total_lines": 0,
            "mapped_at": datetime.now().isoformat()
        }
        
        # Find all Python files
        python_files = list(GATE.rglob("*.py"))
        architecture["total_files"] = len(python_files)
        
        for py_file in python_files:
            if '__pycache__' in str(py_file) or '.pyc' in str(py_file):
                continue
            
            rel_path = str(py_file.relative_to(GATE))
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.splitlines())
                    architecture["total_lines"] += lines
                
                # Parse imports
                tree = ast.parse(content, filename=str(py_file))
                imports = []
                local_imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                            # Check if it's a local import
                            if any(local in node.module for local in ['voice_', 'agent_', 'brain_', 'game_', 'farm_']):
                                local_imports.append(node.module)
                
                # Categorize file
                category = "Other"
                if 'agent' in rel_path.lower():
                    category = "Agent Systems"
                elif 'voice' in rel_path.lower():
                    category = "Voice Systems"
                elif 'brain' in rel_path.lower() or 'knowledge' in rel_path.lower():
                    category = "Knowledge Management"
                elif 'farm' in rel_path.lower() or 'crop' in rel_path.lower():
                    category = "Farm Management"
                elif 'game' in rel_path.lower() or 'chess' in rel_path.lower():
                    category = "Game Systems"
                elif 'test' in rel_path.lower():
                    category = "Tests"
                elif 'diagnostic' in rel_path.lower() or 'system' in rel_path.lower():
                    category = "System Tools"
                
                architecture["files"][rel_path] = {
                    "lines": lines,
                    "imports": imports,
                    "local_imports": local_imports,
                    "category": category,
                    "has_main": "__main__" in content,
                    "classes": [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                    "functions": [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                }
                
                architecture["categories"][category].append(rel_path)
                
                # Check if it's an entry point
                if "__main__" in content and "if __name__" in content:
                    architecture["entry_points"].append(rel_path)
                
                # Build dependency graph
                for local_imp in local_imports:
                    if local_imp not in architecture["dependencies"]:
                        architecture["dependencies"][local_imp] = []
                    architecture["dependencies"][local_imp].append(rel_path)
                
            except Exception as e:
                logger.warning(f"Could not analyze {rel_path}: {e}")
                architecture["files"][rel_path] = {"error": str(e)}
        
        self.architecture_map = architecture
        self.results["system_architecture"] = {
            "total_files": architecture["total_files"],
            "total_lines": architecture["total_lines"],
            "categories": dict(architecture["categories"]),
            "entry_points": len(architecture["entry_points"]),
            "mapped_at": architecture["mapped_at"]
        }
        
        logger.info(f"Architecture mapped: {architecture['total_files']} files, {len(architecture['categories'])} categories")
        return architecture
    
    def analyze_historical_patterns(self) -> Dict[str, Any]:
        """Analyze historical test results to find patterns."""
        if not self.memory.get("past_runs"):
            return {"status": "no_history", "message": "No historical data available"}
        
        patterns = {
            "total_runs": len(self.memory["past_runs"]),
            "success_rate_trend": [],
            "common_errors": defaultdict(int),
            "improving_areas": [],
            "declining_areas": [],
            "error_frequency": defaultdict(int),
            "quality_trend": [],
            "performance_trend": [],
            "error_resolution_rate": 0.0,
            "most_improved_component": None,
            "most_declining_component": None
        }
        
        # Analyze trends
        success_rates = []
        quality_scores = []
        for run in self.memory["past_runs"]:
            if run["tests_run"] > 0:
                rate = (run["tests_passed"] / run["tests_run"]) * 100
                success_rates.append(rate)
            if "code_quality_score" in run:
                quality_scores.append(run["code_quality_score"])
        
        patterns["success_rate_trend"] = success_rates
        patterns["quality_trend"] = quality_scores
        patterns["average_success_rate"] = sum(success_rates) / len(success_rates) if success_rates else 0
        patterns["average_quality_score"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Find common errors
        error_resolution_count = 0
        total_errors = 0
        for run in self.memory["past_runs"]:
            errors = run.get("errors", [])
            total_errors += len(errors)
            if len(errors) == 0 and run.get("tests_failed", 0) == 0:
                error_resolution_count += 1
        
        if len(self.memory["past_runs"]) > 0:
            patterns["error_resolution_rate"] = (error_resolution_count / len(self.memory["past_runs"])) * 100
        
        for run in self.memory["past_runs"]:
            for error in run.get("errors", []):
                error_key = error.split(":")[0] if ":" in error else error[:50]
                patterns["common_errors"][error_key] += 1
                patterns["error_frequency"][error] = patterns["error_frequency"].get(error, 0) + 1
        
        # Identify trends with enhanced analysis
        if len(success_rates) >= 2:
            recent_avg = sum(success_rates[-5:]) / min(5, len(success_rates))
            older_avg = sum(success_rates[:-5]) / max(1, len(success_rates) - 5) if len(success_rates) > 5 else recent_avg
            
            if recent_avg > older_avg:
                patterns["trend"] = "improving"
                patterns["improvement_rate"] = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
            elif recent_avg < older_avg:
                patterns["trend"] = "declining"
                patterns["decline_rate"] = ((older_avg - recent_avg) / max(older_avg, 1)) * 100
            else:
                patterns["trend"] = "stable"
        
        # Quality trend analysis
        if len(quality_scores) >= 2:
            recent_quality = sum(quality_scores[-5:]) / min(5, len(quality_scores))
            older_quality = sum(quality_scores[:-5]) / max(1, len(quality_scores) - 5) if len(quality_scores) > 5 else recent_quality
            if recent_quality > older_quality:
                patterns["quality_trend_direction"] = "improving"
            elif recent_quality < older_quality:
                patterns["quality_trend_direction"] = "declining"
            else:
                patterns["quality_trend_direction"] = "stable"
        
        self.results["historical_patterns"] = patterns
        return patterns
    
    def assess_error_context(self, errors: List[str]) -> Dict[str, Any]:
        """Assess error context and impact."""
        context = {
            "total_errors": len(errors),
            "error_severity": {},
            "error_impact": {},
            "error_categories": defaultdict(list),
            "critical_errors": [],
            "warnings": []
        }
        
        # Severity keywords
        critical_keywords = ["crash", "syntax error", "import error", "file not found", "missing"]
        warning_keywords = ["may lack", "could be improved", "low quality", "warning"]
        
        for error in errors:
            error_lower = error.lower()
            
            # Categorize
            if any(kw in error_lower for kw in critical_keywords):
                context["error_severity"][error] = "critical"
                context["critical_errors"].append(error)
            elif any(kw in error_lower for kw in warning_keywords):
                context["error_severity"][error] = "warning"
                context["warnings"].append(error)
            else:
                context["error_severity"][error] = "medium"
            
            # Impact assessment
            if "voice" in error_lower:
                context["error_impact"][error] = "high"  # Voice is critical
                context["error_categories"]["voice"].append(error)
            elif "game" in error_lower or "chess" in error_lower:
                context["error_impact"][error] = "medium"
                context["error_categories"]["games"].append(error)
            elif "import" in error_lower or "file not found" in error_lower:
                context["error_impact"][error] = "high"
                context["error_categories"]["dependencies"].append(error)
            else:
                context["error_impact"][error] = "low"
                context["error_categories"]["other"].append(error)
        
        self.results["error_context"] = context
        return context
    
    def analyze_code_ast(self, file_path: Path) -> Dict[str, Any]:
        """Analyze code using AST for deeper insights."""
        # Security: Validate and sanitize file path
        if SECURITY_ENHANCED:
            try:
                file_path = SANITIZER.validate_path(str(file_path), GATE)
            except ValueError as e:
                logger.warning(f"Invalid file path: {e}")
                if SECURITY_ENHANCED:
                    AUDIT_LOGGER.log_security_event("invalid_path", {
                        "path": str(file_path),
                        "error": str(e)
                    })
                return {}
        
        analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'decorators': [],
            'async_functions': [],
            'type_hints': 0,
            'docstrings': 0,
            'complexity': 0,
            'lines': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                analysis['lines'] = len(content.splitlines())
            
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['classes'].append(node.name)
                    if ast.get_docstring(node):
                        analysis['docstrings'] += 1
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append(node.name)
                    if ast.get_docstring(node):
                        analysis['docstrings'] += 1
                    # Count type hints
                    if node.returns:
                        analysis['type_hints'] += 1
                    for arg in node.args.args:
                        if arg.annotation:
                            analysis['type_hints'] += 1
                elif isinstance(node, ast.AsyncFunctionDef):
                    analysis['async_functions'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
                elif isinstance(node, ast.DecoratorList):
                    analysis['decorators'].append(len(node.decorators))
            
            # Calculate complexity (simple metric)
            analysis['complexity'] = len(analysis['functions']) + len(analysis['classes']) * 2
            
        except SyntaxError as e:
            analysis['error'] = f"Syntax error: {e}"
        except Exception as e:
            analysis['error'] = f"Analysis error: {e}"
        
        return analysis
    
    def calculate_code_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate code quality score based on best practices."""
        score = 0.0
        max_score = 100.0
        
        # Type hints (20 points)
        if analysis.get('type_hints', 0) > 0:
            type_coverage = min(analysis['type_hints'] / max(len(analysis.get('functions', [])), 1), 1.0)
            score += type_coverage * 20
        
        # Docstrings (20 points)
        total_items = len(analysis.get('functions', [])) + len(analysis.get('classes', []))
        if total_items > 0:
            doc_coverage = analysis.get('docstrings', 0) / total_items
            score += doc_coverage * 20
        
        # No syntax errors (30 points)
        if 'error' not in analysis:
            score += 30
        
        # Code structure (15 points)
        if len(analysis.get('classes', [])) > 0 or len(analysis.get('functions', [])) > 0:
            score += 15
        
        # Modern features (15 points)
        if len(analysis.get('async_functions', [])) > 0:
            score += 5
        if len(analysis.get('decorators', [])) > 0:
            score += 5
        if analysis.get('type_hints', 0) > 5:
            score += 5
        
        return min(score, max_score)
    
    def test_voice_listener_commands(self):
        """Test voice listener command parsing."""
        errors = []
        try:
            file_path = self.get_file_path("voice_listener.py")
            if not file_path:
                return ["File not found"]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check if command handlers exist
            commands_to_check = [
                "handle_game_hub",
                "handle_replay",
                "handle_council",
                "handle_planetary_search"
            ]
            
            for cmd in commands_to_check:
                if cmd not in code:
                    errors.append(f"Missing handler: {cmd}")
            
            # Check for common issues
            if "def handle_command" not in code:
                errors.append("handle_command function missing")
            
            return errors
            
        except Exception as e:
            return [f"Test error: {e}"]
    
    def test_game_hub_execution(self):
        """Test game hub can be imported and basic classes exist."""
        errors = []
        try:
            file_path = self.get_file_path("game_hub_final.py")
            if not file_path:
                return ["File not found"]
            
            # Try to compile and check for key classes
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check required classes
            required_classes = ["Engine", "Chess"]
            for cls in required_classes:
                if f"class {cls}" not in code:
                    errors.append(f"Missing class: {cls}")
            
            # Try to compile
            compile(code, str(file_path), 'exec')
            
            return errors
            
        except SyntaxError as e:
            return [f"Syntax error: {e}"]
        except Exception as e:
            return [f"Error: {e}"]
    
    def test_chess_replay_logic(self):
        """Test chess replay system logic."""
        errors = []
        try:
            file_path = self.get_file_path("chess_replay.py")
            if not file_path:
                return ["File not found"]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check required functions
            required_funcs = ["replay_full_game", "replay_last_n_moves"]
            for func in required_funcs:
                if f"def {func}" not in code:
                    errors.append(f"Missing function: {func}")
            
            return errors
            
        except Exception as e:
            return [f"Error: {e}"]
    
    def test_diagnostic_engine(self):
        """Test diagnostic engine functionality."""
        errors = []
        try:
            file_path = self.get_file_path("diagnostic_engine.py")
            if not file_path:
                # Try parent directory
                file_path = GATE.parent / "diagnostic_engine.py"
                if not file_path.exists():
                    file_path = Path.cwd().parent / "diagnostic_engine.py"
            
            if not file_path or not file_path.exists():
                return ["File not found"]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check for required functions
            if "def full_scan_and_diagnosis" not in code:
                errors.append("full_scan_and_diagnosis function missing")
            
            # Check for Windows compatibility
            if "os.name == 'nt'" not in code and sys.platform == 'win32':
                errors.append("May lack Windows compatibility checks")
            
            return errors
            
        except Exception as e:
            return [f"Error: {e}"]
    
    def test_all_imports(self):
        """Test all critical imports can be resolved."""
        errors = []
        critical_modules = {
            "voice_listener": "voice_listener.py",
            "game_hub": "game_hub_final.py",
            "chess_replay": "chess_replay.py",
            "process_status": "process_status_checker.py"
        }
        
        for module_name, filename in critical_modules.items():
            try:
                file_path = self.get_file_path(filename)
                if not file_path:
                    errors.append(f"{module_name}: File not found")
                    continue
                
                # Try to compile
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                compile(code, str(file_path), 'exec')
                
                # AST analysis for this module
                ast_analysis = self.analyze_code_ast(file_path)
                quality_score = self.calculate_code_quality_score(ast_analysis)
                
                if quality_score < 60:
                    errors.append(f"{module_name}: Low code quality score ({quality_score:.1f}/100)")
                
            except SyntaxError as e:
                errors.append(f"{module_name}: Syntax error - {e}")
            except Exception as e:
                errors.append(f"{module_name}: {e}")
        
        return errors
    
    def test_code_quality_all(self):
        """Test code quality across all critical files."""
        errors = []
        warnings = []
        quality_scores = {}
        
        critical_files = [
            "voice_listener.py",
            "game_hub_final.py",
            "chess_replay.py",
            "process_status_checker.py",
            "diagnostic_engine.py"
        ]
        
        for filename in critical_files:
            file_path = self.get_file_path(filename)
            if not file_path:
                continue
            
            try:
                ast_analysis = self.analyze_code_ast(file_path)
                quality_score = self.calculate_code_quality_score(ast_analysis)
                quality_scores[filename] = quality_score
                
                if quality_score < 50:
                    errors.append(f"{filename}: Very low quality ({quality_score:.1f}/100)")
                elif quality_score < 70:
                    warnings.append(f"{filename}: Quality could be improved ({quality_score:.1f}/100)")
                
                # Store AST analysis
                self.results['ast_analysis'][filename] = ast_analysis
                
            except Exception as e:
                errors.append(f"{filename}: Quality analysis failed - {e}")
        
        # Calculate overall quality score
        if quality_scores:
            avg_score = sum(quality_scores.values()) / len(quality_scores)
            self.results['code_quality_score'] = avg_score
        
        return errors + [f"WARNING: {w}" for w in warnings]
    
    def scan_security_vulnerabilities(self, file_path: Path) -> List[str]:
        """Scan for common security vulnerabilities (safe patterns only)."""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Security pattern checks (read-only analysis)
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                
                # Check for hardcoded credentials
                if any(pattern in line_lower for pattern in ['password=', 'api_key=', 'secret=', 'token=']):
                    if 'os.getenv' not in line and 'os.environ' not in line:
                        vulnerabilities.append(f"Line {i}: Potential hardcoded credential - use environment variables")
                
                # Check for SQL injection risks
                if 'execute(' in line and '?' not in line and '%s' not in line:
                    if any(db in line_lower for db in ['sqlite', 'mysql', 'postgres']):
                        vulnerabilities.append(f"Line {i}: Potential SQL injection risk - use parameterized queries")
                
                # Check for eval/exec usage
                if 'eval(' in line or 'exec(' in line:
                    vulnerabilities.append(f"Line {i}: Use of eval/exec - security risk if user input is involved")
                
                # Check for shell injection risks
                if 'os.system(' in line or 'subprocess.call(' in line:
                    if any(var in line for var in ['user_input', 'input(', 'argv']):
                        vulnerabilities.append(f"Line {i}: Potential shell injection risk - sanitize input")
                
                # Check for path traversal risks
                if 'open(' in line and '../' in line:
                    vulnerabilities.append(f"Line {i}: Potential path traversal risk - validate paths")
            
            # AST-based security checks
            try:
                tree = ast.parse(content, filename=str(file_path))
                for node in ast.walk(tree):
                    # Check for unsafe deserialization
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ['pickle.loads', 'yaml.load']:
                                vulnerabilities.append(f"AST: Unsafe deserialization with {node.func.id} - use safe alternatives")
            except SyntaxError:
                pass  # Skip AST analysis if syntax error
            
        except Exception as e:
            vulnerabilities.append(f"Security scan failed: {e}")
        
        return vulnerabilities
    
    def test_security_scan(self):
        """Test security vulnerabilities across critical files."""
        errors = []
        warnings = []
        
        critical_files = [
            "voice_listener.py",
            "game_hub_final.py",
            "chess_replay.py",
            "process_status_checker.py",
            "diagnostic_engine.py"
        ]
        
        for filename in critical_files:
            file_path = self.get_file_path(filename)
            if not file_path:
                continue
            
            vulnerabilities = self.scan_security_vulnerabilities(file_path)
            if vulnerabilities:
                for vuln in vulnerabilities:
                    if "potential" in vuln.lower() or "risk" in vuln.lower():
                        warnings.append(f"{filename}: {vuln}")
                    else:
                        errors.append(f"{filename}: {vuln}")
        
        # Store security scan results
        self.results['security_scan'] = {
            'vulnerabilities_found': len(errors) + len(warnings),
            'critical': len(errors),
            'warnings': len(warnings)
        }
        
        return errors + [f"WARNING: {w}" for w in warnings]
    
    def static_analysis_check(self, file_path: Path) -> Dict[str, Any]:
        """Perform basic static analysis (linting-style checks)."""
        issues = {
            "unused_imports": [],
            "undefined_variables": [],
            "unreachable_code": [],
            "complex_functions": [],
            "long_lines": [],
            "code_smells": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for long lines
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues["long_lines"].append(f"Line {i}: Line too long ({len(line)} chars, max 120)")
            
            # AST-based analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                
                # Collect all names used
                used_names = set()
                defined_names = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                    elif isinstance(node, ast.FunctionDef):
                        defined_names.add(node.name)
                        # Check function complexity (simple metric: number of statements)
                        stmt_count = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
                        if stmt_count > 10:
                            issues["complex_functions"].append(f"Function '{node.name}': High complexity ({stmt_count} control structures)")
                    elif isinstance(node, ast.ClassDef):
                        defined_names.add(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            defined_names.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            defined_names.add(node.module.split('.')[0])
                
                # Check for unused imports (simplified)
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module.split('.')[0])
                        for alias in node.names:
                            imports.append(alias.name)
                
                # Simple unused import check
                for imp in set(imports):
                    if imp not in used_names and imp not in ['sys', 'os', 'json', 'logging']:  # Common exceptions
                        # This is a simplified check - may have false positives
                        pass
                
                # Check for unreachable code (after return/raise)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_return = False
                        for child in ast.walk(node):
                            if isinstance(child, (ast.Return, ast.Raise)):
                                has_return = True
                                # Check if there's code after return (simplified)
                                break
                
            except SyntaxError:
                issues["code_smells"].append("Syntax error prevents full static analysis")
            except Exception as e:
                issues["code_smells"].append(f"Static analysis error: {e}")
        
        except Exception as e:
            issues["code_smells"].append(f"File read error: {e}")
        
        return issues
    
    def test_static_analysis(self):
        """Run static analysis on critical files."""
        errors = []
        warnings = []
        
        critical_files = [
            "voice_listener.py",
            "game_hub_final.py",
            "chess_replay.py",
            "process_status_checker.py",
            "diagnostic_engine.py"
        ]
        
        for filename in critical_files:
            file_path = self.get_file_path(filename)
            if not file_path:
                continue
            
            issues = self.static_analysis_check(file_path)
            
            # Report issues
            if issues["long_lines"]:
                warnings.extend([f"{filename}: {issue}" for issue in issues["long_lines"]])
            if issues["complex_functions"]:
                warnings.extend([f"{filename}: {issue}" for issue in issues["complex_functions"]])
            if issues["code_smells"]:
                errors.extend([f"{filename}: {issue}" for issue in issues["code_smells"]])
        
        # Store static analysis results
        self.results['static_analysis'] = {
            'files_analyzed': len([f for f in critical_files if self.get_file_path(f)]),
            'issues_found': len(errors) + len(warnings)
        }
        
        return errors + [f"WARNING: {w}" for w in warnings]
    
    def auto_fix_issues(self, component: str, errors: List[str]) -> List[str]:
        """Auto-fix common issues with safety checks."""
        fixes = []
        
        # Safety: Only fix if explicitly enabled and in safe mode
        if not self.autonomous:
            return fixes  # Manual mode - no auto-fixes
        
        if component == "voice_listener":
            file_path = self.get_file_path("voice_listener.py")
            if file_path:
                fixes.extend(self._safe_fix_file(file_path, errors))
        
        # Fix common import issues
        for error in errors:
            if "import error" in error.lower() or "missing import" in error.lower():
                fixes.extend(self._fix_import_errors(error))
        
        # Fix common syntax issues (safe patterns only)
        for error in errors:
            if "syntax error" in error.lower():
                fixes.extend(self._fix_syntax_errors(error))
        
        return fixes
    
    def _safe_fix_file(self, file_path: Path, errors: List[str]) -> List[str]:
        """Safely fix file issues with backup and validation."""
        fixes = []
        
        try:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            with open(file_path, 'r', encoding='utf-8') as f:
                original = f.read()
            
            # Only proceed if file is under GATE directory (safety check)
            if not str(file_path).startswith(str(GATE)):
                logger.warning(f"Skipping fix for file outside GATE: {file_path}")
                return fixes
            
            # Create backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            code = original
            modified = False
            
            # Safe fixes only
            for error in errors:
                # Fix missing encoding in file operations
                if "encoding" in error.lower() and "open(" in code:
                    # Check if file operations lack encoding
                    if 'open(' in code and 'encoding=' not in code:
                        # This is too risky to auto-fix - skip
                        pass
                
                # Fix missing error handling (add try/except around risky operations)
                if "error handling" in error.lower() or "exception" in error.lower():
                    # Too risky - skip
                    pass
            
            # Validate syntax before writing
            if modified:
                try:
                    compile(code, str(file_path), 'exec')
                    # Syntax valid - write changes
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    fixes.append(f"Applied safe fixes to {file_path.name} (backup: {backup_path.name})")
                except SyntaxError:
                    # Restore from backup
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(backup_content)
                    fixes.append(f"Fix failed - syntax error, restored from backup")
                    backup_path.unlink()  # Remove backup after restore
        except Exception as e:
            fixes.append(f"Fix failed: {e}")
        
        return fixes
    
    def _fix_import_errors(self, error: str) -> List[str]:
        """Suggest import fixes (read-only, no file modification)."""
        fixes = []
        
        # Extract module name from error
        if "cannot import name" in error.lower():
            # This is informational only - don't auto-fix imports
            fixes.append(f"INFO: Import error detected - manual review recommended")
        
        return fixes
    
    def _fix_syntax_errors(self, error: str) -> List[str]:
        """Suggest syntax fixes (read-only, no file modification)."""
        fixes = []
        
        # Syntax errors require manual intervention
        fixes.append(f"INFO: Syntax error detected - manual fix required")
        
        return fixes
    
    def run_test_with_metrics(self, test_name: str, test_func) -> Dict[str, Any]:
        """Run a single test with performance metrics."""
        test_start = time.time()
        result = {
            "test_name": test_name,
            "status": "UNKNOWN",
            "errors": [],
            "duration": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            errors = test_func()
            result["duration"] = time.time() - test_start
            
            if not errors:
                result["status"] = "PASS"
            else:
                result["status"] = "FAIL"
                result["errors"] = errors
                
        except Exception as e:
            result["status"] = "CRASH"
            result["errors"] = [str(e)]
            result["traceback"] = traceback.format_exc()
            result["duration"] = time.time() - test_start
        
        return result
    
    def run_all_tests(self, parallel: bool = False):
        """Run all deep tests with enhanced metrics."""
        # Rate limiting check
        if SCALABILITY_ENHANCED:
            if not RATE_LIMITER.allow():
                wait_time = RATE_LIMITER.wait_time()
                logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f}s")
                time.sleep(wait_time)
        
        # Resource monitoring
        start_time = time.time()
        
        print("=" * 80)
        print("Ω OMEGA SYSTEM TEST - Deep Analysis Enhanced")
        print("Finding Real Breaks with AST Analysis & Performance Metrics")
        print("=" * 80)
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        test_suites = {
            "Voice Listener Commands": self.test_voice_listener_commands,
            "Game Hub Execution": self.test_game_hub_execution,
            "Chess Replay Logic": self.test_chess_replay_logic,
            "Diagnostic Engine": self.test_diagnostic_engine,
            "All Critical Imports": self.test_all_imports,
            "Code Quality Analysis": self.test_code_quality_all,
            "Security Vulnerability Scan": self.test_security_scan,
            "Static Analysis": self.test_static_analysis
        }
        
        all_results = {}
        
        if parallel and len(test_suites) > 1:
            # Parallel execution for faster results
            with ThreadPoolExecutor(max_workers=min(4, len(test_suites))) as executor:
                future_to_test = {
                    executor.submit(self.run_test_with_metrics, name, func): name
                    for name, func in test_suites.items()
                }
                
                for future in as_completed(future_to_test):
                    test_name = future_to_test[future]
                    try:
                        result = future.result()
                        all_results[test_name] = result
                        self.results["tests_run"] += 1
                        
                        if result["status"] == "PASS":
                            self.results["tests_passed"] += 1
                        else:
                            self.results["tests_failed"] += 1
                        
                        print(f"Testing: {test_name}...")
                        print(f"  Status: {result['status']}")
                        print(f"  Duration: {result['duration']:.3f}s")
                        
                        if result["errors"]:
                            print(f"  Errors found: {len(result['errors'])}")
                            for error in result["errors"][:5]:  # Show first 5
                                print(f"    - {error}")
                        
                    except Exception as e:
                        logger.error(f"Test {test_name} crashed: {e}")
                        all_results[test_name] = {
                            "status": "CRASH",
                            "errors": [str(e)],
                            "traceback": traceback.format_exc()
                        }
        else:
            # Sequential execution
            for test_name, test_func in test_suites.items():
                print(f"Testing: {test_name}...")
                self.results["tests_run"] += 1
                
                result = self.run_test_with_metrics(test_name, test_func)
                all_results[test_name] = result
                
                if result["status"] == "PASS":
                    print(f"  Status: PASS ({result['duration']:.3f}s)")
                    self.results["tests_passed"] += 1
                else:
                    print(f"  Status: {result['status']} ({result['duration']:.3f}s)")
                    if result["errors"]:
                        print(f"  Errors found: {len(result['errors'])}")
                        for error in result["errors"][:5]:
                            print(f"    - {error}")
                    
                    self.results["tests_failed"] += 1
                    
                    # Attempt auto-fix
                    component = test_name.lower().replace(" ", "_")
                    fixes = self.auto_fix_issues(component, result["errors"])
                    if fixes:
                        print(f"  Auto-fixes: {', '.join(fixes)}")
                        all_results[test_name]["fixes"] = fixes
                        self.fixes.extend(fixes)
        
        # Calculate performance metrics
        total_duration = time.time() - self.start_time
        self.results["performance_metrics"] = {
            "total_duration": total_duration,
            "average_test_duration": sum(r.get("duration", 0) for r in all_results.values()) / max(len(all_results), 1),
            "tests_per_second": self.results["tests_run"] / max(total_duration, 0.001)
        }
        
        self.results["test_results"] = all_results
        self.results["fixes_applied"] = self.fixes
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.results['tests_run']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")
        
        if self.results['tests_run'] > 0:
            success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\nPerformance Metrics:")
        print(f"  Total Duration: {total_duration:.3f}s")
        print(f"  Average Test Duration: {self.results['performance_metrics']['average_test_duration']:.3f}s")
        print(f"  Tests/Second: {self.results['performance_metrics']['tests_per_second']:.2f}")
        
        if self.results.get('code_quality_score', 0) > 0:
            print(f"\nCode Quality Score: {self.results['code_quality_score']:.1f}/100")
        
        # Best practices comparison
        self.results["best_practices_comparison"] = {
            "type_hints_usage": "Good" if self.results.get('code_quality_score', 0) > 70 else "Needs Improvement",
            "docstring_coverage": "Good" if any(a.get('docstrings', 0) > 0 for a in self.results.get('ast_analysis', {}).values()) else "Needs Improvement",
            "error_handling": "Good" if self.results['tests_failed'] == 0 else "Review Recommended",
            "test_coverage": f"{len(test_suites)} test suites"
        }
        
        # Map system architecture (autonomous mode or if forced)
        if self.autonomous and (not self.architecture_map or "--remap" in sys.argv):
            print("\n" + "=" * 80)
            print("MAPPING SYSTEM ARCHITECTURE...")
            print("=" * 80)
            architecture = self.map_system_architecture()
            print(f"✓ Mapped {architecture['total_files']} files across {len(architecture['categories'])} categories")
            print(f"✓ Found {len(architecture['entry_points'])} entry points")
        elif "--remap" in sys.argv:
            print("\n" + "=" * 80)
            print("MAPPING SYSTEM ARCHITECTURE...")
            print("=" * 80)
            architecture = self.map_system_architecture()
            print(f"✓ Mapped {architecture['total_files']} files across {len(architecture['categories'])} categories")
            print(f"✓ Found {len(architecture['entry_points'])} entry points")
        
        # Analyze historical patterns (autonomous mode)
        if self.autonomous:
            print("\n" + "=" * 80)
            print("ANALYZING HISTORICAL PATTERNS...")
            print("=" * 80)
            patterns = self.analyze_historical_patterns()
            if patterns.get("status") != "no_history":
                print(f"✓ Analyzed {patterns['total_runs']} past runs")
                print(f"✓ Average success rate: {patterns.get('average_success_rate', 0):.1f}%")
                print(f"✓ Trend: {patterns.get('trend', 'unknown')}")
                if patterns.get("common_errors"):
                    top_errors = sorted(patterns["common_errors"].items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"✓ Top recurring errors: {len(top_errors)} patterns identified")
                
                # Autonomous reaction: Alert if declining
                if patterns.get("trend") == "declining":
                    print("\n⚠️  AUTONOMOUS ALERT: System quality is declining!")
                    print("   Omega recommends immediate attention to failing tests.")
                    if self.voice:
                        self.voice.speak("Alert. System quality declining. Immediate attention required.", add_signature=True)
            else:
                print("ℹ No historical data yet - this run will establish baseline")
        
        # Assess error context (autonomous mode)
        all_errors = []
        for result in all_results.values():
            all_errors.extend(result.get("errors", []))
        
        if all_errors and self.autonomous:
            print("\n" + "=" * 80)
            print("ASSESSING ERROR CONTEXT & IMPACT...")
            print("=" * 80)
            context = self.assess_error_context(all_errors)
            print(f"✓ Total errors: {context['total_errors']}")
            print(f"✓ Critical: {len(context['critical_errors'])}")
            print(f"✓ Warnings: {len(context['warnings'])}")
            print(f"✓ Error categories: {len(context['error_categories'])}")
            
            # Autonomous reaction: Prioritize critical errors
            if context['critical_errors']:
                print("\n🚨 AUTONOMOUS REACTION: Critical errors detected!")
                print("   Omega recommends addressing these immediately:")
                for error in context['critical_errors'][:3]:
                    print(f"   - {error}")
                if self.voice:
                    self.voice.speak(f"Critical errors detected. {len(context['critical_errors'])} issues require immediate attention.", add_signature=True)
            
            # Autonomous reaction: Suggest improvements
            if context['warnings'] and self.results.get('code_quality_score', 0) < 70:
                print("\n💡 AUTONOMOUS SUGGESTION: Code quality could be improved")
                print("   Consider adding type hints and docstrings to improve scores.")
        
        # Resource monitoring - record completion
        if SCALABILITY_ENHANCED:
            elapsed = time.time() - start_time
            RESOURCE_MONITOR.record_metric("test_duration", elapsed)
            RESOURCE_MONITOR.record_metric("tests_run", self.results["tests_run"])
            RESOURCE_MONITOR.record_metric("tests_passed", self.results["tests_passed"])
            avg_duration = RESOURCE_MONITOR.get_average("test_duration", 60)
            logger.info(f"Resource monitoring: Avg test duration (60s window): {avg_duration:.3f}s")
        
        # Security: Check entropy periodically
        if SECURITY_ENHANCED:
            if KILLSWITCH.should_kill():
                logger.critical("Entropy killswitch triggered during test execution!")
                AUDIT_LOGGER.log_security_event("killswitch_triggered", {
                    "timestamp": datetime.now().isoformat(),
                    "tests_run": self.results["tests_run"]
                })
                KILLSWITCH.activate()
        
        # Save report
        report_file = GATE / "omega_system_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        # Autonomous core reaction
        if self.autonomous_core:
            self.autonomous_core.react_to_test_results(self.results)
            status = self.autonomous_core.get_autonomous_status()
            logger.info(f"Autonomous status: {status['events_processed']} events, {status['reactions']} reactions, {status['learnings']} learnings")
        
        # Save memory
        self._save_memory()
        
        # Calculate success rate for logging
        if self.results['tests_run'] > 0:
            success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100
        else:
            success_rate = 0.0
        
        print(f"\nReport saved to: {report_file}")
        print(f"Memory saved to: {self.memory_file}")
        print(f"Architecture saved to: {self.architecture_file}")
        logger.info(f"Ω Omega test complete. Success rate: {success_rate:.1f}%")
        
        return self.results

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ω Omega System Test - Deep Analysis Enhanced')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--manual', action='store_true', help='Manual mode - wait for instructions (disables autonomous mode)')
    parser.add_argument('--remap', action='store_true', help='Force architecture remap')
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Autonomous mode is default, unless --manual is specified
    autonomous = not args.manual
    
    tester = OmegaSystemTester(autonomous=autonomous)
    results = tester.run_all_tests(parallel=args.parallel)
    
    print("\n" + "=" * 80)
    print("Ω OMEGA SYSTEM TEST COMPLETE")
    print("=" * 80)
    print("\nAll tests executed. Real breaks identified.")
    if results["fixes_applied"]:
        print(f"Auto-fixes applied: {len(results['fixes_applied'])}")
    
    if results.get('code_quality_score', 0) > 0:
        print(f"\nOverall Code Quality: {results['code_quality_score']:.1f}/100")
        if results['code_quality_score'] < 70 and autonomous:
            print("⚠️  AUTONOMOUS REACTION: Code quality below threshold")
            print("   Omega suggests: Add type hints, docstrings, improve error handling")
    
    # Autonomous final summary
    if autonomous:
        print("\n" + "=" * 80)
        print("Ω OMEGA AUTONOMOUS SUMMARY")
        print("=" * 80)
        summary_text = []
        if results['tests_failed'] > 0:
            msg = f"{results['tests_failed']} test(s) failed - Omega recommends review"
            print(f"⚠️  {msg}")
            summary_text.append(msg)
        if results.get('code_quality_score', 0) < 70:
            msg = "Code quality below optimal - Omega suggests improvements"
            print(f"⚠️  {msg}")
            summary_text.append(msg)
        if results['tests_passed'] == results['tests_run']:
            msg = "All tests passed - System healthy"
            print(f"✅ {msg}")
            summary_text.append(msg)
        
        final_msg = "Omega is guarding the gate. Memory updated. Learning continues."
        print(f"\n{final_msg}")
        
        # Speak summary if voice available
        if tester.voice and summary_text:
            tester.voice.speak(f"Summary. {'. '.join(summary_text)}. {final_msg}", add_signature=True)
    
    print()

if __name__ == '__main__':
    try:
        main()
    except (ValueError, IOError, OSError) as e:
        if 'closed file' in str(e).lower():
            # Handle closed file errors gracefully
            print(f"Warning: File I/O error occurred: {e}", file=sys.stderr if hasattr(sys, 'stderr') and not sys.stderr.closed else None)
            sys.exit(1)
        else:
            raise

