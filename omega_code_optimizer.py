"""
Omega Code Optimizer - Space and Performance Optimization
=========================================================
Optimizes code for space efficiency and performance.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Tuple
import re

class CodeOptimizer:
    """Optimizes code for space efficiency"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.optimizations_applied = []
        
    def analyze_file_size(self, file_path: Path) -> Dict:
        """Analyze file size and optimization opportunities"""
        if not file_path.exists():
            return {"error": "File not found"}
        
        size = file_path.stat().st_size
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.splitlines())
            chars = len(content)
        
        opportunities = []
        
        long_strings = re.findall(r'"[^"]{100,}"', content)
        if long_strings:
            opportunities.append(f"Long strings ({len(long_strings)}): Consider extracting to constants")
        
        if content.count("def ") > 20:
            opportunities.append("Many functions: Consider modularization")
        
        dict_count = content.count("{")
        if dict_count > 50:
            opportunities.append("Large data structures: Consider external data files")
        
        comment_lines = len([l for l in content.splitlines() if l.strip().startswith('#')])
        comment_ratio = comment_lines / lines if lines > 0 else 0
        if comment_ratio > 0.4:
            opportunities.append("High comment ratio: Consider condensing comments")
        
        return {
            "size_bytes": size,
            "size_kb": size / 1024,
            "lines": lines,
            "chars": chars,
            "opportunities": opportunities
        }
    
    def optimize_imports(self, content: str) -> Tuple[str, List[str]]:
        """Optimize imports - combine where possible"""
        lines = content.splitlines()
        import_lines = []
        other_lines = []
        in_import_block = False
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append(line)
                in_import_block = True
            elif in_import_block and line.strip() == '':
                import_lines.append(line)
            else:
                in_import_block = False
                other_lines.append(line)
        
        optimized_imports = self._combine_imports(import_lines)
        
        optimized_content = '\n'.join(optimized_imports + other_lines)
        changes = []
        
        if len(optimized_imports) < len(import_lines):
            changes.append(f"Combined imports: {len(import_lines)} → {len(optimized_imports)} lines")
        
        return optimized_content, changes
    
    def _combine_imports(self, import_lines: List[str]) -> List[str]:
        """Combine imports from same module"""
        imports = {}
        blank_lines = []
        
        for line in import_lines:
            if line.strip() == '':
                blank_lines.append(line)
            elif line.strip().startswith('from '):
                match = re.match(r'from\s+(\S+)\s+import\s+(.+)', line)
                if match:
                    module, items = match.groups()
                    if module not in imports:
                        imports[module] = []
                    imports[module].extend([i.strip() for i in items.split(',')])
            elif line.strip().startswith('import '):
                module = line.strip().replace('import ', '').strip()
                imports[module] = []
        
        result = []
        for module, items in sorted(imports.items()):
            if items:
                unique_items = sorted(set(items))
                result.append(f"from {module} import {', '.join(unique_items)}")
            else:
                result.append(f"import {module}")
        
        return result + blank_lines[:1] if blank_lines else result
    
    def remove_unused_imports(self, content: str) -> Tuple[str, List[str]]:
        """Remove unused imports (basic check)"""
        lines = content.splitlines()
        used_names = set()
        
        for line in lines:
            if not line.strip().startswith(('import ', 'from ', '#')):
                words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line)
                used_names.update(words)
        
        import_lines = []
        removed = []
        for line in lines:
            if line.strip().startswith('from '):
                match = re.match(r'from\s+\S+\s+import\s+(.+)', line)
                if match:
                    imported = [i.strip().split(' as ')[0] for i in match.group(1).split(',')]
                    if not all(name in used_names for name in imported):
                        removed.extend([name for name in imported if name not in used_names])
                        continue
            import_lines.append(line)
        
        optimized = '\n'.join(import_lines)
        changes = []
        if removed:
            changes.append(f"Potentially unused imports: {', '.join(removed[:5])}")
        
        return optimized, changes
    
    def optimize_whitespace(self, content: str) -> Tuple[str, List[str]]:
        """Remove excessive whitespace"""
        lines = content.splitlines()
        optimized = []
        prev_blank = False
        blank_count = 0
        
        for line in lines:
            if line.strip() == '':
                if not prev_blank:
                    optimized.append('')
                    blank_count += 1
                prev_blank = True
            else:
                optimized.append(line.rstrip())
                prev_blank = False
        
        optimized_content = '\n'.join(optimized)
        original_size = len(content)
        optimized_size = len(optimized_content)
        savings = original_size - optimized_size
        
        changes = []
        if savings > 0:
            changes.append(f"Whitespace optimization: Saved {savings} bytes")
        
        return optimized_content, changes
    
    def extract_constants(self, content: str) -> Tuple[str, List[str]]:
        """Extract long repeated strings to constants"""
        long_strings = re.findall(r'"[^"]{50,}"', content)
        
        if len(set(long_strings)) < len(long_strings):
            changes = ["Found repeated long strings - consider extracting to constants"]
            return content, changes
        
        return content, []
    
    def optimize_file(self, file_path: Path, backup: bool = True) -> Dict:
        """Optimize a single file"""
        if not file_path.exists() or not file_path.suffix == '.py':
            return {"error": "Not a Python file or doesn't exist"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        original_size = len(original_content)
        optimized_content = original_content
        all_changes = []
        
        optimized_content, changes = self.optimize_whitespace(optimized_content)
        all_changes.extend(changes)
        
        optimized_content, changes = self.optimize_imports(optimized_content)
        all_changes.extend(changes)
        
        optimized_size = len(optimized_content)
        savings = original_size - optimized_size
        savings_pct = (savings / original_size * 100) if original_size > 0 else 0
        
        result = {
            "file": str(file_path),
            "original_size": original_size,
            "optimized_size": optimized_size,
            "savings": savings,
            "savings_pct": savings_pct,
            "changes": all_changes
        }
        
        if savings > 100 or savings_pct > 1:  # Save if >100 bytes or >1%
            if backup:
                backup_path = file_path.with_suffix('.py.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            result["optimized"] = True
        else:
            result["optimized"] = False
        
        return result
    
    def scan_and_optimize(self, pattern: str = "*.py") -> Dict:
        """Scan and optimize all matching files"""
        files = list(self.root_dir.rglob(pattern))
        results = {
            "files_scanned": len(files),
            "files_optimized": 0,
            "total_savings": 0,
            "details": []
        }
        
        for file_path in files:
            if 'bak' in file_path.name or '__pycache__' in str(file_path):
                continue
            
            try:
                result = self.optimize_file(file_path, backup=False)
                if result.get("optimized"):
                    results["files_optimized"] += 1
                    results["total_savings"] += result.get("savings", 0)
                results["details"].append(result)
            except Exception as e:
                results["details"].append({"file": str(file_path), "error": str(e)})
        
        return results

def main():
    """Run code optimization"""
    import sys
    
    optimizer = CodeOptimizer()
    
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.is_file():
            result = optimizer.optimize_file(target)
            print(f"File: {result['file']}")
            print(f"Original: {result['original_size']} bytes")
            print(f"Optimized: {result['optimized_size']} bytes")
            print(f"Savings: {result['savings']} bytes ({result['savings_pct']:.2f}%)")
            if result.get('changes'):
                print("Changes:", ', '.join(result['changes']))
        else:
            print(f"File not found: {target}")
    else:
        results = optimizer.scan_and_optimize()
        print(f"Files scanned: {results['files_scanned']}")
        print(f"Files optimized: {results['files_optimized']}")
        print(f"Total savings: {results['total_savings']} bytes ({results['total_savings']/1024:.2f} KB)")

if __name__ == "__main__":
    main()
