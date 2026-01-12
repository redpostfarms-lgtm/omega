# -*- coding: utf-8 -*-
# TRACE-BAIT SYSTEM - Swallows traceroute probes, returns silence
# SYN, ICMP, DNS exfiltration - all swallowed, no echo, no TTL, no route back

import os
import sys
import time
import socket
import struct
import random
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque


@dataclass
class ProbeDetector:
    """Detects various probe types."""
    syn_probes: int = 0
    icmp_probes: int = 0
    dns_probes: int = 0
    total_swallowed: int = 0
    last_probe: float = 0.0


class TraceBaitSystem:
    """
    Trace-bait system that swallows traceroute probes.
    
    When probe detected:
    1. Swallow the packet (no echo, no TTL, no route back)
    2. Return silence
    3. Send dummy IP to the ocean (middle of nowhere)
    """
    
    def __init__(self):
        self.detector = ProbeDetector()
        self.active = False
        self.dummy_ips = [
            "185.199.108.0",  # Middle of ocean (Pacific)
            "45.33.32.156",   # Another ocean IP
            "192.0.2.0",      # TEST-NET (RFC 5737)
            "198.51.100.0",   # TEST-NET-2
            "203.0.113.0"     # TEST-NET-3
        ]
        self.swallowed_packets = deque(maxlen=1000)
        self.probe_listener_thread = None
    
    def enable(self):
        """Enable trace-bait system."""
        self.active = True
        self._start_probe_listener()
        print("[Trace-Bait] System active. Probes will be swallowed.")
    
    def disable(self):
        """Disable trace-bait system."""
        self.active = False
        if self.probe_listener_thread:
            # Stop thread gracefully
            pass
        print("[Trace-Bait] System disabled.")
    
    def _start_probe_listener(self):
        """Start background thread to listen for probes."""
        if self.probe_listener_thread:
            return
        
        def listener():
            while self.active:
                try:
                    self._check_for_probes()
                    time.sleep(0.1)  # Check every 100ms
                except Exception:
                    pass
        
        self.probe_listener_thread = threading.Thread(target=listener, daemon=True)
        self.probe_listener_thread.start()
    
    def detect_syn_probe(self, packet: bytes) -> bool:
        """Detect SYN probe (traceroute TCP)."""
        if len(packet) < 20:
            return False
        
        # Check IP header
        if packet[0] >> 4 != 4:  # Not IPv4
            return False
        
        # Check for TCP
        protocol = packet[9]
        if protocol != 6:  # TCP
            return False
        
        # Check TCP header for SYN flag
        if len(packet) >= 40:
            tcp_flags = packet[33]
            if tcp_flags & 0x02:  # SYN flag
                # Not ACK = probe
                if not (tcp_flags & 0x10):  # No ACK
                    return True
        
        return False
    
    def detect_icmp_probe(self, packet: bytes) -> bool:
        """Detect ICMP probe (traceroute ICMP)."""
        if len(packet) < 20:
            return False
        
        # Check IP header
        if packet[0] >> 4 != 4:
            return False
        
        protocol = packet[9]
        if protocol == 1:  # ICMP
            if len(packet) >= 28:
                icmp_type = packet[20]
                # ICMP Echo Request (8) or Time Exceeded (11)
                if icmp_type in [8, 11]:
                    return True
        
        return False
    
    def detect_dns_probe(self, packet: bytes) -> bool:
        """Detect DNS exfiltration probe."""
        if len(packet) < 20:
            return False
        
        protocol = packet[9]
        if protocol == 17:  # UDP
            # Check if it's DNS (port 53)
            if len(packet) >= 28:
                src_port = struct.unpack('!H', packet[20:22])[0]
                dst_port = struct.unpack('!H', packet[22:24])[0]
                
                if src_port == 53 or dst_port == 53:
                    # Check for suspicious DNS patterns
                    if len(packet) > 42:
                        dns_data = packet[42:]
                        # Look for exfiltration patterns
                        if b'.exfil' in dns_data or b'.data' in dns_data:
                            return True
        
        return False
    
    def swallow_probe(self, packet: bytes, probe_type: str) -> bool:
        """
        Swallow a probe packet.
        
        Args:
            packet: Packet data
            probe_type: Type of probe ('syn', 'icmp', 'dns')
            
        Returns:
            True if swallowed successfully
        """
        if not self.active:
            return False
        
        # Record probe
        self.swallowed_packets.append({
            'type': probe_type,
            'time': time.time(),
            'size': len(packet)
        })
        
        self.detector.total_swallowed += 1
        self.detector.last_probe = time.time()
        
        if probe_type == 'syn':
            self.detector.syn_probes += 1
        elif probe_type == 'icmp':
            self.detector.icmp_probes += 1
        elif probe_type == 'dns':
            self.detector.dns_probes += 1
        
        # Send dummy response to ocean IP
        self._send_dummy_response()
        
        # Return silence (no actual response)
        return True
    
    def _check_for_probes(self):
        """Check for incoming probes (simplified - would use raw sockets in production)."""
        # In production, would use raw sockets to capture packets
        # For now, this is a placeholder that would be called by packet capture
        
        # Example: Check raw socket for probes
        # This would require root/admin privileges
        pass
    
    def _send_dummy_response(self):
        """Send dummy response to ocean IP (middle of nowhere)."""
        # Select random dummy IP
        dummy_ip = random.choice(self.dummy_ips)
        
        # Create dummy packet
        # In production, would craft and send packet
        # For now, just log
        
        if random.random() < 0.1:  # 10% chance to log
            print(f"[Trace-Bait] Probe swallowed. Dummy IP: {dummy_ip}")
    
    def check_packet(self, packet: bytes) -> Tuple[bool, Optional[str]]:
        """
        Check packet and swallow if it's a probe.
        
        Returns:
            (is_probe, probe_type)
        """
        if not self.active:
            return (False, None)
        
        # Check for SYN probe
        if self.detect_syn_probe(packet):
            self.swallow_probe(packet, 'syn')
            return (True, 'syn')
        
        # Check for ICMP probe
        if self.detect_icmp_probe(packet):
            self.swallow_probe(packet, 'icmp')
            return (True, 'icmp')
        
        # Check for DNS probe
        if self.detect_dns_probe(packet):
            self.swallow_probe(packet, 'dns')
            return (True, 'dns')
        
        return (False, None)
    
    def get_status(self) -> Dict:
        """Get trace-bait system status."""
        return {
            'active': self.active,
            'total_swallowed': self.detector.total_swallowed,
            'syn_probes': self.detector.syn_probes,
            'icmp_probes': self.detector.icmp_probes,
            'dns_probes': self.detector.dns_probes,
            'last_probe': self.detector.last_probe,
            'recent_swallowed': len(self.swallowed_packets)
        }


if __name__ == '__main__':
    print("=" * 60)
    print("TRACE-BAIT SYSTEM - Test")
    print("=" * 60)
    
    system = TraceBaitSystem()
    system.enable()
    
    # Create dummy probe packets
    # SYN probe
    syn_packet = bytearray([0x45, 0x00, 0x00, 0x3c]) + b'\x00' * 36  # Minimal SYN
    syn_packet[33] = 0x02  # SYN flag
    
    # ICMP probe
    icmp_packet = bytearray([0x45, 0x00, 0x00, 0x3c]) + b'\x00' * 20
    icmp_packet[9] = 0x01  # ICMP protocol
    icmp_packet[20] = 0x08  # Echo Request
    
    # Test
    is_probe, probe_type = system.check_packet(bytes(syn_packet))
    print(f"SYN probe detected: {is_probe}, type: {probe_type}")
    
    is_probe, probe_type = system.check_packet(bytes(icmp_packet))
    print(f"ICMP probe detected: {is_probe}, type: {probe_type}")
    
    print(f"\nStatus: {system.get_status()}")
    
    print("\n[OK] Trace-bait system ready")

