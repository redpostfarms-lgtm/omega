# -*- coding: utf-8 -*-
# STONEWALL BAIT FARM - Intelligence gathering system
# Passive intel, zero risk - feeds attackers dummy payloads with backdoors

import os
import sys
import json
import time
import hashlib
import socket
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque


@dataclass
class Attacker:
    """Information about detected attacker."""
    ip: str
    first_seen: float
    last_seen: float
    attack_count: int
    attack_types: List[str]
    payloads_sent: int
    callbacks_received: int
    fingerprint: str
    last_callback: Optional[float] = None


class BaitFarm:
    """
    Bait farm system - passive intelligence gathering.
    
    When attacker detected:
    1. Feed dummy payload with backdoor
    2. Attacker phones home to us
    3. Receive passive intel
    4. Zero risk (all isolated)
    """
    
    def __init__(self, callback_port: int = 8443):
        """Initialize bait farm."""
        self.callback_port = callback_port
        self.attackers: Dict[str, Attacker] = {}
        self.payloads_sent = 0
        self.callbacks_received = 0
        self.intel_data = deque(maxlen=10000)  # Store last 10k callbacks
        self.active = False
        self.callback_server = None
        self.server_thread = None
    
    def enable(self):
        """Enable bait farm."""
        self.active = True
        self._start_callback_server()
        print("[Bait Farm] Active. Waiting for attackers...")
    
    def disable(self):
        """Disable bait farm."""
        self.active = False
        if self.callback_server:
            try:
                self.callback_server.close()
            except:
                pass
        print("[Bait Farm] Disabled.")
    
    def detect_attacker(self, ip: str, attack_type: str, request_data: bytes) -> Optional[str]:
        """
        Detect attacker and feed bait payload.
        
        Args:
            ip: Attacker IP address
            attack_type: Type of attack detected
            request_data: Request data
            
        Returns:
            Payload to send (or None if not an attacker)
        """
        if not self.active:
            return None
        
        # Check if known attacker
        if ip in self.attackers:
            attacker = self.attackers[ip]
            attacker.last_seen = time.time()
            attacker.attack_count += 1
            if attack_type not in attacker.attack_types:
                attacker.attack_types.append(attack_type)
        else:
            # New attacker
            fingerprint = self._generate_fingerprint(ip, request_data)
            attacker = Attacker(
                ip=ip,
                first_seen=time.time(),
                last_seen=time.time(),
                attack_count=1,
                attack_types=[attack_type],
                payloads_sent=0,
                callbacks_received=0,
                fingerprint=fingerprint
            )
            self.attackers[ip] = attacker
            print(f"[Bait Farm] New attacker detected: {ip} ({attack_type})")
        
        # Generate bait payload
        payload = self._generate_bait_payload(ip, attacker)
        attacker.payloads_sent += 1
        self.payloads_sent += 1
        
        print(f"[Bait Farm] Bait payload sent to {ip} (callback: {self.callback_port})")
        
        return payload
    
    def _generate_fingerprint(self, ip: str, data: bytes) -> str:
        """Generate attacker fingerprint."""
        combined = f"{ip}:{data[:100]}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _generate_bait_payload(self, ip: str, attacker: Attacker) -> str:
        """Generate bait payload with backdoor."""
        # Create payload that phones home
        payload_id = hashlib.md5(f"{ip}:{time.time()}".encode()).hexdigest()[:8]
        
        payload = {
            'type': 'data',
            'id': payload_id,
            'callback_url': f"http://{self._get_callback_host()}:{self.callback_port}/callback",
            'timestamp': time.time(),
            'target': 'system_info',
            'command': 'report'
        }
        
        # Encode payload (would be actual executable/script in production)
        payload_encoded = json.dumps(payload).encode('base64' if sys.version_info[0] < 3 else 'base64').decode()
        
        # In production, this would be actual backdoor code
        # For safety, this is just a marker
        return f"BAIT:{payload_encoded}"
    
    def _get_callback_host(self) -> str:
        """Get callback host (would be actual public IP in production)."""
        # In production, would get public IP
        # For now, use localhost
        return "localhost"
    
    def _start_callback_server(self):
        """Start callback server to receive intel."""
        def callback_handler(sock, addr):
            """Handle callback from attacker."""
            try:
                data = sock.recv(4096)
                
                # Record callback
                attacker_ip = addr[0]
                if attacker_ip in self.attackers:
                    attacker = self.attackers[attacker_ip]
                    attacker.callbacks_received += 1
                    attacker.last_callback = time.time()
                
                self.callbacks_received += 1
                
                # Store intel
                intel = {
                    'timestamp': time.time(),
                    'attacker_ip': attacker_ip,
                    'data': data.hex()[:200],  # Store hex of first 200 bytes
                    'size': len(data)
                }
                self.intel_data.append(intel)
                
                # Log
                print(f"[Bait Farm] Callback from {attacker_ip}: {len(data)} bytes")
                
                # Send dummy response (looks legitimate)
                sock.send(b"OK")
                
            except Exception as e:
                pass
            finally:
                sock.close()
        
        def server_loop():
            """Callback server loop."""
            self.callback_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.callback_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                self.callback_server.bind(('0.0.0.0', self.callback_port))
                self.callback_server.listen(10)
                
                while self.active:
                    try:
                        self.callback_server.settimeout(1.0)
                        sock, addr = self.callback_server.accept()
                        thread = threading.Thread(target=callback_handler, args=(sock, addr), daemon=True)
                        thread.start()
                    except socket.timeout:
                        continue
                    except Exception:
                        break
            except Exception as e:
                print(f"[Bait Farm] Server error: {e}")
        
        self.server_thread = threading.Thread(target=server_loop, daemon=True)
        self.server_thread.start()
    
    def get_intel(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent intel data."""
        return list(self.intel_data)[-limit:]
    
    def get_attacker_stats(self) -> Dict[str, Any]:
        """Get statistics on attackers."""
        return {
            'total_attackers': len(self.attackers),
            'total_payloads': self.payloads_sent,
            'total_callbacks': self.callbacks_received,
            'active_attackers': len([a for a in self.attackers.values() 
                                     if time.time() - a.last_seen < 3600]),
            'attackers': {ip: asdict(attacker) for ip, attacker in self.attackers.items()}
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get bait farm status."""
        return {
            'active': self.active,
            'callback_port': self.callback_port,
            'attackers_detected': len(self.attackers),
            'payloads_sent': self.payloads_sent,
            'callbacks_received': self.callbacks_received,
            'intel_stored': len(self.intel_data)
        }


if __name__ == '__main__':
    print("=" * 60)
    print("BAIT FARM - Test")
    print("=" * 60)
    
    farm = BaitFarm()
    farm.enable()
    
    # Simulate attacker
    payload = farm.detect_attacker("192.168.1.100", "crawler", b"GET / HTTP/1.1")
    print(f"\nBait payload: {payload[:100]}...")
    
    time.sleep(1)
    
    status = farm.get_status()
    print(f"\nStatus: {status}")
    
    farm.disable()
    print("\n[OK] Bait farm ready")

