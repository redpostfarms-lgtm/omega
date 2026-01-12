#!/usr/bin/env python3
"""
Gatekeeper Completion Analysis
Analyzes all files and folders in The Gatekeeper directory
and calculates completion percentages (0-100%)
"""

import os
import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

class FileAnalyzer:
    """Analyze individual files for completion."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.size = file_path.stat().st_size if file_path.exists() else 0
        self.content = self._read_file()
        self.file_type = file_path.suffix.lower()
    
    def _read_file(self) -> str:
        """Read file content."""
        try:
            if self.file_path.exists() and self.file_path.is_file():
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception:
            pass
        return ""
    
    def analyze_completion(self) -> Dict[str, Any]:
        """Analyze file completion percentage."""
        completion = {
            'path': str(self.file_path),
            'type': self.file_type,
            'size': self.size,
            'lines': len(self.content.splitlines()) if self.content else 0,
            'completion_percentage': 0,
            'has_content': len(self.content.strip()) > 0,
            'status': 'empty',
            'issues': []
        }
        
        # Skip empty files
        if not completion['has_content']:
            completion['completion_percentage'] = 0
            completion['status'] = 'empty'
            return completion
        
        # Python files - detailed analysis
        if self.file_type == '.py':
            completion.update(self._analyze_python())
        # Markdown files
        elif self.file_type == '.md':
            completion.update(self._analyze_markdown())
        # JSON files
        elif self.file_type == '.json':
            completion.update(self._analyze_json())
        # Other text files
        elif self.file_type in ['.txt', '.bat', '.ps1', '.sh']:
            completion.update(self._analyze_text())
        # Binary or other files
        else:
            completion['completion_percentage'] = 50 if completion['has_content'] else 0
            completion['status'] = 'binary' if completion['has_content'] else 'empty'
        
        return completion
    
    def _analyze_python(self) -> Dict[str, Any]:
        """Analyze Python file completion."""
        issues = []
        score = 0
        max_score = 100
        
        # Check for placeholder patterns
        placeholder_patterns = [
            'TODO', 'FIXME', 'XXX', 'HACK', 'PLACEHOLDER', 'STUB',
            'DUMMY', 'FAKE', 'NOT IMPLEMENTED', 'raise NotImplementedError',
            'pass  #', '...', '# TODO', '# FIXME'
        ]
        
        content_upper = self.content.upper()
        for pattern in placeholder_patterns:
            if pattern.upper() in content_upper:
                issues.append(f'Placeholder marker: {pattern}')
                score -= 10
        
        # Check for actual implementation
        try:
            tree = ast.parse(self.content)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            if len(functions) > 0:
                score += 30
            if len(classes) > 0:
                score += 20
            
            # Check for docstrings
            has_docstrings = any(
                ast.get_docstring(node) for node in [tree] + functions + classes
            )
            if has_docstrings:
                score += 15
            
            # Check for error handling
            has_try_except = any(
                isinstance(node, ast.Try) for node in ast.walk(tree)
            )
            if has_try_except:
                score += 15
            
            # Check file length (content indicator)
            lines = len(self.content.splitlines())
            if lines > 50:
                score += 10
            elif lines > 20:
                score += 5
                
        except SyntaxError:
            issues.append('Syntax errors in code')
            score = max(0, score - 20)
        
        # Check if file has meaningful content
        if len(self.content.strip()) < 50:
            issues.append('Very short file (< 50 chars)')
            score = min(score, 30)
        
        # Normalize score
        completion_percentage = max(0, min(100, score))
        
        status = 'complete' if completion_percentage >= 80 else 'incomplete' if completion_percentage >= 50 else 'placeholder'
        
        return {
            'completion_percentage': completion_percentage,
            'status': status,
            'issues': issues,
            'functions': len([n for n in ast.walk(ast.parse(self.content)) if isinstance(n, ast.FunctionDef)]) if self.content else 0,
            'classes': len([n for n in ast.walk(ast.parse(self.content)) if isinstance(n, ast.ClassDef)]) if self.content else 0,
        }
    
    def _analyze_markdown(self) -> Dict[str, Any]:
        """Analyze Markdown file completion."""
        lines = self.content.splitlines()
        non_empty_lines = [l for l in lines if l.strip()]
        
        if len(non_empty_lines) < 5:
            return {'completion_percentage': 20, 'status': 'skeleton', 'issues': ['Very short document']}
        
        # Check for placeholder markers
        has_placeholder = any(marker in self.content.upper() for marker in ['TODO', 'TBD', 'PLACEHOLDER', 'IN PROGRESS'])
        
        completion = 90 if not has_placeholder else 60
        status = 'complete' if completion >= 80 else 'incomplete'
        
        return {
            'completion_percentage': completion,
            'status': status,
            'issues': ['Has placeholder markers'] if has_placeholder else []
        }
    
    def _analyze_json(self) -> Dict[str, Any]:
        """Analyze JSON file completion."""
        try:
            data = json.loads(self.content)
            if isinstance(data, dict) and len(data) > 0:
                return {'completion_percentage': 95, 'status': 'complete', 'issues': []}
            elif isinstance(data, list) and len(data) > 0:
                return {'completion_percentage': 90, 'status': 'complete', 'issues': []}
            else:
                return {'completion_percentage': 30, 'status': 'empty', 'issues': ['Empty JSON structure']}
        except json.JSONDecodeError:
            return {'completion_percentage': 0, 'status': 'invalid', 'issues': ['Invalid JSON']}
    
    def _analyze_text(self) -> Dict[str, Any]:
        """Analyze text file completion."""
        lines = self.content.splitlines()
        non_empty = len([l for l in lines if l.strip()])
        
        if non_empty < 3:
            return {'completion_percentage': 20, 'status': 'minimal', 'issues': []}
        
        completion = min(90, 40 + (non_empty * 2))
        return {
            'completion_percentage': completion,
            'status': 'complete' if completion >= 70 else 'incomplete',
            'issues': []
        }


class DirectoryAnalyzer:
    """Analyze directory structure and calculate completion."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.ignore_patterns = ['__pycache__', '.git', '.pytest_cache', 'node_modules', '.venv', 'venv']
    
    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.ignore_patterns)
    
    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all files and directories."""
        results = {
            'root': str(self.root_dir),
            'files': [],
            'directories': {},
            'summary': {},
            'by_type': defaultdict(list),
            'by_status': defaultdict(list)
        }
        
        total_files = 0
        total_completion = 0
        
        # Analyze all files
        print(f"Scanning files in {self.root_dir}...", flush=True)
        all_files = list(self.root_dir.rglob('*'))
        file_count = 0
        skipped_count = 0
        
        for file_path in all_files:
            if not file_path.is_file():
                continue
            
            if self.should_ignore(file_path):
                skipped_count += 1
                continue
            
            if self.files_analyzed >= self.max_files_to_analyze:
                print(f"Reached file limit ({self.max_files_to_analyze}), stopping analysis...", flush=True)
                break
            
            try:
                if self.files_analyzed % 500 == 0 and self.files_analyzed > 0:
                    print(f"  Analyzed {self.files_analyzed} files...", flush=True)
                
                analyzer = FileAnalyzer(file_path)
                file_data = analyzer.analyze_completion()
                results['files'].append(file_data)
                
                total_files += 1
                total_completion += file_data['completion_percentage']
                self.files_analyzed += 1
                
                # Group by type
                file_type = file_data['type'] or 'no_ext'
                results['by_type'][file_type].append(file_data['completion_percentage'])
                
                # Group by status
                results['by_status'][file_data['status']].append(file_data)
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}", file=sys.stderr, flush=True)
        
        if skipped_count > 0:
            print(f"Skipped {skipped_count} files in ignored directories", flush=True)
        
        # Calculate summary statistics
        avg_completion = (total_completion / total_files) if total_files > 0 else 0
        
        results['summary'] = {
            'total_files': total_files,
            'average_completion': round(avg_completion, 2),
            'files_by_type': {k: len(v) for k, v in results['by_type'].items()},
            'files_by_status': {k: len(v) for k, v in results['by_status'].items()},
            'avg_by_type': {
                k: round(sum(v) / len(v), 2) if v else 0
                for k, v in results['by_type'].items()
            }
        }
        
        # Analyze directories
        for dir_path in sorted(self.root_dir.rglob('*')):
            if not dir_path.is_dir():
                continue
            
            if self.should_ignore(dir_path):
                continue
            
            dir_files = [f for f in results['files'] if Path(f['path']).parent == dir_path]
            if dir_files:
                dir_completion = sum(f['completion_percentage'] for f in dir_files) / len(dir_files)
                results['directories'][str(dir_path.relative_to(self.root_dir))] = {
                    'file_count': len(dir_files),
                    'average_completion': round(dir_completion, 2),
                    'files': [f['path'] for f in dir_files]
                }
        
        return results


def main():
    """Main analysis function."""
    import sys
    root = Path('.')
    output_file = root / 'gatekeeper_completion_report.json'
    summary_file = root / 'GATEKEEPER_FULL_ANALYSIS_FOR_MARC.md'
    
    try:
        print(f"Analyzing: {root.absolute()}", flush=True)
        print("=" * 80, flush=True)
        
        analyzer = DirectoryAnalyzer(root)
        print("Starting comprehensive analysis...", flush=True)
        results = analyzer.analyze_all()
        
        # Save results
        print(f"Saving JSON report to {output_file}...", flush=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Generate Markdown report
        print(f"Generating Markdown report...", flush=True)
        generate_markdown_report(results, summary_file)
        
        # Print summary
        print(f"\n=== COMPLETION ANALYSIS SUMMARY ===", flush=True)
        print(f"Total Files Analyzed: {results['summary']['total_files']}", flush=True)
        print(f"Overall Average Completion: {results['summary']['average_completion']:.2f}%", flush=True)
        print(f"\nFiles by Type:", flush=True)
        for file_type, count in sorted(results['summary']['files_by_type'].items()):
            avg = results['summary']['avg_by_type'].get(file_type, 0)
            print(f"  {file_type or '(no ext)':15} {count:4} files - Avg: {avg:.1f}%", flush=True)
        
        print(f"\nFiles by Status:", flush=True)
        for status, files in sorted(results['summary']['files_by_status'].items()):
            print(f"  {status:15} {len(files):4} files", flush=True)
        
        print(f"\nDetailed reports saved:", flush=True)
        print(f"  JSON: {output_file}", flush=True)
        print(f"  Markdown: {summary_file}", flush=True)
        
        return results
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return None


def generate_markdown_report(results: Dict[str, Any], output_file: Path):
    """Generate comprehensive Markdown report."""
    summary = results['summary']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Gatekeeper Full Analysis - For Marc\n\n")
        f.write("**Date:** January 2026  \n")
        f.write("**Analyzed by:** Omega  \n")
        f.write("**Requested by:** Marc  \n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"**Total Files Analyzed:** {summary['total_files']}  \n")
        f.write(f"**Overall Average Completion:** {summary['average_completion']:.2f}%  \n\n")
        
        # Files by Type
        f.write("### Files by Type\n\n")
        f.write("| File Type | Count | Average Completion |\n")
        f.write("|-----------|-------|-------------------|\n")
        for file_type, count in sorted(summary['files_by_type'].items()):
            avg = summary['avg_by_type'].get(file_type, 0)
            f.write(f"| `{file_type or '(no extension)'}` | {count} | {avg:.1f}% |\n")
        f.write("\n")
        
        # Files by Status
        f.write("### Files by Status\n\n")
        f.write("| Status | Count |\n")
        f.write("|--------|-------|\n")
        for status, files in sorted(results['by_status'].items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"| {status} | {len(files)} |\n")
        f.write("\n")
        
        # Directory Breakdown
        f.write("## Directory Breakdown\n\n")
        f.write("### Top Level Directories\n\n")
        f.write("| Directory | Files | Average Completion |\n")
        f.write("|-----------|-------|-------------------|\n")
        
        # Group files by top-level directory
        dir_stats = {}
        for file_data in results['files']:
            file_path = Path(file_data['path'])
            if len(file_path.parts) > 1:
                top_dir = file_path.parts[0]
            else:
                top_dir = '(root)'
            
            if top_dir not in dir_stats:
                dir_stats[top_dir] = {'files': [], 'completions': []}
            dir_stats[top_dir]['files'].append(file_data)
            dir_stats[top_dir]['completions'].append(file_data['completion_percentage'])
        
        for dir_name in sorted(dir_stats.keys()):
            stats = dir_stats[dir_name]
            avg_comp = sum(stats['completions']) / len(stats['completions']) if stats['completions'] else 0
            f.write(f"| `{dir_name}` | {len(stats['files'])} | {avg_comp:.1f}% |\n")
        f.write("\n")
        
        # Detailed Directory Listing
        f.write("## Detailed Directory Analysis\n\n")
        for dir_name, dir_data in sorted(results['directories'].items())[:50]:  # Limit to top 50
            f.write(f"### {dir_name}\n\n")
            f.write(f"- **Files:** {dir_data['file_count']}  \n")
            f.write(f"- **Average Completion:** {dir_data['average_completion']:.1f}%  \n\n")
        
        if len(results['directories']) > 50:
            f.write(f"\n*... and {len(results['directories']) - 50} more directories ...*\n\n")
        
        f.write("---\n\n")
        f.write("**Report generated by:** gatekeeper_completion_analysis.py\n")


if __name__ == '__main__':
    main()
