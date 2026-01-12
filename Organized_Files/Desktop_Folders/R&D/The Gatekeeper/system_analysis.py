# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - System Analysis & Error Detection
# Comprehensive 0-100 score with error detection and fixes

import sys
import io
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Get script directory
SCRIPT_DIR = Path(__file__).parent.resolve()
GATE = SCRIPT_DIR
BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'

class SystemAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.score = 100
        self.results = {
            'compilation': {'passed': 0, 'failed': 0, 'total': 0},
            'imports': {'passed': 0, 'failed': 0, 'total': 0},
            'dependencies': {'missing': [], 'optional_missing': []},
            'file_structure': {'missing': [], 'exists': []},
            'syntax': {'errors': []},
            'runtime': {'errors': []}
        }
    
    def check_compilation(self):
        """Check if all Python files compile."""
        print("\n[1/7] Checking compilation...")
        py_files = list(GATE.glob('*.py'))
        self.results['compilation']['total'] = len(py_files)
        
        for py_file in py_files:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.results['compilation']['passed'] += 1
                else:
                    self.results['compilation']['failed'] += 1
                    self.errors.append(f"Compilation error in {py_file.name}: {result.stderr[:200]}")
                    self.score -= 2
            except Exception as e:
                self.results['compilation']['failed'] += 1
                self.errors.append(f"Error checking {py_file.name}: {e}")
                self.score -= 2
        
        print(f"  ✅ {self.results['compilation']['passed']}/{self.results['compilation']['total']} files compile")
        if self.results['compilation']['failed'] > 0:
            print(f"  ❌ {self.results['compilation']['failed']} files failed")
    
    def check_dependencies(self):
        """Check for missing dependencies."""
        print("\n[2/7] Checking dependencies...")
        
        required = {
            'pyttsx3': 'text-to-speech',
            'speech_recognition': 'voice input',
            'requests': 'web scraping',
            'beautifulsoup4': 'web parsing'
        }
        
        optional = {
            'numpy': 'calculations',
            'psutil': 'hardware monitoring',
            'GPUtil': 'GPU monitoring',
            'wmi': 'Windows hardware info',
            'python-docx': 'Word documents',
            'PyPDF2': 'PDF processing'
        }
        
        for module, purpose in required.items():
            try:
                __import__(module)
                self.results['imports']['passed'] += 1
            except ImportError:
                self.results['imports']['failed'] += 1
                self.results['dependencies']['missing'].append(f"{module} ({purpose})")
                self.errors.append(f"Missing required dependency: {module} ({purpose})")
                self.score -= 5
        
        for module, purpose in optional.items():
            try:
                __import__(module)
            except ImportError:
                self.results['dependencies']['optional_missing'].append(f"{module} ({purpose})")
                self.warnings.append(f"Missing optional dependency: {module} ({purpose})")
                self.score -= 0.5
        
        self.results['imports']['total'] = len(required)
        
        print(f"  ✅ {self.results['imports']['passed']}/{self.results['imports']['total']} required dependencies")
        if self.results['dependencies']['missing']:
            print(f"  ❌ Missing: {', '.join(self.results['dependencies']['missing'])}")
        if self.results['dependencies']['optional_missing']:
            print(f"  ⚠️  Optional missing: {', '.join(self.results['dependencies']['optional_missing'])}")
    
    def check_file_structure(self):
        """Check for required files and directories."""
        print("\n[3/7] Checking file structure...")
        
        required_files = [
            'brain_prime.py',
            'auto_heal.py',
            'voice_tuner.py',
            'voiceprint_auth.py',
            'voice_listener.py',
            'hardware_scan.py',
            'planetary_search.py',
            'hive_auto.py',
            'agent_council_v2.py',
            'brain_wakeup.bat'
        ]
        
        required_dirs = [
            ARCHIVED,
            ARCHIVED / 'voiceprint',
            ARCHIVED / 'learning',
            GATE / 'hive_auto'
        ]
        
        for file_name in required_files:
            file_path = GATE / file_name
            if file_path.exists():
                self.results['file_structure']['exists'].append(file_name)
            else:
                self.results['file_structure']['missing'].append(file_name)
                self.errors.append(f"Missing required file: {file_name}")
                self.score -= 3
        
        for dir_path in required_dirs:
            if dir_path.exists():
                self.results['file_structure']['exists'].append(str(dir_path))
            else:
                self.results['file_structure']['missing'].append(str(dir_path))
                self.warnings.append(f"Missing directory: {dir_path}")
                self.score -= 1
        
        print(f"  ✅ {len(self.results['file_structure']['exists'])} files/dirs exist")
        if self.results['file_structure']['missing']:
            print(f"  ❌ Missing: {len(self.results['file_structure']['missing'])} items")
    
    def check_syntax(self):
        """Check for syntax errors."""
        print("\n[4/7] Checking syntax...")
        
        py_files = list(GATE.glob('*.py'))
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                self.results['syntax']['errors'].append(f"{py_file.name}: {e}")
                self.errors.append(f"Syntax error in {py_file.name}: {e}")
                self.score -= 3
            except Exception as e:
                self.warnings.append(f"Error checking {py_file.name}: {e}")
        
        if not self.results['syntax']['errors']:
            print("  ✅ No syntax errors")
        else:
            print(f"  ❌ {len(self.results['syntax']['errors'])} syntax errors")
    
    def check_runtime(self):
        """Check for runtime errors in key modules."""
        print("\n[5/7] Checking runtime...")
        
        test_modules = [
            ('hardware_scan', 'hardware_scan.py'),
            ('planetary_search', 'planetary_search.py'),
        ]
        
        for module_name, file_name in test_modules:
            try:
                # Try importing
                file_path = GATE / file_name
                if file_path.exists():
                    # Just check if it can be imported (basic check)
                    result = subprocess.run(
                        [sys.executable, '-c', f'import sys; sys.path.insert(0, r"{GATE}"); exec(open(r"{file_path}", encoding="utf-8").read())'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        encoding='utf-8',
                        errors='replace'
                    )
                    if result.returncode == 0:
                        print(f"  ✅ {module_name} imports OK")
                    else:
                        self.warnings.append(f"{module_name} has import issues")
                        self.score -= 0.5
            except Exception as e:
                self.warnings.append(f"{module_name}: {e}")
                self.score -= 0.5
    
    def check_error_handling(self):
        """Check for proper error handling."""
        print("\n[6/7] Checking error handling...")
        
        py_files = list(GATE.glob('*.py'))
        files_with_errors = 0
        files_without_errors = 0
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'except' in content or 'try:' in content:
                        files_with_errors += 1
                    else:
                        files_without_errors += 1
            except:
                pass
        
        if files_without_errors > 0:
            self.warnings.append(f"{files_without_errors} files lack error handling")
            self.score -= 0.5 * files_without_errors
        
        print(f"  ✅ {files_with_errors} files have error handling")
        if files_without_errors > 0:
            print(f"  ⚠️  {files_without_errors} files lack error handling")
    
    def check_integration(self):
        """Check integration points."""
        print("\n[7/7] Checking integration...")
        
        # Check if voice_listener can find other modules
        voice_listener = GATE / 'voice_listener.py'
        if voice_listener.exists():
            with open(voice_listener, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'handle_planetary_search' in content:
                    print("  ✅ Planetary search integrated")
                else:
                    self.errors.append("Planetary search not integrated in voice_listener")
                    self.score -= 5
                
                if 'handle_hive' in content:
                    print("  ✅ Hive integrated")
                else:
                    self.warnings.append("Hive not integrated in voice_listener")
                    self.score -= 2
        
        # Check boot sequence
        boot_file = GATE / 'brain_wakeup.bat'
        if boot_file.exists():
            with open(boot_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'hardware_scan.py' in content:
                    print("  ✅ Hardware scan in boot sequence")
                else:
                    self.errors.append("Hardware scan not in boot sequence")
                    self.score -= 3
    
    def generate_report(self):
        """Generate comprehensive report."""
        print("\n" + "=" * 60)
        print("GATEKEEPER SYSTEM ANALYSIS REPORT")
        print("=" * 60)
        
        # Ensure score is between 0-100
        self.score = max(0, min(100, self.score))
        
        print(f"\n📊 OVERALL SCORE: {self.score:.1f}/100")
        
        if self.score >= 90:
            status = "✅ EXCELLENT"
        elif self.score >= 75:
            status = "✅ GOOD"
        elif self.score >= 60:
            status = "⚠️  NEEDS IMPROVEMENT"
        else:
            status = "❌ CRITICAL ISSUES"
        
        print(f"Status: {status}\n")
        
        print("=" * 60)
        print("ERRORS FOUND")
        print("=" * 60)
        if self.errors:
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        else:
            print("✅ No critical errors found")
        
        print("\n" + "=" * 60)
        print("WARNINGS")
        print("=" * 60)
        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")
        else:
            print("✅ No warnings")
        
        print("\n" + "=" * 60)
        print("DETAILED RESULTS")
        print("=" * 60)
        print(f"Compilation: {self.results['compilation']['passed']}/{self.results['compilation']['total']} passed")
        print(f"Imports: {self.results['imports']['passed']}/{self.results['imports']['total']} passed")
        print(f"Missing dependencies: {len(self.results['dependencies']['missing'])}")
        print(f"Optional missing: {len(self.results['dependencies']['optional_missing'])}")
        print(f"Syntax errors: {len(self.results['syntax']['errors'])}")
        
        # Save report
        report_file = GATE / 'system_analysis_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'score': self.score,
                'status': status,
                'errors': self.errors,
                'warnings': self.warnings,
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Report saved to: {report_file}")
        
        return self.score, self.errors, self.warnings

def main():
    analyzer = SystemAnalyzer()
    
    analyzer.check_compilation()
    analyzer.check_dependencies()
    analyzer.check_file_structure()
    analyzer.check_syntax()
    analyzer.check_runtime()
    analyzer.check_error_handling()
    analyzer.check_integration()
    
    score, errors, warnings = analyzer.generate_report()
    
    return score, errors, warnings

if __name__ == '__main__':
    score, errors, warnings = main()
    sys.exit(0 if score >= 75 else 1)

