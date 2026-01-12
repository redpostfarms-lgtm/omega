# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# LIMBO SWEEPER - TEST SETUP & WALKTHROUGH

"""
Test setup and walkthrough for Limbo Sweeper
Interactive configuration and test run
"""

import sys
import io
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional

# Set UTF-8 encoding for Windows
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

ROOT = Path(r'D:\RPF_BRAIN\Omega')
CONFIG_FILE = ROOT / 'limbo_config.json'


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def safe_input(prompt: str, default: str = "") -> str:
    """Safe input with default."""
    try:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    except (EOFError, KeyboardInterrupt):
        return default


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Default configuration
    return {
        'wallet_addresses': [],
        'testnet_address': '',
        'search_name': 'Ruth Berry',
        'search_state': 'TX',
        'enable_btc_puzzles': True,
        'enable_dust_reclaim': True,
        'enable_airdrops': True,
        'enable_refunds': True,
        'enable_bounties': False,  # Requires Selenium
        'test_mode': True,
        'rate_limit_delay': 0.1
    }


def save_config(config: Dict[str, Any]):
    """Save configuration to file."""
    ROOT.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def setup_walkthrough():
    """Interactive setup walkthrough."""
    print_section("LIMBO SWEEPER - TEST SETUP WALKTHROUGH")
    
    print("This walkthrough will help you configure the Limbo Sweeper for testing.")
    print("You can skip any step by pressing Enter to use defaults.\n")
    
    config = load_config()
    
    # Step 1: Wallet Addresses
    print_section("STEP 1: Wallet Addresses")
    print("The sweeper can check specific Bitcoin addresses for dust (small amounts).")
    print("These are public addresses - you're just checking if they have funds.\n")
    
    add_wallets = safe_input("Add wallet addresses to check? (y/n)", "n").lower()
    if add_wallets == 'y':
        wallets = []
        while True:
            addr = safe_input("Enter Bitcoin address (or 'done' to finish)", "")
            if addr.lower() == 'done' or not addr:
                break
            if addr.startswith('1') or addr.startswith('3') or addr.startswith('bc1'):
                wallets.append(addr)
                print(f"  ✓ Added: {addr}")
            else:
                print("  ⚠ Invalid Bitcoin address format")
        config['wallet_addresses'] = wallets
    else:
        print("  Using default test addresses")
    
    # Step 2: Testnet Address
    print_section("STEP 2: Testnet Address (for Airdrops)")
    print("For claiming testnet airdrops, you need a testnet address.")
    print("This is safe - testnet tokens have no real value.\n")
    
    testnet_addr = safe_input("Enter testnet address (or skip)", config.get('testnet_address', ''))
    if testnet_addr:
        config['testnet_address'] = testnet_addr
        print(f"  ✓ Testnet address set: {testnet_addr}")
    
    # Step 3: Unclaimed Funds Search
    print_section("STEP 3: Unclaimed Funds Search")
    print("Search for unclaimed funds in state databases.")
    print("Uses your name and state to search.\n")
    
    search_name = safe_input("Name to search", config.get('search_name', 'Ruth Berry'))
    config['search_name'] = search_name
    
    search_state = safe_input("State code (TX, CA, etc.)", config.get('search_state', 'TX'))
    config['search_state'] = search_state.upper()
    
    # Step 4: Feature Selection
    print_section("STEP 4: Enable Features")
    print("Choose which features to enable for testing:\n")
    
    features = {
        'enable_btc_puzzles': ('Bitcoin Puzzles (#50, #66)', True),
        'enable_dust_reclaim': ('Dust Reclamation', True),
        'enable_airdrops': ('Testnet Airdrops', True),
        'enable_refunds': ('Unclaimed Funds Search', True),
        'enable_bounties': ('Bug Bounty Fuzzing (requires Selenium)', False)
    }
    
    for key, (desc, default) in features.items():
        current = config.get(key, default)
        enable = safe_input(f"Enable {desc}? (y/n)", "y" if current else "n").lower()
        config[key] = enable == 'y'
    
    # Step 5: Test Mode
    print_section("STEP 5: Test Mode")
    print("Test mode limits API calls and uses safe defaults.")
    print("Recommended for first run.\n")
    
    test_mode = safe_input("Enable test mode? (y/n)", "y").lower()
    config['test_mode'] = test_mode == 'y'
    
    # Save configuration
    save_config(config)
    
    print_section("CONFIGURATION SAVED")
    print(f"Configuration saved to: {CONFIG_FILE}")
    print("\nNext steps:")
    print("1. Review the configuration")
    print("2. Run: python limbo_sweeper.py")
    print("3. Check results in: D:\\RPF_BRAIN\\Omega\\tx_dump.json")
    
    return config


def show_config():
    """Show current configuration."""
    config = load_config()
    
    print_section("CURRENT CONFIGURATION")
    
    print("Wallet Addresses:")
    if config.get('wallet_addresses'):
        for addr in config['wallet_addresses']:
            print(f"  - {addr}")
    else:
        print("  (using default test addresses)")
    
    print(f"\nTestnet Address: {config.get('testnet_address', 'not set')}")
    print(f"Search Name: {config.get('search_name', 'Ruth Berry')}")
    print(f"Search State: {config.get('search_state', 'TX')}")
    
    print("\nFeatures:")
    features = [
        ('Bitcoin Puzzles', 'enable_btc_puzzles'),
        ('Dust Reclamation', 'enable_dust_reclaim'),
        ('Airdrops', 'enable_airdrops'),
        ('Unclaimed Funds', 'enable_refunds'),
        ('Bug Bounties', 'enable_bounties')
    ]
    
    for name, key in features:
        status = "✓ ENABLED" if config.get(key, False) else "✗ DISABLED"
        print(f"  {status}: {name}")
    
    print(f"\nTest Mode: {'✓ ENABLED' if config.get('test_mode', True) else '✗ DISABLED'}")


def test_connections():
    """Test API connections."""
    print_section("TESTING CONNECTIONS")
    
    import requests
    
    tests = [
        ("Blockstream API", "https://blockstream.info/api/"),
        ("General Internet", "https://www.google.com")
    ]
    
    for name, url in tests:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f"  ✓ {name}: Connected")
            else:
                print(f"  ⚠ {name}: Status {r.status_code}")
        except Exception as e:
            print(f"  ✗ {name}: Failed - {e}")
    
    # Check database
    db_path = ROOT / 'limbo.db'
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.execute("SELECT COUNT(*) FROM hits")
            count = cur.fetchone()[0]
            conn.close()
            print(f"  ✓ Database: {count} existing hits")
        except Exception as e:
            print(f"  ⚠ Database: Error - {e}")
    else:
        print(f"  ℹ Database: Will be created on first run")


def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Limbo Sweeper Test Setup')
    parser.add_argument('--setup', action='store_true', help='Run interactive setup')
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--test', action='store_true', help='Test connections')
    parser.add_argument('--all', action='store_true', help='Run all: setup, show, test')
    
    args = parser.parse_args()
    
    if args.all or (not args.setup and not args.show and not args.test):
        # Default: run all
        setup_walkthrough()
        print()
        show_config()
        print()
        test_connections()
    else:
        if args.setup:
            setup_walkthrough()
        if args.show:
            show_config()
        if args.test:
            test_connections()


if __name__ == '__main__':
    main()
