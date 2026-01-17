# Nozomi TriStation Dissector Integration Guide
## Wireshark Plugin for TriStation Protocol Analysis

**Date:** 2026-01-01  
**Version:** 1.0  
**Reference:** Nozomi Networks TriStation Protocol Plug-in for Wireshark

---

## Overview

The Nozomi Networks TriStation Dissector is a free, open-source Lua-based Wireshark plugin that parses the proprietary TriStation protocol (UDP port 1502) used by Schneider Electric's Triconex Tricon SIS controllers. This tool is essential for:

- Understanding normal TriStation communications
- Detecting anomalies or malicious activity (e.g., Triton injection)
- Forensic analysis of captured network traffic

**GitHub Repository:** https://github.com/NozomiNetworks/tricotools

---

## Installation

### Step 1: Download the Plugin

1. **Visit the GitHub repository:**
   ```
   https://github.com/NozomiNetworks/tricotools
   ```

2. **Download `TriStation.lua`** (main dissector file)

3. **(Optional) Download `malware_exec.pcap`** (sample PCAP for testing)

### Step 2: Install in Wireshark

**Windows:**
1. Navigate to: `%APPDATA%\Wireshark\plugins`
   - Usually: `C:\Users\<YourUsername>\AppData\Roaming\Wireshark\plugins`
2. Create `plugins` folder if it doesn't exist
3. Copy `TriStation.lua` into the plugins folder
4. Restart Wireshark

**Linux/macOS:**
1. Navigate to: `~/.config/wireshark/plugins` or `~/.wireshark/plugins`
2. Create `plugins` folder if it doesn't exist
3. Copy `TriStation.lua` into the plugins folder
4. Restart Wireshark

### Step 3: Verify Installation

1. Open Wireshark
2. Go to: **Help → About Wireshark → Plugins tab**
3. Look for `TriStation.lua` (should appear as "TriStation Protocol Plug-in")
4. Check for any errors in the console

---

## Usage

### Capturing TriStation Traffic

**Live Capture:**
1. Start Wireshark on interface connected to Triconex network
2. Use SPAN/mirror port for passive monitoring (recommended)
3. Apply filter: `udp.port == 1502`
4. Begin capture

**Offline Analysis:**
1. Open existing PCAP file containing TriStation traffic
2. Apply filter: `udp.port == 1502`
3. Use `malware_exec.pcap` from repository for testing

### Analyzing with the Dissector

Once loaded, Wireshark automatically applies the dissector to UDP/1502 packets.

**Key Elements Visible:**
- **Direction**: Request/response indicators
- **Function Codes**: Translated to human-readable descriptions (e.g., "Program Append", "Safe Append Program Mod")
- **Hardware Info**: Chassis type, connected modules
- **Program Data**: Extracted program content (if uploaded)
- **TRITON Detection**: Highlights malicious program upload indicators

**Example:**
In the sample `malware_exec.pcap`, the plugin flags a malicious upload during the Triton injection phase.

---

## Integration with Wazuh

### Option 1: Passive Network Monitoring

**Setup:**
1. Configure network tap/SPAN port to mirror UDP 1502 traffic
2. Capture packets to PCAP files
3. Analyze with Wireshark + TriStation dissector
4. Export alerts/logs to Wazuh

**Workflow:**
```text
Network Traffic → SPAN Port → PCAP Capture → Wireshark Analysis → Alerts → Wazuh
```text

### Option 2: Automated Analysis Script

**Using tshark (command-line Wireshark):**

```bash
#!/bin/bash
# Analyze TriStation traffic and generate alerts

tshark -r triStation_capture.pcap -Y "udp.port == 1502" -T json > triStation_analysis.json

# Parse JSON and extract Triton indicators
python parse_tristation_alerts.py triStation_analysis.json > wazuh_alerts.log

# Forward to Wazuh
tail -f wazuh_alerts.log | while read line; do
    echo "$line" | /var/ossec/bin/wazuh-logtest
done
```text

### Option 3: Suricata/Zeek Integration

**Configure Suricata/Zeek to forward TriStation alerts:**
1. Enable UDP 1502 monitoring in Suricata/Zeek
2. Use TriStation dissector insights to create detection rules
3. Forward alerts to Wazuh via syslog/JSON

---

## Triton Detection Capabilities

The Nozomi dissector automatically detects TRITON by identifying:

1. **Malicious Program Uploads**
   - Flags suspicious program append operations
   - Highlights non-standard program structures
   - Identifies known Triton payload patterns

2. **Protocol Anomalies**
   - Invalid function codes
   - Malformed packets
   - Unexpected responses

3. **Attack Indicators**
   - SafeAppendProgramMod commands from unauthorized sources
   - Program uploads containing inject.bin/imain.bin patterns
   - Validation failures (redundant processor mismatches)

---

## Troubleshooting

### Common Issues

**No Dissection Occurs:**
- Ensure packets are UDP/1502 (not TCP or other protocols)
- Check for packet fragmentation
- Verify packets are not TCP-encapsulated

**Lua Errors:**
- Check Wireshark console: **Help → About → Plugins → Errors**
- Verify correct file path
- Ensure valid Lua syntax (check for file corruption)

**Performance:**
- Lua dissectors are lightweight (fine for offline analysis)
- For continuous monitoring, use tshark or export to IDS
- Consider commercial OT monitoring tools (Nozomi Guardian, Dragos, Claroty)

---

## Best Practices

1. **Use in Lab Environments First**
   - Test with sample PCAPs before production use
   - Validate detection capabilities
   - Understand normal vs. anomalous patterns

2. **Combine with Wazuh Rules**
   - Use dissector for deep packet analysis
   - Use Wazuh for continuous monitoring and alerting
   - Correlate findings across both systems

3. **Regular Updates**
   - Check GitHub repository for updates
   - Review new detection capabilities
   - Update Wazuh rules based on dissector insights

4. **Security Considerations**
   - Use in air-gapped or lab environments
   - Ensure authorized access only
   - Follow organizational security policies

---

## Additional Resources

- **Official Blog Post**: https://www.nozominetworks.com/blog/new-triton-analysis-tool-wireshark-dissector-for-tristation-protocol
- **Wireshark Lua Dissector Docs**: https://www.wireshark.org/docs/wsdg_html_chunked/wsluarm.html
- **GitHub Repository**: https://github.com/NozomiNetworks/tricotools
- **Sample PCAP**: Included in repository (`malware_exec.pcap`)

---

## Example Output

**Normal TriStation Packet:**
```text
Direction: Request
Function Code: Status Query
Sequence Number: 12345
Checksum: Valid
Response: Acknowledged
```text

**Triton-flagged Packet:**
```text
Direction: Request
Function Code: Safe Append Program Mod
Sequence Number: 12346
Checksum: Valid
⚠ TRITON INDICATOR: Malicious program upload detected
Response: Validation Failure (redundant processor mismatch)
```text

---

**Last Updated:** 2026-01-01  
**Version:** 1.0  
**Status:** Production-Ready
