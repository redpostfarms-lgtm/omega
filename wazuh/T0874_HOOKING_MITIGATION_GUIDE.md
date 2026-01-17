# T0874: Hooking - Mitigation and Detection Guide
## Comprehensive Guide for ICS/OT Environments

**Date:** 2026-01-01  
**Version:** 1.0  
**MITRE ATT&CK for ICS:** T0874 (Execution - TA0104)

---

## Overview

T0874: Hooking is a technique where adversaries intercept and redirect API calls (e.g., via Import Address Table modifications) to execute code, escalate privileges, or evade detection in industrial control systems. This guide provides comprehensive mitigation strategies, detection methods, and vendor-specific guidance for ICS/OT environments.

---

## Table of Contents

1. [Understanding Hooking in ICS](#understanding-hooking-in-ics)
2. [MITRE Mitigations](#mitre-mitigations)
3. [Detection Strategies](#detection-strategies)
4. [Siemens-Specific Mitigations](#siemens-specific-mitigations)
5. [Wazuh Implementation](#wazuh-implementation)
6. [Best Practices](#best-practices)
7. [Real-World Examples](#real-world-examples)

---

## Understanding Hooking in ICS

### What is Hooking?

Hooking in ICS involves intercepting system calls or API functions to alter behavior. Common methods include:

- **IAT (Import Address Table) Hooking**: Modifying DLL import tables to redirect function calls
- **Inline Hooking**: Injecting jump instructions into function prologues
- **API Hooking**: Intercepting Windows API calls (e.g., SetWindowsHookEx)
- **Kernel-Level Hooking**: Modifying kernel callbacks or system service tables

### Why is Hooking Dangerous in ICS?

1. **Stealth**: Can manipulate critical functions without obvious disruption
2. **Persistence**: Hooks survive reboots if embedded in firmware/programs
3. **Privilege Escalation**: Can bypass access controls
4. **Evasion**: Can hide malicious activity from monitoring tools
5. **Process Manipulation**: Can alter safety controller diagnostic data

### Challenges in ICS Environments

- **Resource Constraints**: Embedded devices (PLCs, RTUs) lack kernel-level monitoring
- **Real-Time Requirements**: Intrusive agents can disrupt operations
- **Legacy Systems**: Older devices lack security features
- **Air-Gapped Networks**: Limited visibility during normal operation
- **Physical Access**: Memory card tampering can introduce hooks

---

## MITRE Mitigations

### M0947: Audit

**Description**: Perform regular audits or scans of systems, permissions, software configurations, and device integrity to identify weaknesses.

**ICS-Specific Implementation**:

1. **Firmware Integrity Checks**:
   - Compare cryptographic hashes against known-good baselines
   - Use vendor tools (e.g., Siemens SIMATIC, Rockwell FactoryTalk)
   - Schedule non-intrusive scans during planned downtime
   - Alert on hash mismatches (indicates potential IAT hooking)

2. **File Integrity Monitoring (FIM)**:
   - Monitor critical DLLs, executables, and system files
   - Use Wazuh FIM for engineering stations/HMIs
   - Alert on unexpected changes to API tables or kernel modules

3. **Process Integrity Verification**:
   - Compare in-memory code of running processes to static binaries
   - Use memory forensics tools (Volatility, Rekall) for offline analysis
   - Check for unauthorized jumps, redirects, or inline hooks

**Wazuh Integration**:
```xml
<!-- FIM-based integrity check rule (already in ics_ta0104_rules.xml) -->
<rule id="200914" level="14">
  <if_sid>550</if_sid>
  <field name="file">\.dll$|\.exe$|\.sys$</field>
  <field name="integrity_status">altered|mismatch|hash_failed</field>
  <description>Critical DLL/EXE integrity violation - possible IAT hooking (T0874)</description>
  <mitre><id>T0874</id></mitre>
</rule>
```text

### M0944: Restrict Library Loading

**Description**: Prevent loading of untrusted, remote, or unknown libraries (e.g., DLLs).

**ICS-Specific Implementation**:

1. **Application Allowlisting**:
   - Use Microsoft AppLocker or Windows Defender Application Control
   - Restrict executable and library loading on Windows-based HMIs
   - Enforce code signing requirements for all OT software

2. **Firmware Signing**:
   - Require signed firmware on embedded devices
   - Use secure boot mechanisms (e.g., ATECC CryptoAuthentication chip)
   - Verify signatures during boot/update

3. **Dynamic Library Restrictions**:
   - Block loading of DLLs from network shares
   - Restrict loading from temporary directories
   - Monitor for unusual library loads (Sysmon Event ID 7)

**Wazuh Integration**:
```xml
<!-- Module load anomaly detection (already in ics_ta0104_rules.xml) -->
<rule id="200915" level="11">
  <if_sid>200910</if_sid>
  <field name="event_id">7</field>
  <field name="image_loaded">suspicious|unknown|unsigned</field>
  <description>Suspicious module load in ICS process - possible hooking payload (T0874)</description>
  <mitre><id>T0874</id></mitre>
</rule>
```text

---

## Detection Strategies

### 1. API Call Monitoring

**Windows API Hooks**:
- Monitor for `SetWindowsHookEx`, `SetWinEventHook`, `SetWindowsHook` calls
- Use Sysmon (Event ID 13) for registry changes related to hooks
- Alert on unexpected hook installations from non-engineering processes

**Wazuh Rule** (already implemented):
```xml
<rule id="200911" level="12">
  <if_sid>200910</if_sid>
  <field name="api_call">SetWindowsHookEx|SetWinEventHook|SetWindowsHook</field>
  <field name="process_name">!trusted_engineering|!vendor_process</field>
  <description>Suspicious API call for hook installation - possible Hooking (T0874)</description>
  <mitre><id>T0874</id></mitre>
</rule>
```text

### 2. Memory Forensics and Integrity Checks

**Tools**:
- **Volatility**: Memory analysis framework for Windows/Linux
- **Rekall**: Alternative memory forensics framework
- **PLCTool**: Open-source tool for PLC memory verification

**What to Look For**:
- Inline hooks (e.g., `jmp` instructions in API prologues)
- IAT/EAT (Export Address Table) tampering
- Unauthorized memory modifications

**Process**:
1. Capture memory dumps during maintenance windows
2. Compare runtime images to known-good baselines
3. Check for redirects in import tables
4. Alert on mismatches

### 3. Behavioral Anomaly Monitoring

**Indicators**:
- Unexpected API responses in ICS protocols
- Altered diagnostic data (e.g., modified responses in Modbus/DNP3)
- Unusual process/module loads

**Implementation**:
- Use ML-based anomaly detection (SECML, Nozomi, Dragos)
- Monitor protocol traffic for unexpected redirections
- Correlate with other execution events

**Wazuh Correlation Rule**:
```xml
<rule id="200913" level="14" frequency="5" timeframe="300">
  <if_matched_sid>200910</if_matched_sid>
  <field name="api_response">redirected|unexpected|altered</field>
  <same_process/>
  <description>Multiple anomalous API redirects - possible Hooking (T0874)</description>
  <mitre><id>T0874</id></mitre>
</rule>
```text

### 4. Endpoint Detection and Response (EDR) in OT

**Lightweight OT-EDR Tools** (as of 2026):
- **Armis**: Passive behavioral analysis
- **Claroty xDome**: Kernel callback monitoring
- **Dragos Platform**: OT-specific detection
- **Nozomi Networks**: Behavioral anomaly detection

**Capabilities**:
- Monitor kernel callbacks and API interceptions
- Alert on hooking patterns without agents on embedded devices
- Provide passive network analysis

---

## Siemens-Specific Mitigations

### Core Siemens Security Architecture (2026)

Siemens' security for SIMATIC PLCs (S7-1200, S7-1500, S7-300/400) relies on layered protections:

#### 1. Firmware Integrity & Secure Boot

**Modern S7-1500/S7-1200 PLCs**:
- **Secure Boot**: Cryptographic verification during boot
- **Root of Trust (RoT)**: Hardware-based secure elements (ATECC CryptoAuthentication chip)
- **Firmware Signing**: PKI-based verification

**Impact**: Prevents loading of hooked or tampered firmware. Any modification fails verification → device refuses to boot or enters fail-safe mode.

**Recommendation**: Keep firmware updated (V4.5+ for S7-1200/1500 includes improved PKI and dynamic keys post-2022 disclosures).

#### 2. Know-How Protection & Block-Level Security

**TIA Portal Features**:
- **Know-How Protection**: Password-based obfuscation for OBs/FCs/FBs/DBs
- **Copy Protection**: Bind blocks to specific CPU/memory card serial numbers
- **Access Levels**: Full/read-only/HMI with passwords or UMAC (User Management and Access Control in V19+)

**Impact**: Prevents reading/modifying blocks where hooks could be inserted. Unauthorized engineering access (required for hooking) is blocked.

#### 3. Secure Communication & Protocol Protections

**S7CommPlus Protocol** (V17+):
- **TLS-Secured Communication**: Encrypted connections
- **Secure PG/PC Interface**: Encrypted engineering sessions

**Impact**: Prevents network-based injection of hooked code or interception of engineering sessions needed for payload delivery.

#### 4. Protection Levels & Configuration Integrity

**Protection Levels**:
- **Level 3**: Complete read/write protection
- **Confidential PLC Configuration Data Encryption**: Encrypts configuration data

**Impact**: Blocks unauthorized program downloads/uploads (T0843) or tasking modifications (T0821) — common precursors to hooking.

### Defense-in-Depth & Network Controls

1. **Network Segmentation** (IEC 62443 zones/conduits):
   - Isolate PLCs from IT networks
   - Use DMZs for engineering stations

2. **Access Restrictions**:
   - Limit engineering access to trusted IPs/VPNs
   - Use SINEC Secure Connect for Zero Trust networking

3. **Service Disabling**:
   - Disable unused services (e.g., web server on port 80/443)
   - Close unnecessary ports

### Practical Implementation Steps (2026 Best Practices)

1. **Update Firmware & TIA Portal**:
   - Use TIA Portal V19+ for latest PKI/TLS/UMAC
   - Update PLC firmware to V4.5+ (post-2022 security improvements)

2. **Enable All Protections in TIA Portal**:
   - Know-how protection + copy protection
   - Full access passwords + encrypted config
   - UMAC for user management (V19+)

3. **Verify Integrity**:
   - Use TIA Portal consistency checks
   - Offline hash verification (vendor tools)
   - Wazuh FIM on engineering stations

4. **Monitor Anomalies**:
   - Use Wazuh FIM + network monitoring
   - SINEC Secure Connect for Zero Trust
   - Integrate with SIEM (Wazuh dashboard)

5. **Follow Siemens Guidelines**:
   - See Siemens Industrial Security page
   - Operational guidelines for Defense-in-Depth
   - CVE advisories and patch management

### Limitations & Realistic Expectations

- **No Runtime Hooking Detection**: Embedded PLCs lack kernel-level monitoring
- **Detection Relies on Integrity Failures**: Boot failures, hash mismatches
- **Physical Access Threat**: Memory card tampering requires physical security
- **Legacy Systems**: Older S7-300/400 have limited protections (focus on network isolation)

---

## Wazuh Implementation

### Rules Included

All T0874 (Hooking) detection rules are included in `wazuh/ics_ta0104_rules.xml`:

1. **200911**: API Call Monitoring (SetWindowsHookEx)
2. **200912**: Integrity Violation (Memory vs. Binary Mismatch)
3. **200913**: Correlation (Repeated API Redirects)
4. **200914**: FIM-based (DLL/EXE Integrity Violation)
5. **200915**: Module Load Anomaly (Sysmon Event ID 7)

### Configuration

1. **Install Rules**:
   ```bash
   sudo cp wazuh/ics_ta0104_rules.xml /var/ossec/etc/rules/
   sudo chown wazuh:wazuh /var/ossec/etc/rules/ics_ta0104_rules.xml
   sudo chmod 660 /var/ossec/etc/rules/ics_ta0104_rules.xml
   sudo systemctl restart wazuh-manager
   ```

2. **Enable FIM** (for Rule 200914):
   ```xml
   <!-- In /var/ossec/etc/ossec.conf -->
   <syscheck>
     <directories check_all="yes">/windows/system32,/program files</directories>
   </syscheck>
   ```

3. **Configure Sysmon** (for Rule 200915):
   - Deploy Sysmon on Windows-based HMIs/engineering stations
   - Forward Event ID 7 (Image loaded) logs to Wazuh

### Testing

```bash
# Test with wazuh-logtest
sudo /var/ossec/bin/wazuh-logtest

# Sample log for API hook detection:
# Event: SetWindowsHookEx called by suspicious_process.exe
```text

---

## Best Practices

### General ICS/OT Best Practices

1. **Network Segmentation**: Isolate engineering workstations from production OT
2. **Least Privilege**: Restrict user privileges on HMIs/engineering stations
3. **Patch Management**: Apply vendor patches quickly (after field testing)
4. **Firmware Integrity**: Use secure boot and signed firmware
5. **Physical Security**: Restrict access to USB/serial ports on controllers
6. **Zero Trust**: Verify all code execution via allowlisting

### Hooking-Specific Best Practices

1. **Integrity Baseline**: Establish known-good hashes for all critical files
2. **Regular Audits**: Schedule integrity checks during maintenance windows
3. **Memory Forensics**: Perform periodic memory dumps for offline analysis
4. **Behavioral Monitoring**: Use anomaly detection for unexpected API redirects
5. **Whitelisting**: Block untrusted libraries and executables
6. **Correlation**: Chain hooking detections with other execution events

---

## Real-World Examples

### Triton (2017, S1009)

**Attack**: Adversaries hooked the "get main processor diagnostic data" TriStation command by changing its function pointer.

**Detection**: Initially missed (no runtime integrity checks). Post-incident recommendation: Monitor for anomalous pointer changes via kernel-level logging or firmware audits.

**Lesson**: Implement integrity checks and behavioral monitoring for diagnostic commands.

### Stuxnet (2010, S0603)

**Attack**: Hooked APIs in DLLs to intercept project file openings.

**Detection**: Memory forensics revealed IAT modifications. Tools like Volatility identified jumps in Siemens Step7 processes.

**Lesson**: Use memory forensics for post-incident analysis; implement FIM for DLL changes.

### General APTs (Sandworm, Xenotime)

**Attack**: Use hooking for evasion in power/utility attacks.

**Detection**: Endpoint logs from Windows OT components; behavioral baselines.

**Lesson**: Integrate endpoint monitoring with SIEM; use correlation for detection.

---

## Additional Resources

- **MITRE ATT&CK**: https://attack.mitre.org/techniques/ics/T0874/
- **Siemens Industrial Security**: https://www.siemens.com/industrial-security
- **CISA ICS-CERT**: https://www.cisa.gov/ics-cert
- **IEC 62443**: Industrial network and system security standards
- **NIST SP 800-82r2**: Guide to Industrial Control Systems Security

---

**Status:** Production-Ready  
**Last Updated:** 2026-01-01  
**Version:** 1.0
