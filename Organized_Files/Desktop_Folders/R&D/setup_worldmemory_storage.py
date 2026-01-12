"""
Setup WorldMemory Storage Services
Helps configure storage services for WorldMemory

Red Post Farms, LLC - 2026
"""

import os
import sys
from pathlib import Path

print("="*80)
print("WORLDMEMORY STORAGE SETUP")
print("="*80)
print("\nThis script helps configure storage services for WorldMemory.")
print("WorldMemory can use multiple storage services for permanent storage:\n")

print("1. WEB3.STORAGE (Recommended - Free Tier)")
print("   - 5 GB free storage per month")
print("   - No credit card required")
print("   - Get token at: https://web3.storage")
print("   - Steps:")
print("     1. Visit https://web3.storage")
print("     2. Sign up with email")
print("     3. Create new token")
print("     4. Copy token and set environment variable:")
print("        set WEB3_STORAGE_TOKEN=your_token_here")
print()

print("2. NFT.STORAGE (Alternative - Free Tier)")
print("   - Free IPFS storage")
print("   - Get token at: https://nft.storage")
print("   - Steps:")
print("     1. Visit https://nft.storage")
print("     2. Sign up with email")
print("     3. Create new API key")
print("     4. Copy token and set environment variable:")
print("        set NFT_STORAGE_TOKEN=your_token_here")
print()

print("3. PINATA (IPFS Gateway - Free Tier)")
print("   - 1 GB free storage")
print("   - Get API keys at: https://pinata.cloud")
print("   - Steps:")
print("     1. Visit https://pinata.cloud")
print("     2. Sign up")
print("     3. Go to API Keys section")
print("     4. Create new API key")
print("     5. Set environment variables:")
print("        set PINATA_API_KEY=your_api_key")
print("        set PINATA_API_SECRET=your_api_secret")
print()

print("4. ARWEAVE (Blockchain Storage - Requires AR tokens)")
print("   - Permanent blockchain storage")
print("   - Requires AR tokens (cryptocurrency)")
print("   - Wallet is auto-generated on first run")
print("   - Note: Requires funding with AR tokens")
print()

print("="*80)
print("QUICK SETUP (Windows)")
print("="*80)
print("\nFor Web3.Storage (recommended):")
print("1. Get your token from https://web3.storage")
print("2. Run this command in PowerShell:")
print('   $env:WEB3_STORAGE_TOKEN="your_token_here"')
print("3. Or set permanently in System Environment Variables")
print()

print("For NFT.Storage:")
print("1. Get your token from https://nft.storage")
print("2. Run this command in PowerShell:")
print('   $env:NFT_STORAGE_TOKEN="your_token_here"')
print()

print("For Pinata:")
print("1. Get your API keys from https://pinata.cloud")
print("2. Run these commands in PowerShell:")
print('   $env:PINATA_API_KEY="your_api_key"')
print('   $env:PINATA_API_SECRET="your_api_secret"')
print()

print("="*80)
print("LOCAL-ONLY MODE")
print("="*80)
print("\nWorldMemory now supports LOCAL-ONLY mode!")
print("If no storage services are configured, facts are stored locally.")
print("This means:")
print("  - Facts are saved to the memory map file")
print("  - Data is encrypted and stored locally")
print("  - Can be queried like normal facts")
print("  - Not uploaded to permanent storage")
print("  - Perfect for testing or local use")
print()

print("="*80)
print("VERIFY SETUP")
print("="*80)
print("\nChecking current configuration...\n")

has_web3 = os.getenv("WEB3_STORAGE_TOKEN", "")
has_nft = os.getenv("NFT_STORAGE_TOKEN", "")
has_pinata_key = os.getenv("PINATA_API_KEY", "")
has_pinata_secret = os.getenv("PINATA_API_SECRET", "")

print(f"WEB3_STORAGE_TOKEN: {'CONFIGURED' if has_web3 else 'NOT SET'}")
print(f"NFT_STORAGE_TOKEN: {'CONFIGURED' if has_nft else 'NOT SET'}")
print(f"PINATA_API_KEY: {'CONFIGURED' if has_pinata_key else 'NOT SET'}")
print(f"PINATA_API_SECRET: {'CONFIGURED' if has_pinata_secret else 'NOT SET'}")
print()

if has_web3 or has_nft or (has_pinata_key and has_pinata_secret):
    print("OK At least one storage service is configured!")
    print("\nTest it:")
    print('  python WorldMemory.py add "test fact"')
    print('  python WorldMemory.py query test')
else:
    print("INFO No storage services configured.")
    print("WorldMemory will use LOCAL-ONLY mode.")
    print("Facts will be stored locally (not uploaded to permanent storage).")
    print("\nTo enable permanent storage, configure one of the services above.")

print("\n" + "="*80)
print("SETUP COMPLETE")
print("="*80)

