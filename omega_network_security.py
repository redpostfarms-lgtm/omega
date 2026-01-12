#!/usr/bin/env python3
"""
Omega Network Security System
==============================
VPN, Firewall, Air-Gapping, Attack Detection and Response
"""

import os
import sys
import subprocess
import platform
import socket
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SecurityLevel(Enum):
    """Security levels"""
    NORMAL = "normal"
    ELEVATED = "elevated"
    AIR_GAP = "air_gap"
    LOCKDOWN = "lockdown"

@dataclass
class NetworkConnection:
    """Network connection information"""
    protocol: str
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    status: str
    process: Optional[str] = None

@dataclass
class SecurityEvent:
    """Security event/attack detection"""
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    details: Dict[str, Any]

class VPNManager:
    """VPN connection management"""
    
    def __init__(self):
        self.system = platform.system()
        self.active_connection = None
        self._init_manager()
    
    def _init_manager(self):
        """Initialize VPN manager"""
        self.available_protocols = []
        
        # Check for OpenVPN
        if self._check_command("openvpn"):
            self.available_protocols.append("openvpn")
        
        # Check for WireGuard
        if self._check_command("wg"):
            self.available_protocols.append("wireguard")
        
        # Windows: Check for built-in VPN
        if self.system == "Windows":
            self.available_protocols.append("windows_vpn")
    
    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        try:
            subprocess.run([command, "--version"], 
                         capture_output=True, 
                         stderr=subprocess.DEVNULL,
                         timeout=2)
            return True
        except:
            return False
    
    def connect_vpn(self, config_path: str, protocol: str = "openvpn") -> bool:
        """Connect to VPN"""
        if protocol not in self.available_protocols:
            return False
        
        try:
            if protocol == "openvpn":
                process = subprocess.Popen(
                    ["openvpn", "--config", config_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.active_connection = process
                return True
            elif protocol == "wireguard":
                process = subprocess.Popen(
                    ["wg-quick", "up", config_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.active_connection = process
                return True
            elif protocol == "windows_vpn" and self.system == "Windows":
                # Windows VPN connection
                subprocess.run(["rasdial", "VPN_NAME", "USERNAME", "PASSWORD"])
                return True
        except Exception as e:
            print(f"VPN connection error: {e}")
            return False
        
        return False
    
    def disconnect_vpn(self) -> bool:
        """Disconnect VPN"""
        if not self.active_connection:
            return False
        
        try:
            self.active_connection.terminate()
            self.active_connection = None
            return True
        except:
            return False
    
    def get_vpn_status(self) -> Dict[str, Any]:
        """Get VPN connection status"""
        return {
            "connected": self.active_connection is not None,
            "available_protocols": self.available_protocols
        }

class FirewallManager:
    """Firewall management interface"""
    
    def __init__(self):
        self.system = platform.system()
        self._init_manager()
    
    def _init_manager(self):
        """Initialize firewall manager"""
        self.available = False
        
        if self.system == "Windows":
            # Windows Firewall
            self.available = True
        elif self.system == "Linux":
            # Check for ufw, iptables, firewalld
            if self._check_command("ufw"):
                self.backend = "ufw"
                self.available = True
            elif self._check_command("iptables"):
                self.backend = "iptables"
                self.available = True
            elif self._check_command("firewall-cmd"):
                self.backend = "firewalld"
                self.available = True
    
    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        try:
            subprocess.run([command, "--version"], 
                         capture_output=True, 
                         stderr=subprocess.DEVNULL,
                         timeout=2)
            return True
        except:
            return False
    
    def enable_firewall(self) -> bool:
        """Enable firewall"""
        if not self.available:
            return False
        
        try:
            if self.system == "Windows":
                subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"],
                             check=True)
                return True
            elif self.system == "Linux":
                if self.backend == "ufw":
                    subprocess.run(["sudo", "ufw", "enable"], check=True)
                    return True
        except:
            return False
        
        return False
    
    def block_connection(self, ip: str, port: Optional[int] = None) -> bool:
        """Block a specific IP or IP:port"""
        if not self.available:
            return False
        
        try:
            if self.system == "Windows":
                if port:
                    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule",
                                  f"name=Block_{ip}_{port}", "dir=out", "action=block",
                                  f"remoteip={ip}", f"remoteport={port}"],
                                 check=True)
                else:
                    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule",
                                  f"name=Block_{ip}", "dir=out", "action=block",
                                  f"remoteip={ip}"],
                                 check=True)
                return True
            elif self.system == "Linux":
                if self.backend == "ufw":
                    if port:
                        subprocess.run(["sudo", "ufw", "deny", "from", ip, "to", "any", "port", str(port)],
                                     check=True)
                    else:
                        subprocess.run(["sudo", "ufw", "deny", "from", ip],
                                     check=True)
                    return True
        except:
            return False
        
        return False

class AirGapController:
    """Air-gapping system - complete network isolation"""
    
    def __init__(self, firewall: FirewallManager):
        self.firewall = firewall
        self.active = False
        self.blocked_connections = []
    
    def enable_air_gap(self) -> bool:
        """Enable air-gapping - block all network connections"""
        if self.active:
            return True
        
        try:
            if platform.system() == "Windows":
                # Block all outbound connections
                subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule",
                              "name=AirGap_BlockAll", "dir=out", "action=block"],
                             check=True)
                self.active = True
                return True
            elif platform.system() == "Linux":
                # Use iptables to block all
                subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-j", "DROP"],
                             check=True)
                self.active = True
                return True
        except Exception as e:
            print(f"Air-gap enable error: {e}")
            return False
        
        return False
    
    def disable_air_gap(self) -> bool:
        """Disable air-gapping - restore network access"""
        if not self.active:
            return True
        
        try:
            if platform.system() == "Windows":
                subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule",
                              "name=AirGap_BlockAll"],
                             check=True)
            elif platform.system() == "Linux":
                subprocess.run(["sudo", "iptables", "-D", "OUTPUT", "-j", "DROP"],
                             check=True)
            
            self.active = False
            return True
        except:
            return False
    
    def is_air_gapped(self) -> bool:
        """Check if air-gapping is active"""
        return self.active

class AttackDetector:
    """Attack detection and analysis system"""
    
    def __init__(self):
        self.detected_attacks = []
        self.monitoring = False
    
    def detect_attack(self, connection: NetworkConnection) -> Optional[SecurityEvent]:
        """Detect potential attack from network connection"""
        # Simple heuristics - can be expanded
        suspicious_indicators = []
        
        # Check for suspicious ports
        suspicious_ports = [23, 135, 139, 445, 1433, 3389]  # Common attack vectors
        if connection.remote_port in suspicious_ports:
            suspicious_indicators.append(f"suspicious_port_{connection.remote_port}")
        
        # Check for rapid connections
        # (This would require connection tracking)
        
        if suspicious_indicators:
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type="potential_attack",
                severity="medium",
                source=connection.remote_addr,
                details={
                    "indicators": suspicious_indicators,
                    "connection": {
                        "protocol": connection.protocol,
                        "remote": f"{connection.remote_addr}:{connection.remote_port}",
                        "local": f"{connection.local_addr}:{connection.local_port}"
                    }
                }
            )
            self.detected_attacks.append(event)
            return event
        
        return None
    
    def get_detected_attacks(self) -> List[SecurityEvent]:
        """Get list of detected attacks"""
        return self.detected_attacks

class SecurityManager:
    """Main security management interface"""
    
    def __init__(self):
        self.vpn = VPNManager()
        self.firewall = FirewallManager()
        self.air_gap = AirGapController(self.firewall)
        self.attack_detector = AttackDetector()
        self.security_level = SecurityLevel.NORMAL
    
    def set_security_level(self, level: SecurityLevel):
        """Set security level"""
        self.security_level = level
        
        if level == SecurityLevel.AIR_GAP:
            self.air_gap.enable_air_gap()
        elif level == SecurityLevel.LOCKDOWN:
            self.air_gap.enable_air_gap()
            self.firewall.enable_firewall()
        else:
            self.air_gap.disable_air_gap()
    
    def detect_and_respond(self, connection: NetworkConnection) -> bool:
        """Detect attack and respond automatically"""
        attack = self.attack_detector.detect_attack(connection)
        
        if attack:
            # Auto-response: Enable air-gap and block source
            self.set_security_level(SecurityLevel.AIR_GAP)
            self.firewall.block_connection(connection.remote_addr)
            return True
        
        return False
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            "security_level": self.security_level.value,
            "vpn": self.vpn.get_vpn_status(),
            "air_gapped": self.air_gap.is_air_gapped(),
            "firewall_enabled": self.firewall.available,
            "detected_attacks": len(self.attack_detector.get_detected_attacks())
        }

# Global instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get singleton security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
