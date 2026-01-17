# Wazuh Rules and Decoders Implementation Guide
## Comprehensive Guide for Gatekeeper Integration

**Date:** 2026-01-01  
**Status:** Production-Ready  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [File Structure](#file-structure)
4. [Gatekeeper Decoders](#gatekeeper-decoders)
5. [Gatekeeper Rules](#gatekeeper-rules)
6. [ICS Protocol Decoders](#ics-protocol-decoders)
7. [ICS Rules (TA0107 - Inhibit Response Function)](#ics-rules-ta0107)
8. [ICS Rules (TA0105 - Impact)](#ics-rules-ta0105)
9. [Modbus Rules](#modbus-rules)
10. [Testing](#testing)
11. [MITRE ATT&CK Mappings](#mitre-attck-mappings)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Overview

This implementation provides comprehensive Wazuh decoders and rules for:

- **Gatekeeper Security System**: Custom decoders and rules for threat detection, ROE violations, and counterstrikes
- **ICS Protocols**: Decoders for Modbus, DNP3, IEC 104, and OPC UA
- **Siemens SIMATIC**: Decoders and rules for S7-1200/S7-1500 Syslog events, including Triton attack detection
- **MITRE ATT&CK for ICS**: Rules mapped to TA0104 (Execution), TA0105 (Impact), and TA0107 (Inhibit Response Function)
- **Modbus Security**: Comprehensive rules for detecting malicious Modbus activity

All rules include MITRE ATT&CK mappings for enterprise and ICS contexts.

---

## Installation

### Prerequisites

- Wazuh server installed and running
- Root or sudo access to Wazuh manager
- Access to `/var/ossec/etc/decoders/` and `/var/ossec/etc/rules/` directories

### Step-by-Step Installation

1. **Copy decoder files** to Wazuh manager:
   ```bash
   sudo cp wazuh/gatekeeper_decoders.xml /var/ossec/etc/decoders/
   sudo cp wazuh/ics_protocols_decoders.xml /var/ossec/etc/decoders/
   ```

2. **Copy rule files** to Wazuh manager:
   ```bash
   sudo cp wazuh/gatekeeper_rules.xml /var/ossec/etc/rules/
   sudo cp wazuh/modbus_rules.xml /var/ossec/etc/rules/
   sudo cp wazuh/ics_ta0107_rules.xml /var/ossec/etc/rules/
   sudo cp wazuh/ics_ta0105_rules.xml /var/ossec/etc/rules/
   ```

3. **Set proper ownership and permissions**:
   ```bash
   sudo chown wazuh:wazuh /var/ossec/etc/decoders/gatekeeper_decoders.xml
   sudo chown wazuh:wazuh /var/ossec/etc/decoders/ics_protocols_decoders.xml
   sudo chown wazuh:wazuh /var/ossec/etc/rules/gatekeeper_rules.xml
   sudo chown wazuh:wazuh /var/ossec/etc/rules/modbus_rules.xml
   sudo chown wazuh:wazuh /var/ossec/etc/rules/ics_ta0107_rules.xml
   sudo chown wazuh:wazuh /var/ossec/etc/rules/ics_ta0105_rules.xml
   
   sudo chmod 660 /var/ossec/etc/decoders/*.xml
   sudo chmod 660 /var/ossec/etc/rules/*.xml
   ```

4. **Restart Wazuh manager**:
   ```bash
   sudo systemctl restart wazuh-manager
   ```

5. **Verify installation**:
   ```bash
   sudo systemctl status wazuh-manager
   sudo tail -f /var/ossec/logs/ossec.log
   ```

---

## File Structure

```text
wazuh/
├── gatekeeper_decoders.xml      # Gatekeeper-specific decoders
├── gatekeeper_rules.xml         # Gatekeeper-specific rules
├── ics_protocols_decoders.xml   # ICS protocol decoders (Modbus, DNP3, IEC 104, OPC UA)
├── modbus_rules.xml             # Modbus-specific security rules
├── ics_ta0107_rules.xml         # TA0107 (Inhibit Response Function) rules
├── ics_ta0105_rules.xml         # TA0105 (Impact) rules
└── WAZUH_RULES_AND_DECODERS_GUIDE.md  # This guide
```text

**Rule ID Ranges:**
- `100000-100999`: Gatekeeper-specific rules
- `200000-200999`: Modbus/ICS protocol rules
- `200700-200799`: TA0107 (Inhibit Response Function) rules
- `200800-200899`: TA0105 (Impact) rules

---

## Gatekeeper Decoders

### Supported Log Formats

1. **JSON Format (Recommended)**
   - Uses built-in `JSON_Decoder` plugin
   - All JSON keys become dynamic fields
   - Example: `{"threat_level": "high", "source": "192.168.1.100", "details": "..."}`

2. **Anomaly Detection Format**
   - Format: `Gatekeeper: ANOMALY DETECTED - type=network_spike src=10.10.1.100 count=150 threshold=100 time=2026-01-11T16:00:00Z`
   - Extracts: `anomaly_type`, `srcip`, `anomaly_count`, `threshold`, `anomaly_time`

3. **Threat Detection Format**
   - Format: `Gatekeeper: THREAT DETECTED - level=high source=192.168.10.20 desc=... category=...`
   - Extracts: `threat_level`, `srcip`, `threat_desc`, `threat_category`

4. **ROE Violation Format**
   - Format: `Gatekeeper: ROE VIOLATION - violation=unauthorized_execution src=10.0.0.5 time=... action=...`
   - Extracts: `roe_violation`, `srcip`, `roe_time`, `roe_action`

5. **Counterstrike Format**
   - Format: `Gatekeeper: COUNTERSTRIKE - target=192.168.1.50 port=443 method=quantum_nuke time=...`
   - Extracts: `counterstrike_target`, `counterstrike_port`, `counterstrike_method`, `counterstrike_time`

### Testing Gatekeeper Decoders

```bash
# Test JSON format
echo '2026-01-11 14:30:22 json_event: {"threat_level": "high", "source": "192.168.1.100"}' | /var/ossec/bin/wazuh-logtest

# Test anomaly format
echo 'Gatekeeper: ANOMALY DETECTED - type=network_spike src=10.10.1.100 count=150 threshold=100 time=2026-01-11T16:00:00Z' | /var/ossec/bin/wazuh-logtest
```text

---

## Gatekeeper Rules

### Rule Categories

1. **Anomaly Detection (100200-100299)**
   - Network spike detection
   - Port scan detection
   - Correlation rules for repeated anomalies

2. **Threat Detection (100300-100399)**
   - High/critical threat alerts
   - Correlation rules for targeted attacks

3. **ROE Violations (100400-100499)**
   - Unauthorized execution
   - Unauthorized access
   - Multiple violation correlation

4. **Counterstrike/Response (100500-100599)**
   - Counterstrike activation alerts
   - Quantum payload detection
   - Escalation detection

### Example Gatekeeper Rule

```xml
<rule id="100401" level="14">
  <if_sid>100400</if_sid>
  <field name="roe_violation">unauthorized_execution</field>
  <description>Gatekeeper ROE violation: Unauthorized code execution detected</description>
  <mitre>
    <id>T1059</id>  <!-- Command and Scripting Interpreter -->
    <id>T1204</id>  <!-- User Execution -->
  </mitre>
  <group>gatekeeper,roe,execution,violation,</group>
  <options>alert_by_email</options>
</rule>
```text

---

## Triton/Triconex Decoders and Rules

### Triton Attack Overview

The Triton (TRISIS/HatMan) malware attack (2017) targeted Schneider Electric Triconex Tricon SIS controllers, marking the first publicly known malware designed to disable safety instrumented systems. The attack used:

- **Target**: Triconex Tricon SIS (MP3008 firmware 10.0–10.4)
- **Protocol**: TriStation (UDP port 1502)
- **Method**: Masquerading as `trilog.exe`, using `inject.bin`, `imain.bin` payloads
- **Attribution**: TEMP.Veles / XENOTIME (CNIIHM lab, Russia)
- **MITRE Campaign**: C0030

### Triconex Decoders

**File**: `wazuh/triconex_decoders.xml`

Extracts fields:
- `process_file` (trilog.exe, TriStation processes)
- `src_ip` (source IP addresses)
- `command_type` (program_append, halt, run, etc.)
- `target` (target controller/device)

### Triton Rules

**File**: `wazuh/triton_rules.xml`

**Rule Categories**:
1. **Masquerading & Execution** (211001-211002)
   - Suspicious trilog.exe execution
   - TriStation process with malicious indicators

2. **Program Manipulation** (211010-211011)
   - Program append/download to SIS
   - Repeated modifications (Triton pattern)

3. **Mode Changes** (211020-211021)
   - Halt/run commands
   - Mode change + Program modification (Triton attack chain)

4. **Firmware/System Modification** (211030-211031)
   - Firmware/memory modification
   - Integrity violations

5. **Network/Protocol Anomalies** (211040-211041)
   - TriStation protocol anomalies (UDP 1502)
   - Unauthorized UDP 1502 traffic

6. **Attack Chain Correlation** (211050)
   - Multiple suspicious commands (Triton pattern)

7. **Evasion/Indicator Removal** (211060)
   - Anti-forensics attempts

8. **Safety System Compromise** (211070-211071)
   - Safety bypass/violations
   - Fail-safe trigger (Triton bug indicator)

9. **I/O Manipulation** (211080)
   - I/O image manipulation

### Example Triton Rule

```xml
<rule id="211050" level="15" frequency="3" timeframe="600">
  <if_matched_sid>211010,211020,211030</if_matched_sid>
  <same_srcip/>
  <description>Multiple suspicious commands to Triconex SIS in short time - CRITICAL Triton-like attack pattern</description>
  <mitre>
    <id>T0831</id>  <!-- Manipulation of Control -->
    <id>T0857</id>  <!-- System Firmware -->
    <id>T0843</id>  <!-- Program Download -->
    <id>T0858</id>  <!-- Change Operating Mode -->
    <id>T0880</id>  <!-- Loss of Safety -->
  </mitre>
  <group>ics,triton,attack_chain,critical,</group>
  <options>alert_by_email</options>
</rule>
```text

**See Also**: `TRITON_ATTACK_DETECTION_GUIDE.md` for comprehensive Triton case study and detection strategies.

---

## ICS Protocol Decoders

### Modbus

**JSON Format (Recommended):**
```json
{"src_ip": "192.168.10.50", "dst_ip": "192.168.10.100", "unit_id": 1, "function_code": 3, "function_name": "Read Holding Registers", "address": 107, "quantity": 5, "exception": false}
```text

**Syslog Format:**
```text
Jan 11 15:45:00 plc-gateway modbus: src=192.168.1.20 dst=192.168.1.10 unit=1 func=0x03 addr=40001 qty=10 exception=false
```text

### DNP3

**Syslog Format:**
```text
Jan 11 15:45:00 dnp3-gateway DNP3: src=192.168.1.20 dst=192.168.1.10 src_addr=3 dest_addr=1 fc=129 fc_name=Response obj_type=30 obj_var=1 point=45 value=1.0 event=true
```text

### IEC 104

**Format:**
```text
2026-01-11 16:20:00 IEC104: src=192.168.10.5 dst=192.168.10.100 asdu_type=45 cause=3 io_addr=10045 value=1 quality=good
```text

### OPC UA

**JSON Format (Recommended):**
```json
{"timestamp": "2026-01-11T17:00:00Z", "src": "192.168.20.10", "dst": "192.168.20.50", "node_id": "ns=2;s=PressureSensor", "value": 45.2, "status": "Good", "operation": "Read"}
```text

---

## ICS Rules (TA0107)

### Inhibit Response Function Techniques

All 14 techniques from TA0107 are covered:

- **T0878**: Alarm Suppression
- **T0838**: Modify Alarm Settings
- **T0803**: Block Command Message
- **T0804**: Block Reporting Message
- **T0805**: Block Serial COM
- **T0892**: Change Credential
- **T0809**: Data Destruction
- **T0814**: Denial of Service
- **T0816**: Device Restart/Shutdown
- **T0835**: Manipulate I/O Image
- **T0800**: Activate Firmware Update Mode
- **T0851**: Rootkit
- **T0881**: Service Stop
- **T0857**: System Firmware

### Example TA0107 Rule

```xml
<rule id="200701" level="12" frequency="4" timeframe="300">
  <if_sid>200100</if_sid>
  <field name="alarm_status">suppressed|muted|disabled|acknowledged_false</field>
  <same_dstip/>
  <description>Multiple suppressed alarms on same ICS device - possible Alarm Suppression (T0878)</description>
  <mitre>
    <id>T0878</id>
  </mitre>
  <group>ics,inhibit_response,alarm_suppression,</group>
  <options>alert_by_email</options>
</rule>
```text

---

## ICS Rules (TA0104)

### Execution Techniques

All 10 techniques from TA0104 are covered:

- **T0821**: Modify Controller Tasking
- **T0843**: Program Download
- **T0858**: Change Operating Mode
- **T0871**: Execution through API
- **T0834**: Native API
- **T0807**: Command-Line Interface
- **T0863**: User Execution
- **T0823**: Graphical User Interface
- **T0895**: Autorun Image
- **T0853**: Scripting
- **T0874**: Hooking (expanded detection)

**Expanded T0874 (Hooking) Detection**:
- API Call Monitoring (SetWindowsHookEx)
- Integrity Violation (Memory vs. Binary Mismatch)
- Correlation (Repeated API Redirects)
- FIM-based (DLL/EXE Integrity Violation)
- Module Load Anomaly (Sysmon Event ID 7)

### Example TA0104 Rule

```xml
<rule id="200911" level="12">
  <if_sid>200910</if_sid>
  <field name="api_call">SetWindowsHookEx|SetWinEventHook|SetWindowsHook</field>
  <field name="process_name">!trusted_engineering|!vendor_process</field>
  <description>Suspicious API call for hook installation - possible Hooking (T0874)</description>
  <mitre>
    <id>T0874</id>
  </mitre>
  <group>ics,execution,hooking,api_monitor,</group>
</rule>
```text

**See Also**: `T0874_HOOKING_MITIGATION_GUIDE.md` for comprehensive mitigation and detection strategies.

---

## ICS Rules (TA0105)

### Impact Techniques

Selected high-impact techniques from TA0105:

- **T0879**: Damage to Property
- **T0813**: Denial of Control
- **T0815**: Denial of View
- **T0826**: Loss of Availability
- **T0827**: Loss of Control
- **T0828**: Loss of Productivity and Revenue
- **T0837**: Loss of Protection
- **T0880**: Loss of Safety (CRITICAL)
- **T0829**: Loss of View
- **T0831**: Manipulation of Control
- **T0832**: Manipulation of View
- **T0882**: Theft of Operational Information

### Example TA0105 Rule

```xml
<rule id="200808" level="15">
  <if_sid>200100</if_sid>
  <field name="safety_status">disabled|bypassed|overridden</field>
  <field name="device_type">sis|safety|interlock|emergency</field>
  <description>Safety system compromised - possible Loss of Safety (T0880) - CRITICAL</description>
  <mitre>
    <id>T0880</id>
  </mitre>
  <group>ics,impact,loss_of_safety,critical,</group>
  <options>alert_by_email</options>
</rule>
```text

---

## Modbus Rules

### Key Rule Categories

1. **Reconnaissance (200010-200019)**
   - Device identification (FC 43/14)
   - Diagnostics loopback (FC 08/0x0000)

2. **Write Operations (200020-200029)**
   - Single writes (FC 05/06) - Level 12
   - Multiple writes (FC 15/16) - Level 14
   - Unauthorized source detection

3. **Exception & DoS (200030-200039)**
   - Exception floods
   - Denial of service patterns

4. **Critical Diagnostics (200060-200069)**
   - Force Listen Only Mode (FC 08/0x0004) - Level 14
   - Clear Counters (FC 08/0x000A) - Level 11

5. **Correlation (200050-200059)**
   - Repeated writes
   - Multiple diagnostics

### Example Modbus Rule

```xml
<rule id="200021" level="14">
  <if_sid>200000</if_sid>
  <field name="function_code">15|16|0x0F|0x10</field>
  <field name="quantity">^10$|^[1-9][0-9]+$</field>
  <description>Modbus multiple write (FC 15/16) with large quantity - high risk of mass manipulation</description>
  <mitre>
    <id>T0831</id>  <!-- Manipulation of Control -->
    <id>T0805</id>  <!-- Denial of Service -->
  </mitre>
  <group>ics,impair_process_control,critical_write,modbus,</group>
  <options>alert_by_email</options>
</rule>
```text

---

## Testing

### Using wazuh-logtest

1. **Interactive Mode:**
   ```bash
   sudo /var/ossec/bin/wazuh-logtest
   ```

2. **Test Gatekeeper Log:**
   ```
   Gatekeeper: ANOMALY DETECTED - type=network_spike src=10.10.1.100 count=150 threshold=100 time=2026-01-11T16:00:00Z
   ```

3. **Test Modbus Log:**
   ```
   Jan 11 15:45:00 plc-gateway modbus: src=192.168.1.20 dst=192.168.1.10 unit=1 func=0x06 addr=40001 qty=1 exception=false
   ```

### Expected Output

You should see three phases:
1. **Phase 1: Completed pre-decoding** - Basic syslog fields
2. **Phase 2: Completed decoding** - Extracted fields from decoders
3. **Phase 3: Completed filtering (rules)** - Matching rules with MITRE IDs

### Testing Frequency Rules

Paste the same log multiple times quickly (within the timeframe) to test frequency-based correlation rules.

---

## MITRE ATT&CK Mappings

### Enterprise ATT&CK Mappings (Gatekeeper)

- **T1059**: Command and Scripting Interpreter
- **T1204**: User Execution
- **T1078**: Valid Accounts
- **T1499**: Endpoint Denial of Service
- **T1046**: Network Service Scanning
- **T1595**: Active Scanning
- **T1498**: Network Denial of Service

### ICS ATT&CK Mappings

**TA0107 (Inhibit Response Function):**
- T0878, T0838, T0803, T0804, T0805, T0892, T0809, T0814, T0816, T0835, T0800, T0851, T0881, T0857

**TA0105 (Impact):**
- T0879, T0813, T0815, T0826, T0827, T0828, T0837, T0880, T0829, T0831, T0832, T0882

**Modbus-Specific:**
- T0831 (Manipulation of Control)
- T0835 (Manipulate I/O Image)
- T0801 (Monitor Process State)
- T0805 (Denial of Service)
- T0848 (Rogue Master)
- T0858 (Change Operating Mode)
- T0872 (Indicator Removal on Host)

---

## Best Practices

1. **Start with JSON logs** - Easiest to decode and maintain
2. **Test extensively** - Use `wazuh-logtest` for every new decoder/rule
3. **Tune frequency thresholds** - Adjust based on your environment's normal traffic
4. **Whitelist maintenance IPs** - Reduce false positives for authorized operations
5. **Monitor rule performance** - Check for high false positive rates
6. **Use correlation rules** - Combine multiple events for better detection
7. **Document customizations** - Keep notes on any environment-specific changes
8. **Regular updates** - Review and update rules based on new threats

---

## Troubleshooting

### Decoders Not Matching

1. **Check log format** - Verify it matches the decoder's expected format
2. **Test with wazuh-logtest** - See Phase 2 output for decoder matching
3. **Check prematch patterns** - Make sure they're specific enough
4. **Verify regex syntax** - Use PCRE2 format (`type="pcre2"`)

### Rules Not Firing

1. **Check decoder output** - Rules only work on decoded fields
2. **Verify field names** - Must match exactly (case-sensitive)
3. **Check rule order** - Parent rules (level 0) must fire first
4. **Test field values** - Use `wazuh-logtest` to see extracted fields
5. **Check frequency/timeframe** - May need multiple events in time window

### High False Positive Rate

1. **Increase frequency thresholds** - Require more events
2. **Lengthen timeframes** - Spread events over longer periods
3. **Add IP whitelists** - Exclude known-good sources
4. **Raise severity levels** - Only alert on truly suspicious activity
5. **Add more conditions** - Combine multiple fields for specificity

### Performance Issues

1. **Optimize prematch patterns** - Make them specific to reduce false matches
2. **Use hierarchy** - Parent/child decoders are more efficient
3. **Reduce rule complexity** - Simpler regex patterns perform better
4. **Monitor system resources** - Check CPU/memory usage on Wazuh manager

---

## Additional Resources

- **Wazuh Documentation**: https://documentation.wazuh.com/
- **MITRE ATT&CK for ICS**: https://attack.mitre.org/matrices/ics/
- **MITRE ATT&CK for Enterprise**: https://attack.mitre.org/matrices/enterprise/
- **Wazuh API Documentation**: https://documentation.wazuh.com/current/user-manual/api/index.html

---

**Status:** Production-Ready  
**Last Updated:** 2026-01-01  
**Version:** 1.0
