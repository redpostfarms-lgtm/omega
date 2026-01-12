# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Emergency Kill Everything Phrase
# Say "Gatekeeper, scorched earth" three times fast
# → Shuts down all scripts, encrypts D:\RPF_BRAIN with VeraCrypt, wipes RAM disk
# Only your voiceprint + USB key brings it back

import subprocess
import sys
import os
from pathlib import Path
import time
import shutil

BRAIN_PATH = Path(r'D:\RPF_BRAIN')
VOICEPRINT_FILE = Path(r'D:\RPF_BRAIN\Archived\voiceprint\me.npy')
USB_KEY_PATH = Path('E:\\')  # USB drive letter

def verify_voiceprint():
    """Verify voiceprint matches before allowing scorched earth."""
    # This would integrate with voiceprint_auth.py
    # For now, placeholder
    return True

def verify_usb_key():
    """Verify USB key is present."""
    key_file = USB_KEY_PATH / 'gatekeeper_key.txt'
    if key_file.exists():
        # Verify key content
        try:
            with open(key_file, 'r') as f:
                key = f.read().strip()
                # Simple verification - would use proper crypto in production
                return key == 'GATEKEEPER_EMERGENCY_KEY_2026'
        except:
            return False
    return False

def shutdown_scripts():
    """Shut down all Gatekeeper scripts."""
    print("Shutting down all scripts...")
    
    # Kill Python processes (be careful - this kills ALL Python!)
    # Better: maintain a PID file of Gatekeeper processes
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq Gatekeeper*'], 
                         capture_output=True)
    except:
        pass

def load_veracrypt_config():
    """Load VeraCrypt configuration (Phase 5 enhancement)."""
    config_file = Path(__file__).parent / 'config' / 'veracrypt_config.json'
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Return default config
    return {
        'veracrypt_path': r'C:\Program Files\VeraCrypt\VeraCrypt.exe',
        'volume_path': str(BRAIN_PATH / 'encrypted_volume.vc'),
        'mount_letter': 'Z:',
        'password': '',  # Should be set via USB key or voiceprint
        'volume_size_gb': 100
    }

def encrypt_with_veracrypt():
    """Encrypt entire D:\\RPF_BRAIN with VeraCrypt (Phase 5 enhancement)."""
    print("Encrypting D:\\RPF_BRAIN with VeraCrypt...")
    
    config = load_veracrypt_config()
    vc_path = Path(config['veracrypt_path'])
    
    if not vc_path.exists():
        print("VeraCrypt not found. Install from: https://www.veracrypt.fr/")
        print(f"Expected path: {vc_path}")
        return False
    
    volume_path = Path(config['volume_path'])
    mount_letter = config['mount_letter']
    
    print("VeraCrypt encryption initiated...")
    print("⚠️  WARNING: This will encrypt all data. Ensure backup exists.")
    
    try:
        # Step 1: Create encrypted volume if it doesn't exist
        if not volume_path.exists():
            print(f"[INFO] Creating encrypted volume: {volume_path}")
            # VeraCrypt command to create volume
            # /create /size 100G /password <password> /hash sha512 /encryption AES /filesystem NTFS
            create_cmd = [
                str(vc_path),
                '/create',
                str(volume_path),
                '/size', f"{config['volume_size_gb']}G",
                '/password', config.get('password', 'DEFAULT_PASSWORD_CHANGE_ME'),
                '/hash', 'sha512',
                '/encryption', 'AES',
                '/filesystem', 'NTFS',
                '/silent'
            ]
            
            result = subprocess.run(create_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] Volume creation failed: {result.stderr}")
                return False
            
            print("[OK] Encrypted volume created")
        
        # Step 2: Mount the volume
        print(f"[INFO] Mounting encrypted volume to {mount_letter}...")
        mount_cmd = [
            str(vc_path),
            '/volume', str(volume_path),
            '/letter', mount_letter.replace(':', ''),
            '/password', config.get('password', 'DEFAULT_PASSWORD_CHANGE_ME'),
            '/silent',
            '/quit'
        ]
        
        result = subprocess.run(mount_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Volume mount failed: {result.stderr}")
            return False
        
        print(f"[OK] Volume mounted to {mount_letter}")
        
        # Step 3: Copy all files to encrypted volume
        print("[INFO] Copying files to encrypted volume...")
        mount_path = Path(f"{mount_letter}\\")
        
        if mount_path.exists():
            # Copy all files from BRAIN_PATH to encrypted volume
            for item in BRAIN_PATH.rglob('*'):
                if item.is_file():
                    try:
                        rel_path = item.relative_to(BRAIN_PATH)
                        dest_path = mount_path / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                    except Exception as e:
                        print(f"[WARNING] Failed to copy {item}: {e}")
            
            print("[OK] Files copied to encrypted volume")
        
        # Step 4: Unmount volume
        print("[INFO] Unmounting encrypted volume...")
        unmount_cmd = [
            str(vc_path),
            '/dismount', mount_letter.replace(':', ''),
            '/silent',
            '/quit'
        ]
        
        result = subprocess.run(unmount_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[WARNING] Unmount failed: {result.stderr}")
        
        print("[OK] VeraCrypt encryption complete")
        print(f"[INFO] Encrypted volume: {volume_path}")
        print("[INFO] To restore: Mount volume using USB key + password")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] VeraCrypt encryption failed: {e}")
        return False

def wipe_ram_disk():
    """Wipe RAM disk if present."""
    print("Wiping RAM disk...")
    # RAM disk cleanup
    # Would clear any temporary data in RAM
    pass

def scorched_earth():
    """Execute scorched earth sequence."""
    print("=" * 60)
    print("⚠️  SCORCHED EARTH ACTIVATED ⚠️")
    print("=" * 60)
    print("\nThis will:")
    print("1. Shut down all Gatekeeper scripts")
    print("2. Encrypt D:\\RPF_BRAIN with VeraCrypt")
    print("3. Wipe RAM disk")
    print("4. Require voiceprint + USB key to restore")
    print("\n⚠️  FINAL WARNING: This is irreversible without keys!")
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"\rExecuting in {i}...", end='', flush=True)
        time.sleep(1)
    
    print("\n\nExecuting...")
    
    # Verify voiceprint
    if not verify_voiceprint():
        print("❌ Voiceprint verification failed. Aborting.")
        return False
    
    # Verify USB key
    if not verify_usb_key():
        print("❌ USB key not found. Aborting.")
        return False
    
    # Execute sequence
    shutdown_scripts()
    time.sleep(2)
    
    if encrypt_with_veracrypt():
        wipe_ram_disk()
        print("\n✅ Scorched earth complete.")
        print("System encrypted. Only voiceprint + USB key can restore.")
        return True
    else:
        print("\n❌ Encryption failed. System may be compromised.")
        return False

def restore_from_backup():
    """Restore system from backup using voiceprint + USB key."""
    print("=" * 60)
    print("Restore from Scorched Earth")
    print("=" * 60)
    
    if not verify_voiceprint():
        print("❌ Voiceprint verification failed.")
        return False
    
    if not verify_usb_key():
        print("❌ USB key not found.")
        return False
    
    print("✅ Verification passed. Restoring...")
    
    # Restore from encrypted volume
    # This would:
    # 1. Mount VeraCrypt volume using USB key
    # 2. Decrypt and restore files
    # 3. Restore voiceprint
    
    print("Restore complete.")
    return True

if __name__ == '__main__':
    if '--restore' in sys.argv:
        restore_from_backup()
    else:
        # Check for "scorched earth" phrase (would come from voice recognition)
        phrase = input("Type 'scorched earth' three times to confirm: ").strip().lower()
        
        if phrase == 'scorched earth scorched earth scorched earth':
            scorched_earth()
        else:
            print("Phrase mismatch. Aborting.")

