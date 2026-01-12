#!/usr/bin/env python3
"""
Gatekeeper Threat Simulation Module (SimPy Integration)
========================================================
SimPy-based threat scenario simulation for testing and validation.
Adapted from SimPy patterns for discrete-event simulation.
"""

import random
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ThreatScenario:
    """Represents a threat scenario for simulation."""
    name: str
    threat_type: str  # 'port_scan', 'dos', 'intrusion', 'malware', 'phishing'
    intensity: float  # 0.0 to 1.0
    duration: float  # seconds
    target_port: Optional[int] = None
    source_ip: Optional[str] = None
    description: str = ""


class ThreatSimulator:
    """
    Threat simulation framework using SimPy-inspired patterns.
    Generates realistic attack scenarios for testing.
    """
    
    def __init__(self, scenario_file: Optional[Path] = None):
        """Initialize threat simulator."""
        self.scenario_file = scenario_file or Path("threat_scenarios.json")
        self.scenarios: List[ThreatScenario] = []
        self.active_simulations: Dict[str, Dict] = {}
        self.simulation_history: List[Dict] = []
        
        # Load predefined scenarios
        self._load_scenarios()
    
    def _load_scenarios(self):
        """Load threat scenarios from file or create defaults."""
        if self.scenario_file.exists():
            try:
                with open(self.scenario_file, 'r') as f:
                    data = json.load(f)
                    self.scenarios = [ThreatScenario(**s) for s in data.get('scenarios', [])]
            except Exception as e:
                print(f"Error loading scenarios: {e}")
                self._create_default_scenarios()
        else:
            self._create_default_scenarios()
    
    def _create_default_scenarios(self):
        """Create default threat scenarios."""
        default_scenarios = [
            ThreatScenario(
                name="Port Scan Attack",
                threat_type="port_scan",
                intensity=0.7,
                duration=30.0,
                target_port=443,
                source_ip="192.168.1.100",
                description="Sequential port scanning attack"
            ),
            ThreatScenario(
                name="DDoS Attack",
                threat_type="dos",
                intensity=0.9,
                duration=60.0,
                description="Distributed denial of service attack"
            ),
            ThreatScenario(
                name="Intrusion Attempt",
                threat_type="intrusion",
                intensity=0.8,
                duration=45.0,
                target_port=22,
                source_ip="10.0.0.50",
                description="Unauthorized access attempt"
            ),
            ThreatScenario(
                name="Malware Propagation",
                threat_type="malware",
                intensity=0.6,
                duration=120.0,
                description="Malware spreading attempt"
            ),
            ThreatScenario(
                name="Phishing Campaign",
                threat_type="phishing",
                intensity=0.5,
                duration=180.0,
                description="Phishing email campaign"
            ),
        ]
        self.scenarios = default_scenarios
        self._save_scenarios()
    
    def _save_scenarios(self):
        """Save scenarios to file."""
        try:
            data = {
                'scenarios': [asdict(s) for s in self.scenarios],
                'updated': datetime.now().isoformat()
            }
            with open(self.scenario_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving scenarios: {e}")
    
    def simulate_scenario(self, scenario_name: str, custom_params: Optional[Dict] = None) -> Dict:
        """
        Simulate a threat scenario.
        
        Args:
            scenario_name: Name of scenario to simulate
            custom_params: Optional custom parameters to override defaults
        
        Returns:
            Dictionary with simulation results
        """
        # Find scenario
        scenario = next((s for s in self.scenarios if s.name == scenario_name), None)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        # Apply custom parameters
        if custom_params:
            for key, value in custom_params.items():
                if hasattr(scenario, key):
                    setattr(scenario, key, value)
        
        # Create simulation record
        sim_id = f"{scenario_name}_{int(time.time())}"
        simulation = {
            'id': sim_id,
            'scenario': asdict(scenario),
            'start_time': datetime.now().isoformat(),
            'events': [],
            'status': 'running'
        }
        
        self.active_simulations[sim_id] = simulation
        
        # Simulate events (discrete-event simulation pattern)
        events = self._generate_events(scenario)
        simulation['events'] = events
        simulation['status'] = 'completed'
        simulation['end_time'] = datetime.now().isoformat()
        simulation['total_events'] = len(events)
        
        # Move to history
        self.simulation_history.append(simulation)
        del self.active_simulations[sim_id]
        
        return simulation
    
    def _generate_events(self, scenario: ThreatScenario) -> List[Dict]:
        """Generate simulation events based on scenario."""
        events = []
        event_count = int(scenario.duration * scenario.intensity * 10)  # Events per second scaled by intensity
        
        for i in range(event_count):
            event_time = (i / event_count) * scenario.duration
            
            if scenario.threat_type == "port_scan":
                event = {
                    'time': event_time,
                    'type': 'port_scan_attempt',
                    'port': (scenario.target_port or 80) + i % 100,
                    'source_ip': scenario.source_ip or f"192.168.1.{random.randint(1, 255)}",
                    'intensity': scenario.intensity,
                    'status': 'blocked' if random.random() > 0.3 else 'detected'
                }
            elif scenario.threat_type == "dos":
                event = {
                    'time': event_time,
                    'type': 'dos_attack',
                    'requests_per_second': int(scenario.intensity * 10000),
                    'source_ips': [f"10.0.0.{random.randint(1, 255)}" for _ in range(10)],
                    'intensity': scenario.intensity,
                    'status': 'mitigated' if random.random() > 0.2 else 'ongoing'
                }
            elif scenario.threat_type == "intrusion":
                event = {
                    'time': event_time,
                    'type': 'intrusion_attempt',
                    'target_port': scenario.target_port or 22,
                    'source_ip': scenario.source_ip or f"172.16.0.{random.randint(1, 255)}",
                    'method': random.choice(['brute_force', 'exploit', 'credential_stuffing']),
                    'intensity': scenario.intensity,
                    'status': 'blocked'
                }
            elif scenario.threat_type == "malware":
                event = {
                    'time': event_time,
                    'type': 'malware_detection',
                    'file_hash': f"{random.randint(100000, 999999)}",
                    'source': random.choice(['email', 'download', 'usb']),
                    'intensity': scenario.intensity,
                    'status': 'quarantined'
                }
            elif scenario.threat_type == "phishing":
                event = {
                    'time': event_time,
                    'type': 'phishing_attempt',
                    'target_email': f"user{random.randint(1, 100)}@example.com",
                    'campaign_id': f"campaign_{random.randint(1, 10)}",
                    'intensity': scenario.intensity,
                    'status': 'blocked'
                }
            else:
                event = {
                    'time': event_time,
                    'type': 'generic_threat',
                    'intensity': scenario.intensity,
                    'status': 'detected'
                }
            
            events.append(event)
        
        return events
    
    def run_random_simulation(self) -> Dict:
        """Run a random scenario simulation."""
        if not self.scenarios:
            raise ValueError("No scenarios available")
        
        scenario = random.choice(self.scenarios)
        return self.simulate_scenario(scenario.name)
    
    def get_simulation_history(self, limit: int = 100) -> List[Dict]:
        """Get recent simulation history."""
        return self.simulation_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """Get simulation statistics."""
        if not self.simulation_history:
            return {'total_simulations': 0}
        
        threat_types = {}
        for sim in self.simulation_history:
            threat_type = sim['scenario']['threat_type']
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
        
        return {
            'total_simulations': len(self.simulation_history),
            'threat_type_distribution': threat_types,
            'active_simulations': len(self.active_simulations),
            'most_recent': self.simulation_history[-1]['scenario']['name'] if self.simulation_history else None
        }


def test_simulator():
    """Test the threat simulator."""
    print("=== Gatekeeper Threat Simulation Module Test ===\n")
    
    simulator = ThreatSimulator()
    
    print(f"Loaded {len(simulator.scenarios)} scenarios:")
    for scenario in simulator.scenarios:
        print(f"  - {scenario.name} ({scenario.threat_type}, intensity: {scenario.intensity:.2f})")
    
    print("\n=== Running Random Simulation ===\n")
    result = simulator.run_random_simulation()
    
    print(f"Simulation: {result['scenario']['name']}")
    print(f"Status: {result['status']}")
    print(f"Total Events: {result['total_events']}")
    print(f"Duration: {result['scenario']['duration']:.2f}s")
    print(f"\nFirst 5 Events:")
    for event in result['events'][:5]:
        print(f"  [{event['time']:.2f}s] {event['type']} - {event.get('status', 'N/A')}")
    
    print("\n=== Statistics ===")
    stats = simulator.get_statistics()
    print(f"Total Simulations: {stats['total_simulations']}")
    print(f"Threat Types: {stats['threat_type_distribution']}")
    
    print("\n✓ Threat simulation module test complete!")


if __name__ == "__main__":
    test_simulator()
