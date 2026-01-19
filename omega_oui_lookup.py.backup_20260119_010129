#!/usr/bin/env python3
"""
Omega OUI Lookup System
=======================
Organizationally Unique Identifier (OUI) lookup for network device identification.
Essential for ICS/OT security, asset inventory, and MAC spoofing detection.

Features:
- Offline OUI database support (air-gapped environments)
- Online API fallback (macvendors.com, maclookup.app)
- Multiple MAC address format support
- Batch lookup capabilities
- Integration with network monitoring systems
"""

import csv
import re
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import urllib.request
import urllib.error
import time

# OUI Database Configuration
OUI_CSV_URL = "https://standards-oui.ieee.org/oui/oui.csv"
OUI_CSV_LOCAL = Path("oui.csv")
OUI_JSON_CACHE = Path(".oui_cache.json")

# Online API endpoints (fallback)
MACVENDORS_API = "https://api.macvendors.com"
MACLOOKUP_API = "https://api.maclookup.app/v2/macs"

@dataclass
class VendorInfo:
    """Vendor information from OUI lookup"""
    oui: str
    vendor_name: str
    assignment_date: Optional[str] = None
    company_address: Optional[str] = None
    is_private: bool = False
    is_locally_administered: bool = False
    lookup_method: str = "unknown"  # 'local', 'api_macvendors', 'api_maclookup'

class OUILookup:
    """OUI Lookup System for Network Device Identification"""
    
    def __init__(self, oui_csv_path: Optional[Path] = None, use_cache: bool = True):
        """
        Initialize OUI lookup system.
        
        Args:
            oui_csv_path: Path to local OUI CSV file (downloads if not provided)
            use_cache: Whether to use JSON cache for faster lookups
        """
        self.oui_csv_path = oui_csv_path or OUI_CSV_LOCAL
        self.use_cache = use_cache
        self.oui_db: Dict[str, Dict] = {}
        self.cache_loaded = False
        
        # Load OUI database
        self._load_oui_database()
    
    def _load_oui_database(self):
        """Load OUI database from CSV or cache"""
        # Try loading from JSON cache first (faster)
        if self.use_cache and OUI_JSON_CACHE.exists():
            try:
                with OUI_JSON_CACHE.open('r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.oui_db = cache_data.get('oui_map', {})
                    self.cache_loaded = True
                    print(f"[OUI] Loaded {len(self.oui_db)} OUIs from cache")
                    return
            except Exception as e:
                print(f"[OUI] Cache load failed: {e}, loading from CSV...")
        
        # Load from CSV
        if self.oui_csv_path.exists():
            try:
                self._load_from_csv()
                # Save to cache for next time
                if self.use_cache:
                    self._save_cache()
            except Exception as e:
                print(f"[OUI] Failed to load CSV: {e}")
                print(f"[OUI] Will use online API fallback")
        else:
            print(f"[OUI] CSV not found at {self.oui_csv_path}")
            print(f"[OUI] Download from: {OUI_CSV_URL}")
            print(f"[OUI] Will use online API fallback")
    
    def _load_from_csv(self):
        """Load OUI database from IEEE CSV file"""
        print(f"[OUI] Loading OUI database from {self.oui_csv_path}...")
        oui_count = 0
        
        with self.oui_csv_path.open('r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Extract OUI from Assignment column (format: "00-1A-2B" or "001A2B")
                    assignment = row.get("Assignment", "").strip()
                    if not assignment:
                        continue
                    
                    # Normalize OUI (remove separators, uppercase)
                    oui = assignment.replace("-", "").replace(":", "").replace(".", "").upper()
                    if len(oui) < 6:
                        continue
                    oui = oui[:6]  # Take first 6 hex digits
                    
                    # Store vendor information
                    vendor_name = row.get("Organization Name", "").strip()
                    if vendor_name:
                        self.oui_db[oui] = {
                            'vendor': vendor_name,
                            'assignment': assignment,
                            'address': row.get("Organization Address", "").strip(),
                            'date': row.get("Registry", "").strip()
                        }
                        oui_count += 1
                except Exception as e:
                    # Skip malformed rows
                    continue
        
        print(f"[OUI] Loaded {oui_count} OUIs from CSV")
        self.cache_loaded = True
    
    def _save_cache(self):
        """Save OUI database to JSON cache for faster loading"""
        try:
            cache_data = {
                'oui_map': self.oui_db,
                'last_updated': datetime.now().isoformat(),
                'count': len(self.oui_db)
            }
            with OUI_JSON_CACHE.open('w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print(f"[OUI] Cache saved to {OUI_JSON_CACHE}")
        except Exception as e:
            print(f"[OUI] Failed to save cache: {e}")
    
    def _extract_oui(self, mac: str) -> Optional[str]:
        """
        Extract OUI (first 6 hex digits) from MAC address.
        Handles multiple formats: 00:1A:2B:3C:4D:5E, 00-1A-2B-3C-4D-5E, 001A.2B3C.4D5E, etc.
        """
        # Remove all separators and convert to uppercase
        cleaned = ''.join(c for c in mac.upper() if c.isalnum())
        
        # Validate: must be at least 6 hex digits
        if len(cleaned) < 6:
            return None
        
        # Check if all characters are valid hex
        if not all(c in '0123456789ABCDEF' for c in cleaned[:6]):
            return None
        
        oui = cleaned[:6]
        
        # Check if locally administered (U/L bit = 1)
        # Second LSB of first byte: if bit 1 of first hex digit is set
        first_byte = int(oui[0:2], 16)
        is_locally_administered = bool(first_byte & 0x02)
        
        return oui
    
    def _check_locally_administered(self, mac: str) -> bool:
        """Check if MAC address is locally administered (U/L bit = 1)"""
        cleaned = ''.join(c for c in mac.upper() if c.isalnum())
        if len(cleaned) < 2:
            return False
        first_byte = int(cleaned[0:2], 16)
        return bool(first_byte & 0x02)
    
    def _lookup_online_macvendors(self, oui: str) -> Optional[str]:
        """Lookup vendor using macvendors.com API"""
        try:
            url = f"{MACVENDORS_API}/{oui}"
            with urllib.request.urlopen(url, timeout=5) as response:
                vendor = response.read().decode('utf-8').strip()
                if vendor and not vendor.startswith("Not Found"):
                    return vendor
        except Exception:
            pass
        return None
    
    def _lookup_online_maclookup(self, oui: str) -> Optional[Dict]:
        """Lookup vendor using maclookup.app API"""
        try:
            # Format OUI with dashes for API
            oui_formatted = f"{oui[0:2]}-{oui[2:4]}-{oui[4:6]}"
            url = f"{MACLOOKUP_API}/{oui_formatted}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('success') and data.get('vendor'):
                    return {
                        'vendor': data.get('vendor'),
                        'address': data.get('address', ''),
                        'country': data.get('country', '')
                    }
        except Exception:
            pass
        return None
    
    def lookup(self, mac: str, use_online: bool = True) -> VendorInfo:
        """
        Lookup vendor information for a MAC address.
        
        Args:
            mac: MAC address in any format (00:1A:2B:3C:4D:5E, etc.)
            use_online: Whether to use online API if local lookup fails
        
        Returns:
            VendorInfo object with vendor details
        """
        # Extract OUI
        oui = self._extract_oui(mac)
        if not oui:
            return VendorInfo(
                oui="",
                vendor_name="Invalid MAC format",
                lookup_method="error"
            )
        
        # Check if locally administered
        is_locally_administered = self._check_locally_administered(mac)
        if is_locally_administered:
            return VendorInfo(
                oui=oui,
                vendor_name="Locally Administered (U/L bit = 1)",
                is_locally_administered=True,
                lookup_method="local_check"
            )
        
        # Try local database first
        if self.oui_db and oui in self.oui_db:
            vendor_data = self.oui_db[oui]
            return VendorInfo(
                oui=oui,
                vendor_name=vendor_data['vendor'],
                assignment_date=vendor_data.get('date'),
                company_address=vendor_data.get('address'),
                lookup_method="local"
            )
        
        # Try online APIs if enabled
        if use_online:
            # Try macvendors.com first (simpler)
            vendor = self._lookup_online_macvendors(oui)
            if vendor:
                return VendorInfo(
                    oui=oui,
                    vendor_name=vendor,
                    lookup_method="api_macvendors"
                )
            
            # Try maclookup.app (more detailed)
            vendor_data = self._lookup_online_maclookup(oui)
            if vendor_data:
                return VendorInfo(
                    oui=oui,
                    vendor_name=vendor_data['vendor'],
                    company_address=vendor_data.get('address', ''),
                    lookup_method="api_maclookup"
                )
        
        # Not found
        return VendorInfo(
            oui=oui,
            vendor_name="Unknown / Unassigned OUI",
            lookup_method="not_found"
        )
    
    def lookup_batch(self, mac_addresses: List[str], use_online: bool = True) -> List[VendorInfo]:
        """
        Lookup multiple MAC addresses at once.
        
        Args:
            mac_addresses: List of MAC addresses
            use_online: Whether to use online API for missing entries
        
        Returns:
            List of VendorInfo objects
        """
        results = []
        for mac in mac_addresses:
            result = self.lookup(mac, use_online=use_online)
            results.append(result)
            # Rate limiting for online API (be nice to free services)
            if use_online and result.lookup_method.startswith("api_"):
                time.sleep(0.1)  # 100ms delay between API calls
        return results
    
    def download_oui_database(self, force: bool = False) -> bool:
        """
        Download latest OUI database from IEEE.
        
        Args:
            force: Force download even if file exists
        
        Returns:
            True if successful, False otherwise
        """
        if self.oui_csv_path.exists() and not force:
            print(f"[OUI] Database already exists at {self.oui_csv_path}")
            return True
        
        print(f"[OUI] Downloading OUI database from IEEE...")
        try:
            urllib.request.urlretrieve(OUI_CSV_URL, self.oui_csv_path)
            print(f"[OUI] Download complete: {self.oui_csv_path}")
            # Reload database
            self._load_from_csv()
            if self.use_cache:
                self._save_cache()
            return True
        except Exception as e:
            print(f"[OUI] Download failed: {e}")
            return False


# Convenience functions
_global_lookup = None

def get_oui_lookup() -> OUILookup:
    """Get global OUI lookup instance (singleton)"""
    global _global_lookup
    if _global_lookup is None:
        _global_lookup = OUILookup()
    return _global_lookup

def lookup_vendor(mac: str, use_online: bool = True) -> str:
    """
    Quick lookup function - returns vendor name as string.
    
    Args:
        mac: MAC address
        use_online: Whether to use online API if local lookup fails
    
    Returns:
        Vendor name string
    """
    lookup = get_oui_lookup()
    result = lookup.lookup(mac, use_online=use_online)
    return result.vendor_name

def lookup_vendor_detailed(mac: str, use_online: bool = True) -> VendorInfo:
    """
    Detailed lookup function - returns full VendorInfo object.
    
    Args:
        mac: MAC address
        use_online: Whether to use online API if local lookup fails
    
    Returns:
        VendorInfo object with all details
    """
    lookup = get_oui_lookup()
    return lookup.lookup(mac, use_online=use_online)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("OMEGA OUI LOOKUP SYSTEM")
    print("=" * 80)
    print()
    
    # Initialize lookup system
    lookup = OUILookup()
    
    # Test MAC addresses
    test_macs = [
        "00:1A:2B:3C:4D:5E",      # Dell Inc.
        "00-50-56-AB-CD-EF",      # VMware, Inc.
        "001A.2B3C.4D5E",         # Dell Inc. (different format)
        "AA:BB:CC:DD:EE:FF",      # Unknown
        "02:00:00:00:00:00",      # Locally administered
    ]
    
    print("Testing OUI Lookup:")
    print("-" * 80)
    for mac in test_macs:
        result = lookup.lookup(mac, use_online=True)
        print(f"MAC: {mac:20} → {result.vendor_name:40} [{result.lookup_method}]")
        if result.is_locally_administered:
            print(f"  └─ Locally administered address (U/L bit = 1)")
        if result.company_address:
            print(f"  └─ Address: {result.company_address}")
    print()
    
    # Instructions for downloading database
    if not OUI_CSV_LOCAL.exists():
        print("=" * 80)
        print("SETUP INSTRUCTIONS")
        print("=" * 80)
        print(f"1. Download OUI database from: {OUI_CSV_URL}")
        print(f"2. Save to: {OUI_CSV_LOCAL}")
        print("3. Or run: lookup.download_oui_database()")
        print()
        print("For air-gapped environments, download the CSV manually and place")
        print("it in the project directory.")
        print()
