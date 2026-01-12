#!/usr/bin/env python3
"""
Full Analysis Script for Marc
Runs comprehensive analysis of all files in The Gatekeeper
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gatekeeper_completion_analysis import DirectoryAnalyzer, generate_markdown_report
import json

def main():
    print("=" * 80)
    print("GATEKEEPER FULL ANALYSIS - FOR MARC")
    print("=" * 80)
    print()
    
    root = Path('.')
    output_json = root / 'gatekeeper_completion_report.json'
    output_md = root / 'GATEKEEPER_FULL_ANALYSIS_FOR_MARC.md'
    
    print(f"Root directory: {root.absolute()}")
    print(f"JSON output: {output_json}")
    print(f"Markdown output: {output_md}")
    print()
    print("Starting analysis...")
    print()
    
    try:
        analyzer = DirectoryAnalyzer(root)
        results = analyzer.analyze_all()
        
        print()
        print("Saving results...")
        
        # Save JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON report saved: {output_json}")
        
        # Generate and save Markdown
        try:
            generate_markdown_report(results, output_md)
            print(f"✓ Markdown report saved: {output_md}")
        except NameError:
            # Fallback if function not available
            print("Markdown report generation skipped (function not found)")
        
        # Print summary
        summary = results['summary']
        print()
        print("=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total Files Analyzed: {summary['total_files']}")
        print(f"Overall Average Completion: {summary['average_completion']:.2f}%")
        print()
        print("Files by Type:")
        for file_type, count in sorted(summary['files_by_type'].items()):
            avg = summary['avg_by_type'].get(file_type, 0)
            print(f"  {file_type or '(no ext)':15} {count:4} files - Avg: {avg:.1f}%")
        
        print()
        print("Files by Status:")
        for status, files in sorted(results['by_status'].items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {status:15} {len(files):4} files")
        
        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    main()
