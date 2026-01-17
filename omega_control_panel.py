#!/usr/bin/env python3
"""
Omega Control Panel
===================
Comprehensive control panel dashboard with real-time monitoring and control.
Layout:
- Red section: Main status/control area
- Yellow section: Notifications, temperature pie chart, fan speed & RGB toggles
- Green section: Integrated systems, CPU info, temperature, processing power
- Blue section: Processes needing improvement (percentage levels)
- Orange section: Optional learning/processes (daily scan updates)
"""

import os
import sys
import time
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import threading

# Visualization
try:
    import matplotlib
    # Try multiple backends for compatibility
    backends = ['TkAgg', 'Qt5Agg', 'Qt4Agg']
    backend_set = False
    for backend in backends:
        try:
            matplotlib.use(backend, force=True)
            backend_set = True
            break
        except Exception:
            # Backend not available, try next one
            continue
    if not backend_set:
        matplotlib.use('TkAgg')  # Fallback to default
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.animation import FuncAnimation
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Control panel will use text mode.")

# Hardware and system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from omega_comprehensive_hardware import get_hardware_controller
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

try:
    from omega_developer_integrations import get_integration_manager
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

# Cache for fast loading
try:
    from omega_control_panel_cache import ControlPanelCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

@dataclass
class Notification:
    """Notification message"""
    message: str
    level: str  # 'info', 'warning', 'error', 'success'
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class IntegratedSystem:
    """Integrated system information"""
    name: str
    status: str  # 'active', 'inactive', 'error'
    cpu_usage: float  # Percentage
    temperature: float  # Celsius
    processing_power: float  # Percentage
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class ProcessImprovement:
    """Process that needs improvement"""
    name: str
    current_percentage: float
    target_percentage: float
    priority: str  # 'high', 'medium', 'low'
    description: str

@dataclass
class OptionalProcess:
    """Optional learning/process"""
    name: str
    description: str
    usefulness_score: float  # 0-100
    category: str
    last_scanned: datetime = field(default_factory=datetime.now)

class ControlPanel:
    """Omega Control Panel"""
    
    def __init__(self, use_gradual_loading: bool = True):
        self.running = False
        self.update_interval = 2.0  # Update every 2 seconds
        
        # GPU Load Balancer for optimal resource distribution
        try:
            from omega_gpu_load_balancer import get_load_balancer
            self.load_balancer = get_load_balancer()
            self.load_balancer.start_monitoring(interval=2.0)
            print("[Control Panel] GPU Load Balancer initialized")
        except Exception as e:
            print(f"[Control Panel] Load Balancer not available: {e}")
            self.load_balancer = None
        
        # Resource manager for CPU/GPU/RAM optimization
        try:
            from omega_resource_manager import get_resource_manager, GradualLoader
            self.resource_manager = get_resource_manager()
            self.gradual_loader = GradualLoader(self.resource_manager) if use_gradual_loading else None
            self.use_gpu = self.resource_manager.can_use_gpu()
            print(f"[Resource Manager] Performance profile: {self.resource_manager.performance_profile}")
            if self.use_gpu:
                print(f"[Resource Manager] GPU available: {self.resource_manager.gpu_name}")
        except (ImportError, Exception) as e:
            print(f"[Resource Manager] Not available: {e}")
            self.resource_manager = None
            self.gradual_loader = None
            self.use_gpu = False
            self.gradual_loader = None
            self.use_gpu = False
        
        # Cache for fast loading
        self.cache = None
        if CACHE_AVAILABLE:
            self.cache = ControlPanelCache()
            cached_data = self.cache.get_cached_data()
            if cached_data:
                print("[Cache] Loading last known data for fast startup...")
        
        # Hardware controller
        self.hw_controller = None
        if HARDWARE_AVAILABLE:
            try:
                self.hw_controller = get_hardware_controller()
            except Exception as e:
                # Hardware controller not available - continue without it
                pass
        
        # Developer integrations
        self.integration_manager = None
        if INTEGRATION_AVAILABLE:
            try:
                from omega_developer_integrations import get_integration_manager
                self.integration_manager = get_integration_manager()
            except Exception as e:
                # Integration manager not available - continue without it
                pass
        
        # Notifications (yellow section)
        self.notifications: deque = deque(maxlen=20)
        
        # Integrated systems (green section)
        self.integrated_systems: List[IntegratedSystem] = []
        self._update_integrated_systems()
        
        # Process improvements (blue section)
        self.process_improvements: List[ProcessImprovement] = []
        self._scan_process_improvements()
        
        # Optional processes (orange section)
        self.optional_processes: List[OptionalProcess] = []
        self.last_optional_scan = None
        self._scan_optional_processes()
        
        # Fan speed and RGB state
        self.fan_speed_percentage = 50
        self.rgb_enabled = True
        self.rgb_color = "#FFD700"  # Gold
        
        # Daily scan scheduler
        self.daily_scan_thread = None
        self._start_daily_scan_scheduler()
        
        # Matplotlib figure
        self.fig = None
        self.ax_red = None
        self.ax_yellow = None
        self.ax_green = None
        self.ax_blue = None
        self.ax_orange = None
        self.ax_files = None  # File list section (left column)
        self.ax_oip = None  # OIP section (Omega Introduction Panel)
        
        # Important files to display (always need updates)
        self.important_files = [
            'omega_control_panel.py',
            'omega_operational_startup.py',
            'omega_relationship_system.py',
            'omega_full_brain.py',
            'hands_free_omega.py',
            'omega_comprehensive_hardware.py',
            'omega_developer_integrations.py',
            'omega_api_keys_enhanced.py'
        ]
        
        # Audio monitoring for OIP visual effects
        self.current_audio_file = None
        self.audio_waveform = None
        self.audio_position = 0
        self.speaking = False
        
        # Audio analysis library
        try:
            import librosa
            self.librosa_available = True
        except ImportError:
            self.librosa_available = False
        
        # KITT Scanner integration (load gradually)
        self.scanner_integration = None
        self.scanner_available = False
        if self.gradual_loader:
            # Will be loaded gradually during GUI creation
            pass
        else:
            # Immediate load
            try:
                from omega_scanner_integration import OmegaScannerIntegration
                self.scanner_integration = OmegaScannerIntegration()
                self.scanner_available = True
            except ImportError:
                self.scanner_integration = None
                self.scanner_available = False
        
        # Control buttons state
        self.push_to_talk_active = False
        self.muted = False
        self.volume_level = 0.8  # 0.0 to 1.0
        
    def _update_integrated_systems(self):
        """Update list of integrated systems"""
        self.integrated_systems = []
        
        # Get CPU info
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_temp = self._get_cpu_temperature()
            system = IntegratedSystem(
                name="CPU (Local System)",
                status="active",
                cpu_usage=cpu_percent,
                temperature=cpu_temp or 0.0,
                processing_power=cpu_percent
            )
            self.integrated_systems.append(system)
        
        # Get integrated developer tools
        if self.integration_manager:
            try:
                for tool_name, tool in self.integration_manager.tools.items():
                    status = "active" if tool.status.value == "complete" else "inactive"
                    # Estimate CPU usage (placeholder - would need actual monitoring)
                    cpu_usage = 0.0
                    if status == "active":
                        cpu_usage = 5.0  # Placeholder
                    
                    system = IntegratedSystem(
                        name=tool.name,
                        status=status,
                        cpu_usage=cpu_usage,
                        temperature=0.0,  # Not applicable for cloud services
                        processing_power=cpu_usage
                    )
                    self.integrated_systems.append(system)
            except Exception as e:
                # Integration error - continue without this system
                pass
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature"""
        if not self.hw_controller:
            return None
        
        try:
            temps = self.hw_controller.temperature.get_all_temperatures()
            return temps.get("CPU", None)
        except Exception:
            # Temperature reading failed - return None
            return None
    
    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage percentage"""
        if self.resource_manager and self.use_gpu:
            try:
                gpu_info = self.resource_manager.get_gpu_usage()
                if gpu_info and 'memory_total_gb' in gpu_info:
                    # Calculate GPU memory usage percentage
                    if gpu_info['memory_total_gb'] > 0:
                        usage = (gpu_info['memory_allocated_gb'] / gpu_info['memory_total_gb']) * 100
                        return min(usage, 100.0)
            except Exception:
                pass
        
        # Try nvidia-smi as fallback
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return float(result.stdout.strip().split('\n')[0])
        except Exception:
            pass
        
        return None
    
    def _get_gpu_temperature(self) -> Optional[float]:
        """Get GPU temperature"""
        if not self.hw_controller:
            return None
        
        try:
            temps = self.hw_controller.temperature.get_all_temperatures()
            return temps.get("GPU", None)
        except Exception:
            # Try nvidia-smi as fallback
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    return float(result.stdout.strip().split('\n')[0])
            except Exception:
                pass
            return None
    
    def _get_ram_usage(self) -> float:
        """Get RAM usage percentage"""
        if PSUTIL_AVAILABLE:
            return psutil.virtual_memory().percent
        return 0.0
    
    def _get_ram_temperature(self) -> Optional[float]:
        """Get RAM temperature (if available)"""
        if not self.hw_controller:
            return None
        
        try:
            temps = self.hw_controller.temperature.get_all_temperatures()
            return temps.get("RAM", temps.get("Memory", None))
        except Exception:
            return None
    
    def _scan_process_improvements(self):
        """Scan for processes that need improvement"""
        self.process_improvements = []
        
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 80:
                self.process_improvements.append(ProcessImprovement(
                    name="CPU Usage",
                    current_percentage=cpu_percent,
                    target_percentage=70.0,
                    priority="high",
                    description="CPU usage is high. Consider closing unnecessary processes."
                ))
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent > 80:
                self.process_improvements.append(ProcessImprovement(
                    name="Memory Usage",
                    current_percentage=memory_percent,
                    target_percentage=70.0,
                    priority="high",
                    description="Memory usage is high. Consider freeing up memory."
                ))
            
            # Check disk usage
            disk_path = os.path.splitdrive(os.getcwd())[0] + os.sep if os.name == 'nt' else '/'
            disk = psutil.disk_usage(disk_path)
            disk_percent = disk.percent
            if disk_percent > 85:
                self.process_improvements.append(ProcessImprovement(
                    name="Disk Usage",
                    current_percentage=disk_percent,
                    target_percentage=75.0,
                    priority="medium",
                    description="Disk space is running low. Consider cleaning up files."
                ))
            
            # Check temperature
            cpu_temp = self._get_cpu_temperature()
            if cpu_temp and cpu_temp > 70:
                self.process_improvements.append(ProcessImprovement(
                    name="CPU Temperature",
                    current_percentage=cpu_temp,
                    target_percentage=60.0,
                    priority="high",
                    description="CPU temperature is high. Check cooling system."
                ))
        except Exception as e:
            self.add_notification(f"Error scanning process improvements: {e}", "error")
    
    def _scan_optional_processes(self):
        """Scan for optional learning/processes (daily scan)"""
        self.optional_processes = []
        
        # List of optional improvements
        optional_list = [
            OptionalProcess(
                name="Adaptive Confidence Thresholds",
                description="Dynamically adjust confidence thresholds based on audio quality",
                usefulness_score=95.0,
                category="Audio Processing"
            ),
            OptionalProcess(
                name="Audio Quality Monitoring",
                description="Real-time audio quality monitoring and feedback",
                usefulness_score=90.0,
                category="Audio Processing"
            ),
            OptionalProcess(
                name="Performance Monitoring Dashboard",
                description="Track and visualize performance metrics over time",
                usefulness_score=85.0,
                category="Monitoring"
            ),
            OptionalProcess(
                name="Code Optimization Scanner",
                description="Automated code optimization and improvement suggestions",
                usefulness_score=80.0,
                category="Development"
            ),
            OptionalProcess(
                name="Enhanced Web Scraping",
                description="Advanced web scraping with rate limiting and concurrent scraping",
                usefulness_score=75.0,
                category="Research"
            ),
            OptionalProcess(
                name="Quantum-Level Research",
                description="Deep, multi-source, cross-referenced research capabilities",
                usefulness_score=90.0,
                category="Research"
            ),
        ]
        
        self.optional_processes = optional_list
        self.last_optional_scan = datetime.now()
    
    def _start_daily_scan_scheduler(self):
        """Start daily scan scheduler for optional processes"""
        def daily_scan_worker():
            while self.running:
                time.sleep(3600)  # Check every hour
                now = datetime.now()
                # Run scan at midnight
                if now.hour == 0 and now.minute < 5:
                    if not self.last_optional_scan or (now - self.last_optional_scan).days >= 1:
                        self._scan_optional_processes()
                        self.add_notification("Daily optional processes scan completed", "info")
        
        self.daily_scan_thread = threading.Thread(target=daily_scan_worker, daemon=True)
        self.daily_scan_thread.start()
    
    def add_notification(self, message: str, level: str = "info"):
        """Add a notification"""
        notification = Notification(message=message, level=level)
        self.notifications.append(notification)
    
    def set_fan_speed(self, percentage: int):
        """Set fan speed percentage"""
        self.fan_speed_percentage = max(0, min(100, percentage))
        if self.hw_controller:
            try:
                # Set all fans to the same percentage
                for fan in self.hw_controller.fans.fans:
                    self.hw_controller.fans.set_fan_percentage(fan["fan_id"], self.fan_speed_percentage)
                self.add_notification(f"Fan speed set to {self.fan_speed_percentage}%", "success")
            except Exception as e:
                self.add_notification(f"Error setting fan speed: {e}", "error")
    
    def set_rgb_color(self, color: str):
        """Set RGB color"""
        self.rgb_color = color
        if self.hw_controller:
            try:
                self.hw_controller.set_rgb_color(hex_color=color)
                self.add_notification(f"RGB color set to {color}", "success")
            except Exception as e:
                self.add_notification(f"Error setting RGB color: {e}", "error")
    
    def set_rgb_enabled(self, enabled: bool):
        """Set RGB enabled state"""
        self.rgb_enabled = enabled
        if self.hw_controller:
            try:
                if enabled:
                    self.hw_controller.set_rgb_color(hex_color=self.rgb_color)
                    self.add_notification("RGB lighting enabled", "success")
                else:
                    self.hw_controller.rgb.disable_rgb()
                    self.add_notification("RGB lighting disabled", "info")
            except Exception as e:
                self.add_notification(f"Error setting RGB: {e}", "error")
    
    def toggle_rgb(self):
        """Toggle RGB lighting"""
        self.set_rgb_enabled(not self.rgb_enabled)
    
    def _create_text_panel(self):
        """Create text-based control panel (fallback)"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("OMEGA CONTROL PANEL")
        print("=" * 80)
        print()
        
        # Red section - Main status
        print("[RED SECTION] Main Status")
        print("-" * 80)
        print(f"Status: {'RUNNING' if self.running else 'STOPPED'}")
        print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Yellow section - Notifications and Temperature
        print("[YELLOW SECTION] Notifications & Temperature")
        print("-" * 80)
        cpu_temp = self._get_cpu_temperature()
        if cpu_temp:
            print(f"CPU Temperature: {cpu_temp:.1f}°C")
        print(f"Fan Speed: {self.fan_speed_percentage}%")
        print(f"RGB: {'ON' if self.rgb_enabled else 'OFF'} ({self.rgb_color})")
        print("\nRecent Notifications:")
        for notif in list(self.notifications)[-5:]:
            print(f"  [{notif.level.upper()}] {notif.message}")
        print()
        
        # Green section - Integrated Systems
        print("[GREEN SECTION] Integrated Systems")
        print("-" * 80)
        for system in self.integrated_systems:
            print(f"{system.name}: {system.status.upper()}")
            print(f"  CPU: {system.cpu_usage:.1f}% | Temp: {system.temperature:.1f}°C | Power: {system.processing_power:.1f}%")
        print()
        
        # Blue section - Process Improvements
        print("[BLUE SECTION] Process Improvements Needed")
        print("-" * 80)
        for proc in self.process_improvements:
            print(f"{proc.name}: {proc.current_percentage:.1f}% (Target: {proc.target_percentage:.1f}%) [{proc.priority.upper()}]")
            print(f"  {proc.description}")
        print()
        
        # Orange section - Optional Processes
        print("[ORANGE SECTION] Optional Learning/Processes")
        print("-" * 80)
        for opt in self.optional_processes[:5]:
            print(f"{opt.name}: {opt.usefulness_score:.0f}% useful [{opt.category}]")
            print(f"  {opt.description}")
        print()
        
        print("=" * 80)
        print("Press Ctrl+C to exit")
    
    def _create_gui_panel(self):
        """Create matplotlib GUI control panel"""
        if not MATPLOTLIB_AVAILABLE:
            self._create_text_panel()
            return
        
        # Create figure with grid layout (3 rows, 4 cols)
        self.fig = plt.figure(figsize=(18, 11))
        self.fig.suptitle('OMEGA CONTROL PANEL', fontsize=18, fontweight='bold', color='#1a1a1a')
        gs = GridSpec(3, 4, figure=self.fig, hspace=0.35, wspace=0.35, width_ratios=[1.0, 2.2, 1.1, 2.2])
        
        # File list section (left column, spans all rows)
        self.ax_files = self.fig.add_subplot(gs[:, 0])
        self.ax_files.set_facecolor('#F0F0F0')
        self.ax_files.set_title('Important Files', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_files.axis('off')
        
        # OIP section (Omega Introduction Panel - white/grey area, top of column 2)
        self.ax_oip = self.fig.add_subplot(gs[0, 1])
        self.ax_oip.set_facecolor('#FAFAFA')
        self.ax_oip.set_title('Omega Introduction Panel', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_oip.axis('off')
        
        # Red section (top-middle, column 2, row 0, now shifted)
        self.ax_red = self.fig.add_subplot(gs[0, 2])
        self.ax_red.set_facecolor('#FFE5E5')
        self.ax_red.set_title('System Status', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_red.axis('off')
        
        # Yellow section (top-right)
        self.ax_yellow = self.fig.add_subplot(gs[0, 3])
        self.ax_yellow.set_facecolor('#FFF9E5')
        self.ax_yellow.set_title('Temperature & Controls', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        
        # Green section (middle row, spans columns 1-3)
        self.ax_green = self.fig.add_subplot(gs[1, 1:4])
        self.ax_green.set_facecolor('#E5FFE5')
        self.ax_green.set_title('Integrated Systems - CPU Usage & Processing Power', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        
        # Blue section (bottom-left, column 1)
        self.ax_blue = self.fig.add_subplot(gs[2, 1])
        self.ax_blue.set_facecolor('#E5E5FF')
        self.ax_blue.set_title('Process Improvements Needed', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_blue.axis('off')
        
        # Orange section (bottom-right, spans columns 2-3)
        self.ax_orange = self.fig.add_subplot(gs[2, 2:4])
        self.ax_orange.set_facecolor('#FFF0E5')
        self.ax_orange.set_title('Optional Learning/Processes (Daily Scan)', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_orange.axis('off')
        
        # Animation - FuncAnimation will handle updates automatically
        self.ani = FuncAnimation(self.fig, self._update_gui, interval=int(self.update_interval * 1000), blit=False)
        
        # Note: Window will be shown by run() method using plt.show(block=True)
        # FuncAnimation doesn't need plt.ion() - it works with block=True
        # plt.ion() can interfere with plt.show(block=True) blocking properly
        
        # Create control buttons (after window is shown)
        # Use gradual loading if available
        if self.gradual_loader:
            def load_buttons():
                self._create_control_buttons()
            self.gradual_loader.load_component("control_buttons", load_buttons)
        else:
            self._create_control_buttons()
    
    def _create_control_buttons(self):
        """Create control buttons in the three bottom sections"""
        from matplotlib.widgets import Button
        
        if not self.fig:
            return
        
        fig = self.fig
        
        # Push to Talk button in yellow section (Notifications - top-right)
        bbox_yellow = self.ax_yellow.get_position()
        ax_ptt = fig.add_axes([bbox_yellow.x0 + 0.05 * bbox_yellow.width,
                               bbox_yellow.y0 + 0.05 * bbox_yellow.height,
                               0.4 * bbox_yellow.width, 0.35 * bbox_yellow.height])
        self.button_ptt = Button(ax_ptt, 'Push to\nTalk', color='#4CAF50', hovercolor='#45a049')
        self.push_to_talk_active = False
        
        def on_ptt_press(event):
            self.push_to_talk_active = True
            self.button_ptt.color = '#66BB6A'
            fig.canvas.draw()
            print("[Control Panel] Push to Talk: ON")
        
        def on_ptt_release(event):
            self.push_to_talk_active = False
            self.button_ptt.color = '#4CAF50'
            fig.canvas.draw()
            print("[Control Panel] Push to Talk: OFF")
        
        self.button_ptt.on_clicked(lambda event: None)
        self.button_ptt.on_pressed = on_ptt_press
        self.button_ptt.on_released = on_ptt_release
        
        # Enter button in blue section (Process Improvements - bottom-left)
        bbox_blue = self.ax_blue.get_position()
        ax_enter = fig.add_axes([bbox_blue.x0 + 0.25 * bbox_blue.width,
                                 bbox_blue.y0 + 0.05 * bbox_blue.height,
                                 0.5 * bbox_blue.width, 0.35 * bbox_blue.height])
        self.button_enter = Button(ax_enter, 'Enter', color='#2196F3', hovercolor='#1976D2')
        
        def on_enter_click(event):
            print("[Control Panel] Enter button pressed")
            # Enter button action can be implemented here
        
        self.button_enter.on_clicked(on_enter_click)
        
        # Mute button in orange section (Optional Processes - bottom-right)
        bbox_orange = self.ax_orange.get_position()
        ax_mute = fig.add_axes([bbox_orange.x0 + 0.05 * bbox_orange.width,
                                bbox_orange.y0 + 0.05 * bbox_orange.height,
                                0.35 * bbox_orange.width, 0.35 * bbox_orange.height])
        self.button_mute = Button(ax_mute, 'Mute', color='#FF9800', hovercolor='#F57C00')
        self.muted = False
        
        def on_mute_click(event):
            self.muted = not self.muted
            if self.muted:
                self.button_mute.color = '#F44336'
                self.button_mute.label.set_text('Unmute')
                print("[Control Panel] Muted")
            else:
                self.button_mute.color = '#FF9800'
                self.button_mute.label.set_text('Mute')
                print("[Control Panel] Unmuted")
            fig.canvas.draw()
        
        self.button_mute.on_clicked(on_mute_click)
        
        # Volume control in orange section (next to mute)
        self.volume_level = 0.8
        
        # Volume label
        ax_vol_label = fig.add_axes([bbox_orange.x0 + 0.45 * bbox_orange.width,
                                     bbox_orange.y0 + 0.15 * bbox_orange.height,
                                     0.15 * bbox_orange.width, 0.15 * bbox_orange.height])
        ax_vol_label.axis('off')
        self.vol_label_text = ax_vol_label.text(0.5, 0.5, 'Vol', ha='center', va='center',
                                                fontsize=8, fontweight='bold')
        
        # Volume display
        ax_vol_display = fig.add_axes([bbox_orange.x0 + 0.45 * bbox_orange.width,
                                       bbox_orange.y0 + 0.05 * bbox_orange.height,
                                       0.15 * bbox_orange.width, 0.1 * bbox_orange.height])
        ax_vol_display.axis('off')
        self.vol_display_text = ax_vol_display.text(0.5, 0.5, f'{int(self.volume_level * 100)}%',
                                                    ha='center', va='center',
                                                    fontsize=9, fontweight='bold')
        
        # Volume down button
        ax_vol_down = fig.add_axes([bbox_orange.x0 + 0.62 * bbox_orange.width,
                                    bbox_orange.y0 + 0.1 * bbox_orange.height,
                                    0.12 * bbox_orange.width, 0.25 * bbox_orange.height])
        self.button_vol_down = Button(ax_vol_down, '−', color='#9E9E9E', hovercolor='#757575')
        
        # Volume up button
        ax_vol_up = fig.add_axes([bbox_orange.x0 + 0.75 * bbox_orange.width,
                                  bbox_orange.y0 + 0.1 * bbox_orange.height,
                                  0.12 * bbox_orange.width, 0.25 * bbox_orange.height])
        self.button_vol_up = Button(ax_vol_up, '+', color='#9E9E9E', hovercolor='#757575')
        
        def on_vol_down(event):
            self.volume_level = max(0.0, self.volume_level - 0.1)
            self.vol_display_text.set_text(f'{int(self.volume_level * 100)}%')
            print(f"[Control Panel] Volume: {int(self.volume_level * 100)}%")
            fig.canvas.draw()
        
        def on_vol_up(event):
            self.volume_level = min(1.0, self.volume_level + 0.1)
            self.vol_display_text.set_text(f'{int(self.volume_level * 100)}%')
            print(f"[Control Panel] Volume: {int(self.volume_level * 100)}%")
            fig.canvas.draw()
        
        self.button_vol_down.on_clicked(on_vol_down)
        self.button_vol_up.on_clicked(on_vol_up)
    
    def _update_gui(self, frame):
        """Update GUI panels"""
        # Update data
        self._update_integrated_systems()
        self._scan_process_improvements()
        
        # File list section - Important files only
        self.ax_files.clear()
        self.ax_files.set_facecolor('#F0F0F0')
        self.ax_files.set_title('Important Files', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_files.axis('off')
        
        y_pos = 0.95
        base_dir = Path.cwd()
        for filename in self.important_files:
            filepath = base_dir / filename
            exists = filepath.exists()
            color = '#27AE60' if exists else '#E74C3C'
            status = '✓' if exists else '✗'
            bg_color = '#E8F5E9' if exists else '#FFEBEE'
            
            # Truncate long filenames
            display_name = filename if len(filename) <= 28 else filename[:25] + '...'
            
            # Add subtle background box for each file
            self.ax_files.add_patch(mpatches.Rectangle((0.02, y_pos - 0.08), 0.96, 0.09,
                                                       facecolor=bg_color, edgecolor=color,
                                                       linewidth=1.5, alpha=0.6,
                                                       transform=self.ax_files.transAxes))
            
            self.ax_files.text(0.05, y_pos - 0.04, f'{status} {display_name}', 
                              fontsize=9, color=color, transform=self.ax_files.transAxes,
                              family='monospace', verticalalignment='top', fontweight='bold')
            y_pos -= 0.12
        
        # OIP section - Omega Introduction Panel with KITT scanner effect
        self.ax_oip.clear()
        self.ax_oip.set_facecolor('#FAFAFA')
        self.ax_oip.set_title('Omega Introduction Panel', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_oip.axis('off')
        
        # Use KITT scanner if available, otherwise fallback to waveform
        if self.scanner_available and self.scanner_integration and self.scanner_integration.scanner:
            # Update scanner with audio
            audio_files = ['response.wav', 'omega_intro.wav']
            audio_found = None
            for af in audio_files:
                audio_path = base_dir / af
                if audio_path.exists():
                    audio_found = str(audio_path)
                    break
            
            if audio_found:
                # Try to update scanner with audio file, fallback to speech detection if it fails
                try:
                    self.scanner_integration.update_scanner(
                        audio_file=audio_found,
                        audio_position=0.5  # Current position (can be improved with actual position tracking)
                    )
                except Exception:
                    # Fallback to speech detection if scanner update fails
                    self.scanner_integration.update_scanner(
                        speech_active=self.speaking,
                        audio_amplitude=0.7 if self.speaking else 0.0
                    )
            else:
                self.scanner_integration.update_scanner(
                    speech_active=self.speaking,
                    audio_amplitude=0.7 if self.speaking else 0.0
                )
            
            # Render KITT scanner to OIP
            self.scanner_integration.render_to_axes(self.ax_oip, num_bars=16)
        
        else:
            # Fallback to original waveform visualization
            self.ax_oip.set_facecolor('#FAFAFA')
            self.ax_oip.set_title('Omega Introduction Panel', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
            self.ax_oip.axis('off')
            
            # Check for audio file and display visual effects
            audio_files = ['response.wav', 'omega_intro.wav']
            audio_found = None
            for af in audio_files:
                audio_path = base_dir / af
                if audio_path.exists():
                    audio_found = audio_path
                    break
            
            if audio_found and self.librosa_available:
                try:
                    import librosa
                    import numpy as np
                    
                    # Load audio for visualization
                    audio, sr = librosa.load(str(audio_found), sr=None, duration=5.0)
                    
                    # Create waveform visualization (simplified bars for real-time effect)
                    num_bars = 24
                    chunk_size = len(audio) // num_bars
                    bars = []
                    for i in range(num_bars):
                        chunk = audio[i*chunk_size:(i+1)*chunk_size]
                        if len(chunk) > 0:
                            bar_height = np.abs(chunk).max() * 100
                            bars.append(bar_height)
                        else:
                            bars.append(0)
                    
                    # Normalize bars
                    if max(bars) > 0:
                        bars = [b / max(bars) for b in bars]
                    
                    # Draw bars (vertical equalizer style with gradient)
                    x_positions = np.linspace(0.08, 0.92, num_bars)
                    bar_width = 0.025
                    
                    for i, (x, height) in enumerate(zip(x_positions, bars)):
                        # Create gradient color based on height and position
                        color_intensity = height
                        color = plt.cm.plasma(color_intensity * 0.7 + 0.3)
                        
                        # Draw bar with rounded effect
                        bar_height_scaled = height * 0.75
                        self.ax_oip.bar(x, bar_height_scaled, width=bar_width, bottom=0.15, 
                                       color=color, alpha=0.85, edgecolor='white', linewidth=0.5)
                    
                    # Add pulsing indicator
                    pulse_alpha = 0.5 + 0.5 * np.sin(frame * 0.2)
                    self.ax_oip.text(0.5, 0.05, '● Audio Active', ha='center', va='bottom',
                                    fontsize=10, color='#27AE60', fontweight='bold',
                                    alpha=pulse_alpha, transform=self.ax_oip.transAxes)
                except Exception as e:
                    self.ax_oip.text(0.5, 0.5, 'OIP Ready\n(Visual effects active)', 
                                    ha='center', va='center', fontsize=11,
                                    bbox=dict(boxstyle='round', facecolor='#E3F2FD', alpha=0.9, edgecolor='#2196F3', linewidth=2),
                                    color='#1976D2', fontweight='bold',
                                    transform=self.ax_oip.transAxes)
            else:
                # Default display when no audio
                self.ax_oip.text(0.5, 0.5, 'OIP Ready\n(Awaiting speech)', 
                                ha='center', va='center', fontsize=11,
                                bbox=dict(boxstyle='round', facecolor='#FFF3E0', alpha=0.9, edgecolor='#FF9800', linewidth=2),
                                color='#F57C00', fontweight='bold',
                                transform=self.ax_oip.transAxes)
        
        # Red section - Main status with color-coded CPU/GPU/RAM tiles
        self.ax_red.clear()
        self.ax_red.set_facecolor('#FFE5E5')
        self.ax_red.set_title('System Status', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_red.axis('off')
        
        # Get usage stats
        cpu_usage = psutil.cpu_percent(interval=0.1) if PSUTIL_AVAILABLE else 0.0
        gpu_usage = self._get_gpu_usage() or 0.0
        ram_usage = self._get_ram_usage()
        
        # Get temperatures
        cpu_temp = self._get_cpu_temperature() or 0.0
        gpu_temp = self._get_gpu_temperature() or 0.0
        ram_temp = self._get_ram_temperature() or 0.0
        
        # Get frame time for flashing effect
        flash_on = (frame % 30) < 15  # Flash every 30 frames
        
        # Draw CPU/GPU/RAM tiles with color-coding
        tiles = [
            ('CPU', cpu_usage, cpu_temp),
            ('GPU', gpu_usage, gpu_temp),
            ('RAM', ram_usage, ram_temp)
        ]
        
        for i, (name, usage, temp) in enumerate(tiles):
            x_pos = 0.1 + i * 0.28
            y_pos = 0.75
            
            # Determine tile color based on usage thresholds
            if usage < 60:
                tile_color = '#4CAF50'  # Green
                rim_color = '#4CAF50'
            elif usage < 70:
                tile_color = '#4CAF50'  # Green tile
                rim_color = '#FFD700'  # Yellow rim
            elif usage < 90:
                tile_color = '#FFA500'  # Orange
                rim_color = '#FFA500'
            else:
                # 90%+ - red (flashing)
                tile_color = '#FF0000' if flash_on else '#CC0000'
                rim_color = '#FF0000'
            
            # Draw tile background
            rect = mpatches.Rectangle((x_pos - 0.12, y_pos - 0.15), 0.24, 0.3,
                                     facecolor=tile_color, edgecolor=rim_color, linewidth=3,
                                     transform=self.ax_red.transAxes, alpha=0.8)
            self.ax_red.add_patch(rect)
            
            # Draw usage percentage
            usage_text = f"{name}\n{usage:.1f}%"
            self.ax_red.text(x_pos, y_pos, usage_text, fontsize=11, fontweight='bold',
                           ha='center', va='center', color='white',
                           transform=self.ax_red.transAxes,
                           bbox=dict(boxstyle='round', facecolor='black', alpha=0.3, pad=2))
            
            # Draw sweat drop icon at 90%+
            if usage >= 90:
                # Draw sweat drop (simple droplet shape)
                drop_path = mpatches.Path(
                    [(x_pos + 0.08, y_pos - 0.02),
                     (x_pos + 0.10, y_pos - 0.05),
                     (x_pos + 0.08, y_pos - 0.08),
                     (x_pos + 0.06, y_pos - 0.08)],
                    [mpatches.Path.MOVETO, mpatches.Path.LINETO, mpatches.Path.LINETO, mpatches.Path.CLOSEPOLY]
                )
                drop = mpatches.PathPatch(drop_path, facecolor='#FFFFFF', edgecolor='none',
                                         transform=self.ax_red.transAxes, alpha=0.9)
                self.ax_red.add_patch(drop)
            
            # Draw temperature dot (white -> amber -> deep red)
            temp_dot_y = y_pos - 0.22
            if temp > 0:
                if temp < 50:
                    dot_color = '#FFFFFF'  # White
                elif temp < 70:
                    dot_color = '#FFA500'  # Amber
                else:
                    dot_color = '#8B0000'  # Deep red
                
                temp_dot = mpatches.Circle((x_pos, temp_dot_y), 0.015, color=dot_color,
                                          transform=self.ax_red.transAxes)
                self.ax_red.add_patch(temp_dot)
                # Temperature label
                self.ax_red.text(x_pos, temp_dot_y - 0.04, f"{temp:.0f}°C", fontsize=8,
                               ha='center', va='top', color='black',
                               transform=self.ax_red.transAxes)
        
        # Status text at bottom
        status_text = f"Status: {'RUNNING' if self.running else 'STOPPED'} | "
        status_text += f"Update: {datetime.now().strftime('%H:%M:%S')}"
        
        status_color = '#27AE60' if self.running else '#E74C3C'
        self.ax_red.text(0.5, 0.05, status_text, fontsize=9, ha='center', va='bottom',
                         family='monospace', color=status_color, fontweight='bold',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, pad=5),
                         transform=self.ax_red.transAxes)
        
        # Yellow section - Notifications, Temperature Pie Chart, Controls
        self.ax_yellow.clear()
        self.ax_yellow.set_facecolor('#FFF9E5')
        self.ax_yellow.set_title('Temperature & Controls', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        
        # Temperature pie chart
        cpu_temp = self._get_cpu_temperature()
        if cpu_temp:
            # Create pie chart for temperature ranges
            temp_ranges = ['Normal (<50°C)', 'Warm (50-70°C)', 'Hot (>70°C)']
            if cpu_temp < 50:
                values = [100, 0, 0]
                colors = ['#00FF00', '#FFA500', '#FF0000']
            elif cpu_temp < 70:
                values = [0, 100, 0]
                colors = ['#00FF00', '#FFA500', '#FF0000']
            else:
                values = [0, 0, 100]
                colors = ['#00FF00', '#FFA500', '#FF0000']
            
            self.ax_yellow.pie(values, labels=temp_ranges, colors=colors, autopct='%1.1f%%',
                              startangle=90, radius=0.6, center=(0.5, 0.7))
            self.ax_yellow.text(0.5, 0.3, f'{cpu_temp:.1f}°C', ha='center', va='center',
                               fontsize=14, fontweight='bold')
        else:
            self.ax_yellow.text(0.5, 0.5, 'Temperature\nNot Available', ha='center', va='center',
                               fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add control info
        control_text = f"Fan: {self.fan_speed_percentage}%\n"
        control_text += f"RGB: {'ON' if self.rgb_enabled else 'OFF'}\n"
        control_text += f"Color: {self.rgb_color}"
        self.ax_yellow.text(0.5, 0.1, control_text, ha='center', va='top',
                           fontsize=9, family='monospace', fontweight='bold',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                                    edgecolor='#FFA500', linewidth=2, pad=8))
        
        # Green section - Integrated Systems
        self.ax_green.clear()
        self.ax_green.set_facecolor('#E5FFE5')
        self.ax_green.set_title('Integrated Systems - CPU Usage & Processing Power', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        
        if self.integrated_systems:
            systems = [s.name for s in self.integrated_systems]
            cpu_usages = [s.cpu_usage for s in self.integrated_systems]
            processing_powers = [s.processing_power for s in self.integrated_systems]
            temps = [s.temperature for s in self.integrated_systems]
            
            x = range(len(systems))
            width = 0.35
            
            bars1 = self.ax_green.bar([i - width/2 for i in x], cpu_usages, width, label='CPU Usage (%)', color='#4CAF50')
            bars2 = self.ax_green.bar([i + width/2 for i in x], processing_powers, width, label='Processing Power (%)', color='#2196F3')
            
            # Add temperature annotations
            for i, (sys, temp) in enumerate(zip(systems, temps)):
                if temp > 0:
                    self.ax_green.text(i, max(cpu_usages[i], processing_powers[i]) + 5,
                                      f'{temp:.1f}°C', ha='center', fontsize=8)
            
            self.ax_green.set_xlabel('Systems')
            self.ax_green.set_ylabel('Percentage (%)')
            self.ax_green.set_xticks(x)
            self.ax_green.set_xticklabels(systems, rotation=45, ha='right')
            self.ax_green.legend()
            self.ax_green.set_ylim(0, 100)
            self.ax_green.grid(True, alpha=0.3)
        else:
            self.ax_green.text(0.5, 0.5, 'No integrated systems found', ha='center', va='center',
                              fontsize=12, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Blue section - Process Improvements
        self.ax_blue.clear()
        self.ax_blue.set_facecolor('#E5E5FF')
        self.ax_blue.set_title('Process Improvements Needed', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_blue.axis('off')
        
        if self.process_improvements:
            # Calculate spacing to fit all items within visible area (0.0 to 1.0)
            # Rectangle: bottom = y_pos - 0.15, height = 0.16, top = y_pos + 0.01
            # Strategy: First item at y_pos=0.95, last item positioned so its bottom >= 0.05
            # This ensures all rectangles stay within the visible axis range
            num_items = min(5, len(self.process_improvements))
            if num_items > 1:
                # First item: y_pos = 0.95, rectangle from 0.80 to 0.96
                first_y = 0.95
                # Last item: we want rectangle bottom at 0.05, so y_pos = 0.20
                # (since rect bottom = y_pos - 0.15, we need y_pos = 0.05 + 0.15 = 0.20)
                last_y = 0.20  # Ensures last rect bottom = 0.20 - 0.15 = 0.05
                # Calculate even spacing between items
                spacing = (first_y - last_y) / (num_items - 1)
                # Verify: With 5 items, spacing = (0.95 - 0.20) / 4 = 0.1875
                # This ensures all items fit: last item rect from 0.05 to 0.21 (within bounds)
            else:
                spacing = 0.16
            
            y_pos = 0.95
            for proc in self.process_improvements[:5]:  # Show top 5
                priority_color = {'high': '#E74C3C', 'medium': '#F39C12', 'low': '#F1C40F'}.get(proc.priority, '#34495E')
                improvement_text = f"{proc.name}: {proc.current_percentage:.1f}% → {proc.target_percentage:.1f}%"
                
                # Add background box for each improvement
                # Ensure rectangle stays within visible bounds (y >= 0)
                rect_bottom = max(0.0, y_pos - 0.15)  # Safety check: never below 0
                rect_height = min(0.16, 1.0 - rect_bottom)  # Adjust height if near top
                bg_color = '#FFEBEE' if proc.priority == 'high' else '#FFF3E0' if proc.priority == 'medium' else '#FFFDE7'
                self.ax_blue.add_patch(mpatches.Rectangle((0.02, rect_bottom), 0.96, rect_height,
                                                           facecolor=bg_color, edgecolor=priority_color,
                                                           linewidth=2, alpha=0.7,
                                                           transform=self.ax_blue.transAxes))
                
                self.ax_blue.text(0.05, y_pos - 0.02, improvement_text, fontsize=9, color=priority_color,
                                 transform=self.ax_blue.transAxes, fontweight='bold')
                self.ax_blue.text(0.05, y_pos - 0.1, proc.description[:55] + "...", fontsize=8,
                                 transform=self.ax_blue.transAxes, color='#2c3e50')
                y_pos -= spacing
        else:
            self.ax_blue.text(0.5, 0.5, 'No improvements needed', ha='center', va='center',
                             fontsize=11, bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.9,
                                                   edgecolor='#27AE60', linewidth=2, pad=10),
                             color='#27AE60', fontweight='bold')
        
        # Orange section - Optional Processes
        self.ax_orange.clear()
        self.ax_orange.set_facecolor('#FFF0E5')
        self.ax_orange.set_title('Optional Learning/Processes (Daily Scan)', fontweight='bold', pad=12, fontsize=11, color='#2c3e50')
        self.ax_orange.axis('off')
        
        if self.optional_processes:
            # Sort by usefulness score
            sorted_processes = sorted(self.optional_processes, key=lambda x: x.usefulness_score, reverse=True)
            
            y_pos = 0.95
            for opt in sorted_processes[:6]:  # Show top 6
                score_color = '#27AE60' if opt.usefulness_score > 85 else '#F39C12' if opt.usefulness_score > 70 else '#3498DB'
                process_text = f"{opt.name} ({opt.usefulness_score:.0f}% useful) [{opt.category}]"
                
                # Add subtle background for each process
                bg_alpha = 0.5 if opt.usefulness_score > 85 else 0.4
                self.ax_orange.add_patch(mpatches.Rectangle((0.01, y_pos - 0.12), 0.98, 0.13,
                                                            facecolor='white', edgecolor=score_color,
                                                            linewidth=1.5, alpha=bg_alpha,
                                                            transform=self.ax_orange.transAxes))
                
                self.ax_orange.text(0.02, y_pos - 0.02, process_text, fontsize=9, color=score_color,
                                   transform=self.ax_orange.transAxes, fontweight='bold')
                self.ax_orange.text(0.02, y_pos - 0.08, opt.description[:75] + "...", fontsize=8,
                                   transform=self.ax_orange.transAxes, color='#2c3e50')
                y_pos -= 0.16
            
            # Add last scan time
            if self.last_optional_scan:
                scan_text = f"Last Scan: {self.last_optional_scan.strftime('%Y-%m-%d %H:%M')}"
                self.ax_orange.text(0.5, 0.02, scan_text, ha='center', fontsize=9, fontweight='bold',
                                   transform=self.ax_orange.transAxes,
                                   bbox=dict(boxstyle='round', facecolor='#FFF3E0', alpha=0.9,
                                            edgecolor='#FF9800', linewidth=2, pad=8),
                                   color='#F57C00')
        else:
            self.ax_orange.text(0.5, 0.5, 'No optional processes found', ha='center', va='center',
                               fontsize=11, bbox=dict(boxstyle='round', facecolor='#FFF3E0', alpha=0.9,
                                                     edgecolor='#FF9800', linewidth=2, pad=10),
                               color='#F57C00', fontweight='bold')
        
        plt.tight_layout()
    
    def run(self):
        """Run the control panel"""
        self.running = True
        
        if MATPLOTLIB_AVAILABLE:
            try:
                # Create the GUI panel (this creates FuncAnimation and shows window)
                self._create_gui_panel()
                print("[OK] GUI window created - window should be visible now")
                print("The window will stay open and remain interactive.")
                print("Close the window or press Ctrl+C to exit.")
                print()
                
                # FuncAnimation handles the updates, we just need to keep the window open
                # Using block=True keeps the window open until closed by user
                # FuncAnimation will continue updating while the window is open
                # Ensure non-interactive mode for proper blocking
                plt.ioff()  # Turn off interactive mode to ensure block=True works
                try:
                    plt.show(block=True)  # Block until window is closed - keeps UI alive
                except KeyboardInterrupt:
                    # Handle Ctrl+C during blocking show
                    self.running = False
                    plt.close('all')
            except KeyboardInterrupt:
                self.running = False
                if MATPLOTLIB_AVAILABLE:
                    plt.close('all')
            except Exception as e:
                print(f"Error running GUI panel: {e}")
                import traceback
                traceback.print_exc()
                self._create_text_panel()
        else:
            try:
                while self.running:
                    self._create_text_panel()
                    time.sleep(self.update_interval)
            except KeyboardInterrupt:
                self.running = False
    
    def stop(self):
        """Stop the control panel"""
        self.running = False
        
        # Save cache before stopping
        if self.cache:
            try:
                import psutil
                cache_data = {
                    'cpu_usage': psutil.cpu_percent(interval=0.1) if PSUTIL_AVAILABLE else 0.0,
                    'cpu_temperature': self._get_cpu_temperature() or 0.0,
                    'memory_usage': psutil.virtual_memory().percent if PSUTIL_AVAILABLE else 0.0,
                    'disk_usage': psutil.disk_usage(os.path.splitdrive(os.getcwd())[0] + os.sep if os.name == 'nt' else '/').percent if PSUTIL_AVAILABLE else 0.0,
                    'fan_speed': self.fan_speed_percentage,
                    'rgb_enabled': self.rgb_enabled,
                    'rgb_color': self.rgb_color,
                    'notifications': [{'message': n.message, 'level': n.level, 'timestamp': n.timestamp.isoformat()} for n in list(self.notifications)],
                    'integrated_systems': [{'name': s.name, 'status': s.status, 'cpu_usage': s.cpu_usage, 'temperature': s.temperature, 'processing_power': s.processing_power} for s in self.integrated_systems],
                    'process_improvements': [{'name': p.name, 'current_percentage': p.current_percentage, 'target_percentage': p.target_percentage, 'priority': p.priority, 'description': p.description} for p in self.process_improvements],
                    'optional_processes': [{'name': o.name, 'description': o.description, 'usefulness_score': o.usefulness_score, 'category': o.category} for o in self.optional_processes]
                }
                self.cache.save_cache(cache_data)
                print("[Cache] Data saved for next startup")
            except Exception as e:
                print(f"[Cache] Failed to save cache: {e}")
        
        # Stop animation if running
        if hasattr(self, 'ani') and self.ani:
            try:
                self.ani.event_source.stop()
            except Exception:
                pass
        
        # Close matplotlib figures
        if self.fig:
            plt.close('all')

def main():
    """Main function"""
    panel = ControlPanel()
    
    print("=" * 80)
    print("OMEGA CONTROL PANEL")
    print("=" * 80)
    print()
    print("Starting control panel...")
    print("Press Ctrl+C to exit")
    print()
    
    try:
        panel.run()
    except KeyboardInterrupt:
        print("\n\nShutting down control panel...")
        panel.stop()
        print("Control panel stopped.")

if __name__ == "__main__":
    main()
