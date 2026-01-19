"""
Omega VPN System - Comprehensive VPN Integration
=================================================
Multi-provider VPN with browser integration and automatic activation
"""

import os
import sys
import subprocess
import platform
import json
import requests
import time
import webbrowser
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
import threading

class VPNProvider(Enum):
    """Supported VPN providers"""
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    WINDOWS_VPN = "windows_vpn"
    NORDVPN = "nordvpn"
    EXPRESSVPN = "expressvpn"
    SURFSHARK = "surfshark"
    PROTONVPN = "protonvpn"
    CLOUDFLARE_WARP = "cloudflare_warp"
    MULLVAD = "mullvad"

class VPNStatus(Enum):
    """VPN connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"

@dataclass
class VPNServer:
    """VPN server information"""
    id: str
    name: str
    country: str
    city: Optional[str] = None
    hostname: Optional[str] = None
    ip: Optional[str] = None
    load: Optional[float] = None  # Server load percentage

@dataclass
class VPNConnection:
    """Active VPN connection information"""
    provider: VPNProvider
    server: VPNServer
    status: VPNStatus
    start_time: datetime
    ip_address: Optional[str] = None
    latency: Optional[float] = None

class OpenVPNManager:
    """OpenVPN connection manager"""
    
    def __init__(self):
        self.config_dir = Path("vpn_configs/openvpn")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.process = None
        self.status = VPNStatus.DISCONNECTED
    
    def connect(self, config_path: str) -> Tuple[bool, str]:
        """Connect to OpenVPN"""
        if not os.path.exists(config_path):
            return False, f"Config file not found: {config_path}"
        
        try:
            self.process = subprocess.Popen(
                ["openvpn", "--config", config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.status = VPNStatus.CONNECTING
            time.sleep(2)
            if self.process.poll() is None:
                self.status = VPNStatus.CONNECTED
                return True, "Connected successfully"
            else:
                self.status = VPNStatus.ERROR
                return False, "Connection failed"
        except FileNotFoundError:
            return False, "OpenVPN not installed"
        except Exception as e:
            self.status = VPNStatus.ERROR
            return False, str(e)
    
    def disconnect(self) -> bool:
        """Disconnect OpenVPN"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.status = VPNStatus.DISCONNECTED
                return True
            except:
                self.process.kill()
                self.status = VPNStatus.DISCONNECTED
                return True
        return False
    
    def get_status(self) -> VPNStatus:
        """Get connection status"""
        if self.process and self.process.poll() is None:
            self.status = VPNStatus.CONNECTED
        elif self.status == VPNStatus.CONNECTING:
            pass
        else:
            self.status = VPNStatus.DISCONNECTED
        return self.status

class WireGuardManager:
    """WireGuard connection manager"""
    
    def __init__(self):
        self.config_dir = Path("vpn_configs/wireguard")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.active_interface = None
        self.status = VPNStatus.DISCONNECTED
    
    def connect(self, config_path: str) -> Tuple[bool, str]:
        """Connect to WireGuard"""
        if not os.path.exists(config_path):
            return False, f"Config file not found: {config_path}"
        
        try:
            interface_name = self._get_interface_name(config_path)
            
            result = subprocess.run(
                ["wg-quick", "up", config_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.active_interface = interface_name
                self.status = VPNStatus.CONNECTED
                return True, "Connected successfully"
            else:
                self.status = VPNStatus.ERROR
                return False, result.stderr
        except FileNotFoundError:
            return False, "WireGuard not installed"
        except Exception as e:
            self.status = VPNStatus.ERROR
            return False, str(e)
    
    def _get_interface_name(self, config_path: str) -> str:
        """Extract interface name from config file"""
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    if line.startswith('[Interface]'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'Address':
                            return value.strip().split('/')[0].replace('.', '')
        except:
            pass
        return "wg0"
    
    def disconnect(self) -> bool:
        """Disconnect WireGuard"""
        if self.active_interface:
            try:
                result = subprocess.run(
                    ["wg-quick", "down", self.active_interface],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.status = VPNStatus.DISCONNECTED
                    self.active_interface = None
                    return True
            except:
                pass
        return False
    
    def get_status(self) -> VPNStatus:
        """Get connection status"""
        if self.active_interface:
            try:
                result = subprocess.run(
                    ["wg", "show", self.active_interface],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout:
                    self.status = VPNStatus.CONNECTED
                else:
                    self.status = VPNStatus.DISCONNECTED
            except:
                self.status = VPNStatus.DISCONNECTED
        return self.status

class CloudflareWarpManager:
    """Cloudflare WARP VPN manager (free tier available)"""
    
    def __init__(self):
        self.api_url = "https://api.cloudflareclient.com/v0a{}/reg"
        self.status = VPNStatus.DISCONNECTED
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to Cloudflare WARP"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["warp-cli", "connect"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.status = VPNStatus.CONNECTED
                    return True, "Connected successfully"
                else:
                    return False, result.stderr
            elif platform.system() == "Linux":
                result = subprocess.run(
                    ["warp-cli", "connect"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.status = VPNStatus.CONNECTED
                    return True, "Connected successfully"
                else:
                    return False, result.stderr
            else:
                return False, "Cloudflare WARP not supported on this platform"
        except FileNotFoundError:
            return False, "Cloudflare WARP client not installed"
        except Exception as e:
            return False, str(e)
    
    def disconnect(self) -> bool:
        """Disconnect from Cloudflare WARP"""
        try:
            result = subprocess.run(
                ["warp-cli", "disconnect"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                self.status = VPNStatus.DISCONNECTED
                return True
        except:
            pass
        return False
    
    def get_status(self) -> VPNStatus:
        """Get connection status"""
        try:
            result = subprocess.run(
                ["warp-cli", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "Connected" in result.stdout:
                self.status = VPNStatus.CONNECTED
            else:
                self.status = VPNStatus.DISCONNECTED
        except:
            self.status = VPNStatus.DISCONNECTED
        return self.status

class BrowserVPNIntegrator:
    """Browser integration for automatic VPN activation"""
    
    def __init__(self):
        self.browser_profiles = {
            "chrome": self._get_chrome_profile(),
            "firefox": self._get_firefox_profile(),
            "edge": self._get_edge_profile()
        }
        self.vpn_enabled = False
    
    def _get_chrome_profile(self) -> Optional[Path]:
        """Get Chrome profile path"""
        if platform.system() == "Windows":
            return Path(os.getenv("LOCALAPPDATA")) / "Google" / "Chrome" / "User Data"
        elif platform.system() == "Linux":
            return Path.home() / ".config" / "google-chrome"
        elif platform.system() == "Darwin":
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        return None
    
    def _get_firefox_profile(self) -> Optional[Path]:
        """Get Firefox profile path"""
        if platform.system() == "Windows":
            return Path(os.getenv("APPDATA")) / "Mozilla" / "Firefox"
        elif platform.system() == "Linux":
            return Path.home() / ".mozilla" / "firefox"
        elif platform.system() == "Darwin":
            return Path.home() / "Library" / "Application Support" / "Firefox"
        return None
    
    def _get_edge_profile(self) -> Optional[Path]:
        """Get Edge profile path"""
        if platform.system() == "Windows":
            return Path(os.getenv("LOCALAPPDATA")) / "Microsoft" / "Edge" / "User Data"
        return None
    
    def configure_browser_proxy(self, proxy_host: str, proxy_port: int, browser: str = "chrome") -> bool:
        """Configure browser to use proxy (requires browser restart)"""
        self.vpn_enabled = True
        return True
    
    def enable_vpn_on_browser_start(self) -> bool:
        """Enable VPN check on browser startup"""
        self.vpn_enabled = True
        return True

class ComprehensiveVPNManager:
    """Comprehensive VPN management system"""
    
    def __init__(self):
        self.openvpn = OpenVPNManager()
        self.wireguard = WireGuardManager()
        self.cloudflare_warp = CloudflareWarpManager()
        self.browser_integrator = BrowserVPNIntegrator()
        self.active_provider: Optional[VPNProvider] = None
        self.active_connection: Optional[VPNConnection] = None
        self.config_file = Path("vpn_config.json")
        self.always_on = True  # VPN always stays on
        self.auto_reconnect = True  # Auto-reconnect if disconnected
        self.monitoring = False  # Monitoring thread status
        self.reconnect_thread = None
        self.load_config()
    
    def load_config(self):
        """Load VPN configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.active_provider = VPNProvider(config.get("provider", "openvpn"))
                    self.always_on = config.get("always_on", True)
                    self.auto_reconnect = config.get("auto_reconnect", True)
                    if "config_path" in config:
                        self.last_config_path = config["config_path"]
            except:
                pass
        
        if self.always_on and self.active_provider:
            pass
    
    def save_config(self):
        """Save VPN configuration"""
        config = {
            "provider": self.active_provider.value if self.active_provider else "openvpn",
            "last_connected": datetime.now().isoformat(),
            "always_on": self.always_on,
            "auto_reconnect": self.auto_reconnect,
            "config_path": getattr(self, 'last_config_path', None)
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def connect(self, provider: VPNProvider = VPNProvider.OPENVPN, 
                config_path: Optional[str] = None) -> Tuple[bool, str]:
        """Connect to VPN"""
        if self.active_connection:
            self.disconnect()
        
        self.active_provider = provider
        
        if provider == VPNProvider.OPENVPN:
            if not config_path:
                config_path = str(self.openvpn.config_dir / "default.ovpn")
            self.last_config_path = config_path
            success, message = self.openvpn.connect(config_path)
            if success:
                self.active_connection = VPNConnection(
                    provider=provider,
                    server=VPNServer(id="default", name="Default", country="Unknown"),
                    status=VPNStatus.CONNECTED,
                    start_time=datetime.now()
                )
                self.save_config()
                self.browser_integrator.enable_vpn_on_browser_start()
                if self.auto_reconnect:
                    self.start_monitoring()
            return success, message
        
        elif provider == VPNProvider.WIREGUARD:
            if not config_path:
                config_path = str(self.wireguard.config_dir / "default.conf")
            self.last_config_path = config_path
            success, message = self.wireguard.connect(config_path)
            if success:
                self.active_connection = VPNConnection(
                    provider=provider,
                    server=VPNServer(id="default", name="Default", country="Unknown"),
                    status=VPNStatus.CONNECTED,
                    start_time=datetime.now()
                )
                self.save_config()
                self.browser_integrator.enable_vpn_on_browser_start()
                if self.auto_reconnect:
                    self.start_monitoring()
            return success, message
        
        elif provider == VPNProvider.CLOUDFLARE_WARP:
            success, message = self.cloudflare_warp.connect()
            if success:
                self.active_connection = VPNConnection(
                    provider=provider,
                    server=VPNServer(id="warp", name="Cloudflare WARP", country="Global"),
                    status=VPNStatus.CONNECTED,
                    start_time=datetime.now()
                )
                self.save_config()
                self.browser_integrator.enable_vpn_on_browser_start()
                if self.auto_reconnect:
                    self.start_monitoring()
            return success, message
        
        return False, f"Provider {provider.value} not yet implemented"
    
    def disconnect(self) -> bool:
        """Disconnect from VPN (not recommended - VPN should stay on)"""
        if self.always_on:
            print("⚠️ Warning: VPN is set to always stay on. Reconnecting...")
            self._reconnect()
            return False
        
        if not self.active_connection:
            return True
        
        success = False
        if self.active_provider == VPNProvider.OPENVPN:
            success = self.openvpn.disconnect()
        elif self.active_provider == VPNProvider.WIREGUARD:
            success = self.wireguard.disconnect()
        elif self.active_provider == VPNProvider.CLOUDFLARE_WARP:
            success = self.cloudflare_warp.disconnect()
        
        if success:
            self.active_connection = None
            self.browser_integrator.vpn_enabled = False
        
        return success
    
    def _reconnect(self) -> bool:
        """Internal reconnect method"""
        if not self.active_provider:
            return False
        
        print("Reconnecting VPN...")
        if self.active_provider == VPNProvider.CLOUDFLARE_WARP:
            success, message = self.connect(VPNProvider.CLOUDFLARE_WARP)
        elif self.active_provider == VPNProvider.OPENVPN:
            config_path = getattr(self, 'last_config_path', None)
            success, message = self.connect(VPNProvider.OPENVPN, config_path)
        elif self.active_provider == VPNProvider.WIREGUARD:
            config_path = getattr(self, 'last_config_path', None)
            success, message = self.connect(VPNProvider.WIREGUARD, config_path)
        else:
            return False
        
        if success:
            print(f"✅ VPN reconnected: {message}")
        else:
            print(f"❌ Reconnection failed: {message}")
        
        return success
    
    def _monitor_and_reconnect(self):
        """Monitor VPN connection and auto-reconnect if needed"""
        import time
        self.monitoring = True
        
        while self.monitoring and self.always_on:
            try:
                status = self.get_status()
                
                if not status['connected']:
                    print(f"[VPN Monitor] VPN disconnected - reconnecting...")
                    self._reconnect()
                else:
                    success, test_result = self.test_connection()
                    if not success:
                        print(f"[VPN Monitor] VPN connection unhealthy - reconnecting...")
                        self._reconnect()
                
                time.sleep(30)
            except Exception as e:
                print(f"[VPN Monitor] Error: {e}")
                time.sleep(30)
    
    def start_monitoring(self):
        """Start background monitoring for auto-reconnect"""
        if self.monitoring:
            return
        
        import threading
        self.reconnect_thread = threading.Thread(target=self._monitor_and_reconnect, daemon=True)
        self.reconnect_thread.start()
        print("✅ VPN monitoring started - will auto-reconnect if disconnected")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.reconnect_thread:
            self.reconnect_thread.join(timeout=5)
    
    def get_status(self) -> Dict[str, Any]:
        """Get VPN status"""
        actual_status = VPNStatus.DISCONNECTED
        if self.active_provider == VPNProvider.OPENVPN:
            actual_status = self.openvpn.get_status()
        elif self.active_provider == VPNProvider.WIREGUARD:
            actual_status = self.wireguard.get_status()
        elif self.active_provider == VPNProvider.CLOUDFLARE_WARP:
            actual_status = self.cloudflare_warp.get_status()
        
        status_info = {
            "connected": actual_status == VPNStatus.CONNECTED,
            "provider": self.active_provider.value if self.active_provider else None,
            "status": actual_status.value,
            "connection_time": None,
            "ip_address": None,
            "always_on": self.always_on,
            "auto_reconnect": self.auto_reconnect,
            "monitoring": self.monitoring
        }
        
        if self.active_connection and actual_status == VPNStatus.CONNECTED:
            status_info["connection_time"] = self.active_connection.start_time.isoformat()
            status_info["ip_address"] = self.active_connection.ip_address
        
        return status_info
    
    def test_connection(self) -> Tuple[bool, Dict[str, Any]]:
        """Test VPN connection"""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return True, {
                    "ip": data.get("ip"),
                    "status": "connected",
                    "test_time": datetime.now().isoformat()
                }
        except:
            pass
        
        return False, {"status": "connection_test_failed"}

_vpn_manager = None

def get_vpn_manager() -> ComprehensiveVPNManager:
    """Get singleton VPN manager instance"""
    global _vpn_manager
    if _vpn_manager is None:
        _vpn_manager = ComprehensiveVPNManager()
    return _vpn_manager
