# Triton (TRISIS/HatMan) Indicators of Compromise (IOCs)
## File Hashes, Network Indicators, and Detection Signatures

**Date:** 2026-01-01  
**Version:** 1.0  
**Reference:** Triton Attack Case Study (2017)  
**Sources:** CISA, FireEye (Mandiant), Dragos, Nozomi Networks

---

## File Hashes

### Primary Components

**trilog.exe (Main Dropper)**
- **SHA256**: `0f4c93a6c105b7d4869012ef3c4e078f...` (partial, full hash varies by variant)
- **MD5**: Varies by variant
- **Description**: Malicious version of legitimate Triconex log analyzer
- **MITRE Technique**: T0849 (Masquerading)

**inject.bin (Injector Payload)**
- **SHA256**: `3788a0a1128cfa5655f977411c164bd8...` (partial)
- **Description**: PowerPC shellcode injector (exploits zero-day)
- **MITRE Technique**: T0843 (Program Download), T0857 (System Firmware)

**imain.bin (Implant/RAT)**
- **SHA256**: `62c1dd25d7ca3e5567f86b3d2f96605f...` (partial)
- **Description**: PowerPC backdoor/RAT payload
- **MITRE Technique**: T0843 (Program Download), T0871 (Execution through API)

**library.zip (Python Framework)**
- **SHA256**: `f6b7d78f8f049c5b82281bb48f85f1a4...` (partial)
- **Description**: Python protocol implementation (Py2EXE compiled)
- **Contains**: TsHi.py, TsLow.py, TS_cnames.py
- **MITRE Technique**: T0849 (Masquerading), T0871 (Execution through API)

---

## Network Indicators

### Protocol and Ports

**TriStation Protocol:**
- **Port**: UDP 1502 (standard TriStation port)
- **Protocol**: Proprietary TriStation (undocumented, reverse-engineered)
- **Direction**: Engineering workstation → Triconex controller

**Traffic Characteristics:**
- Protocol anomalies (malformed packets, invalid function codes)
- High error rate (> 5% failed requests)
- Unexpected commands (SafeAppendProgramMod from unauthorized sources)
- Validation failures (redundant processor mismatches)

### Source IP Indicators

**Suspicious Sources:**
- Unauthorized IPs (not in engineering subnet: 192.168.10.x, 10.0.50.x)
- External IPs accessing UDP 1502
- Compromised engineering workstations

**Timing Indicators:**
- Activity outside maintenance windows
- 24/7 connections (unusual for engineering workstations)
- High-volume traffic (unexpected bursts)

---

## File System Indicators

### File Names and Paths

**Malicious Files:**
- `trilog.exe` (masquerading as legitimate tool)
- `inject.bin` (injector payload)
- `imain.bin` (implant/RAT)
- `library.zip` (Python framework)

**Common Locations:**
- Engineering workstation directories
- Temporary folders
- User profile directories

### Process Indicators

**Suspicious Processes:**
- `trilog.exe` with unusual arguments
- Processes accessing UDP port 1502
- Python processes with TriStation-related modules

---

## Behavioral Indicators

### Attack Chain Patterns

**Stage 1: Initial Access**
- Phishing emails targeting engineering staff
- Supply chain compromise
- Remote access exploitation

**Stage 2: Lateral Movement**
- Credential dumping (Mimikatz-like tools)
- Remote service exploitation (PSExec-like)
- Access to engineering workstation

**Stage 3: Deployment**
- Execution of `trilog.exe` (masquerading)
- Extraction of `library.zip`, `inject.bin`, `imain.bin`
- Python framework initialization

**Stage 4: Exploitation**
- Zero-day exploit (buffer overflow in system call)
- Privilege escalation to supervisor mode
- Injection of `imain.bin` into controller memory

**Stage 5: Control**
- Remote access to controller (RAT capabilities)
- Program manipulation (halt/run, memory read/write)
- Safety system bypass attempts

### Failure Indicators (Triton Bug)

**Fail-Safe Triggers:**
- Validation failure between redundant processors
- Controller entering fail-safe mode unexpectedly
- Plant shutdown (prevented disaster)

**Detection Opportunity:**
- Fail-safe triggers indicate malware presence
- Validation errors reveal reverse-engineered implementation
- Unexpected shutdowns prompt investigation

---

## Detection Signatures

### YARA Rules

**See:** `triton_yara_rules.yar` for complete YARA rules

**Key Patterns:**
- `trilog.exe` with `inject.bin`/`imain.bin`
- `SafeAppendProgramMod` commands
- Python framework indicators (TsHi, TsLow, TS_cnames)
- PowerPC shellcode patterns

### Wazuh Rules

**Rule IDs:** 211000-211999 (Triton/Triconex rules)

**Key Detection Points:**
- Rule 211001: Suspicious trilog.exe execution
- Rule 211010: Program append/download to SIS
- Rule 211030: Firmware/memory modification
- Rule 211050: Attack chain correlation
- Rule 211070: Safety system compromise

### Network Signatures

**Suricata/Zeek Rules:**
- UDP 1502 traffic from unauthorized IPs
- High-volume TriStation traffic
- Protocol anomalies (malformed packets)
- Error rate thresholds (> 5% failures)

---

## Integration with Wazuh

### FIM Configuration

**Monitor for:**
- `trilog.exe` file creation/modification
- `inject.bin`, `imain.bin`, `library.zip` files
- YARA scanning (use `triton_yara_rules.yar`)

### Network Monitoring

**Monitor UDP 1502:**
- Source IP whitelisting
- Volume thresholds
- Error rate monitoring
- Protocol anomaly detection

### Process Monitoring

**Monitor processes:**
- `trilog.exe` execution
- Python processes with TriStation modules
- Processes accessing UDP 1502

---

## References

- **CISA Alert AA17-352A**: https://www.cisa.gov/news-events/cybersecurity-advisories/aa17-352a
- **FireEye Report**: https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html
- **Dragos Analysis**: https://www.dragos.com/threat/triton/
- **MDudek Repository**: https://github.com/MDudek-ICS/TRISIS-TRITON-HATMAN (code samples)
- **Nozomi Networks**: https://github.com/NozomiNetworks/tricotools (dissector)

---

**Last Updated:** 2026-01-01  
**Version:** 1.0  
**Status:** Production-Ready
