#!/usr/bin/env python3
"""
Quantum Armor v1.0 - Security Simulation Tool (OPTIMIZED)
==========================================================
Tkinter-based security simulation tool with improved code quality.
Note: This is simulation/demo code - uses random values, no actual network operations.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
from pathlib import Path


class IncidentLogger:
    """Forensic & Legal Logger - Logs security events to file."""
    
    def __init__(self, log_file='defense_log.txt'):
        self.report = []
        self.log_file = Path(log_file)
    
    def stamp(self, action, threat_level='DEFENSE'):
        """Log an incident with timestamp."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.report.append(
            f'[{timestamp}] {action.upper()} - Threat Level: {threat_level} - Self-Defense Activated'
        )
    
    def get_report(self):
        """Save report to file and return status."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.report))
            return f'Report saved as {self.log_file}'
        except Exception as e:
            return f'Error saving report: {e}'


class MilitaryROE:
    """Military Rules of Engagement - Threat evaluation and authorization."""
    
    def __init__(self, logger=None):
        self.logger = logger  # Fixed: logger passed in __init__
        self.principles = {
            'self_defense': 'Inherent right - Nothing limits unit/individual defense',
            'necessity': 'Non-force alternatives exhausted?',
            'proportionality': 'Force mirrors incoming only - No escalation',
            'hostile_intent_threshold': 0.8
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


class QuantumArmor:
    """Quantum Armor Core - Main security simulation system."""
    
    def __init__(self):
        self.layers = ['Outer Shield (Windows)', 'Middle Guard', 'Core Sentinel']
        self.active_layers = {layer: True for layer in self.layers}
        self.logger = IncidentLogger()
        self.roe = MilitaryROE(logger=self.logger)  # Fixed: pass logger to ROE
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
        self.entangle_seed = 1  # Quantum entanglement seed (grows with each attack)
        self._running = True
    
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
        """Nuke Gate - Confirm quantum counterstrike authorization."""
        if messagebox.askyesno(
            'QUANTUM NUKE AUTH',
            'Launch quantum payload? Superposition breach - Irreversible entropy flood.'
        ):
            self.swarm_active = True
            self.logger.stamp('Nuke sequence: Quantum payload authorized - Last Resort Protocol')
            port = self.detect_mirrored_port()
            if port:
                threading.Thread(target=self.quantum_nuke, args=(port,), daemon=True).start()
    
    def launch_interface(self):
        """Launch Interface - Create and show GUI."""
        self.gui = tk.Tk()
        self.gui.title('Quantum Armor Control - MILITARY GRADE')
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
            text='NUKE THREAT',
            command=self.confirm_nuke,
            style='Destructive.TButton',
            state='disabled'
        )
        self.nuke_button.pack(pady=8)
        
        # Handle window close
        self.gui.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # Auto-scan every 3s
        threading.Thread(target=self.__predict_loop, daemon=True).start()
        
        # Threat monitoring
        threading.Thread(target=self.monitor_threat, daemon=True).start()
        
        self.gui.mainloop()
    
    def on_closing(self):
        """Handle window close event."""
        self._running = False
        try:
            self.logger.get_report()
        except Exception:
            pass
        if self.gui:
            self.gui.destroy()
    
    def __predict_loop(self):
        """Background loop for threat prediction."""
        while self._running:
            if not self.swarm_active:
                self.predict_threat()
            time.sleep(3)
    
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
        while self._running:
            try:
                if random.random() > 0.95:  # 5% chance - simulate detection
                    # Threat detected - update panel
                    self.threat_detected = True
                    self._safe_update_threat_panel('THREAT DETECTED', 'green', True)
                    self.logger.stamp('THREAT VALIDATED - All guidelines cleared - NUKE AUTHORIZED')
                    
                    # Enable nuke button
                    if self.nuke_button:
                        self.gui.after(0, lambda: self.nuke_button.config(state='normal'))
                    
                    # Cooldown period
                    time.sleep(20)
                    
                    # Reset to secure
                    self.threat_detected = False
                    self._safe_update_threat_panel('SYSTEM SECURE', 'gray', False)
                    
                    # Disable nuke button
                    if self.nuke_button:
                        self.gui.after(0, lambda: self.nuke_button.config(state='disabled'))
                
                time.sleep(4)  # Check interval
            except Exception as e:
                print(f'Threat monitor error: {e}')
                time.sleep(4)
    
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
        """Quantum Nuke - Execute quantum payload with decoherence."""
        self.logger.stamp('NUKE+QUANTUM INITIATED - Superposition breach engaged')
        self._safe_insert_text(f'\n[⚛] Entangling port {port}...\n')
        
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
        """Quantum decoherence - Collapse attacker's quantum state."""
        num_packets = 9  # Number of packets to decohere
        
        for i in range(1, num_packets + 1):
            self._safe_insert_text(
                f'[q-{i}] Wave function collapsing... attacker packet {i} obliterated.\n'
            )
            time.sleep(random.uniform(0.1, 0.4))
        
        self._safe_insert_text(
            '\n[⚛] Quantum killswitch triggered. Reality reset on intruder side.\n'
        )
        time.sleep(0.5)
        
        # Entropy flood message
        self._safe_insert_text(
            '[⚛] Every bit flipped like a dying qubit—zero, one, gone.\n'
        )
        self._safe_insert_text(
            '[⚛] They can\'t patch what they can\'t read.\n'
        )
        time.sleep(0.3)
        
        self.logger.stamp('QUANTUM ATTACK COMPLETE - Irreversible entropy flood')
        
        # Auto-improve: next time it's faster, smarter (entanglement seed grows)
        self.entangle_seed = self.entangle_seed + 1
        self.logger.stamp(f'Entanglement seed increased to {self.entangle_seed} - Entropy growing')
        
        self.swarm_active = False
        self._safe_insert_text('\n\n[⚛+] Quantum kill confirmed. System secure. Mission logged.\n')
        
        try:
            self.logger.get_report()
            messagebox.showinfo(
                'Quantum Kill',
                f'Threat quantum-decohered. Entanglement seed: {self.entangle_seed}. Log saved.'
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
        armor = QuantumArmor()
        armor.launch_interface()
    except KeyboardInterrupt:
        print('\nExiting...')
    except Exception as e:
        print(f'Error: {e}')
        messagebox.showerror('Error', f'Application error: {e}')


if __name__ == '__main__':
    main()
