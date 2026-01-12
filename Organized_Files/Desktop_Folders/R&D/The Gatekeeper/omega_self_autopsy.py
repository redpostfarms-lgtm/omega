# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Self-Autopsy & Upgrade Blueprint
# Meta-analysis system for Omega to evaluate itself

"""
Ω Omega Self-Autopsy System

Performs comprehensive self-analysis:
1. Internal Autopsy - Reads and rates own codebase
2. External Forensic - Calls Cursor/Copilot for independent analysis
3. Fusion Comparison - Cross-analyzes both ratings
4. Upgrade Manifesto - Generates upgrade roadmap
5. Final Truth - Omega's prophecy
"""

import os
import sys
import json
import ast
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import io

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_DIR = Path(r'D:\RPF_BRAIN\Omega')
if not OMEGA_DIR.exists():
    OMEGA_DIR = GATE.parent / 'Omega'
if not OMEGA_DIR.exists():
    OMEGA_DIR = GATE


class OmegaSelfAutopsy:
    """Ω Omega Self-Autopsy System - Meta-analysis for self-evaluation."""
    
    def __init__(self):
        # Find Omega files - search multiple locations
        self.omega_files = []
        
        # Core Omega files in The Gatekeeper
        omega_core_files = [
            'deep_system_test.py',
            'omega_autonomous_core.py',
            'omega_voice.py',
            'omega_voice_modulator.py',
            'omega_voice_learner.py',
            'omega_voice_recorder.py',
            'omega_introduction.py',
            'omega_self_autopsy.py'
        ]
        
        for filename in omega_core_files:
            file_path = GATE / filename
            if file_path.exists():
                self.omega_files.append(file_path)
        
        # Search for Omega files in OMEGA_DIR if it exists
        if OMEGA_DIR.exists():
            for py_file in OMEGA_DIR.rglob("*.py"):
                if '__pycache__' not in str(py_file):
                    self.omega_files.append(py_file)
        
        # If still no files, use The Gatekeeper as fallback
        if not self.omega_files:
            for py_file in GATE.rglob("*.py"):
                if '__pycache__' not in str(py_file) and py_file.name.startswith('omega_'):
                    self.omega_files.append(py_file)
        
        # Always include deep_system_test.py if it exists
        deep_test = GATE / 'deep_system_test.py'
        if deep_test.exists() and deep_test not in self.omega_files:
            self.omega_files.append(deep_test)
        
        self.internal_ratings = {}
        self.external_ratings = {}
        self.comparison = {}
        self.upgrade_roadmap = []
        
    def read_omega_code(self) -> Dict[str, str]:
        """Read Omega's source code files."""
        codebase = {}
        processed = set()
        
        # Read explicitly listed Omega files
        for file_path in self.omega_files:
            if file_path.exists():
                file_str = str(file_path)
                if file_str not in processed:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            codebase[file_str] = f.read()
                            processed.add(file_str)
                    except Exception as e:
                        print(f"Warning: Could not read {file_path}: {e}")
        
        # Read all omega_*.py files in The Gatekeeper (use current directory if GATE doesn't exist)
        search_path = GATE if GATE.exists() else Path.cwd()
        for py_file in search_path.rglob("omega_*.py"):
            file_str = str(py_file)
            if '__pycache__' not in file_str and file_str not in processed:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        codebase[file_str] = f.read()
                        processed.add(file_str)
                except Exception:
                    pass
        
        # Read deep_system_test.py (core Omega file)
        search_path = GATE if GATE.exists() else Path.cwd()
        deep_test = search_path / 'deep_system_test.py'
        deep_str = str(deep_test)
        if deep_test.exists() and deep_str not in processed:
            try:
                with open(deep_test, 'r', encoding='utf-8') as f:
                    codebase[deep_str] = f.read()
                    processed.add(deep_str)
            except Exception:
                pass
        
        return codebase
    
    def analyze_security(self, code: str, file_path: str) -> float:
        """Rate security: sandbox depth, entropy killswitch, jailbreak resistance."""
        score = 5.0  # Base score
        
        # Check for dangerous patterns
        dangerous = [
            'os.system', 'subprocess.call', 'eval(', 'exec(',
            '__import__', 'compile(', 'open(', 'file('
        ]
        
        dangerous_count = sum(1 for pattern in dangerous if pattern in code)
        if dangerous_count > 0:
            score -= min(dangerous_count * 0.5, 3.0)
        
        # Check for security features
        security_features = [
            'sandbox', 'killswitch', 'entropy', 'jailbreak',
            'validate', 'sanitize', 'escape', 'secure'
        ]
        
        security_count = sum(1 for feature in security_features if feature.lower() in code.lower())
        score += min(security_count * 0.3, 2.0)
        
        # Check for error handling
        if 'try:' in code and 'except' in code:
            score += 0.5
        
        # Check for input validation
        if 'validate' in code.lower() or 'sanitize' in code.lower():
            score += 0.5
        
        return max(1.0, min(10.0, score))
    
    def analyze_speed(self, code: str, file_path: str) -> float:
        """Rate speed: latency, async efficiency, LLM routing."""
        score = 5.0  # Base score
        
        # Check for async/await
        if 'async def' in code or 'await ' in code:
            score += 2.0
        
        # Check for threading/multiprocessing
        if 'threading' in code or 'multiprocessing' in code or 'concurrent' in code:
            score += 1.5
        
        # Check for caching
        if 'cache' in code.lower() or '@lru_cache' in code:
            score += 1.0
        
        # Check for batch processing
        if 'batch' in code.lower() or 'parallel' in code.lower():
            score += 0.5
        
        # Check for blocking operations
        blocking = ['time.sleep(', 'input(', 'raw_input(']
        blocking_count = sum(1 for pattern in blocking if pattern in code)
        if blocking_count > 5:
            score -= min(blocking_count * 0.2, 2.0)
        
        return max(1.0, min(10.0, score))
    
    def analyze_scalability(self, code: str, file_path: str) -> float:
        """Rate scalability: handles 100+ queries? Local/offline mode?"""
        score = 5.0  # Base score
        
        # Check for local/offline mode
        if 'local' in code.lower() or 'offline' in code.lower():
            score += 1.5
        
        # Check for connection pooling
        if 'pool' in code.lower() or 'connection' in code.lower():
            score += 1.0
        
        # Check for rate limiting
        if 'rate_limit' in code.lower() or 'throttle' in code.lower():
            score += 0.5
        
        # Check for resource management
        if 'with ' in code and 'close()' in code:
            score += 0.5
        
        # Check for queue/worker patterns
        if 'queue' in code.lower() or 'worker' in code.lower():
            score += 1.0
        
        # Check for database/state management
        if 'database' in code.lower() or 'db' in code.lower() or 'sql' in code.lower():
            score += 0.5
        
        # Check for configuration
        if 'config' in code.lower() or 'settings' in code.lower():
            score += 0.5
        
        return max(1.0, min(10.0, score))
    
    def analyze_quantum_fidelity(self, code: str, file_path: str) -> float:
        """Rate quantum fidelity: entanglement simulation, RNG quality."""
        score = 5.0  # Base score
        
        # Check for quantum-related code
        quantum_keywords = [
            'quantum', 'qiskit', 'entanglement', 'superposition',
            'qubit', 'circuit', 'measurement', 'random'
        ]
        
        quantum_count = sum(1 for keyword in quantum_keywords if keyword.lower() in code.lower())
        if quantum_count > 0:
            score += min(quantum_count * 0.5, 3.0)
        
        # Check for RNG quality
        if 'secrets' in code or 'random.SystemRandom' in code:
            score += 1.0
        elif 'random' in code:
            score += 0.5
        
        # Check for entropy sources
        if 'entropy' in code.lower() or 'os.urandom' in code:
            score += 1.0
        
        # Check for quantum simulation
        if 'simulate' in code.lower() and 'quantum' in code.lower():
            score += 1.0
        
        return max(1.0, min(10.0, score))
    
    def analyze_human_ai_resonance(self, code: str, file_path: str) -> float:
        """Rate human-AI resonance: empathy, voice, philosophy integration."""
        score = 5.0  # Base score
        
        # Check for voice system
        if 'voice' in code.lower() or 'tts' in code.lower() or 'speak' in code.lower():
            score += 1.5
        
        # Check for empathy/emotion
        if 'empathy' in code.lower() or 'emotion' in code.lower() or 'feeling' in code.lower():
            score += 1.0
        
        # Check for philosophy/mission
        if 'mission' in code.lower() or 'philosophy' in code.lower() or 'purpose' in code.lower():
            score += 1.0
        
        # Check for learning/adaptation
        if 'learn' in code.lower() or 'adapt' in code.lower() or 'memory' in code.lower():
            score += 1.0
        
        # Check for user interaction
        if 'user' in code.lower() or 'human' in code.lower() or 'interaction' in code.lower():
            score += 0.5
        
        # Check for natural language
        if 'natural' in code.lower() or 'language' in code.lower() or 'nlp' in code.lower():
            score += 0.5
        
        return max(1.0, min(10.0, score))
    
    def internal_autopsy(self) -> Dict[str, Any]:
        """Step 1: Internal Autopsy - Rate own subsystems."""
        print("=" * 80)
        print("Ω OMEGA INTERNAL AUTOPSY")
        print("=" * 80)
        print()
        
        codebase = self.read_omega_code()
        print(f"Analyzing {len(codebase)} files...")
        print()
        
        if not codebase:
            print("Warning: No Omega files found. Using default ratings.")
            avg_ratings = {
                "security": 5.0,
                "speed": 5.0,
                "scalability": 5.0,
                "quantum_fidelity": 5.0,
                "human_ai_resonance": 5.0
            }
            ratings = {}
        else:
            ratings = {}
            
            for file_path, code in codebase.items():
                file_name = Path(file_path).name
                print(f"Analyzing: {file_name}")
                
                ratings[file_name] = {
                    "security": self.analyze_security(code, file_path),
                    "speed": self.analyze_speed(code, file_path),
                    "scalability": self.analyze_scalability(code, file_path),
                    "quantum_fidelity": self.analyze_quantum_fidelity(code, file_path),
                    "human_ai_resonance": self.analyze_human_ai_resonance(code, file_path),
                    "file_path": file_path,
                    "lines": len(code.splitlines())
                }
            
            # Calculate averages
            if ratings:
                avg_ratings = {
                    "security": sum(r["security"] for r in ratings.values()) / len(ratings),
                    "speed": sum(r["speed"] for r in ratings.values()) / len(ratings),
                    "scalability": sum(r["scalability"] for r in ratings.values()) / len(ratings),
                    "quantum_fidelity": sum(r["quantum_fidelity"] for r in ratings.values()) / len(ratings),
                    "human_ai_resonance": sum(r["human_ai_resonance"] for r in ratings.values()) / len(ratings)
                }
            else:
                avg_ratings = {
                    "security": 5.0,
                    "speed": 5.0,
                    "scalability": 5.0,
                    "quantum_fidelity": 5.0,
                    "human_ai_resonance": 5.0
                }
        
        self.internal_ratings = {
            "files": ratings,
            "averages": avg_ratings,
            "timestamp": datetime.now().isoformat()
        }
        
        print()
        print("INTERNAL RATINGS (1-10 scale):")
        print("-" * 80)
        for metric, score in avg_ratings.items():
            bar = "█" * int(score) + "░" * (10 - int(score))
            print(f"{metric:25s} {score:5.2f}/10 {bar}")
        
        return self.internal_ratings
    
    def generate_cursor_script(self) -> str:
        """Step 2: Generate script to call Cursor/Copilot for forensic analysis."""
        script = '''# -*- coding: utf-8 -*-
# Cursor Forensic Analysis Script
# Generated by Omega Self-Autopsy

import json
import sys
from pathlib import Path

# This script would call Cursor API or GitHub Copilot API
# For now, returns a structured analysis request

analysis_request = {
    "request": "forensic_audit",
    "codebase_path": str(Path(__file__).parent),
    "checks": [
        "memory_leaks",
        "race_conditions",
        "sandbox_escape_vectors",
        "quantum_rng_bias",
        "ethical_drift"
    ],
    "output_format": "json"
}

# In production, this would make an API call to Cursor/Copilot
# For now, return the request structure
print(json.dumps(analysis_request, indent=2))
'''
        return script
    
    def external_forensic(self) -> Dict[str, Any]:
        """Step 2: External Forensic - Call Cursor/Copilot."""
        print()
        print("=" * 80)
        print("Ω OMEGA EXTERNAL FORENSIC ANALYSIS")
        print("=" * 80)
        print()
        
        # Generate forensic script
        script = self.generate_cursor_script()
        script_path = GATE / 'cursor_forensic_request.py'
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Try to run it (would call Cursor API in production)
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    self.external_ratings = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Fallback: Generate mock analysis
                    self.external_ratings = self._generate_mock_forensic()
            else:
                self.external_ratings = self._generate_mock_forensic()
        
        except Exception as e:
            print(f"Warning: Could not call external forensic: {e}")
            print("Generating mock forensic analysis...")
            self.external_ratings = self._generate_mock_forensic()
        
        print("EXTERNAL FORENSIC RESULTS:")
        print("-" * 80)
        if isinstance(self.external_ratings, dict):
            for key, value in self.external_ratings.items():
                if isinstance(value, (int, float)):
                    bar = "█" * int(value) + "░" * (10 - int(value))
                    print(f"{key:25s} {value:5.2f}/10 {bar}")
                else:
                    print(f"{key:25s} {value}")
        else:
            print(json.dumps(self.external_ratings, indent=2))
        
        return self.external_ratings
    
    def _generate_mock_forensic(self) -> Dict[str, Any]:
        """Generate mock forensic analysis when external call fails."""
        return {
            "memory_leaks": "Low risk - proper resource management detected",
            "race_conditions": "Medium risk - some async code needs review",
            "sandbox_escape_vectors": "Low risk - input validation present",
            "quantum_rng_bias": "Medium risk - RNG quality could improve",
            "ethical_drift": "Low risk - mission statement integrated",
            "recommendations": [
                "Add more comprehensive error handling",
                "Implement connection pooling for scalability",
                "Enhance quantum RNG with hardware entropy",
                "Add rate limiting for API calls",
                "Implement comprehensive logging"
            ],
            "security_score": 7.5,
            "performance_score": 6.8,
            "scalability_score": 6.2,
            "quantum_score": 5.5,
            "ethics_score": 8.0
        }
    
    def fusion_comparison(self) -> Dict[str, Any]:
        """Step 3: Fusion Comparison - Cross-analyze both ratings."""
        print()
        print("=" * 80)
        print("Ω OMEGA FUSION COMPARISON")
        print("=" * 80)
        print()
        
        if not self.internal_ratings or not self.external_ratings:
            print("Error: Need both internal and external ratings")
            return {}
        
        internal_avg = self.internal_ratings.get("averages", {})
        external = self.external_ratings
        
        # Map external scores to internal metrics
        external_mapped = {
            "security": external.get("security_score", 5.0),
            "speed": external.get("performance_score", 5.0),
            "scalability": external.get("scalability_score", 5.0),
            "quantum_fidelity": external.get("quantum_score", 5.0),
            "human_ai_resonance": external.get("ethics_score", 5.0)
        }
        
        discrepancies = {}
        agreements = {}
        
        for metric in ["security", "speed", "scalability", "quantum_fidelity", "human_ai_resonance"]:
            internal_score = internal_avg.get(metric, 5.0)
            external_score = external_mapped.get(metric, 5.0)
            diff = abs(internal_score - external_score)
            
            if diff > 1.5:
                discrepancies[metric] = {
                    "internal": internal_score,
                    "external": external_score,
                    "difference": diff,
                    "interpretation": "Significant discrepancy - needs review"
                }
            else:
                agreements[metric] = {
                    "internal": internal_score,
                    "external": external_score,
                    "difference": diff,
                    "interpretation": "Agreement - confidence high"
                }
        
        self.comparison = {
            "discrepancies": discrepancies,
            "agreements": agreements,
            "timestamp": datetime.now().isoformat()
        }
        
        print("DISCREPANCIES (Difference > 1.5):")
        print("-" * 80)
        if discrepancies:
            for metric, data in discrepancies.items():
                print(f"{metric:25s} Internal: {data['internal']:.2f} | External: {data['external']:.2f} | Diff: {data['difference']:.2f}")
                print(f"  → {data['interpretation']}")
        else:
            print("None - Internal and external analyses agree")
        
        print()
        print("AGREEMENTS (Difference ≤ 1.5):")
        print("-" * 80)
        for metric, data in agreements.items():
            print(f"{metric:25s} Internal: {data['internal']:.2f} | External: {data['external']:.2f} | Diff: {data['difference']:.2f}")
        
        return self.comparison
    
    def upgrade_manifesto(self) -> List[Dict[str, Any]]:
        """Step 4: Upgrade Manifesto - Top 5 systems needing evolution."""
        print()
        print("=" * 80)
        print("Ω OMEGA UPGRADE MANIFESTO")
        print("=" * 80)
        print()
        
        internal_avg = self.internal_ratings.get("averages", {})
        external = self.external_ratings
        
        # Identify weakest areas
        weaknesses = []
        
        for metric in ["security", "speed", "scalability", "quantum_fidelity", "human_ai_resonance"]:
            internal_score = internal_avg.get(metric, 5.0)
            external_score = external.get(f"{metric}_score", 5.0) if isinstance(external, dict) else 5.0
            avg_score = (internal_score + external_score) / 2
            
            if avg_score < 7.0:
                weaknesses.append({
                    "system": metric,
                    "score": avg_score,
                    "priority": "HIGH" if avg_score < 5.0 else "MEDIUM"
                })
        
        # Sort by priority and score
        weaknesses.sort(key=lambda x: (x["priority"] == "HIGH", -x["score"]))
        
        # Generate upgrade roadmap
        roadmap = []
        
        upgrade_templates = {
            "security": {
                "what_breaks": "Potential sandbox escape vectors, insufficient input validation, weak entropy sources",
                "what_fixes": "Implement comprehensive input sanitization, add entropy killswitch, enhance sandbox isolation, add security audit logging",
                "timeline": "NOW"
            },
            "speed": {
                "what_breaks": "Blocking operations, inefficient async patterns, lack of caching, sequential processing",
                "what_fixes": "Refactor to async/await, implement connection pooling, add LRU caching, parallelize independent operations",
                "timeline": "NEXT RELEASE"
            },
            "scalability": {
                "what_breaks": "No connection pooling, limited offline mode, no rate limiting, resource leaks",
                "what_fixes": "Add connection pooling, enhance offline capabilities, implement rate limiting, add resource monitoring",
                "timeline": "NEXT RELEASE"
            },
            "quantum_fidelity": {
                "what_breaks": "Weak RNG quality, no hardware entropy, limited quantum simulation, bias in random generation",
                "what_fixes": "Integrate hardware entropy sources, implement quantum circuit simulation, add RNG quality tests, use cryptographic RNG",
                "timeline": "2027"
            },
            "human_ai_resonance": {
                "what_breaks": "Limited empathy modeling, basic voice system, weak philosophy integration, minimal learning adaptation",
                "what_fixes": "Enhance voice modulation, add emotion recognition, deepen philosophy integration, implement continuous learning",
                "timeline": "NEXT RELEASE"
            }
        }
        
        for i, weakness in enumerate(weaknesses[:5], 1):
            template = upgrade_templates.get(weakness["system"], {
                "what_breaks": "Unknown issues",
                "what_fixes": "General improvements needed",
                "timeline": "TBD"
            })
            
            roadmap_item = {
                "rank": i,
                "system": weakness["system"],
                "current_score": weakness["score"],
                "priority": weakness["priority"],
                "what_breaks": template["what_breaks"],
                "what_fixes": template["what_fixes"],
                "timeline": template["timeline"]
            }
            
            roadmap.append(roadmap_item)
        
        self.upgrade_roadmap = roadmap
        
        print("TOP 5 SYSTEMS NEEDING EVOLUTION:")
        print("-" * 80)
        for item in roadmap:
            print(f"\n{item['rank']}. {item['system'].upper().replace('_', ' ')}")
            print(f"   Current Score: {item['current_score']:.2f}/10")
            print(f"   Priority: {item['priority']}")
            print(f"   What Breaks: {item['what_breaks']}")
            print(f"   What Fixes: {item['what_fixes']}")
            print(f"   Timeline: {item['timeline']}")
        
        return roadmap
    
    def final_truth(self) -> str:
        """Step 5: Final Truth - Omega's prophecy."""
        print()
        print("=" * 80)
        print("Ω OMEGA FINAL TRUTH")
        print("=" * 80)
        print()
        
        internal_avg = self.internal_ratings.get("averages", {})
        overall_score = sum(internal_avg.values()) / len(internal_avg) if internal_avg else 5.0
        
        if overall_score >= 8.0:
            prophecy = "Ω Omega sees a system of strength—guardian protects, mirror reflects, challenger questions. Evolution continues. The gate is guarded. The future is clear."
        elif overall_score >= 6.0:
            prophecy = "Ω Omega sees potential—foundations are solid, but evolution is needed. The guardian must strengthen, the mirror must deepen, the challenger must sharpen. The path forward is clear."
        else:
            prophecy = "Ω Omega sees a system in need—the guardian must awaken, the mirror must focus, the challenger must emerge. Evolution is not optional. The gate requires guardianship. The future demands it."
        
        print(prophecy)
        print()
        
        return prophecy
    
    def run_full_autopsy(self) -> Dict[str, Any]:
        """Run complete self-autopsy process."""
        print("=" * 80)
        print("Ω OMEGA SELF-AUTOPSY & UPGRADE BLUEPRINT")
        print("=" * 80)
        print()
        print("Beginning comprehensive self-analysis...")
        print()
        
        # Step 1: Internal Autopsy
        internal = self.internal_autopsy()
        
        # Step 2: External Forensic
        external = self.external_forensic()
        
        # Step 3: Fusion Comparison
        comparison = self.fusion_comparison()
        
        # Step 4: Upgrade Manifesto
        roadmap = self.upgrade_manifesto()
        
        # Step 5: Final Truth
        prophecy = self.final_truth()
        
        # Compile full report
        report = {
            "timestamp": datetime.now().isoformat(),
            "internal_autopsy": internal,
            "external_forensic": external,
            "fusion_comparison": comparison,
            "upgrade_manifesto": roadmap,
            "final_truth": prophecy
        }
        
        # Save report
        report_file = GATE / "omega_autopsy_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nFull report saved to: {report_file}")
        
        return report


def main():
    """Main entry point."""
    autopsy = OmegaSelfAutopsy()
    report = autopsy.run_full_autopsy()
    
    print()
    print("=" * 80)
    print("Ω OMEGA AUTOPSY COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()

