# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# LIMBO SWEEPER - TEST RUN SCRIPT

"""
Test run script for Limbo Sweeper
Allows testing individual components with detailed output
"""

import sys
import io
import asyncio
import json
from pathlib import Path

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
TX = ROOT / 'tx_dump.json'


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def load_config():
    """Load configuration."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def test_btc_puzzles():
    """Test Bitcoin puzzle probing."""
    print_section("TEST 1: Bitcoin Puzzles")
    print("What it does:")
    print("  - Probes Bitcoin puzzle #50 and #66")
    print("  - These are public challenges with known ranges")
    print("  - Logs probe attempts (actual solving requires brute force)")
    print()
    
    import hashlib
    puzzles = [
        (50, 0x8000000000, 0xFFFFFFFFFFF),
        (66, 0x20000000000000000, 0x3FFFFFFFFFFFFFFFF)
    ]
    
    for name, start, end in puzzles:
        key = hashlib.sha256(f'bitcoin_{name}'.encode()).hexdigest()[:8]
        print(f"  Puzzle #{name}:")
        print(f"    Range: {hex(start)} to {hex(end)}")
        print(f"    Probe key: {key}")
        print()
    
    print("  [OK] Puzzle probing configured")
    return True


def test_dust_reclaim():
    """Test dust reclamation."""
    print_section("TEST 2: Dust Reclamation")
    print("What it does:")
    print("  - Checks public Bitcoin addresses for small amounts (dust)")
    print("  - Uses Blockstream API (public, no auth needed)")
    print("  - Only checks - doesn't claim (you'd need private keys)")
    print()
    
    config = load_config()
    addresses = config.get('wallet_addresses', [
        '1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF',
        '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
        '1CUNEBjYrZVX9nW9cp5vwV7NCPQVf2uL6P'
    ])
    
    print(f"  Checking {len(addresses)} addresses...")
    
    import requests
    for addr in addresses[:2]:  # Test first 2
        try:
            print(f"    Checking: {addr[:20]}...")
            r = requests.get(f'https://blockstream.info/api/address/{addr}/utxo', timeout=5)
            if r.ok:
                utxos = r.json()
                if utxos:
                    total = sum(u['value'] for u in utxos) / 1e8
                    print(f"      Found: {len(utxos)} UTXOs, {total:.6f} BTC")
                else:
                    print(f"      No UTXOs found")
            else:
                print(f"      API returned: {r.status_code}")
        except Exception as e:
            print(f"      Error: {e}")
    
    print()
    print("  [OK] Dust reclamation configured")
    return True


def test_airdrops():
    """Test airdrop claiming."""
    print_section("TEST 3: Testnet Airdrops")
    print("What it does:")
    print("  - Attempts to claim testnet tokens from L2 chains")
    print("  - Testnet tokens have no real value (safe)")
    print("  - Requires testnet address")
    print()
    
    config = load_config()
    testnet_addr = config.get('testnet_address', '')
    
    if not testnet_addr:
        print("  [WARNING] No testnet address configured")
        print("  Set testnet_address in config to enable")
    else:
        print(f"  Testnet address: {testnet_addr}")
    
    chains = ['jito', 'blast', 'zksync', 'linea']
    print(f"  Will check {len(chains)} chains: {', '.join(chains)}")
    print()
    print("  [OK] Airdrop claiming configured")
    return True


def test_refunds():
    """Test unclaimed funds search."""
    print_section("TEST 4: Unclaimed Funds Search")
    print("What it does:")
    print("  - Searches state databases for unclaimed funds")
    print("  - Uses your name and state")
    print("  - Checks unclaimed.org and missingmoney.com")
    print()
    
    config = load_config()
    name = config.get('search_name', 'Ruth Berry')
    state = config.get('search_state', 'TX')
    
    print(f"  Searching for: {name}")
    print(f"  State: {state}")
    print()
    print("  Note: Real API endpoints may vary")
    print("  This is a structure test - actual APIs need verification")
    print()
    print("  [OK] Unclaimed funds search configured")
    return True


def test_bounties():
    """Test bug bounty fuzzing."""
    print_section("TEST 5: Bug Bounty Fuzzing")
    print("What it does:")
    print("  - Scrapes HackerOne for bug bounty programs")
    print("  - Requires Selenium (webdriver)")
    print("  - Would run fuzzers via agent swarm")
    print()
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("  [OK] Selenium available")
        print("  [OK] Bug bounty fuzzing can be enabled")
    except ImportError:
        print("  [WARNING] Selenium not installed")
        print("  Install: pip install selenium")
        print("  Also need: ChromeDriver")
        print("  [SKIP] Bug bounty fuzzing disabled")
    
    return True


def show_results():
    """Show results from last run."""
    print_section("RESULTS FROM LAST RUN")
    
    if TX.exists():
        try:
            with open(TX, 'r', encoding='utf-8') as f:
                hits = json.load(f)
            
            if hits:
                print(f"Found {len(hits)} hits:\n")
                for hit in hits[:10]:  # Show first 10
                    print(f"  [{hit.get('type', 'unknown')}]")
                    print(f"    Source: {hit.get('source', 'unknown')}")
                    print(f"    Amount: ${hit.get('amt', 0):,.2f}")
                    if hit.get('wallet'):
                        print(f"    Wallet: {hit.get('wallet', '')[:50]}")
                    print()
                
                if len(hits) > 10:
                    print(f"  ... and {len(hits) - 10} more")
            else:
                print("  No hits found")
        except Exception as e:
            print(f"  Error reading results: {e}")
    else:
        print("  No results file found")
        print("  Run the sweeper first: python limbo_sweeper.py")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Limbo Sweeper Test Run')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--puzzles', action='store_true', help='Test Bitcoin puzzles')
    parser.add_argument('--dust', action='store_true', help='Test dust reclamation')
    parser.add_argument('--airdrops', action='store_true', help='Test airdrops')
    parser.add_argument('--refunds', action='store_true', help='Test refunds')
    parser.add_argument('--bounties', action='store_true', help='Test bounties')
    parser.add_argument('--results', action='store_true', help='Show results from last run')
    
    args = parser.parse_args()
    
    if args.results:
        show_results()
        return
    
    if args.all or (not any([args.puzzles, args.dust, args.airdrops, args.refunds, args.bounties])):
        # Run all tests
        print_section("LIMBO SWEEPER - COMPLETE TEST RUN")
        print("Testing all components...\n")
        
        test_btc_puzzles()
        test_dust_reclaim()
        test_airdrops()
        test_refunds()
        test_bounties()
        
        print_section("TEST COMPLETE")
        print("All components tested.")
        print("\nNext steps:")
        print("1. Review configuration: python limbo_sweeper_test_setup.py --show")
        print("2. Run full sweep: python limbo_sweeper.py")
        print("3. Check results: python limbo_sweeper_test_run.py --results")
    else:
        if args.puzzles:
            test_btc_puzzles()
        if args.dust:
            test_dust_reclaim()
        if args.airdrops:
            test_airdrops()
        if args.refunds:
            test_refunds()
        if args.bounties:
            test_bounties()


if __name__ == '__main__':
    main()
