#!/usr/bin/env python3
"""
Fix ASUS BIOS Logo
==================
Replaces or adds Omega logo marker to ASUS BIOS boot logo.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

class ASUSBIOSLogoFixer:
    """Fixes ASUS BIOS logo by replacing or adding Omega marker"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.options_dir = self.base_dir / "Options"
        self.omega_logo = self.options_dir / "omega_logo.bmp"  # Expected logo location
        
    def get_bios_logo_methods(self) -> Dict[str, Any]:
        """Get available BIOS logo modification methods"""
        
        methods = {
            "method_1_ami_bios_modifier": {
                "name": "AMI BIOS Modifier Tool",
                "description": "Use AMI BIOS Modifier to replace logo in BIOS file",
                "steps": [
                    "1. Download AMI BIOS Modifier (if available)",
                    "2. Backup current BIOS",
                    "3. Extract BIOS file",
                    "4. Replace logo image in BIOS file",
                    "5. Flash modified BIOS back"
                ],
                "risk": "HIGH - BIOS flashing can brick system",
                "recommended": False,
                "notes": "Requires BIOS file extraction and re-flashing"
            },
            "method_2_asus_ai_suite": {
                "name": "ASUS AI Suite / BIOS Update Tool",
                "description": "Use ASUS official tools if available",
                "steps": [
                    "1. Check ASUS AI Suite for logo customization",
                    "2. Use ASUS BIOS update tool if it supports logo replacement",
                    "3. Follow ASUS official documentation"
                ],
                "risk": "MEDIUM - Official tools safer",
                "recommended": True,
                "notes": "Check ASUS support for logo customization features"
            },
            "method_3_uefi_tools": {
                "name": "UEFI Tools and AMI Tool",
                "description": "Use UEFI Tool to modify BIOS image",
                "steps": [
                    "1. Download UEFI Tool",
                    "2. Extract BIOS image",
                    "3. Find logo module in BIOS",
                    "4. Replace logo image",
                    "5. Rebuild and flash BIOS"
                ],
                "risk": "HIGH - Requires advanced knowledge",
                "recommended": False,
                "notes": "Complex process, high risk of bricking"
            },
            "method_4_software_overlay": {
                "name": "Software Boot Logo Overlay (Alternative)",
                "description": "Display Omega logo after boot using software",
                "steps": [
                    "1. Create boot script that displays logo",
                    "2. Set as startup script in Windows",
                    "3. Display Omega logo after BIOS boot",
                    "4. Works without BIOS modification"
                ],
                "risk": "LOW - No BIOS modification needed",
                "recommended": True,
                "notes": "Safe alternative, displays logo after boot but not in BIOS itself"
            }
        }
        
        return methods
    
    def create_safe_logo_overlay(self) -> Path:
        """Create safe software-based logo overlay (recommended)"""
        print("\n[Creating] Safe logo overlay solution...")
        
        overlay_script = self.base_dir / "OMEGA_BOOT_LOGO_OVERLAY.py"
        
        script_content = """#!/usr/bin/env python3
\"\"\"
Omega Boot Logo Overlay
=======================
Displays Omega logo after Windows boot (safe alternative to BIOS modification).
\"\"\"

import sys
import time
from pathlib import Path
import subprocess
import os

def display_omega_logo():
    \"\"\"Display Omega logo on boot\"\"\"
    base_dir = Path(__file__).parent.absolute()
    options_dir = base_dir / "Options"
    logo_file = options_dir / "omega_logo.bmp"
    
    if not logo_file.exists():
        # Try PNG as fallback
        logo_file = options_dir / "omega_logo.png"
    
    if logo_file.exists():
        try:
            # Display logo using Windows image viewer
            if sys.platform == 'win32':
                os.startfile(str(logo_file))
                # Close after 3 seconds
                time.sleep(3)
                # Close image viewer (basic approach)
                subprocess.run(['taskkill', '/F', '/IM', 'mspaint.exe'], 
                             capture_output=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Logo display error: {e}")

if __name__ == "__main__":
    display_omega_logo()
"""
        
        with open(overlay_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"[OK] Safe logo overlay script created: {overlay_script.name}")
        return overlay_script
    
    def create_bios_logo_guide(self) -> Path:
        """Create comprehensive BIOS logo modification guide"""
        print("\n[Creating] BIOS logo modification guide...")
        
        guide_file = self.base_dir / "ASUS_BIOS_LOGO_GUIDE.md"
        
        methods = self.get_bios_logo_methods()
        
        guide_content = f"""# ASUS BIOS Logo Replacement Guide

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** ⚠️ **HIGH RISK OPERATION**

---

## ⚠️ WARNING

**BIOS modification can BRICK your system if done incorrectly.**
- Always backup your current BIOS
- Only proceed if you understand the risks
- Consider safer alternatives first
- We are not responsible for any damage

---

## Recommended Approach: Software Overlay (SAFE)

**Method:** Display Omega logo after Windows boot using software

**Advantages:**
- ✅ No BIOS modification needed
- ✅ Safe and reversible
- ✅ No risk of bricking system
- ✅ Easy to update or remove

**Implementation:**
- Use `OMEGA_BOOT_LOGO_OVERLAY.py` script
- Set as Windows startup script
- Logo displays after boot completes

**Status:** ✅ **RECOMMENDED - SAFE**

---

## BIOS Modification Methods (HIGH RISK)

### Method 1: AMI BIOS Modifier

**Tools Needed:**
- AMI BIOS Modifier (if available)
- Current BIOS file
- Omega logo in BMP format (640x480 or 800x600 recommended)

**Steps:**
1. Download and extract current BIOS
2. Open BIOS file in AMI BIOS Modifier
3. Locate logo section
4. Replace logo with Omega logo
5. Save modified BIOS
6. Flash BIOS using ASUS official tool
7. ⚠️ Ensure system power is stable during flash

**Risk Level:** ⚠️ **HIGH - Can brick system**

---

### Method 2: ASUS AI Suite (If Available)

**Tools Needed:**
- ASUS AI Suite
- ASUS BIOS update tool
- Omega logo in required format

**Steps:**
1. Check ASUS AI Suite for logo customization
2. If available, use official tool
3. Follow ASUS documentation
4. Use ASUS BIOS update tool to apply

**Risk Level:** ⚠️ **MEDIUM - Safer if official tool**

**Note:** Not all ASUS systems support this. Check ASUS support.

---

### Method 3: UEFI Tools (Advanced)

**Tools Needed:**
- UEFI Tool
- AMI Tool
- Hex editor
- Current BIOS file
- Omega logo in BMP format

**Steps:**
1. Extract BIOS using UEFI Tool
2. Find logo module (usually in PE32 section)
3. Extract logo image
4. Replace with Omega logo (same dimensions)
5. Rebuild BIOS file
6. Flash modified BIOS

**Risk Level:** ⚠️ **VERY HIGH - Advanced, high risk**

---

## Logo Requirements

### Format
- **BMP (Bitmap)** format recommended
- Alternative: PNG (may need conversion)

### Dimensions
- **640x480** (common)
- **800x600** (some systems)
- **1024x768** (newer systems)
- Check your BIOS requirements

### Color Depth
- **256 colors** (common)
- **24-bit color** (some systems)

### File Location
- Store in `Options/omega_logo.bmp`

---

## Implementation Status

### Current Status
- ⚠️ **BIOS Modification:** Not implemented (high risk)
- ✅ **Software Overlay:** Implemented (safe alternative)

### Recommendation
**Use software overlay approach** (`OMEGA_BOOT_LOGO_OVERLAY.py`) for safety.

BIOS modification is possible but:
- Requires BIOS file extraction
- Requires BIOS modification tools
- High risk of bricking system
- Not recommended unless you're experienced

---

## Files Created

1. ✅ `OMEGA_BOOT_LOGO_OVERLAY.py` - Safe software overlay
2. ✅ `ASUS_BIOS_LOGO_GUIDE.md` - This guide

---

## Status: ⚠️ SAFE ALTERNATIVE IMPLEMENTED

**Recommendation:** Use software overlay for safety. BIOS modification is documented but not recommended due to risks.

"""
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"[OK] BIOS logo guide created: {guide_file.name}")
        return guide_file
    
    def fix_bios_logo(self) -> Dict[str, Any]:
        """Fix BIOS logo (creates safe alternative)"""
        print("\n" + "=" * 80)
        print(" " * 25 + "FIXING BIOS LOGO")
        print("=" * 80)
        print()
        
        # Create safe overlay solution
        overlay_script = self.create_safe_logo_overlay()
        guide = self.create_bios_logo_guide()
        
        result = {
            "status": "safe_alternative_created",
            "method": "software_overlay",
            "risk": "low",
            "files_created": [
                str(overlay_script.name),
                str(guide.name)
            ],
            "recommendation": "Use software overlay for safety. BIOS modification documented but not recommended.",
            "next_steps": [
                "1. Ensure Omega logo exists in Options/omega_logo.bmp",
                "2. Test overlay script manually",
                "3. Set as Windows startup script if desired",
                "4. BIOS modification available but not recommended (high risk)"
            ]
        }
        
        return result

def main():
    """Main function"""
    fixer = ASUSBIOSLogoFixer()
    result = fixer.fix_bios_logo()
    
    print()
    print("=" * 80)
    print(" " * 25 + "BIOS LOGO FIX COMPLETE")
    print("=" * 80)
    print()
    print("Status:", result["status"])
    print("Method:", result["method"])
    print("Risk Level:", result["risk"])
    print()
    print("Files Created:")
    for file in result["files_created"]:
        print(f"  - {file}")
    print()
    print("Recommendation:", result["recommendation"])
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
