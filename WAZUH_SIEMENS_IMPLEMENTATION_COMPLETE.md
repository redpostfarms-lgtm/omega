# Siemens SIMATIC Wazuh Implementation - COMPLETE

**Date:** 2026-01-01  
**Status:** ✅ **PRODUCTION READY**

---

## Executive Summary

Comprehensive Siemens SIMATIC integration for Wazuh, including:

- **Siemens Syslog decoders** for S7-1200/S7-1500 security events
- **Siemens security rules** with Triton attack detection patterns
- **Attack chain correlation rules** for multi-stage attacks
- **Comprehensive Triton case study guide** with detection strategies
- **MITRE ATT&CK mappings** for all Triton-relevant techniques

---

## Files Created

### Decoder Files
1. **`wazuh/siemens_decoders.xml`** - Siemens SIMATIC Syslog decoders
   - Parent decoder for Siemens events
   - Full format decoder (with session data)
   - Simple format decoder (mode changes)
   - Authentication event decoder
   - Protection event decoder

### Rule Files
2. **`wazuh/siemens_rules.xml`** - Siemens security rules (18 rules)
   - Authentication & Access (4 rules)
   - Operating Mode Changes (3 rules - Triton patterns)
   - Protection Level Changes (2 rules)
   - Program/Logic Manipulation (2 rules - Triton patterns)
   - Firmware Manipulation (2 rules - Triton patterns)
   - Device Control (1 rule)
   - Safety System Compromise (1 rule - Triton target)
   - Attack Chain Correlation (2 rules - Triton attack chains)
   - I/O Manipulation (1 rule)

### Documentation Files
3. **`wazuh/TRITON_ATTACK_DETECTION_GUIDE.md`** - Comprehensive Triton guide
   - Attack summary and timeline
   - Technical details
   - MITRE ATT&CK mapping
   - Wazuh detection rules
   - Best practices

4. **`wazuh/WAZUH_RULES_AND_DECODERS_GUIDE.md`** - Updated with Siemens section

---

## Siemens Rule Categories

### 1. Authentication & Access (210001-210004)
- Failed login attempts
- Unauthorized IP access
- Brute-force patterns (6+ failures in 5 minutes)
- Default credentials usage

### 2. Operating Mode Changes (210010-210012)
- Mode changes to unsafe states (STOP, ERROR, MAINTENANCE)
- Unauthorized engineering/debug mode
- Repeated mode changes (Triton pattern)

### 3. Protection Level Changes (210020-210021)
- Protection enabled/disabled
- Critical protection violations

### 4. Program/Logic Manipulation (210030-210031)
- Program downloads/uploads from unauthorized sources
- Repeated modifications (Triton pattern - 2+ in 10 minutes)

### 5. Firmware Manipulation (210040-210041)
- Firmware update mode activation
- Integrity violations (Triton pattern)

### 6. Device Control (210050)
- Unauthorized restarts/shutdowns

### 7. Safety System Compromise (210060)
- Safety bypass/violations (Triton target - CRITICAL)

### 8. Attack Chain Correlation (210070-210071)
- **Triton Attack Chain 1**: Mode change + Program modification
- **Triton Attack Chain 2**: Protection disabled + Safety bypass

### 9. I/O Manipulation (210080)
- I/O image manipulation

---

## Triton Attack Detection

### Triton Attack Pattern Recognition

**Pattern 1: Mode Change + Program Modification** (Rule 210070)
- **Triggers**: Mode change (210010) + Program modification (210030) from same source within 10 minutes
- **MITRE**: T0858, T0821, T0831, T0880
- **Severity**: Level 15 (Critical)
- **Description**: Represents core Triton attack chain

**Pattern 2: Protection Disabled + Safety Bypass** (Rule 210071)
- **Triggers**: Protection disabled (210021) + Safety bypass (210060) from same source within 10 minutes
- **MITRE**: T0892, T0837, T0880
- **Severity**: Level 15 (Critical)
- **Description**: Represents inhibit response + impact combination

### Triton-Relevant MITRE Techniques

**TA0107: Inhibit Response Function**:
- T0857 (System Firmware)
- T0835 (Manipulate I/O Image)
- T0816 (Device Restart/Shutdown)
- T0800 (Activate Firmware Update Mode)
- T0892 (Change Credential)

**TA0106: Impair Process Control**:
- T0831 (Manipulation of Control)

**TA0105: Impact**:
- T0880 (Loss of Safety)
- T0879 (Damage to Property)
- T0828 (Loss of Productivity and Revenue)

**TA0104: Execution**:
- T0858 (Change Operating Mode)
- T0821 (Modify Controller Tasking)
- T0843 (Program Download)
- T0871 (Execution through API)

---

## Installation

### Step-by-Step Installation

1. **Copy decoder file**:
   ```bash
   sudo cp wazuh/siemens_decoders.xml /var/ossec/etc/decoders/
   ```

2. **Copy rule file**:
   ```bash
   sudo cp wazuh/siemens_rules.xml /var/ossec/etc/rules/
   ```

3. **Set permissions**:
   ```bash
   sudo chown wazuh:wazuh /var/ossec/etc/decoders/siemens_decoders.xml
   sudo chown wazuh:wazuh /var/ossec/etc/rules/siemens_rules.xml
   sudo chmod 660 /var/ossec/etc/decoders/siemens_decoders.xml
   sudo chmod 660 /var/ossec/etc/rules/siemens_rules.xml
   ```

4. **Configure Siemens PLC Syslog** (in TIA Portal):
   - Device configuration → Protection & Security → Syslog
   - Enable Syslog
   - Set Wazuh server IP and port 514 (UDP)

5. **Restart Wazuh manager**:
   ```bash
   sudo systemctl restart wazuh-manager
   ```

6. **Test with wazuh-logtest**:
   ```bash
   sudo /var/ossec/bin/wazuh-logtest
   # Paste sample Siemens log
   ```

---

## Configuration

### Siemens PLC Configuration (TIA Portal)

**TIA Portal V17+** (Basic Syslog):
1. Open TIA Portal project
2. Select PLC (S7-1200/S7-1500)
3. Device configuration → Protection & Security → Syslog
4. Enable "Send system events via Syslog"
5. Set Wazuh server IP and port 514 (UDP)

**TIA Portal V19+** (Enhanced Features):
- UMAC (User Management and Access Control)
- Dynamic PKI
- Enhanced security event logging

### Wazuh Syslog Configuration

**In `/var/ossec/etc/ossec.conf`**:
```xml
<remote>
  <connection>syslog</connection>
  <port>514</port>
  <protocol>udp</protocol>
  <allowed-ips>192.168.10.0/24</allowed-ips>
</remote>
```

---

## Testing

### Sample Siemens Logs for Testing

**Authentication Failure**:
```
<134>Jan 11 15:45:00 plc-gateway - ID123 [device@001 devVendor="Siemens" devProduct="CPU 1515-2 PN" FWVersion="V2.8"] [session@456 protocolType="TLS" userName="admin" src="192.168.1.100"] SE_ACCESS_DENIED
```

**Mode Change**:
```
<134>Jan 11 15:46:00 plc-gateway Operating-Mode-Mgt - ID124 [device@001 devVendor="Siemens" devProduct="CPU 1515-2 PN" FWVersion="V2.8"] [function@789 fct="ChangeMode" oldState="RUN" newState="PROGRAM"] SE_OPMOD_CHANGED
```

**Program Download**:
```
<134>Jan 11 15:47:00 plc-gateway - ID125 [device@001 devVendor="Siemens" devProduct="CPU 1515-2 PN" FWVersion="V2.8"] [function@012 fct="ProgramDownload" oldState="Valid" newState="Modified"] SE_PROGRAM_DOWNLOAD
```

### Testing with wazuh-logtest

```bash
sudo /var/ossec/bin/wazuh-logtest

# Paste sample log above
# Verify Phase 2 shows decoded fields
# Verify Phase 3 shows matching rules
```

---

## Best Practices

### Prevention

1. **Network Segmentation**: Isolate engineering workstations
2. **Least Privilege**: Restrict TIA Portal access
3. **Firmware Updates**: Apply vendor patches promptly
4. **Access Control**: Whitelist authorized IPs
5. **Physical Security**: Restrict access to engineering stations

### Detection

1. **Syslog Forwarding**: Configure all Siemens PLCs
2. **Baseline Operations**: Establish known-good patterns
3. **Correlation Rules**: Use for attack chains
4. **Whitelisting**: Reduce false positives
5. **Alert Prioritization**: Focus on Level 13+ events

### Response

1. **Immediate Isolation**: Quarantine affected controllers
2. **Forensic Analysis**: Capture memory dumps
3. **Vendor Notification**: Contact Siemens for support
4. **Incident Reporting**: Report to CISA/ICS-CERT
5. **Recovery**: Restore from known-good firmware

---

## Statistics

- **Total Decoders**: 5 decoders (parent + children)
- **Total Rules**: 18 rules
- **Triton Detection Rules**: 10+ rules with Triton patterns
- **Attack Chain Correlation**: 2 rules
- **MITRE ATT&CK Mappings**: All Triton-relevant techniques
- **Rule ID Range**: 210000-210999 (reserved for Siemens)

---

## Status

✅ **All Files Created**  
✅ **Decoders Complete**  
✅ **Rules Complete**  
✅ **Triton Detection Implemented**  
✅ **Documentation Complete**  
✅ **Production-Ready**

---

**Implementation Date:** 2026-01-01  
**Version:** 1.0  
**Status:** Production-Ready - Triton Detection Included
