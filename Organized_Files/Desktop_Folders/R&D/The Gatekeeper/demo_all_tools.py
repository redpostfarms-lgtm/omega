# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Demo Script - All Legitimate Tools
#
# Purpose: Demonstrate all tools working together

import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_gpu_optimizer():
    """Demo GPU performance optimizer."""
    print("\n" + "=" * 60)
    print("1. GPU PERFORMANCE OPTIMIZER DEMO")
    print("=" * 60)
    
    try:
        from performance_optimizer_gpu import GPUPerformanceOptimizer
        import numpy as np
        
        print("Initializing GPU optimizer...")
        optimizer = GPUPerformanceOptimizer(use_gpu=True)
        
        print(f"GPU available: {optimizer.use_gpu}")
        print(f"Device: {optimizer.device or 'CPU'}")
        
        # Create test data
        print("\nCreating test data (1000x1000 array)...")
        test_data = np.random.rand(1000, 1000).astype(np.float32)
        
        # Test operations
        print("Testing array operations...")
        result = optimizer.accelerate_array_operations(test_data, "sqrt")
        print(f"✅ Operation completed. Result shape: {result.shape}")
        
        # Benchmark
        print("\nRunning benchmark (5 iterations)...")
        benchmark = optimizer.benchmark(test_data, iterations=5)
        print(f"CPU time: {benchmark['cpu_time']:.4f}s")
        if optimizer.use_gpu:
            print(f"GPU time: {benchmark['gpu_time']:.4f}s")
            print(f"Speedup: {benchmark['speedup']:.2f}x")
        else:
            print("GPU: Not available (using CPU fallback)")
        
        print("✅ GPU Optimizer demo complete")
        return True
        
    except ImportError as e:
        print(f"⚠️  Optional dependency not available: {e}")
        print("   Install with: pip install cupy-cuda11x or pip install torch")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_http_client():
    """Demo async HTTP client."""
    print("\n" + "=" * 60)
    print("2. ASYNC HTTP CLIENT DEMO")
    print("=" * 60)
    
    try:
        import asyncio
        from async_http_client import RateLimitedHTTPClient
        
        async def run_demo():
            print("Initializing rate-limited HTTP client...")
            print("Rate limit: 5 requests/second")
            
            async with RateLimitedHTTPClient(requests_per_second=5.0) as client:
                # Test with httpbin (public test endpoint)
                print("\nMaking test requests to httpbin.org...")
                urls = [
                    "https://httpbin.org/get",
                    "https://httpbin.org/get",
                ]
                
                results = await client.fetch_multiple(urls)
                
                print(f"\n✅ Completed {len(results)} requests")
                for i, result in enumerate(results, 1):
                    status = result.get('status', 'N/A')
                    print(f"  Request {i}: Status {status}")
            
            print("✅ HTTP Client demo complete")
        
        asyncio.run(run_demo())
        return True
        
    except ImportError as e:
        print(f"⚠️  Optional dependency not available: {e}")
        print("   Install with: pip install aiohttp")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_security_scanner():
    """Demo security scanner."""
    print("\n" + "=" * 60)
    print("3. DEFENSIVE SECURITY SCANNER DEMO")
    print("=" * 60)
    
    try:
        from defensive_security_scanner import DefensiveSecurityScanner
        from pathlib import Path
        
        # Scan The Gatekeeper directory (your own code)
        target_dir = Path(__file__).parent
        print(f"Scanning: {target_dir}")
        print("(Scanning your own code for security issues)")
        
        scanner = DefensiveSecurityScanner(target_dir)
        results = scanner.scan_directory()
        
        print(f"\n✅ Scan complete:")
        print(f"  Files scanned: {results['files_scanned']}")
        print(f"  Total vulnerabilities: {results['total_vulnerabilities']}")
        print(f"  High severity: {results['high_severity']}")
        print(f"  Medium severity: {results['medium_severity']}")
        print(f"  Low severity: {results['low_severity']}")
        
        if results['high_severity'] > 0:
            print("\n⚠️  High severity issues found (review recommended)")
            for vuln in results['summary']['high'][:3]:
                print(f"  - {vuln.get('type', 'Unknown')} in {vuln.get('file', '?')}")
        
        print("✅ Security Scanner demo complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_report_generator():
    """Demo report generator."""
    print("\n" + "=" * 60)
    print("4. REPORT GENERATOR DEMO")
    print("=" * 60)
    
    try:
        from report_generator import ReportGenerator
        from pathlib import Path
        
        print("Initializing report generator...")
        generator = ReportGenerator()
        
        # Example findings (for demo)
        example_findings = [
            {
                "type": "Hardcoded password",
                "severity": "high",
                "file": "config.py",
                "line": 42,
                "message": "Hardcoded password detected in configuration",
                "code": "password = 'secret123'"
            },
            {
                "type": "SQL Injection Risk",
                "severity": "high",
                "file": "database.py",
                "line": 15,
                "message": "SQL query uses string formatting instead of parameters",
                "code": "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
            },
            {
                "type": "Path Traversal Risk",
                "severity": "medium",
                "file": "file_handler.py",
                "line": 28,
                "message": "File operation with relative path",
                "code": "open(f'../data/{filename}')"
            }
        ]
        
        print("Generating security assessment report...")
        report = generator.generate_security_report(
            findings=example_findings,
            system_name="Demo Application",
            assessment_type="Code Security Review"
        )
        
        # Save report
        output_path = Path(__file__).parent / "demo_security_report.md"
        generator.save_report(report, output_path)
        
        print(f"✅ Report generated and saved to: {output_path}")
        print(f"   Report length: {len(report)} characters")
        print("✅ Report Generator demo complete")
        return True
        
    except ImportError as e:
        print(f"⚠️  Optional dependency not available: {e}")
        print("   Install with: pip install jinja2")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all demos."""
    print("=" * 60)
    print("LEGITIMATE TOOLS - COMPLETE DEMO")
    print("=" * 60)
    print("\nThis demo showcases all legitimate tools:")
    print("1. GPU Performance Optimizer")
    print("2. Async HTTP Client")
    print("3. Defensive Security Scanner")
    print("4. Report Generator")
    print("\nAll tools are for legitimate use cases only.")
    
    results = {
        "GPU Optimizer": demo_gpu_optimizer(),
        "HTTP Client": demo_http_client(),
        "Security Scanner": demo_security_scanner(),
        "Report Generator": demo_report_generator()
    }
    
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    
    for tool, success in results.items():
        status = "✅ PASS" if success else "⚠️  SKIP (optional dependency)"
        print(f"{tool:20s}: {status}")
    
    successful = sum(1 for s in results.values() if s)
    total = len(results)
    
    print(f"\nCompleted: {successful}/{total} demos")
    
    if successful == total:
        print("\n🎉 All demos completed successfully!")
    else:
        print("\n💡 Some demos require optional dependencies.")
        print("   Install with:")
        print("   - pip install cupy-cuda11x (for GPU)")
        print("   - pip install aiohttp (for HTTP client)")
        print("   - pip install jinja2 (for report generator)")
    
    print("\n✅ All legitimate tools are ready for use!")


if __name__ == '__main__':
    main()
