#!/usr/bin/env python3
"""
Wazuh Rules Testing Script
==========================
Helper script for testing Wazuh decoders and rules with sample log data.

Usage:
    python test_wazuh_rules.py [--decoder DECODER_NAME] [--rule RULE_ID]
    python test_wazuh_rules.py --all  # Test all decoders/rules
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional


# Sample log data for testing
SAMPLE_LOGS = {
    "gatekeeper_anomaly": "Gatekeeper: ANOMALY DETECTED - type=network_spike src=10.10.1.100 count=150 threshold=100 time=2026-01-11T16:00:00Z",
    "gatekeeper_threat": "Gatekeeper: THREAT DETECTED - level=high source=192.168.10.20 desc=ROE violation detected category=unauthorized_execution",
    "gatekeeper_roe": "Gatekeeper: ROE VIOLATION - violation=unauthorized_execution src=10.0.0.5 time=2026-01-11T16:00:00Z action=blocked",
    "gatekeeper_counterstrike": "Gatekeeper: COUNTERSTRIKE - target=192.168.1.50 port=443 method=quantum_nuke time=2026-01-11T16:00:00Z",
    "gatekeeper_json": '2026-01-11 14:30:22 json_event: {"threat_level": "high", "source": "192.168.1.100", "details": "ROE violation detected"}',
    "modbus_json": '2026-01-11 14:30:22 {"src_ip":"192.168.10.50","dst_ip":"192.168.10.100","unit_id":1,"function_code":6,"function_name":"Write Single Register","address":107,"quantity":1,"exception":false}',
    "modbus_syslog": "Jan 11 15:45:00 plc-gateway modbus: src=192.168.1.20 dst=192.168.1.10 unit=1 func=0x06 addr=40001 qty=1 exception=false",
    "modbus_write_multiple": "Jan 11 15:45:00 plc-gateway modbus: src=192.168.1.20 dst=192.168.1.10 unit=1 func=0x10 addr=40001 qty=50 exception=false",
    "modbus_diagnostics": "Jan 11 15:45:00 plc-gateway modbus: src=192.168.1.20 dst=192.168.1.10 unit=1 func=0x08 sub_func=0x0004 exception=false",
    "dnp3_syslog": "Jan 11 15:45:00 dnp3-gateway DNP3: src=192.168.1.20 dst=192.168.1.10 src_addr=3 dest_addr=1 fc=129 fc_name=Response obj_type=30 obj_var=1 point=45 value=1.0 event=true",
    "iec104": "2026-01-11 16:20:00 IEC104: src=192.168.10.5 dst=192.168.10.100 asdu_type=45 cause=3 io_addr=10045 value=1 quality=good",
    "opcua_json": '{"timestamp":"2026-01-11T17:00:00Z","src":"192.168.20.10","dst":"192.168.20.50","node_id":"ns=2;s=PressureSensor","value":45.2,"status":"Good","operation":"Read"}',
}


def run_wazuh_logtest(log_line: str) -> Optional[str]:
    """
    Run wazuh-logtest with a sample log line.
    
    Args:
        log_line: The log line to test
        
    Returns:
        Output from wazuh-logtest or None if error
    """
    try:
        # Note: This requires wazuh-logtest to be installed on the system
        # In a real environment, this would run: /var/ossec/bin/wazuh-logtest
        # For testing purposes, we'll simulate or require the actual tool
        
        print(f"\n{'='*80}")
        print(f"Testing log: {log_line}")
        print(f"{'='*80}")
        
        # In production, uncomment this:
        # process = subprocess.Popen(
        #     ['/var/ossec/bin/wazuh-logtest'],
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True
        # )
        # stdout, stderr = process.communicate(input=log_line, timeout=10)
        # return stdout
        
        # For now, just print the log (user can test manually)
        print(f"To test this log, run:")
        print(f"  echo '{log_line}' | /var/ossec/bin/wazuh-logtest")
        return None
        
    except FileNotFoundError:
        print("ERROR: wazuh-logtest not found. Install Wazuh server first.")
        return None
    except subprocess.TimeoutExpired:
        print("ERROR: wazuh-logtest timed out.")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def test_all_logs():
    """Test all sample logs."""
    print("Testing all sample logs...\n")
    
    for name, log_line in SAMPLE_LOGS.items():
        print(f"\n[{name}]")
        run_wazuh_logtest(log_line)
        print()


def test_decoder(decoder_name: str):
    """Test a specific decoder."""
    decoder_logs = {
        "gatekeeper": ["gatekeeper_anomaly", "gatekeeper_threat", "gatekeeper_roe"],
        "modbus": ["modbus_json", "modbus_syslog", "modbus_write_multiple"],
        "dnp3": ["dnp3_syslog"],
        "iec104": ["iec104"],
        "opcua": ["opcua_json"],
    }
    
    if decoder_name not in decoder_logs:
        print(f"ERROR: Unknown decoder '{decoder_name}'")
        print(f"Available decoders: {', '.join(decoder_logs.keys())}")
        return
    
    print(f"Testing decoder: {decoder_name}\n")
    
    for log_name in decoder_logs[decoder_name]:
        if log_name in SAMPLE_LOGS:
            print(f"\n[{log_name}]")
            run_wazuh_logtest(SAMPLE_LOGS[log_name])


def print_sample_logs():
    """Print all sample logs for manual testing."""
    print("Sample Logs for Manual Testing:")
    print("=" * 80)
    print("\nCopy and paste these into wazuh-logtest:\n")
    
    for name, log_line in SAMPLE_LOGS.items():
        print(f"[{name}]")
        print(f"  {log_line}\n")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Wazuh decoders and rules with sample log data"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all sample logs"
    )
    parser.add_argument(
        "--decoder",
        type=str,
        help="Test a specific decoder (gatekeeper, modbus, dnp3, iec104, opcua)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available sample logs"
    )
    parser.add_argument(
        "--logtest-path",
        type=str,
        default="/var/ossec/bin/wazuh-logtest",
        help="Path to wazuh-logtest executable (default: /var/ossec/bin/wazuh-logtest)"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print_sample_logs()
        return
    
    if args.all:
        test_all_logs()
    elif args.decoder:
        test_decoder(args.decoder)
    else:
        print("Wazuh Rules Testing Script")
        print("=" * 80)
        print("\nUsage:")
        print("  python test_wazuh_rules.py --all              # Test all logs")
        print("  python test_wazuh_rules.py --decoder MODBUS   # Test Modbus decoder")
        print("  python test_wazuh_rules.py --list             # List all sample logs")
        print("\nAvailable decoders:")
        print("  - gatekeeper")
        print("  - modbus")
        print("  - dnp3")
        print("  - iec104")
        print("  - opcua")
        print("\nNote: This script requires wazuh-logtest to be installed on the Wazuh server.")
        print("      In production, run tests directly on the Wazuh manager.")


if __name__ == "__main__":
    main()
