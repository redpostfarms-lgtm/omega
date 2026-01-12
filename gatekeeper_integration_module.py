#!/usr/bin/env python3
"""
Gatekeeper Integration Module
==============================
Main integration module connecting all enhanced components.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import enhanced modules
try:
    from gatekeeper_threat_simulation import ThreatSimulator
    THREAT_SIM_AVAILABLE = True
except ImportError:
    THREAT_SIM_AVAILABLE = False
    print("Warning: Threat simulation module not available")

try:
    from gatekeeper_forensic_analysis import ForensicAnalyzer
    FORENSIC_AVAILABLE = True
except ImportError:
    FORENSIC_AVAILABLE = False
    print("Warning: Forensic analysis module not available")

try:
    from gatekeeper_enhanced_monitoring import EnhancedMonitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("Warning: Enhanced monitoring module not available")

try:
    from gatekeeper_wazuh_integration import WazuhClient, WazuhIntegration, create_wazuh_client
    WAZUH_AVAILABLE = True
except ImportError:
    WAZUH_AVAILABLE = False
    print("Warning: Wazuh integration module not available")


class GatekeeperIntegration:
    """
    Main integration class for Gatekeeper enhanced features.
    Connects threat simulation, forensic analysis, and monitoring.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize Gatekeeper integration."""
        self.config_file = config_file or Path("gatekeeper_integration_config.json")
        self.config = self._load_config()
        
        # Initialize modules
        self.threat_simulator = None
        self.forensic_analyzer = None
        self.monitor = None
        self.wazuh_integration = None
        
        if THREAT_SIM_AVAILABLE and self.config.get('enable_threat_simulation', True):
            self.threat_simulator = ThreatSimulator()
        
        if FORENSIC_AVAILABLE and self.config.get('enable_forensic_analysis', True):
            log_dir = Path(self.config.get('log_directory', 'logs'))
            self.forensic_analyzer = ForensicAnalyzer(log_dir)
        
        if MONITORING_AVAILABLE and self.config.get('enable_monitoring', True):
            metrics_file = Path(self.config.get('metrics_file', 'system_metrics.json'))
            self.monitor = EnhancedMonitor(metrics_file)
            self.monitor.load_metrics()
        
        if WAZUH_AVAILABLE and self.config.get('enable_wazuh', False):
            wazuh_config = self.config.get('wazuh', {})
            wazuh_client = create_wazuh_client(wazuh_config)
            if wazuh_client:
                self.wazuh_integration = WazuhIntegration(wazuh_client)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            'enable_threat_simulation': True,
            'enable_forensic_analysis': True,
            'enable_monitoring': True,
            'enable_wazuh': False,  # Disabled by default (requires Wazuh server)
            'log_directory': 'logs',
            'metrics_file': 'system_metrics.json',
            'auto_collect_metrics': True,
            'metrics_interval_seconds': 60,
            'wazuh': {
                'host': 'localhost',
                'port': 55000,
                'protocol': 'https',
                'username': 'wazuh-wui',
                'password': None,  # Must be set in config
                'verify_ssl': False
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        return default_config
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def run_threat_simulation(self, scenario_name: Optional[str] = None) -> Dict[str, Any]:
        """Run a threat simulation."""
        if not self.threat_simulator:
            return {'error': 'Threat simulation not available'}
        
        if scenario_name:
            try:
                result = self.threat_simulator.simulate_scenario(scenario_name)
            except ValueError as e:
                return {'error': str(e)}
        else:
            result = self.threat_simulator.run_random_simulation()
        
        return result
    
    def analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Analyze a log file for threats."""
        if not self.forensic_analyzer:
            return {'error': 'Forensic analysis not available'}
        
        return self.forensic_analyzer.analyze_log_file(log_file)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        if not self.monitor:
            return {'error': 'Monitoring not available'}
        
        metrics = self.monitor.collect_metrics()
        summary = self.monitor.get_metrics_summary()
        
        return {
            'current_metrics': {
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'memory_used_mb': metrics.memory_used_mb,
                'disk_usage_percent': metrics.disk_usage_percent,
            },
            'summary': summary
        }
    
    def get_wazuh_threats(
        self,
        min_level: int = 7,
        hours: int = 1
    ) -> Dict[str, Any]:
        """
        Get recent threats from Wazuh.
        
        Args:
            min_level: Minimum alert level (default: 7)
            hours: Hours to look back (default: 1)
            
        Returns:
            Dictionary with threats or error
        """
        if not self.wazuh_integration:
            return {'error': 'Wazuh integration not available'}
        
        threats = self.wazuh_integration.get_recent_threats(min_level=min_level, hours=hours)
        return {
            'threats': threats,
            'count': len(threats),
            'source': 'wazuh'
        }
    
    def get_wazuh_status(self) -> Dict[str, Any]:
        """Get Wazuh integration status."""
        if not self.wazuh_integration:
            return {'error': 'Wazuh integration not available'}
        
        return self.wazuh_integration.get_status_report()
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'modules': {
                'threat_simulation': {
                    'available': THREAT_SIM_AVAILABLE,
                    'enabled': self.threat_simulator is not None,
                    'scenarios': len(self.threat_simulator.scenarios) if self.threat_simulator else 0
                },
                'forensic_analysis': {
                    'available': FORENSIC_AVAILABLE,
                    'enabled': self.forensic_analyzer is not None
                },
                'monitoring': {
                    'available': MONITORING_AVAILABLE,
                    'enabled': self.monitor is not None,
                    'metrics_count': len(self.monitor.metrics_history) if self.monitor else 0
                },
                'wazuh': {
                    'available': WAZUH_AVAILABLE,
                    'enabled': self.wazuh_integration is not None,
                    'configured': self.config.get('wazuh', {}).get('password') is not None
                }
            },
            'config': self.config
        }
    
    def generate_full_report(self, output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive integration report."""
        output_file = output_file or Path("gatekeeper_integration_report.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': self.get_status(),
            'system_metrics': self.get_system_metrics() if self.monitor else None,
            'threat_simulation_stats': self.threat_simulator.get_statistics() if self.threat_simulator else None,
        }
        
        if self.forensic_analyzer:
            report['forensic_analysis'] = {
                'total_analyses': len(self.forensic_analyzer.analysis_results),
                'correlated_events': self.forensic_analyzer.correlate_events()
            }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            return f"Report saved to {output_file}"
        except Exception as e:
            return f"Error generating report: {e}"


def main():
    """Main function for testing integration."""
    print("=== Gatekeeper Integration Module Test ===\n")
    
    integration = GatekeeperIntegration()
    
    print("=== Integration Status ===")
    status = integration.get_status()
    print(f"Threat Simulation: {'✓' if status['modules']['threat_simulation']['enabled'] else '✗'}")
    print(f"Forensic Analysis: {'✓' if status['modules']['forensic_analysis']['enabled'] else '✗'}")
    print(f"Monitoring: {'✓' if status['modules']['monitoring']['enabled'] else '✗'}")
    print(f"Wazuh Integration: {'✓' if status['modules']['wazuh']['enabled'] else '✗'} (Available: {status['modules']['wazuh']['available']})")
    
    if integration.monitor:
        print("\n=== System Metrics ===")
        metrics = integration.get_system_metrics()
        current = metrics['current_metrics']
        print(f"CPU: {current['cpu_percent']:.1f}%")
        print(f"Memory: {current['memory_percent']:.1f}% ({current['memory_used_mb']:.0f} MB used)")
        if current.get('disk_usage_percent'):
            print(f"Disk: {current['disk_usage_percent']:.1f}%")
    
    if integration.threat_simulator:
        print("\n=== Threat Simulation Test ===")
        result = integration.run_threat_simulation()
        if 'error' not in result:
            print(f"Scenario: {result['scenario']['name']}")
            print(f"Events: {result['total_events']}")
            print(f"Status: {result['status']}")
    
    print("\n=== Generating Report ===")
    report_msg = integration.generate_full_report()
    print(f"  {report_msg}")
    
    print("\n✓ Integration module test complete!")


if __name__ == "__main__":
    main()
