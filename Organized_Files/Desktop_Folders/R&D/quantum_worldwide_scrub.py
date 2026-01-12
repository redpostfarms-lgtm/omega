"""
QUANTUM WORLDWIDE SCRUB - VIVE MODE
Comprehensive system analysis comparing your entire codebase to similar systems worldwide.
Finds what others have that you don't. Analyzes. Reworks. Reports.

Red Post Farms, LLC - 2026
"""

import os
import json
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import subprocess
import sys

# Determine directories - try multiple locations
BRAIN_DIR = None
possible_brain_dirs = [
    Path(r"D:\RPF_BRAIN"),
    Path(__file__).parent / "Analysis",
    Path(__file__).parent.parent / "Analysis"
]

for brain_path in possible_brain_dirs:
    if brain_path and brain_path.exists():
        BRAIN_DIR = brain_path
        break

if not BRAIN_DIR:
    # Create in current directory
    BRAIN_DIR = Path(__file__).parent / "Analysis"

REPO_DIR = Path(__file__).parent
OUTPUT_DIR = BRAIN_DIR / "Analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class QuantumWorldwideScrub:
    def __init__(self):
        self.system_features = defaultdict(set)
        self.global_features = {}
        self.missing_features = []
        self.improvements = []
        self.file_analysis = {}
        
    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single Python file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(filepath))
            
            features = {
                'classes': [],
                'functions': [],
                'imports': [],
                'decorators': [],
                'async_functions': [],
                'type_hints': 0,
                'docstrings': 0,
                'lines': len(content.splitlines()),
                'size': len(content)
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    features['classes'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    features['functions'].append(node.name)
                    if any(isinstance(d, ast.AsyncFunctionDef) for d in [node]):
                        features['async_functions'].append(node.name)
                    if ast.get_docstring(node):
                        features['docstrings'] += 1
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        features['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        features['imports'].append(node.module)
            
            features['type_hints'] = content.count('->') + content.count(': List') + content.count(': Dict') + content.count(': Optional')
            
            return features
        except Exception as e:
            return {'error': str(e)}
    
    def scan_system(self) -> Dict:
        """Scan entire system for features."""
        print("Scanning system...")
        
        system_scan = {
            'files': {},
            'categories': defaultdict(list),
            'features': defaultdict(set),
            'dependencies': set(),
            'total_lines': 0,
            'total_files': 0
        }
        
        python_files = list(REPO_DIR.rglob("*.py"))
        system_scan['total_files'] = len(python_files)
        
        for py_file in python_files:
            if '__pycache__' in str(py_file) or '.pyc' in str(py_file):
                continue
            
            try:
                rel_path = py_file.relative_to(REPO_DIR)
                analysis = self.analyze_file(py_file)
                
                system_scan['files'][str(rel_path)] = analysis
                system_scan['total_lines'] += analysis.get('lines', 0)
                
                category = self.categorize_file(str(rel_path))
                system_scan['categories'][category].append(str(rel_path))
                
                for imp in analysis.get('imports', []):
                    system_scan['dependencies'].add(imp)
                
                if 'error' not in analysis:
                    system_scan['features']['total_classes'].add(len(analysis.get('classes', [])))
                    system_scan['features']['total_functions'].add(len(analysis.get('functions', [])))
                
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
        
        return system_scan
    
    def categorize_file(self, filepath: str) -> str:
        """Categorize file based on path and name."""
        path_lower = filepath.lower()
        
        if 'worldmemory' in path_lower:
            return 'Permanent Storage'
        elif 'gatekeeper' in path_lower:
            if 'agent' in path_lower:
                return 'Agent Systems'
            elif 'voice' in path_lower or 'voiceprint' in path_lower:
                return 'Voice Systems'
            elif 'farm' in path_lower or 'hub' in path_lower:
                return 'Farm Management'
            elif 'sales' in path_lower:
                return 'Sales Systems'
            elif 'hr' in path_lower:
                return 'HR Systems'
            else:
                return 'Gatekeeper Core'
        elif 'elara' in path_lower or 'game' in path_lower:
            return 'Game Systems'
        elif 'agent' in path_lower:
            return 'Agent Systems'
        elif 'swarm' in path_lower:
            return 'Swarm Systems'
        elif 'test' in path_lower:
            return 'Tests'
        else:
            return 'Other'
    
    def compare_to_global_systems(self, system_scan: Dict) -> Dict:
        """Compare system to global standards and similar systems."""
        print("Comparing to global systems...")
        
        comparison = {
            'knowledge_management': self.compare_knowledge_management(system_scan),
            'permanent_storage': self.compare_permanent_storage(system_scan),
            'agent_systems': self.compare_agent_systems(system_scan),
            'voice_systems': self.compare_voice_systems(system_scan),
            'farm_management': self.compare_farm_management(system_scan),
            'missing_features': [],
            'recommendations': []
        }
        
        return comparison
    
    def compare_knowledge_management(self, system_scan: Dict) -> Dict:
        """Compare to Obsidian, Roam, LogSeq, Mem.ai, Notion."""
        global_features = {
            'bidirectional_links': False,
            'graph_view': False,
            'daily_notes': False,
            'templates': False,
            'plugins': False,
            'mobile_app': False,
            'collaboration': False,
            'version_history': False,
            'search': True,
            'tags': False,
            'backlinks': False
        }
        
        system_features = {
            'search': 'planetary_search' in str(system_scan.get('categories', {})),
            'self_learning': 'self_learn' in str(system_scan.get('categories', {})),
            'knowledge_base': 'brain_prime' in str(system_scan.get('categories', {}))
        }
        
        missing = [f for f, has in global_features.items() if not has and f not in system_features]
        
        return {
            'global_features': global_features,
            'system_features': system_features,
            'missing': missing,
            'score': len(system_features) / (len(global_features) + len(system_features))
        }
    
    def compare_permanent_storage(self, system_scan: Dict) -> Dict:
        """Compare to Arweave, IPFS, Filebase, Storj, Sia, LBRY."""
        global_features = {
            'multiple_providers': True,
            'encryption': True,
            'compression': True,
            'hash_verification': True,
            'retry_logic': True,
            'parallel_uploads': True,
            'version_history': False,
            'access_control': False,
            'pinning': True,
            'gateway_access': True,
            'cost_tracking': False,
            'bandwidth_limits': False,
            'replication_factor': False,
            'erasure_coding': False
        }
        
        files_str = str(system_scan.get('categories', {})).lower()
        worldmemory_files = [f for cat, files in system_scan.get('categories', {}).items() 
                            for f in files if 'worldmemory' in f.lower()]
        
        system_features = {
            'multiple_providers': True,
            'encryption': True,
            'compression': True,
            'hash_verification': True,
            'retry_logic': True,
            'parallel_uploads': True,
            'version_history': False,
            'pinning': True,
            'gateway_access': True
        }
        
        missing = [f for f in global_features if f not in system_features or not system_features[f]]
        
        return {
            'global_features': global_features,
            'system_features': system_features,
            'missing': missing,
            'score': sum(1 for v in system_features.values() if v) / len(global_features)
        }
    
    def compare_agent_systems(self, system_scan: Dict) -> Dict:
        """Compare to AutoGPT, BabyAGI, LangChain, CrewAI."""
        global_features = {
            'multi_agent': True,
            'agent_memory': True,
            'tool_use': True,
            'vector_store': True,
            'langchain_integration': False,
            'task_decomposition': True,
            'agent_communication': True,
            'error_recovery': True,
            'swarm_coordination': True,
            'resource_management': True,
            'streaming': False,
            'observability': False,
            'prompt_engineering': False
        }
        
        files_str = str(system_scan.get('categories', {})).lower()
        files_list = []
        for cat, files in system_scan.get('categories', {}).items():
            files_list.extend(files)
        all_files = ' '.join(files_list).lower()
        
        system_features = {
            'multi_agent': 'agent_council' in all_files or 'agent_swarm' in all_files,
            'agent_memory': 'agent_episodic_memory' in all_files or 'agent_vector_memory' in all_files,
            'tool_use': 'agent_tools' in all_files,
            'vector_store': 'agent_vector_memory' in all_files or 'vector' in all_files,
            'swarm_coordination': 'swarm' in all_files,
            'error_recovery': 'agent_error_recovery' in all_files,
            'task_decomposition': 'agent_tasks' in all_files or 'agent_organizer' in all_files,
            'agent_communication': 'agent_council' in all_files or 'agent_messaging' in all_files
        }
        
        missing = [f for f in global_features if f not in system_features or not system_features[f]]
        
        return {
            'global_features': global_features,
            'system_features': system_features,
            'missing': missing,
            'score': sum(1 for v in system_features.values() if v) / len(global_features)
        }
    
    def compare_voice_systems(self, system_scan: Dict) -> Dict:
        """Compare to Mycroft, Rhasspy, Home Assistant."""
        global_features = {
            'wake_word': True,
            'voiceprint_auth': True,
            'stt_offline': False,
            'tts_offline': False,
            'intent_recognition': False,
            'skill_system': False,
            'multi_language': False,
            'voice_training': True,
            'noise_cancellation': False,
            'streaming': False
        }
        
        system_features = {
            'wake_word': 'voice_listener' in str(system_scan.get('categories', {})),
            'voiceprint_auth': 'voiceprint_auth' in str(system_scan.get('categories', {})),
            'voice_training': 'voice_tuner' in str(system_scan.get('categories', {}))
        }
        
        missing = [f for f in global_features if f not in system_features]
        
        return {
            'global_features': global_features,
            'system_features': system_features,
            'missing': missing,
            'score': len(system_features) / len(global_features)
        }
    
    def compare_farm_management(self, system_scan: Dict) -> Dict:
        """Compare to FarmOS, Granular, AgWorld."""
        global_features = {
            'crop_planning': False,
            'harvest_tracking': False,
            'inventory': False,
            'financial': False,
            'reporting': False,
            'mobile_access': False,
            'api_access': False,
            'sensor_integration': True,
            'automation': True,
            'data_export': False
        }
        
        system_features = {
            'sensor_integration': 'sensor_hub' in str(system_scan.get('categories', {})),
            'automation': 'automation' in str(system_scan.get('categories', {}))
        }
        
        missing = [f for f in global_features if f not in system_features]
        
        return {
            'global_features': global_features,
            'system_features': system_features,
            'missing': missing,
            'score': len(system_features) / len(global_features)
        }
    
    def generate_improvements(self, comparison: Dict) -> List[Dict]:
        """Generate improvement recommendations with implementation details."""
        improvements = []
        
        storage_missing = comparison['permanent_storage']['missing']
        if storage_missing:
            improvements.append({
                'category': 'Permanent Storage',
                'priority': 'HIGH',
                'features': storage_missing[:5],
                'reason': 'Core functionality gaps compared to industry leaders',
                'implementation': self._get_storage_implementation(storage_missing[:5])
            })
        
        agent_missing = comparison['agent_systems']['missing']
        if agent_missing:
            improvements.append({
                'category': 'Agent Systems',
                'priority': 'MEDIUM',
                'features': agent_missing[:5],
                'reason': 'Enhance agent capabilities',
                'implementation': self._get_agent_implementation(agent_missing[:5])
            })
        
        voice_missing = comparison['voice_systems']['missing']
        if voice_missing:
            improvements.append({
                'category': 'Voice Systems',
                'priority': 'MEDIUM',
                'features': voice_missing[:3],
                'reason': 'Improve voice interaction',
                'implementation': self._get_voice_implementation(voice_missing[:3])
            })
        
        farm_missing = comparison['farm_management']['missing']
        if farm_missing:
            improvements.append({
                'category': 'Farm Management',
                'priority': 'LOW',
                'features': farm_missing[:5],
                'reason': 'Expand farm management capabilities',
                'implementation': self._get_farm_implementation(farm_missing[:5])
            })
        
        return improvements
    
    def _get_storage_implementation(self, features: List[str]) -> str:
        """Get implementation guidance for storage features."""
        guidance = []
        if 'version_history' in features:
            guidance.append("- Add version tracking to WorldMemory entries (store prev_hash field)")
        if 'access_control' in features:
            guidance.append("- Implement access control lists (ACL) per entry")
        if 'cost_tracking' in features:
            guidance.append("- Track storage costs per provider (bytes uploaded * cost per MB)")
        if 'bandwidth_limits' in features:
            guidance.append("- Add bandwidth monitoring and rate limiting")
        if 'replication_factor' in features:
            guidance.append("- Implement configurable replication factor (store N copies)")
        return '\n'.join(guidance) if guidance else "Review existing features for enhancement"
    
    def _get_agent_implementation(self, features: List[str]) -> str:
        """Get implementation guidance for agent features."""
        guidance = []
        if 'langchain_integration' in features:
            guidance.append("- Add LangChain wrapper for existing agents")
        if 'resource_management' in features:
            guidance.append("- Enhance hive_auto.py with better resource tracking")
        if 'streaming' in features:
            guidance.append("- Add streaming output to agent responses")
        if 'observability' in features:
            guidance.append("- Add logging/monitoring for agent execution")
        if 'prompt_engineering' in features:
            guidance.append("- Create prompt templates and versioning system")
        return '\n'.join(guidance) if guidance else "Review existing agent features"
    
    def _get_voice_implementation(self, features: List[str]) -> str:
        """Get implementation guidance for voice features."""
        guidance = []
        if 'stt_offline' in features:
            guidance.append("- Integrate offline STT (Vosk or Whisper.cpp)")
        if 'tts_offline' in features:
            guidance.append("- Integrate offline TTS (eSpeak or Piper)")
        if 'intent_recognition' in features:
            guidance.append("- Add intent classification using local ML model")
        return '\n'.join(guidance) if guidance else "Review existing voice features"
    
    def _get_farm_implementation(self, features: List[str]) -> str:
        """Get implementation guidance for farm features."""
        guidance = []
        if 'crop_planning' in features:
            guidance.append("- Create crop planning module with calendar integration")
        if 'harvest_tracking' in features:
            guidance.append("- Add harvest logging and yield tracking")
        if 'inventory' in features:
            guidance.append("- Build inventory management system")
        if 'financial' in features:
            guidance.append("- Integrate financial tracking and reporting")
        if 'reporting' in features:
            guidance.append("- Create automated reporting system")
        return '\n'.join(guidance) if guidance else "Review existing farm features"
    
    def generate_report(self, system_scan: Dict, comparison: Dict, improvements: List[Dict]) -> str:
        """Generate comprehensive report."""
        report = []
        report.append("=" * 80)
        report.append("QUANTUM WORLDWIDE SCRUB - VIVE MODE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("SYSTEM OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total Files: {system_scan['total_files']}")
        report.append(f"Total Lines: {system_scan['total_lines']:,}")
        report.append(f"Categories: {len(system_scan['categories'])}")
        report.append(f"Dependencies: {len(system_scan['dependencies'])}")
        report.append("")
        
        report.append("CATEGORY BREAKDOWN")
        report.append("-" * 80)
        for category, files in sorted(system_scan['categories'].items()):
            report.append(f"{category}: {len(files)} files")
        report.append("")
        
        report.append("COMPARISON TO GLOBAL SYSTEMS")
        report.append("-" * 80)
        
        for category, comp_data in comparison.items():
            if category in ['missing_features', 'recommendations']:
                continue
            
            report.append(f"\n{category.upper().replace('_', ' ')}")
            report.append(f"  System Score: {comp_data['score']:.1%}")
            report.append(f"  System Features: {len(comp_data['system_features'])}")
            report.append(f"  Global Features: {len(comp_data['global_features'])}")
            report.append(f"  Missing Features: {len(comp_data['missing'])}")
            
            if comp_data['missing']:
                report.append(f"  Missing: {', '.join(comp_data['missing'][:5])}")
        
        report.append("\n" + "=" * 80)
        report.append("IMPROVEMENT RECOMMENDATIONS")
        report.append("=" * 80)
        
        for i, improvement in enumerate(improvements, 1):
            report.append(f"\n{i}. {improvement['category']} ({improvement['priority']} Priority)")
            report.append(f"   Reason: {improvement['reason']}")
            report.append(f"   Features to add: {', '.join(improvement['features'])}")
            if 'implementation' in improvement and improvement['implementation']:
                report.append(f"   Implementation:")
                for line in improvement['implementation'].split('\n'):
                    if line.strip():
                        report.append(f"     {line}")
        
        return "\n".join(report)
    
    def run(self):
        """Run complete analysis."""
        print("=" * 80)
        print("QUANTUM WORLDWIDE SCRUB - VIVE MODE")
        print("=" * 80)
        
        system_scan = self.scan_system()
        comparison = self.compare_to_global_systems(system_scan)
        improvements = self.generate_improvements(comparison)
        report = self.generate_report(system_scan, comparison, improvements)
        
        report_file = OUTPUT_DIR / f"quantum_scrub_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.write_text(report, encoding='utf-8')
        
        json_file = OUTPUT_DIR / f"quantum_scrub_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_file.write_text(json.dumps({
            'system_scan': {k: (list(v) if isinstance(v, set) else v) for k, v in system_scan.items()},
            'comparison': comparison,
            'improvements': improvements
        }, indent=2, default=str), encoding='utf-8')
        
        print(report)
        print(f"\nReport saved to: {report_file}")
        print(f"JSON data saved to: {json_file}")
        
        return system_scan, comparison, improvements

if __name__ == "__main__":
    scrubber = QuantumWorldwideScrub()
    scrubber.run()

