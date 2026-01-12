# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Auto-heal system for Gatekeeper voice configuration
# Binary, checksummed, auto-verified on boot
# If file's gone or hash flips? Rebuilds automatically.

import hashlib
import pickle
import json
import sys
import io
from pathlib import Path
import subprocess
import urllib.request
import urllib.error

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

VOICE_DIR = Path(r'D:\RPF_BRAIN\Archived\voiceprint\tuned')
VOICE_DIR.mkdir(parents=True, exist_ok=True)
TUNE_FILE = VOICE_DIR / 'tune.pkl'
CHECKSUM_FILE = VOICE_DIR / 'tune.checksum'
GITHUB_REPO = "your-username/your-repo"  # Update with actual repo
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/The%20Gatekeeper/voice_tuner.py"

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def save_checksum(file_path, checksum_file):
    """Save checksum to file."""
    checksum = calculate_checksum(file_path)
    if checksum:
        with open(checksum_file, 'w') as f:
            f.write(checksum)
    return checksum

def verify_checksum(file_path, checksum_file):
    """Verify file integrity against saved checksum."""
    if not file_path.exists():
        return False
    
    if not checksum_file.exists():
        # First run - save checksum
        save_checksum(file_path, checksum_file)
        return True
    
    current_checksum = calculate_checksum(file_path)
    saved_checksum = checksum_file.read_text().strip()
    
    return current_checksum == saved_checksum

def download_from_github(file_url, save_path):
    """Download file from GitHub raw URL."""
    try:
        print(f"Downloading from GitHub: {file_url}")
        urllib.request.urlretrieve(file_url, save_path)
        print(f"Downloaded to: {save_path}")
        return True
    except urllib.error.URLError as e:
        print(f"GitHub download failed: {e}")
        return False

def rebuild_voice():
    """Rebuild voice configuration from defaults or GitHub."""
    print("Rebuilding voice configuration...")
    
    # Try to download from GitHub first
    voice_tuner_path = Path(__file__).parent / 'voice_tuner.py'
    if not voice_tuner_path.exists():
        # Try downloading voice_tuner.py from GitHub
        if download_from_github(GITHUB_RAW, voice_tuner_path):
            print("Voice tuner downloaded from GitHub.")
    
    # Rebuild with defaults
    default_tune = {'pitch': 55, 'echo': 0.12}
    
    try:
        with open(TUNE_FILE, 'wb') as f:
            pickle.dump(default_tune, f)
        print(f"Rebuilt tune.pkl with defaults: {default_tune}")
        
        # Save checksum
        save_checksum(TUNE_FILE, CHECKSUM_FILE)
        print("Checksum saved.")
        return True
    except Exception as e:
        print(f"Failed to rebuild: {e}")
        return False

def restore_voiceprint():
    """Restore voiceprint from backup or GitHub."""
    voiceprint_file = Path(r'D:\RPF_BRAIN\Archived\voiceprint\me.npy')
    voiceprint_backup = Path(r'D:\RPF_BRAIN\Archived\voiceprint\me.npy.backup')
    
    if voiceprint_backup.exists():
        print("Restoring voiceprint from backup...")
        import shutil
        shutil.copy(voiceprint_backup, voiceprint_file)
        print("Voiceprint restored.")
        return True
    else:
        print("No voiceprint backup found. Run voiceprint_auth.py to capture.")
        return False

def auto_heal():
    """Main auto-heal routine - runs on boot."""
    print("=" * 60)
    print("Gatekeeper Auto-Heal System")
    print("=" * 60)
    print(f"Checking: {TUNE_FILE}")
    
    # Check if tune.pkl exists
    if not TUNE_FILE.exists():
        print("❌ tune.pkl missing. Rebuilding...")
        if rebuild_voice():
            print("✅ Rebuilt successfully.")
        else:
            print("❌ Rebuild failed. Manual intervention needed.")
            return False
    
    # Verify checksum
    if not verify_checksum(TUNE_FILE, CHECKSUM_FILE):
        print("❌ Checksum mismatch. File may be corrupted. Rebuilding...")
        if rebuild_voice():
            print("✅ Rebuilt and verified.")
        else:
            print("❌ Rebuild failed.")
            return False
    else:
        print("✅ Checksum verified. File integrity OK.")
    
    # Verify voiceprint
    voiceprint_file = Path(r'D:\RPF_BRAIN\Archived\voiceprint\me.npy')
    if not voiceprint_file.exists():
        print("⚠️  Voiceprint missing. Attempting restore...")
        restore_voiceprint()
    
    # Verify voice tuner script exists
    voice_tuner = Path(__file__).parent / 'voice_tuner.py'
    if not voice_tuner.exists():
        print("⚠️  voice_tuner.py missing. Downloading from GitHub...")
        download_from_github(GITHUB_RAW, voice_tuner)
    
    print("\n✅ Auto-heal complete. Gatekeeper ready.")
    # RPF-GK-OWNER-2026-7A3F9B2C (ownership signature)
    return True

def create_backup():
    """Create backup of critical files."""
    print("Creating backups...")
    
    # Backup tune.pkl
    if TUNE_FILE.exists():
        backup_file = TUNE_FILE.with_suffix('.pkl.backup')
        import shutil
        shutil.copy(TUNE_FILE, backup_file)
        print(f"Backed up: {backup_file}")
    
    # Backup voiceprint
    voiceprint_file = Path(r'D:\RPF_BRAIN\Archived\voiceprint\me.npy')
    if voiceprint_file.exists():
        backup_file = voiceprint_file.with_suffix('.npy.backup')
        import shutil
        shutil.copy(voiceprint_file, backup_file)
        print(f"Backed up: {backup_file}")
    
    # Save checksum
    if TUNE_FILE.exists():
        save_checksum(TUNE_FILE, CHECKSUM_FILE)
        print(f"Checksum saved: {CHECKSUM_FILE}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gatekeeper Auto-Heal System')
    parser.add_argument('--backup', action='store_true', help='Create backup of critical files')
    parser.add_argument('--verify', action='store_true', help='Verify integrity only')
    
    args = parser.parse_args()
    
    if args.backup:
        create_backup()
    elif args.verify:
        if verify_checksum(TUNE_FILE, CHECKSUM_FILE):
            print("✅ Verification passed.")
        else:
            print("❌ Verification failed.")
            sys.exit(1)
    else:
        # Default: auto-heal on boot
        success = auto_heal()
        sys.exit(0 if success else 1)

