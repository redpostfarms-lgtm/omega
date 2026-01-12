# TriStation Protocol Baseline Patterns
## Normal vs. Anomalous Traffic Documentation

**Date:** 2026-01-01  
**Version:** 1.0  
**Purpose:** Baseline traffic patterns for TriStation protocol (UDP 1502) to aid in anomaly detection

---

## Overview

This document provides baseline traffic patterns for legitimate TriStation 1131 software usage, enabling detection of anomalies indicative of Triton/TRISIS/HatMan malware activity.

---

## Normal TriStation Traffic (Baseline)

### Source Characteristics

**Authorized Sources:**
- Engineering workstations (known IPs, typically 192.168.10.x or 10.0.50.x)
- TriStation 1131 software (official Schneider Electric application)
- During maintenance windows (scheduled hours)
- From known user accounts

**Traffic Pattern:**
- Low steady-state (periodic status polls: ~1 packet/minute)
- Bursts during engineering sessions (program upload/download)
- Predictable timing (maintenance windows, not 24/7)

### Packet Characteristics

**Legitimate TriStation Packets:**
- **UDP Port 1502** (standard TriStation port)
- **Valid Function Codes**: Known codes (e.g., program_append, status_query, read/write memory)
- **Valid Sequence Numbers**: Sequential, no gaps
- **Valid Checksums**: All packets pass checksum validation
- **Valid Responses**: Controller responds with expected acknowledgments

**Normal Operations:**
- Program download/upload (during maintenance)
- Status queries (periodic polling)
- Memory reads/writes (engineering operations)
- Halt/run commands (scheduled operations)
- Diagnostics (authorized maintenance)

**Expected Error Rate:**
- Low (< 1% failed requests)
- No repeated validation failures
- No unexpected protocol errors

---

## Anomalous TriStation Traffic (Triton Indicators)

### Source Anomalies

**Unauthorized Sources:**
- Unknown IPs (not in engineering subnet)
- Compromised workstations
- External IPs (should not access UDP 1502)
- Non-engineering hours (outside maintenance windows)

**Traffic Pattern Anomalies:**
- High volume (unexpected bursts)
- Persistent connections (24/7 activity)
- Unusual timing (outside maintenance windows)

### Packet Anomalies

**Malformed Packets:**
- Invalid function codes (unknown/undefined codes)
- Invalid sequence numbers (gaps, duplicates)
- Invalid checksums (failed validation)
- Unexpected payloads (garbage data)

**Suspicious Commands:**
- Program append/download from unauthorized sources
- Multiple program modifications in short time
- Memory writes to unexpected addresses
- Halt/run commands outside scheduled windows
- Unusual diagnostic commands

**Error Patterns:**
- High error rate (> 5% failed requests)
- Repeated validation failures
- Controller entering fail-safe mode unexpectedly
- Redundant processor mismatches (Triton bug indicator)

### Triton-Specific Indicators

**Malware Artifacts:**
- `SafeAppendProgramMod` commands from unauthorized sources
- Program uploads containing known Triton payloads
- Protocol errors indicating reverse-engineered implementation
- Fail-safe triggers (validation failures between redundant processors)

**Attack Chain Indicators:**
- Mode change followed by program modification
- Multiple suspicious commands in short time window
- Firmware modification indicators
- Safety system bypass attempts

---

## Detection Thresholds

### Volume Thresholds

**Normal:**
- Status polls: 1-2 packets/minute (steady-state)
- Engineering sessions: 10-50 packets/minute (bursts)
- Total daily volume: < 1000 packets (typical environment)

**Anomalous:**
- > 100 packets/minute (sustained)
- > 5000 packets/day (unusual volume)
- 24/7 activity (no maintenance windows)

### Error Rate Thresholds

**Normal:**
- < 1% failed requests
- No repeated failures
- No validation errors

**Anomalous:**
- > 5% failed requests
- 3+ consecutive failures
- Validation failures (redundant processor mismatches)

### Timing Thresholds

**Normal:**
- Maintenance windows: 8 AM - 5 PM (typical)
- Scheduled operations only
- No activity during off-hours

**Anomalous:**
- Activity outside maintenance windows
- 24/7 connections
- Unusual timing patterns

---

## Baseline Establishment Process

### Step 1: Data Collection

1. **Monitor legitimate TriStation traffic for 30 days**
   - Capture all UDP 1502 traffic
   - Log source IPs, destination IPs, packet counts
   - Record function codes, error rates, timing

2. **Document authorized sources**
   - Engineering workstation IPs
   - User accounts
   - Maintenance schedules

### Step 2: Pattern Analysis

1. **Calculate normal baselines**
   - Average packet volume per hour
   - Typical function code distribution
   - Normal error rates
   - Maintenance window patterns

2. **Define thresholds**
   - Volume thresholds (mean + 3σ)
   - Error rate thresholds
   - Timing windows

### Step 3: Rule Tuning

1. **Configure Wazuh rules**
   - Set frequency/timeframe thresholds
   - Whitelist authorized IPs
   - Adjust alert levels based on deviations

2. **Test with known-good traffic**
   - Verify no false positives
   - Adjust thresholds as needed

---

## Example Baseline Values

### Typical Environment

**Packet Volume:**
- Steady-state: 1-2 packets/minute
- Engineering sessions: 10-50 packets/minute
- Daily total: 500-1000 packets

**Function Codes:**
- Status queries: 80%
- Program operations: 15%
- Diagnostics: 5%

**Error Rate:**
- < 1% failed requests
- No validation failures

**Timing:**
- Maintenance window: 8 AM - 5 PM (weekdays)
- No activity: 5 PM - 8 AM (weekdays), weekends

### Thresholds for Alerting

**Volume Alerts:**
- > 100 packets/minute (Level 11)
- > 5000 packets/day (Level 12)

**Error Alerts:**
- > 5% error rate (Level 12)
- 3+ consecutive failures (Level 13)
- Validation failures (Level 14-15)

**Timing Alerts:**
- Activity outside maintenance windows (Level 10)
- 24/7 connections (Level 11)

---

## Integration with Wazuh

### Rule Configuration

Use these baseline patterns to tune Wazuh rules:

```xml
<!-- High volume TriStation traffic -->
<rule id="211042" level="11">
  <if_sid>211000</if_sid>
  <match>UDP.*1502</match>
  <frequency>100</frequency>
  <timeframe>60</timeframe>
  <description>High-volume TriStation traffic - possible Triton activity</description>
</rule>
```

### Whitelisting

Whitelist authorized engineering IPs:

```xml
<rule id="211043" level="0">
  <if_sid>211000</if_sid>
  <field name="src_ip">^192\.168\.10\.|^10\.0\.50\.</field>
  <description>Authorized engineering subnet - whitelist</description>
</rule>
```

---

## References

- **Nozomi Networks TriStation Dissector**: https://github.com/NozomiNetworks/tricotools
- **Triton Attack Case Study**: CISA Alert AA17-352A
- **TriStation Protocol Documentation**: Schneider Electric Technical Documentation

---

**Last Updated:** 2026-01-01  
**Version:** 1.0  
**Status:** Production-Ready
