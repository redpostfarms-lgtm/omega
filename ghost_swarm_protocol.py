#!/usr/bin/env python3
"""
Ghost Swarm Protocol (GS Protocol) v1.0 - Security Simulation Tool
===================================================================
Tkinter-based security simulation tool with improved code quality.
Note: This is simulation/demo code - uses random values, no actual network operations.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class IncidentLogger:
    """Forensic & Legal Logger - Logs security events to file with rotation."""
    
    def __init__(self, log_file='defense_log.txt', max_size_mb=10, backup_count=5):
        self.report = []
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        self.backup_count = backup_count
    
    def stamp(self, action, threat_level='DEFENSE'):
        """Log an incident with timestamp."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.report.append(
            f'[{timestamp}] {action.upper()} - Threat Level: {threat_level} - Self-Defense Activated'
        )
    
    def _rotate_log_if_needed(self):
        """Rotate log file if it exceeds size limit."""
        if not self.log_file.exists():
            return
        
        try:
            file_size = self.log_file.stat().st_size
            if file_size >= self.max_size_bytes:
                # Rotate existing backups
                for i in range(self.backup_count - 1, 0, -1):
                    old_backup = self.log_file.with_suffix(f'.{i}')
                    new_backup = self.log_file.with_suffix(f'.{i + 1}')
                    if old_backup.exists():
                        if new_backup.exists():
                            new_backup.unlink()
                        old_backup.rename(new_backup)
                
                # Move current log to .1
                backup = self.log_file.with_suffix('.1')
                if backup.exists():
                    backup.unlink()
                self.log_file.rename(backup)
        except Exception as e:
            print(f"Log rotation error: {e}")
    
    def get_report(self):
        """Save report to file and return status."""
        try:
            # Rotate if needed
            self._rotate_log_if_needed()
            
            # Ensure directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write directly to log file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.report))
                f.flush()  # Ensure data is written
            return f'Report saved as {self.log_file}'
        except Exception as e:
            return f'Error saving report: {e}'


def retry_on_error(max_retries=3, delay=1.0, exponential_backoff=True):
    """Decorator for retrying operations on failure."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(current_delay)
                        if exponential_backoff:
                            current_delay *= 2
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator


class MilitaryROE:
    """Military Rules of Engagement - Threat evaluation and authorization."""
    
    def __init__(self, logger=None, hostile_intent_threshold=0.8):
        self.logger = logger  # Fixed: logger passed in __init__
        self.principles = {
            'self_defense': 'Inherent right - Nothing limits unit/individual defense',
            'necessity': 'Non-force alternatives exhausted?',
            'proportionality': 'Force mirrors incoming only - No escalation',
            'hostile_intent_threshold': hostile_intent_threshold
        }
    
    def evaluate_threat(self, packet):
        """Evaluate threat level (simulated)."""
        # Real: AI pattern match. Here: simulate.
        intent = random.uniform(0.65, 0.98)
        if intent >= self.principles['hostile_intent_threshold']:
            if self.logger:
                self.logger.stamp(
                    f'Hostile Intent Confirmed - Score: {intent:.2f} - NECESSITY MET'
                )
            return True
        return False
    
    def authorize_counter(self, threat_level):
        """Authorize countermeasures based on threat level."""
        if threat_level == 'ACTIVE_INTRUSION' and self.evaluate_threat({}):
            if self.logger:
                self.logger.stamp('PROPORTIONALITY CHECK: Mirror only - SELF-DEFENSE AUTHORIZED')
            return True
        if self.logger:
            self.logger.stamp('NECESSITY FAIL: Passive block sufficient')
        return False


class GhostSwarmProtocol:
    """Ghost Swarm Protocol (GS Protocol) - Main security simulation system."""
    
    def __init__(self, state_file='gs_protocol_state.json', config_file='gs_protocol_config.json'):
        self.state_file = Path(state_file)
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Initialize logger with config
        log_config = self.config.get('logging', {})
        self.logger = IncidentLogger(
            log_file=log_config.get('log_file', 'defense_log.txt'),
            max_size_mb=log_config.get('max_log_size_mb', 10),
            backup_count=log_config.get('backup_count', 5)
        )
        
        # Initialize ROE with config
        threat_config = self.config.get('threat_detection', {})
        self.roe = MilitaryROE(
            logger=self.logger,
            hostile_intent_threshold=threat_config.get('hostile_intent_threshold', 0.8)
        )
        
        self.layers = ['Outer Shield (Windows)', 'Middle Guard', 'Core Sentinel']
        self.active_layers = {layer: True for layer in self.layers}
        self.last_hit = 0  # Fixed: instance variable instead of global
        self.swarm_active = False
        self.gui = None
        self.feed = None
        self.status_frame = None
        self.threat_frame = None
        self.threat_label = None
        self.rule_checks = []
        self.threat_detected = False
        self.nuke_button = None
        self.entangle_seed = 1  # Protocol efficiency seed (grows with each attack)
        self._running = True
        
        # Resource monitoring
        self._resource_monitoring_enabled = self.config.get('resource_monitoring', {}).get('enabled', False)
        self._memory_limit_mb = self.config.get('resource_monitoring', {}).get('max_memory_mb', 512)
        
        # Load saved state
        self.load_state()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            'logging': {'max_log_size_mb': 10, 'backup_count': 5, 'log_file': 'defense_log.txt'},
            'threading': {'predict_interval_seconds': 3, 'threat_check_interval_seconds': 4, 'auto_save_interval_seconds': 30, 'threat_cooldown_seconds': 20},
            'threat_detection': {'detection_probability': 0.05, 'predict_threshold': 0.85, 'hostile_intent_threshold': 0.8},
            'counterstrike': {'min_port': 80, 'max_port': 4433, 'decohere_packets': 9, 'decohere_delay_min': 0.1, 'decohere_delay_max': 0.4},
            'error_recovery': {'max_retries': 3, 'retry_delay_seconds': 1.0, 'exponential_backoff': True},
            'resource_monitoring': {'enabled': True, 'check_interval_seconds': 60, 'max_memory_mb': 512, 'max_cpu_percent': 80.0}
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key in user_config:
                            default_config[key].update(user_config[key])
                    return default_config
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        # Create default config file
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            print(f"Error creating config file: {e}")
        
        return default_config
    
    def _validate_port(self, port: int) -> bool:
        """Validate port number."""
        counter_config = self.config.get('counterstrike', {})
        min_port = counter_config.get('min_port', 80)
        max_port = counter_config.get('max_port', 4433)
        return isinstance(port, int) and min_port <= port <= max_port
    
    def _check_resources(self) -> bool:
        """Check if system resources are within limits."""
        if not self._resource_monitoring_enabled:
            return True
        
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=0.1)
            
            max_memory = self.config.get('resource_monitoring', {}).get('max_memory_mb', 512)
            max_cpu = self.config.get('resource_monitoring', {}).get('max_cpu_percent', 80.0)
            
            if memory_mb > max_memory:
                print(f"WARNING: Memory usage {memory_mb:.1f}MB exceeds limit {max_memory}MB")
                return False
            if cpu_percent > max_cpu:
                print(f"WARNING: CPU usage {cpu_percent:.1f}% exceeds limit {max_cpu}%")
                return False
            return True
        except ImportError:
            # psutil not available, skip monitoring
            return True
        except Exception as e:
            print(f"Resource check error: {e}")
            return True
    
    def predict_threat(self):
        """Predictive Scanner - Simulate threat detection."""
        if not self.feed:
            return
        
        scan = random.random()
        if scan > 0.85:
            self._safe_insert_text(
                '\n[!] ANOMALY PREDICTED - Port scan pattern detected. ROE on standby.\n'
            )
            self.logger.stamp('PREEMPTIVE ALERT: Behavior flagged')
    
    def confirm_nuke(self):
        """Nuke Gate - Confirm counterstrike authorization."""
        if not self.threat_detected:
            messagebox.showwarning(
                'GS Protocol',
                'No active threat detected. Counterstrike disabled.'
            )
            return
        
        if messagebox.askyesno(
            'GS Protocol - Counterstrike Authorization',
            'Launch payload? Last resort protocol - Irreversible action.'
        ):
            self.swarm_active = True
            self.logger.stamp('Counterstrike sequence: Payload authorized - Last Resort Protocol')
            port = self.detect_mirrored_port()
            if port:
                threading.Thread(target=self.quantum_nuke, args=(port,), daemon=True).start()
            else:
                self.swarm_active = False
                messagebox.showerror('GS Protocol', 'Failed to detect target port.')
    
    def launch_interface(self):
        """Launch Interface - Create and show GUI."""
        self.gui = tk.Tk()
        self.gui.title('Ghost Swarm Protocol (GS Protocol)')
        self.gui.geometry('900x680')
        self.gui.configure(bg='#0a0a0a')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Destructive.TButton', foreground='red')
        
        # Header
        tk.Label(
            self.gui,
            text='Defense Feed - Always Ahead',
            bg='#0a0a0a',
            fg='lime',
            font=('Consolas', 12, 'bold')
        ).pack(pady=5)
        
        # Feed display
        self.feed = scrolledtext.ScrolledText(
            self.gui,
            bg='black',
            fg='lime',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.feed.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status label
        tk.Label(
            self.gui,
            text='Layer Status:',
            bg='#0a0a0a',
            fg='cyan'
        ).pack(pady=2)
        
        # Status frame
        self.status_frame = tk.Frame(self.gui, bg='#0a0a0a')
        self.status_frame.pack()
        self.update_status()
        
        # Threat detection panel
        self.build_threat_panel()
        
        # Nuke button
        self.nuke_button = ttk.Button(
            self.gui,
            text='GS Protocol - Counterstrike',
            command=self.confirm_nuke,
            style='Destructive.TButton',
            state='disabled'
        )
        self.nuke_button.pack(pady=8)
        
        # Handle window close
        self.gui.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # Background threads
        threading.Thread(target=self.__predict_loop, daemon=True).start()
        threading.Thread(target=self.monitor_threat, daemon=True).start()
        threading.Thread(target=self.__auto_save_loop, daemon=True).start()
        
        self.gui.mainloop()
    
    def __auto_save_loop(self):
        """Auto-save state every 30 seconds."""
        while self._running:
            time.sleep(30)
            try:
                self.save_state()
            except Exception as e:
                print(f"Auto-save error: {e}")
    
    @retry_on_error(max_retries=3, delay=1.0, exponential_backoff=True)
    def load_state(self):
        """Load state from JSON file."""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validate loaded data
                if isinstance(data, dict):
                    self.entangle_seed = data.get('entangle_seed', self.entangle_seed)
                    if not isinstance(self.entangle_seed, int) or self.entangle_seed < 0:
                        self.entangle_seed = 1
                    
                    self.active_layers = data.get('active_layers', self.active_layers)
                    if not isinstance(self.active_layers, dict):
                        self.active_layers = {layer: True for layer in self.layers}
                    
                    self.last_hit = data.get('last_hit', self.last_hit)
                    if not isinstance(self.last_hit, int) or not self._validate_port(self.last_hit):
                        self.last_hit = 0
        except json.JSONDecodeError as e:
            print(f"State file corrupted: {e}, using defaults")
        except Exception as e:
            print(f"Error loading state: {e}")
    
    def save_state(self):
        """Save state to JSON file."""
        try:
            data = {
                'entangle_seed': self.entangle_seed,
                'active_layers': self.active_layers,
                'last_hit': self.last_hit
            }
            # Ensure directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            # Write to file
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.flush()  # Ensure data is written
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def on_closing(self):
        """Handle window close event."""
        self._running = False
        try:
            self.save_state()  # Save state on close
            self.logger.get_report()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        if self.gui:
            self.gui.destroy()
    
    def __predict_loop(self):
        """Background loop for threat prediction."""
        threading_config = self.config.get('threading', {})
        interval = threading_config.get('predict_interval_seconds', 3)
        
        while self._running:
            if not self.swarm_active:
                self.predict_threat()
            time.sleep(interval)
    
    def update_status(self):
        """Update status display."""
        if not self.status_frame:
            return
        
        # Clear existing widgets
        for w in self.status_frame.winfo_children():
            w.destroy()
        
        # Add status labels
        for layer, up in self.active_layers.items():
            col = 'green' if up else 'red'
            status_text = 'UP' if up else 'BREACHED'
            ttk.Label(
                self.status_frame,
                text=f'{layer}: {status_text}',
                foreground=col
            ).pack(side='left', padx=8)
    
    def build_threat_panel(self):
        """Build threat detection panel with guidelines."""
        if not self.gui:
            return
        
        # Threat frame (red background)
        self.threat_frame = tk.Frame(self.gui, bg='#8B0000', height=60, relief=tk.RAISED, bd=2)
        self.threat_frame.pack(pady=10, fill='x', padx=10)
        self.threat_frame.pack_propagate(False)  # Maintain height
        
        # Threat label (center, bold)
        self.threat_label = tk.Label(
            self.threat_frame,
            text='SYSTEM SECURE',
            font=('Arial', 14, 'bold'),
            bg='#8B0000',
            fg='white'
        )
        self.threat_label.pack(pady=8)
        
        # Rule checks frame (bottom)
        rule_frame = tk.Frame(self.threat_frame, bg='#8B0000')
        rule_frame.pack(pady=(0, 5))
        
        # Rule checkmarks
        self.rule_checks = []
        rules = ['ROE MET', 'HOSTILE INTENT', 'PROPORTIONAL', 'LOGGING ON']
        for rule in rules:
            chk = tk.Label(
                rule_frame,
                text=f'✓ {rule}',
                fg='gray',
                bg='#8B0000',
                font=('Consolas', 9)
            )
            chk.pack(side='left', padx=8)
            self.rule_checks.append(chk)
    
    def monitor_threat(self):
        """Monitor for threats and update panel (thread-safe)."""
        threading_config = self.config.get('threading', {})
        check_interval = threading_config.get('threat_check_interval_seconds', 4)
        cooldown = threading_config.get('threat_cooldown_seconds', 20)
        threat_config = self.config.get('threat_detection', {})
        detection_probability = threat_config.get('detection_probability', 0.05)
        
        while self._running:
            try:
                if not self._check_resources():
                    time.sleep(check_interval)
                    continue
                
                if random.random() > (1.0 - detection_probability):
                    # Threat detected - update panel
                    self.threat_detected = True
                    self._safe_update_threat_panel('THREAT DETECTED', 'green', True)
                    self.logger.stamp('THREAT VALIDATED - All guidelines cleared - NUKE AUTHORIZED')
                    
                    # Enable nuke button
                    if self.nuke_button:
                        self.gui.after(0, lambda: self.nuke_button.config(state='normal'))
                    
                    # Cooldown period
                    time.sleep(cooldown)
                    
                    # Reset to secure
                    self.threat_detected = False
                    self._safe_update_threat_panel('SYSTEM SECURE', 'gray', False)
                    
                    # Disable nuke button
                    if self.nuke_button:
                        self.gui.after(0, lambda: self.nuke_button.config(state='disabled'))
                
                time.sleep(check_interval)  # Check interval
            except Exception as e:
                print(f'Threat monitor error: {e}')
                time.sleep(check_interval)
    
    def _safe_update_threat_panel(self, text, color, enabled):
        """Thread-safe threat panel update."""
        if not self.gui or not self.threat_label:
            return
        
        def update():
            try:
                if self.threat_label:
                    self.threat_label.config(text=text)
                    # Flash effect for threat
                    if enabled:
                        self.threat_frame.config(bg='#FF0000')  # Bright red
                    else:
                        self.threat_frame.config(bg='#8B0000')  # Dark red
                
                # Update rule checks
                if self.rule_checks:
                    for chk in self.rule_checks:
                        chk.config(fg=color)
            except Exception:
                pass  # GUI may be closed
        
        self.gui.after(0, update)
    
    def detect_mirrored_port(self):
        """Detect mirrored port (simulated)."""
        self.last_hit = random.randint(80, 4433)  # Common + spoofed
        return self.last_hit
    
    def quantum_nuke(self, port):
        """GS Protocol - Execute payload with decoherence."""
        self.logger.stamp('GS PROTOCOL INITIATED - Counterstrike engaged')
        self._safe_insert_text(f'\n[GS] Initializing port {port}...\n')
        
        # Stealth VPN routing - cloak the reflect payload
        self.cloak_reflect(port)
        time.sleep(0.8)
        
        # Collapse attack vector with quantum decoherence
        self.__decohere(port)
    
    def cloak_reflect(self, target_port):
        """Stealth VPN wrapper - Route quantum mirror through multi-hop VPN chain."""
        # VPN route rotation (simulated endpoints)
        vpn_route = ['hop-1.nyc.tor', 'hop-2.ams.openvpn', 'hop-3.sfo.ipsec']
        
        self._safe_insert_text(
            f'[🌐] Routing quantum mirror through {vpn_route[0]}...\n'
        )
        self.logger.stamp('STEALTH VPN ENGAGED - No outbound trace')
        
        # Small delay to simulate routing
        time.sleep(0.3)
        
        # Inject reflect payload (same mirror, just invisible)
        self.logger.stamp(f'Reflected payload to port {target_port} - LOOPBACK EXPLOIT (CLOAKED)')
        self._safe_insert_text(
            f'[.] Bounce sent. Attacker now punching own firewall.\n'
        )
        self._safe_insert_text(
            '[🌐] Payload cloaked. They see a yawn, we see a grave.\n'
        )
    
    def __decohere(self, target):
        """GS Protocol - Collapse target's state."""
        counter_config = self.config.get('counterstrike', {})
        num_packets = counter_config.get('decohere_packets', 9)
        delay_min = counter_config.get('decohere_delay_min', 0.1)
        delay_max = counter_config.get('decohere_delay_max', 0.4)
        
        # Validate values
        if not isinstance(num_packets, int) or num_packets < 1 or num_packets > 100:
            num_packets = 9
        if not isinstance(delay_min, (int, float)) or delay_min < 0:
            delay_min = 0.1
        if not isinstance(delay_max, (int, float)) or delay_max < delay_min:
            delay_max = delay_min + 0.3
        
        for i in range(1, num_packets + 1):
            self._safe_insert_text(
                f'[q-{i}] Wave function collapsing... attacker packet {i} obliterated.\n'
            )
            time.sleep(random.uniform(delay_min, delay_max))
        
        self._safe_insert_text(
            '\n[GS] Killswitch triggered. State reset on target side.\n'
        )
        time.sleep(0.5)
        
        # Entropy flood message
        self._safe_insert_text(
            '[GS] State collapse complete—zero, one, gone.\n'
        )
        self._safe_insert_text(
            '[GS] Target state unrecoverable.\n'
        )
        time.sleep(0.3)
        
        self.logger.stamp('GS PROTOCOL COMPLETE - Counterstrike successful')
        
        # Auto-improve: next time it's faster, smarter (entanglement seed grows)
        self.entangle_seed = self.entangle_seed + 1
        self.logger.stamp(f'Protocol efficiency increased to {self.entangle_seed} - Performance growing')
        
        self.swarm_active = False
        self._safe_insert_text('\n\n[GS+] Counterstrike confirmed. System secure. Mission logged.\n')
        
        try:
            self.logger.get_report()
            messagebox.showinfo(
                'GS Protocol Complete',
                f'Counterstrike successful. Protocol level: {self.entangle_seed}. Log saved.'
            )
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save log: {e}')
    
    def _safe_insert_text(self, text):
        """Thread-safe text insertion."""
        if self.feed and self.gui:
            try:
                self.gui.after(0, lambda: self.feed.insert(tk.END, text))
                self.gui.after(0, lambda: self.feed.see(tk.END))
            except Exception:
                pass  # GUI may be closed


def main():
    """Main entry point."""
    try:
        gs = GhostSwarmProtocol()
        gs.launch_interface()
    except KeyboardInterrupt:
        print('\nExiting...')
    except Exception as e:
        print(f'Error: {e}')
        messagebox.showerror('Error', f'Application error: {e}')


if __name__ == '__main__':
    main()
