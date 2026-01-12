# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# WALLET ACCESS - View and Check Wallets

import sys
import io
import json
import webbrowser
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
WALLET_FILE = ROOT / 'crypto_wallets.json'
CONFIG_FILE = ROOT / 'limbo_config.json'


def load_wallets():
    """Load wallet information."""
    if WALLET_FILE.exists():
        try:
            with open(WALLET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def load_config():
    """Load configuration."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def show_wallets():
    """Display wallet information."""
    print("=" * 80)
    print("  CRYPTO WALLETS - ACCESS")
    print("=" * 80)
    print()
    
    wallets = load_wallets()
    config = load_config()
    
    if wallets:
        print("Bitcoin Wallet:")
        print(f"  Address: {wallets['bitcoin']['address']}")
        print(f"  Type: {wallets['bitcoin']['type']}")
        print(f"  Check balance: https://blockstream.info/address/{wallets['bitcoin']['address']}")
        print()
        
        print("Ethereum Wallet:")
        print(f"  Address: {wallets['ethereum']['address']}")
        print(f"  Type: {wallets['ethereum']['type']}")
        print(f"  Check balance: https://etherscan.io/address/{wallets['ethereum']['address']}")
        print()
        
        print("Testnet Wallet:")
        print(f"  Address: {wallets['testnet']['address']}")
        print(f"  Type: {wallets['testnet']['type']}")
        print(f"  Check balance: https://sepolia.etherscan.io/address/{wallets['testnet']['address']}")
        print()
        
        print("Private Keys:")
        print("  ⚠️  Private keys are stored in: crypto_wallets.json")
        print("  ⚠️  Keep this file secure!")
        print()
    else:
        print("No wallets found. Run limbo_sweeper_wallet_generator.py first.")
        print()
    
    if config:
        print("Payment Methods:")
        if config.get('paypal_email'):
            print(f"  PayPal: {config['paypal_email']}")
        print()
    
    print("=" * 80)


def open_bitcoin_explorer():
    """Open Bitcoin address in block explorer."""
    wallets = load_wallets()
    if wallets:
        address = wallets['bitcoin']['address']
        url = f'https://blockstream.info/address/{address}'
        webbrowser.open(url)
        print(f"Opened Bitcoin explorer: {url}")
    else:
        print("No Bitcoin wallet found")


def open_ethereum_explorer():
    """Open Ethereum address in block explorer."""
    wallets = load_wallets()
    if wallets:
        address = wallets['ethereum']['address']
        url = f'https://etherscan.io/address/{address}'
        webbrowser.open(url)
        print(f"Opened Ethereum explorer: {url}")
    else:
        print("No Ethereum wallet found")


def open_testnet_explorer():
    """Open testnet address in block explorer."""
    wallets = load_wallets()
    if wallets:
        address = wallets['testnet']['address']
        url = f'https://sepolia.etherscan.io/address/{address}'
        webbrowser.open(url)
        print(f"Opened testnet explorer: {url}")
    else:
        print("No testnet wallet found")


def show_private_keys():
    """Show private keys (with warning)."""
    wallets = load_wallets()
    if wallets:
        print("=" * 80)
        print("  PRIVATE KEYS - KEEP SECURE!")
        print("=" * 80)
        print()
        print("⚠️  WARNING: Never share private keys with anyone!")
        print("⚠️  Anyone with your private key can access your wallet!")
        print()
        print("Bitcoin Private Key:")
        print(f"  {wallets['bitcoin']['private_key']}")
        print()
        print("Ethereum Private Key:")
        print(f"  {wallets['ethereum']['private_key']}")
        print()
        print("Testnet Private Key:")
        print(f"  {wallets['testnet']['private_key']}")
        print()
        print("=" * 80)
    else:
        print("No wallets found")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Wallet Access')
    parser.add_argument('--show', action='store_true', help='Show wallet info')
    parser.add_argument('--btc', action='store_true', help='Open Bitcoin explorer')
    parser.add_argument('--eth', action='store_true', help='Open Ethereum explorer')
    parser.add_argument('--testnet', action='store_true', help='Open testnet explorer')
    parser.add_argument('--keys', action='store_true', help='Show private keys (WARNING)')
    
    args = parser.parse_args()
    
    if args.btc:
        open_bitcoin_explorer()
    elif args.eth:
        open_ethereum_explorer()
    elif args.testnet:
        open_testnet_explorer()
    elif args.keys:
        show_private_keys()
    else:
        show_wallets()


if __name__ == '__main__':
    main()
