# Triton Attack Detection Guide
## Comprehensive Detection Patterns for Wazuh

**Date:** 2026-01-01  
**Version:** 1.0  
**Reference:** Triton (TRISIS/HatMan) Attack Case Study (2017)

---

## Overview

The Triton malware attack (2017) represents one of the most significant ICS cybersecurity incidents — the first publicly known malware designed to target and disable safety instrumented systems (SIS). This guide provides comprehensive detection patterns for Wazuh to identify Triton-like attacks on Triconex Safety Instrumented Systems (SIS) and Siemens SIMATIC systems.

---

## Table of Contents

1. [Triton Attack Summary](#triton-attack-summary)
2. [Attack Timeline](#attack-timeline)
3. [Technical Details](#technical-details)
4. [MITRE ATT&CK Mapping](#mitre-attack-mapping)
5. [Wazuh Detection Rules](#wazuh-detection-rules)
6. [Siemens-Specific Patterns](#siemens-specific-patterns)
7. [Attack Chain Correlation](#attack-chain-correlation)
8. [Best Practices](#best-practices)

---

## Triton Attack Summary

### Background

**Date Discovered**: December 2017  
**Target**: Petrochemical facility in Saudi Arabia (Petro Rabigh complex)  
**Malware**: Triton (TRISIS, HatMan)  
**Target Systems**: Schneider Electric Triconex Tricon SIS controllers (MP3008 firmware 10.0–10.4)  
**Attribution**: Russian state-sponsored group TEMP.Veles / XENOTIME (CNIIHM lab)

### Key Characteristics

- **First malware targeting safety systems** (last line of defense)
- **Designed to cause physical harm** (explosions, toxic releases)
- **Sophisticated framework** requiring deep Triconex knowledge
- **Fail-safe trigger prevented disaster** (malware bug caused automatic shutdown)
- **No confirmed new deployments** post-2017, but tools persist (2026)

---

## Attack Timeline

### Phase 1: Initial Access (2014–2016)
- **Entry Point**: Corporate IT network (likely phishing or supply chain)
- **Dwell Time**: 2–3 years (dormant reconnaissance)
- **Objective**: Establish foothold for lateral movement

### Phase 2: Lateral Movement (Early 2017)
- **Movement**: IT → OT network
- **Target**: Engineering workstation with TriStation software
- **Objective**: Access to Triconex programming tools

### Phase 3: Deployment (June–August 2017)
- **June 2017**: First accidental trigger (malware bug exposed itself)
- **August 2017**: Second shutdown triggers full investigation
- **Discovery**: FireEye (Mandiant) and Dragos identify sophisticated malware

### Phase 4: Attribution (2018–2022)
- **2018**: FireEye attributes to CNIIHM (Russian government lab)
- **2020**: U.S. Treasury sanctions CNIIHM
- **2022**: DOJ unseals indictment against Evgeny Viktorovich Gladkikh (CNIIHM employee)

### Phase 5: Persistent Threat (2022–2026+)
- **Status**: Group remains active in energy sector reconnaissance
- **Tools**: Framework evolves, no confirmed new deployments
- **Threat Level**: High (capability proven)

---

## Technical Details

### Malware Components

1. **Dropper**: Disguised as legitimate `trilog.exe` (Triconex log analyzer)
2. **Exploit**: Zero-day vulnerability (buffer overflow) for privilege escalation
3. **Payload**: Custom framework for Triconex manipulation

### Core Capabilities

- **Read/Write Programs**: Modify controller logic
- **Halt/Run Programs**: Control execution
- **Query State**: Reconnaissance and validation
- **Memory Manipulation**: In-memory firmware modification
- **Anti-Forensics**: Overwrite malicious code with junk on failure

### Attack Methods

1. **Protocol Reimplementation**: Proprietary TriStation protocol communication
2. **Memory Injection**: In-memory firmware modification (no disk changes)
3. **Function Hooking**: Intercept diagnostic commands (e.g., "get main processor diagnostic data")
4. **Mode Switching**: Activate firmware update mode for manipulation

### Fail-Safe Trigger

**Malware Bug**: Validation failure between redundant processors → controllers entered safe state → plant shutdown → attack discovered

**Key Lesson**: Fail-safe design prevented disaster, but also exposed the attack

---

## MITRE ATT&CK Mapping

### Primary Tactics

**TA0107: Inhibit Response Function** (Primary)
- **T0857**: System Firmware (firmware manipulation)
- **T0835**: Manipulate I/O Image (I/O tampering)
- **T0816**: Device Restart/Shutdown (controller reset)
- **T0800**: Activate Firmware Update Mode (update mode activation)

**TA0106: Impair Process Control**
- **T0831**: Manipulation of Control (program modification)

**TA0105: Impact** (End Goal)
- **T0880**: Loss of Safety (safety system bypass)
- **T0879**: Damage to Property (physical damage potential)
- **T0828**: Loss of Productivity and Revenue (plant shutdown)

### Supporting Techniques

- **T0843**: Program Download (TriStation uploads)
- **T0871**: Execution through API (TriStation protocol)
- **T0849**: Masquerading (disguised as legitimate tool)
- **T0858**: Change Operating Mode (engineering/debug mode)

---

## Wazuh Detection Rules

### Rule Categories

All rules are in `wazuh/siemens_rules.xml` with rule IDs 210000-210999:

1. **Authentication & Access** (210001-210004)
   - Failed login attempts
   - Unauthorized IP access
   - Brute-force patterns
   - Default credentials

2. **Operating Mode Changes** (210010-210012)
   - Mode changes to unsafe states
   - Unauthorized engineering mode
   - Repeated mode changes

3. **Protection Level Changes** (210020-210021)
   - Protection enabled/disabled
   - Critical protection violations

4. **Program/Logic Manipulation** (210030-210031)
   - Program downloads/uploads
   - Repeated modifications

5. **Firmware Manipulation** (210040-210041)
   - Firmware update mode
   - Integrity violations

6. **Device Control** (210050)
   - Unauthorized restarts/shutdowns

7. **Safety System Compromise** (210060)
   - Safety bypass/violations

8. **Attack Chain Correlation** (210070-210071)
   - Mode change + Program modification
   - Protection disabled + Safety bypass

9. **I/O Manipulation** (210080)
   - I/O image manipulation

### Example Critical Rule

```xml
<rule id="210070" level="15" frequency="2" timeframe="600">
  <if_matched_sid>210010,210030</if_matched_sid>
  <same_srcip/>
  <description>Siemens S7 mode change followed by program modification - CRITICAL Triton attack chain detected</description>
  <mitre>
    <id>T0858</id>  <!-- Change Operating Mode -->
    <id>T0821</id>  <!-- Modify Controller Tasking -->
    <id>T0831</id>  <!-- Manipulation of Control -->
    <id>T0880</id>  <!-- Loss of Safety -->
  </mitre>
  <group>ics,execution,siemens,triton_attack_chain,critical,</group>
  <options>alert_by_email</options>
</rule>
```text

---

## Siemens-Specific Patterns

### Event Codes to Monitor

**Authentication Events**:
- `SE_ACCESS_DENIED`
- `SE_LOGIN_FAILED`
- `SE_LOGIN_SUCCESS`
- `SE_DEFAULT_USER_AUTHENTICATION_USED`

**Mode Changes**:
- `SE_OPMOD_CHANGED`
- `SE_OPMOD_CHANGE_INITIATE`
- `SE_MODE_CHANGE`

**Protection Events**:
- `SE_PROTECTION_ENABLED`
- `SE_PROTECTION_DISABLED`
- `SE_PROTECTION_CHANGED`

**Program Events**:
- `SE_PROGRAM_DOWNLOAD`
- `SE_PROGRAM_UPLOAD`
- `SE_LOGIC_MODIFIED`

**Firmware Events**:
- `SE_FIRMWARE_UPDATE`
- `SE_FIRMWARE_MODE`
- `SE_FIRMWARE_INTEGRITY_FAILED`

**Safety Events**:
- `SE_SAFETY_BYPASS`
- `SE_SAFETY_DISABLED`
- `SE_SIS_VIOLATION`

### Log Format

**Siemens Syslog Format** (TIA Portal V17+):
```text
<PRI>timestamp hostname - IDxx [device@... devVendor="Siemens" devProduct="CPU 151x..." FWVersion="V..."] 
[function@... fct="..." oldState="..." newState="..."] 
[session@... protocolType="..." userName="..." src="..."] EVENT_CODE
```text

**Decoder**: Use `wazuh/siemens_decoders.xml` to extract fields:
- `device_id`, `product`, `fw_version`
- `function_id`, `fct`, `old_state`, `new_state`
- `session_id`, `protocol`, `username`, `src_ip`
- `event_code`

---

## Attack Chain Correlation

### Triton Attack Chain Detection

**Pattern 1: Mode Change + Program Modification**
- Rule ID: 210070
- Triggers: Mode change (210010) + Program modification (210030) from same source
- MITRE: T0858, T0821, T0831, T0880
- Severity: Level 15 (Critical)

**Pattern 2: Protection Disabled + Safety Bypass**
- Rule ID: 210071
- Triggers: Protection disabled (210021) + Safety bypass (210060) from same source
- MITRE: T0892, T0837, T0880
- Severity: Level 15 (Critical)

### Timeline-Based Detection

Monitor for events occurring within:
- **600 seconds (10 minutes)**: Attack chain correlation
- **300 seconds (5 minutes)**: Repeated mode changes
- **300 seconds**: Repeated failed logins (brute-force)

---

## Wazuh Detection Rules

### Rule Categories

All rules are in `wazuh/triton_rules.xml` with rule IDs 211000-211999:

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

### Example Critical Rule

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

### YARA Integration

Wazuh supports YARA scans via FIM/active response. Use public YARA rules (e.g., from Mandiant/FireEye, ICS-CERT) for:
- `trilog.exe` hash detection
- `inject.bin`, `imain.bin` payload detection
- Python framework indicators (Py2EXE compiled)

**Example YARA Rule** (from public sources):
```yara
rule TRITON_Framework {
  meta:
    description = "TRITON/TRISIS/HatMan framework indicators"
    author = "ICS-CERT/Mandiant"
  strings:
    $pyc = ".pyc" nocase wide
    $ts = "TsHi" nocase wide
    $inject = "inject.bin" nocase
    $library = "library.zip" nocase
  condition:
    2 of them and filesize < 3MB
}
```text

### Log Sources

1. **Engineering Workstations**:
   - Windows Sysmon/Event Logs for `trilog.exe` execution
   - FIM for `inject.bin`, `imain.bin`, `library.zip`
   - Process monitoring for TriStation/Triconex processes

2. **Network Monitoring**:
   - Suricata/Zeek for UDP port 1502 anomalies
   - Nozomi/Dragos TriStation dissectors (if available)
   - Protocol anomaly detection

3. **Triconex Controllers**:
   - Syslog (if enabled via Triconex gateway or protocol converter)
   - Mode changes, protection events
   - Fail-safe triggers
   - Note: Triconex controllers use TriStation protocol (UDP 1502), not standard Syslog like Siemens

---

## Best Practices

### Prevention

1. **Network Segmentation**: Isolate engineering workstations from production OT
2. **Least Privilege**: Restrict access to TriStation/TIA Portal
3. **Firmware Updates**: Apply vendor patches promptly (Schneider patched 2018)
4. **Access Control**: Whitelist authorized IPs/subnets
5. **Physical Security**: Restrict access to engineering workstations

### Detection

1. **Syslog Forwarding**: Configure Siemens PLCs to send logs to Wazuh
2. **Baseline Normal Operations**: Establish known-good patterns
3. **Correlation Rules**: Use frequency/timeframe for attack chains
4. **Whitelisting**: Reduce false positives with authorized IPs
5. **Alert Prioritization**: Focus on Level 13+ (critical) events

### Response

1. **Immediate Isolation**: Quarantine affected controllers
2. **Forensic Analysis**: Capture memory dumps during maintenance
3. **Vendor Notification**: Contact Siemens/Schneider for support
4. **Incident Reporting**: Report to CISA/ICS-CERT
5. **Recovery**: Restore from known-good firmware/programs

---

## Additional Resources

- **FireEye Triton Report**: https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html
- **Dragos Triton Analysis**: https://www.dragos.com/threat/triton/
- **CISA Alert**: https://www.cisa.gov/news-events/cybersecurity-advisories/aa17-352a
- **MITRE ATT&CK**: https://attack.mitre.org/campaigns/C0030/
- **Nozomi Networks TriStation Dissector**: https://github.com/NozomiNetworks/tricotools
- **MDudek TRISIS Repository**: https://github.com/MDudek-ICS/TRISIS-TRITON-HATMAN (code samples and artifacts)
- **Siemens Industrial Security**: https://www.siemens.com/industrial-security
- **Schneider Electric Security**: https://www.se.com/ww/en/work/support/cybersecurity/

### Related Documentation

- **TriStation Baseline Patterns**: See `TRISTATION_BASELINE_PATTERNS.md`
- **Nozomi Dissector Guide**: See `NOZOMI_TRISTATION_DISSECTOR_GUIDE.md`
- **YARA Rules**: See `triton_yara_rules.yar`
- **IOCs**: See `TRITON_IOCS.md`

---

## Status

✅ **Detection Rules Implemented**  
✅ **Siemens Decoders Created**  
✅ **MITRE ATT&CK Mappings Included**  
✅ **Attack Chain Correlation Rules**  
✅ **Production-Ready**

---

**Last Updated:** 2026-01-01  
**Version:** 1.0  
**Status:** Production-Ready
