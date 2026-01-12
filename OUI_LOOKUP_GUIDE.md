# OUI Lookup System - User Guide

**Date:** 2026-01-10  
**Status:** ✅ Complete and Ready

---

## Overview

The OUI (Organizationally Unique Identifier) Lookup System enables identification of network device manufacturers based on MAC addresses. This is essential for:

- **ICS/OT Security**: Identify unknown devices on industrial networks
- **Asset Inventory**: Map all network devices to vendors
- **MAC Spoofing Detection**: Detect when devices claim incorrect vendors
- **Network Monitoring**: Track device types and manufacturers

---

## Quick Start

### Basic Usage

```python
from omega_oui_lookup import lookup_vendor, lookup_vendor_detailed

# Simple lookup (returns vendor name string)
vendor = lookup_vendor("00:1A:2B:3C:4D:5E")
print(vendor)  # → "Dell Inc."

# Detailed lookup (returns VendorInfo object)
info = lookup_vendor_detailed("00:50:56:AB:CD:EF")
print(f"Vendor: {info.vendor_name}")
print(f"Method: {info.lookup_method}")
print(f"OUI: {info.oui}")
```

### Advanced Usage

```python
from omega_oui_lookup import OUILookup

# Initialize lookup system
lookup = OUILookup()

# Lookup single MAC address
result = lookup.lookup("00:1A:2B:3C:4D:5E", use_online=True)
print(f"Vendor: {result.vendor_name}")
print(f"Address: {result.company_address}")
print(f"Locally Administered: {result.is_locally_administered}")

# Batch lookup (multiple MACs)
macs = [
    "00:1A:2B:3C:4D:5E",
    "00-50-56-AB-CD-EF",
    "001A.2B3C.4D5E"
]
results = lookup.lookup_batch(macs, use_online=True)
for result in results:
    print(f"{result.oui} → {result.vendor_name}")
```

---

## Setup Instructions

### Option 1: Online API (No Setup Required)

The system will automatically use online APIs (macvendors.com, maclookup.app) if the local database is not available. This works immediately but requires internet access.

### Option 2: Offline Database (Recommended for ICS/OT)

For air-gapped environments or faster lookups:

1. **Download OUI Database:**
   ```python
   from omega_oui_lookup import OUILookup
   lookup = OUILookup()
   lookup.download_oui_database()
   ```

2. **Or Download Manually:**
   - URL: https://standards-oui.ieee.org/oui/oui.csv
   - Save to: `oui.csv` in project directory

3. **Automatic Caching:**
   - First load creates `.oui_cache.json` for faster subsequent lookups
   - Cache is automatically used if available

---

## MAC Address Formats Supported

The system handles multiple MAC address formats:

- `00:1A:2B:3C:4D:5E` (colon-separated)
- `00-1A-2B-3C-4D-5E` (dash-separated)
- `001A.2B3C.4D5E` (dot-separated)
- `001A2B3C4D5E` (no separators)

---

## Special Cases

### Locally Administered Addresses

MAC addresses with the U/L (Universal/Local) bit set (second LSB of first byte = 1) are locally administered and cannot be looked up:

```python
result = lookup.lookup("02:00:00:00:00:00")
print(result.vendor_name)  # → "Locally Administered (U/L bit = 1)"
print(result.is_locally_administered)  # → True
```

**Common Uses:**
- Virtual machines (VMware, VirtualBox)
- Privacy-randomized MACs (iOS, Android)
- Locally bridged networks

### Unknown/Unassigned OUIs

If an OUI is not found in the database:

```python
result = lookup.lookup("AA:BB:CC:DD:EE:FF")
print(result.vendor_name)  # → "Unknown / Unassigned OUI"
```

**Possible Reasons:**
- OUI not yet assigned by IEEE
- Private OUI block (not in public registry)
- Invalid MAC address

---

## Integration Examples

### Network Security Integration

```python
from omega_oui_lookup import get_oui_lookup
from omega_network_security import SecurityManager

lookup = get_oui_lookup()
security = SecurityManager()

# Check network connections
connections = security.get_active_connections()
for conn in connections:
    if conn.mac_address:
        vendor_info = lookup.lookup(conn.mac_address)
        
        # Alert on suspicious vendors in OT network
        if "VMware" in vendor_info.vendor_name:
            print(f"[ALERT] Virtual machine detected: {conn.mac_address}")
        
        # Check for expected vendors
        expected_vendors = ["Siemens", "Rockwell", "Schneider"]
        if not any(v in vendor_info.vendor_name for v in expected_vendors):
            print(f"[WARNING] Unexpected vendor: {vendor_info.vendor_name}")
```

### Asset Inventory

```python
from omega_oui_lookup import OUILookup
import psutil

lookup = OUILookup()

# Get all network interfaces
interfaces = psutil.net_if_addrs()
inventory = {}

for interface_name, addresses in interfaces.items():
    for addr in addresses:
        if addr.family == psutil.AF_LINK:  # MAC address
            mac = addr.address
            vendor_info = lookup.lookup(mac)
            inventory[interface_name] = {
                'mac': mac,
                'vendor': vendor_info.vendor_name,
                'oui': vendor_info.oui
            }

# Print inventory
for iface, info in inventory.items():
    print(f"{iface}: {info['mac']} → {info['vendor']}")
```

### MAC Spoofing Detection

```python
from omega_oui_lookup import OUILookup

lookup = OUILookup()

# Device claims to be Siemens PLC
claimed_device = "Siemens CPU 1515"
device_mac = "00:0A:35:12:34:56"

vendor_info = lookup.lookup(device_mac)

# Check if MAC matches claimed vendor
if "Siemens" not in vendor_info.vendor_name:
    print(f"[ALERT] MAC Spoofing Detected!")
    print(f"  Claimed: {claimed_device}")
    print(f"  MAC OUI: {vendor_info.vendor_name}")
    print(f"  Possible spoofing or misconfiguration")
```

---

## ICS/OT Security Use Cases

### 1. Unknown Device Detection

```python
# Scan network and identify unknown devices
known_devices = {
    "00:1A:2B:3C:4D:5E": "Engineering Workstation",
    "00:50:56:AB:CD:EF": "VMware VM"
}

detected_macs = ["00:1A:2B:3C:4D:5E", "AA:BB:CC:DD:EE:FF"]

for mac in detected_macs:
    if mac not in known_devices:
        vendor_info = lookup.lookup(mac)
        print(f"[UNKNOWN DEVICE] {mac}")
        print(f"  Vendor: {vendor_info.vendor_name}")
        print(f"  OUI: {vendor_info.oui}")
```

### 2. Virtual Machine Detection

```python
# Detect virtual machines in OT network (potential Triton attack vector)
lookup = OUILookup()

network_devices = ["00:1A:2B:3C:4D:5E", "00:50:56:AB:CD:EF"]

for mac in network_devices:
    vendor_info = lookup.lookup(mac)
    if "VMware" in vendor_info.vendor_name or "VirtualBox" in vendor_info.vendor_name:
        print(f"[ALERT] Virtual machine in OT network: {mac}")
        print(f"  Vendor: {vendor_info.vendor_name}")
        print(f"  Risk: Engineering workstations often compromised via VMs")
```

### 3. Vendor Baseline

```python
# Establish vendor baseline for OT network
lookup = OUILookup()

baseline_vendors = {
    "Siemens": ["00:0A:35", "00:1C:06"],
    "Rockwell": ["00:00:BC", "00:1D:9C"],
    "Schneider": ["00:80:F4", "00:30:DE"]
}

# Check if detected MACs match expected vendors
detected_mac = "00:0A:35:12:34:56"
vendor_info = lookup.lookup(detected_mac)

if "Siemens" in vendor_info.vendor_name:
    print(f"[OK] Siemens device detected: {detected_mac}")
else:
    print(f"[WARNING] Unexpected vendor: {vendor_info.vendor_name}")
```

---

## API Reference

### `OUILookup` Class

#### Methods

- `lookup(mac: str, use_online: bool = True) -> VendorInfo`
  - Lookup vendor for a single MAC address
  
- `lookup_batch(mac_addresses: List[str], use_online: bool = True) -> List[VendorInfo]`
  - Lookup multiple MAC addresses
  
- `download_oui_database(force: bool = False) -> bool`
  - Download latest OUI database from IEEE

### `VendorInfo` Dataclass

- `oui: str` - OUI (first 6 hex digits)
- `vendor_name: str` - Vendor/manufacturer name
- `assignment_date: Optional[str]` - Assignment date (if available)
- `company_address: Optional[str]` - Company address (if available)
- `is_private: bool` - Whether OUI is private
- `is_locally_administered: bool` - Whether MAC is locally administered
- `lookup_method: str` - How lookup was performed ('local', 'api_macvendors', etc.)

---

## Performance Notes

- **Local Database**: ~50,000+ OUIs, instant lookups
- **Online API**: ~100-200ms per lookup (rate-limited)
- **Cache**: First load creates JSON cache for 10x faster subsequent loads

---

## Troubleshooting

### "CSV not found" Warning

**Solution:** Download the OUI database:
```python
from omega_oui_lookup import OUILookup
lookup = OUILookup()
lookup.download_oui_database()
```

### Online API Timeouts

**Solution:** Use offline database for air-gapped environments or when APIs are unavailable.

### "Unknown / Unassigned OUI"

**Possible Reasons:**
- OUI not yet assigned by IEEE
- Private OUI block
- Invalid MAC address format
- Database needs updating

**Solution:** Update OUI database monthly for latest assignments.

---

## References

- **IEEE OUI Registry**: https://standards-oui.ieee.org/oui/oui.csv
- **macvendors.com API**: https://api.macvendors.com
- **maclookup.app API**: https://api.maclookup.app
- **IEEE Registration Authority**: https://standards.ieee.org/products-programs/regauth/oui/

---

**Status:** ✅ Ready for production use in ICS/OT security environments
