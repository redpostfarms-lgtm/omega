# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# OMEGA V5 SWARM - RUN SCRIPT

"""
Run the Omega V5 Swarm
"""

import sys
import io
import asyncio
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

from omega_v5_swarm import OMEGA_V5_SWARM, run_swarm

async def main():
    """Main run function."""
    print("=" * 80)
    print("  OMEGA V5 SWARM - EXECUTING")
    print("=" * 80)
    print()
    
    # Check killswitch
    if OMEGA_V5_SWARM.check_killswitch():
        print("  Killswitch active - swarm stopped")
        return
    
    # Load config
    from omega_v5_swarm_config import load_config
    config = load_config()
    
    # Get targets
    targets = config.get('targets', [])
    if not targets:
        print("  No targets configured")
        print("  Add targets to: omega_swarm/swarm_config.json")
        print()
        print("  Example targets (for testing):")
        print("    - https://httpbin.org/get")
        print("    - https://jsonplaceholder.typicode.com/posts/1")
        return
    
    # Get base payloads
    base_payloads = config.get('base_payloads', ['test'])
    
    print(f"  Targets: {len(targets)}")
    print(f"  Base Payloads: {len(base_payloads)}")
    print()
    print("  Starting swarm...")
    print()
    
    # Run swarm on each target
    total_stats = {
        'payloads_generated': 0,
        'payloads_tested': 0,
        'real_vulns': 0,
        'false_positives': 0,
        'reports_submitted': 0
    }
    
    for target in targets:
        if OMEGA_V5_SWARM.check_killswitch():
            print(f"  Killswitch activated - stopping")
            break
        
        print(f"  Fuzzing: {target}")
        
        for base_payload in base_payloads[:1]:  # Limit for demo
            if OMEGA_V5_SWARM.check_killswitch():
                break
            
            try:
                stats = await run_swarm(target, base_payload)
                if stats:
                    total_stats['payloads_generated'] += stats.get('payloads_generated', 0)
                    total_stats['payloads_tested'] += stats.get('payloads_tested', 0)
                    total_stats['real_vulns'] += stats.get('real_vulns', 0)
                    total_stats['false_positives'] += stats.get('false_positives', 0)
                    total_stats['reports_submitted'] += stats.get('reports_submitted', 0)
            except Exception as e:
                print(f"    Error: {e}")
        
        print()
    
    # Final stats
    print("=" * 80)
    print("  SWARM EXECUTION COMPLETE")
    print("=" * 80)
    print()
    print("Final Stats:")
    print(f"  Payloads Generated: {total_stats['payloads_generated']:,}")
    print(f"  Payloads Tested: {total_stats['payloads_tested']:,}")
    print(f"  Real Vulns: {total_stats['real_vulns']}")
    print(f"  False Positives: {total_stats['false_positives']}")
    print(f"  Reports Submitted: {total_stats['reports_submitted']}")
    print()
    
    # Show current stats
    current_stats = OMEGA_V5_SWARM.get_stats()
    print("System Stats:")
    print(f"  GPU Available: {current_stats.get('gpu_available', False)}")
    print(f"  GPU VRAM: {current_stats.get('gpu_vram_gb', 0):.1f} GB")
    print(f"  Proxies Loaded: {current_stats.get('proxies_loaded', 0)}")
    print(f"  Rejected Patterns: {current_stats.get('rejected_patterns', 0)}")
    print(f"  Killswitch Active: {current_stats.get('killswitch_active', False)}")
    print()
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(main())
