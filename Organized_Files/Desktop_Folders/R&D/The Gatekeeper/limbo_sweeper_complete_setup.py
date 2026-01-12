# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# LIMBO SWEEPER - COMPLETE SETUP
# Sets up PayPal, crypto wallets, and all features

import sys
import io
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
WALLET_FILE = ROOT / 'crypto_wallets.json'


def load_wallets():
    """Load crypto wallets."""
    if WALLET_FILE.exists():
        try:
            with open(WALLET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def complete_setup():
    """Complete setup with PayPal and crypto wallets."""
    print("=" * 80)
    print("  LIMBO SWEEPER - COMPLETE SETUP")
    print("=" * 80)
    print()
    
    # Load wallets
    wallets = load_wallets()
    if not wallets:
        print("Generating crypto wallets...")
        from limbo_sweeper_wallet_generator import create_wallets
        wallets = create_wallets()
        print()
    
    # PayPal configuration
    paypal_email = 'wipost21@gmail.com'
    
    # Create complete configuration
    config = {
        # Crypto wallets
        'bitcoin_address': wallets['bitcoin']['address'],
        'ethereum_address': wallets['ethereum']['address'],
        'testnet_address': wallets['testnet']['address'],
        
        # PayPal
        'paypal_email': paypal_email,
        'paypal_enabled': True,
        
        # Search settings
        'search_name': 'Ruth Berry',
        'search_state': 'TX',
        
        # Wallet addresses to check (add Bitcoin address)
        'wallet_addresses': [
            wallets['bitcoin']['address'],
            '1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF',  # Default test addresses
            '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
            '1CUNEBjYrZVX9nW9cp5vwV7NCPQVf2uL6P'
        ],
        
        # Features - ALL ENABLED
        'enable_btc_puzzles': True,
        'enable_dust_reclaim': True,
        'enable_airdrops': True,
        'enable_refunds': True,
        'enable_bounties': False,  # Requires Selenium
        
        # Settings
        'test_mode': False,  # Full mode
        'rate_limit_delay': 0.1
    }
    
    # Save configuration
    ROOT.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("Configuration Complete:")
    print()
    print("Crypto Wallets:")
    print(f"  Bitcoin: {config['bitcoin_address']}")
    print(f"  Ethereum: {config['ethereum_address']}")
    print(f"  Testnet: {config['testnet_address']}")
    print()
    print("Payment Methods:")
    print(f"  PayPal: {config['paypal_email']}")
    print()
    print("Search Settings:")
    print(f"  Name: {config['search_name']}")
    print(f"  State: {config['search_state']}")
    print()
    print("Features:")
    print(f"  Bitcoin Puzzles: {'✓' if config['enable_btc_puzzles'] else '✗'}")
    print(f"  Dust Reclamation: {'✓' if config['enable_dust_reclaim'] else '✗'}")
    print(f"  Airdrops: {'✓' if config['enable_airdrops'] else '✗'}")
    print(f"  Unclaimed Funds: {'✓' if config['enable_refunds'] else '✗'}")
    print(f"  Bug Bounties: {'✓' if config['enable_bounties'] else '✗'}")
    print()
    print(f"Configuration saved to: {CONFIG_FILE}")
    print()
    print("=" * 80)
    print("  SETUP COMPLETE - READY TO SWEEP")
    print("=" * 80)
    print()
    print("Next step: python limbo_sweeper.py")
    
    return config


if __name__ == '__main__':
    complete_setup()
