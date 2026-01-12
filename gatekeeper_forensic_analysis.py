#!/usr/bin/env python3
"""
Gatekeeper Forensic Analysis Module (Dshell-Inspired)
======================================================
Forensic analysis tools for attack investigation.
Inspired by Dshell (US Army Research Laboratory) patterns.
"""

import json
import re
import ipaddress
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class PacketAnalysis:
    """Represents analyzed packet data."""
    timestamp: str
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: str
    packet_size: int
    flags: str
    analysis: Dict[str, Any]


@dataclass
class ConnectionFlow:
    """Represents a network connection flow."""
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: str
    packet_count: int
    bytes_sent: int
    bytes_received: int
    start_time: str
    end_time: str
    duration: float
    flags: List[str]


class ForensicAnalyzer:
    """
    Forensic analysis engine for attack investigation.
    Pattern matching and correlation for threat detection.
    """
    
    def __init__(self, log_directory: Optional[Path] = None):
        """Initialize forensic analyzer."""
        self.log_directory = log_directory or Path("logs")
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Analysis patterns
        self.threat_patterns = self._load_threat_patterns()
        self.connection_flows: Dict[str, ConnectionFlow] = {}
        self.analysis_results: List[Dict] = []
    
    def _load_threat_patterns(self) -> Dict[str, List[Dict]]:
        """Load threat detection patterns."""
        return {
            'port_scan': [
                {'pattern': r'port.*scan', 'flags': re.IGNORECASE},
                {'pattern': r'connection.*refused.*multiple', 'flags': re.IGNORECASE},
            ],
            'dos_attack': [
                {'pattern': r'high.*connection.*rate', 'flags': re.IGNORECASE},
                {'pattern': r'flood.*attack', 'flags': re.IGNORECASE},
                {'pattern': r'syn.*flood', 'flags': re.IGNORECASE},
            ],
            'intrusion': [
                {'pattern': r'unauthorized.*access', 'flags': re.IGNORECASE},
                {'pattern': r'brute.*force', 'flags': re.IGNORECASE},
                {'pattern': r'failed.*login.*multiple', 'flags': re.IGNORECASE},
            ],
            'malware': [
                {'pattern': r'malware.*detected', 'flags': re.IGNORECASE},
                {'pattern': r'virus.*signature', 'flags': re.IGNORECASE},
                {'pattern': r'suspicious.*file', 'flags': re.IGNORECASE},
            ],
            'exploit': [
                {'pattern': r'buffer.*overflow', 'flags': re.IGNORECASE},
                {'pattern': r'sql.*injection', 'flags': re.IGNORECASE},
                {'pattern': r'command.*injection', 'flags': re.IGNORECASE},
            ],
        }
    
    def analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """
        Analyze a log file for threats.
        
        Args:
            log_file: Path to log file to analyze
        
        Returns:
            Analysis results dictionary
        """
        if not log_file.exists():
            return {'error': f'Log file not found: {log_file}'}
        
        results = {
            'file': str(log_file),
            'timestamp': datetime.now().isoformat(),
            'threats_detected': [],
            'patterns_matched': [],
            'statistics': {}
        }
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Analyze each line
            for line_num, line in enumerate(lines, 1):
                line_analysis = self._analyze_line(line, line_num)
                if line_analysis['threats']:
                    results['threats_detected'].extend(line_analysis['threats'])
                if line_analysis['patterns']:
                    results['patterns_matched'].extend(line_analysis['patterns'])
            
            # Generate statistics
            results['statistics'] = {
                'total_lines': len(lines),
                'threat_count': len(results['threats_detected']),
                'pattern_matches': len(results['patterns_matched']),
                'threat_types': self._count_threat_types(results['threats_detected'])
            }
            
            self.analysis_results.append(results)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _analyze_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Analyze a single log line for threat patterns."""
        threats = []
        patterns = []
        
        for threat_type, pattern_list in self.threat_patterns.items():
            for pattern_info in pattern_list:
                pattern = pattern_info['pattern']
                flags = pattern_info.get('flags', 0)
                
                if re.search(pattern, line, flags):
                    match = {
                        'type': threat_type,
                        'line': line_num,
                        'pattern': pattern,
                        'context': line.strip()[:100]  # First 100 chars
                    }
                    threats.append(match)
                    patterns.append(match)
        
        return {'threats': threats, 'patterns': patterns}
    
    def _count_threat_types(self, threats: List[Dict]) -> Dict[str, int]:
        """Count threat types in detected threats."""
        counts = defaultdict(int)
        for threat in threats:
            counts[threat['type']] += 1
        return dict(counts)
    
    def analyze_connection_flow(self, packets: List[Dict]) -> ConnectionFlow:
        """
        Analyze connection flow from packets.
        Similar to Dshell's stream reassembly.
        
        Args:
            packets: List of packet dictionaries
        
        Returns:
            ConnectionFlow object
        """
        if not packets:
            raise ValueError("No packets provided")
        
        # Extract connection identifiers
        first_packet = packets[0]
        source_ip = first_packet.get('source_ip', '0.0.0.0')
        dest_ip = first_packet.get('dest_ip', '0.0.0.0')
        source_port = first_packet.get('source_port', 0)
        dest_port = first_packet.get('dest_port', 0)
        protocol = first_packet.get('protocol', 'TCP')
        
        # Create flow key
        flow_key = f"{source_ip}:{source_port}-{dest_ip}:{dest_port}"
        
        # Calculate flow statistics
        bytes_sent = sum(p.get('size', 0) for p in packets if p.get('source_ip') == source_ip)
        bytes_received = sum(p.get('size', 0) for p in packets if p.get('source_ip') == dest_ip)
        flags = list(set(p.get('flags', '') for p in packets if p.get('flags')))
        
        timestamps = [p.get('timestamp', '') for p in packets if p.get('timestamp')]
        start_time = min(timestamps) if timestamps else datetime.now().isoformat()
        end_time = max(timestamps) if timestamps else datetime.now().isoformat()
        
        # Calculate duration
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds()
        except Exception:
            # Invalid timestamp format - default to 0.0
            duration = 0.0
        
        flow = ConnectionFlow(
            source_ip=source_ip,
            dest_ip=dest_ip,
            source_port=source_port,
            dest_port=dest_port,
            protocol=protocol,
            packet_count=len(packets),
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            flags=flags
        )
        
        self.connection_flows[flow_key] = flow
        return flow
    
    def get_ip_geolocation_info(self, ip_address: str) -> Dict[str, Any]:
        """
        Get geolocation information for an IP address.
        Simplified version - in production, use MaxMind GeoIP2 or similar.
        
        Args:
            ip_address: IP address to look up
        
        Returns:
            Geolocation information dictionary
        """
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            
            # Simple private IP detection
            if ip_obj.is_private:
                return {
                    'ip': ip_address,
                    'type': 'private',
                    'is_private': True,
                    'is_public': False
                }
            
            # Public IP (in production, use GeoIP database)
            return {
                'ip': ip_address,
                'type': 'public',
                'is_private': False,
                'is_public': True,
                'note': 'Full geolocation requires GeoIP database'
            }
        except ValueError:
            return {
                'ip': ip_address,
                'error': 'Invalid IP address'
            }
    
    def correlate_events(self, time_window: float = 300.0) -> List[Dict]:
        """
        Correlate events within a time window.
        Similar to OSSEC's correlation engine.
        
        Args:
            time_window: Time window in seconds
        
        Returns:
            List of correlated event groups
        """
        if not self.analysis_results:
            return []
        
        # Group events by time
        event_groups = []
        current_group = []
        last_time = None
        
        for result in self.analysis_results:
            result_time = datetime.fromisoformat(result['timestamp'])
            
            if last_time is None:
                last_time = result_time
                current_group = [result]
            else:
                time_diff = (result_time - last_time).total_seconds()
                
                if time_diff <= time_window:
                    current_group.append(result)
                else:
                    if len(current_group) > 1:
                        event_groups.append({
                            'events': current_group,
                            'count': len(current_group),
                            'time_span': time_diff
                        })
                    current_group = [result]
                    last_time = result_time
        
        # Add last group
        if len(current_group) > 1:
            event_groups.append({
                'events': current_group,
                'count': len(current_group),
                'time_span': 0.0
            })
        
        return event_groups
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate forensic analysis report."""
        output_file = output_file or Path("forensic_report.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_analyses': len(self.analysis_results),
            'total_flows': len(self.connection_flows),
            'analyses': self.analysis_results,
            'connection_flows': [asdict(f) for f in self.connection_flows.values()],
            'correlated_events': self.correlate_events()
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            return f"Report saved to {output_file}"
        except Exception as e:
            return f"Error generating report: {e}"


def test_analyzer():
    """Test the forensic analyzer."""
    print("=== Gatekeeper Forensic Analysis Module Test ===\n")
    
    analyzer = ForensicAnalyzer()
    
    print(f"Loaded {len(analyzer.threat_patterns)} threat pattern categories:")
    for category, patterns in analyzer.threat_patterns.items():
        print(f"  - {category}: {len(patterns)} patterns")
    
    # Create test log file
    test_log = Path("test_attack_log.txt")
    test_log.write_text("""
[2025-01-27 10:00:01] Port scan detected from 192.168.1.100
[2025-01-27 10:00:05] Connection refused - multiple ports scanned
[2025-01-27 10:00:10] Unauthorized access attempt from 10.0.0.50
[2025-01-27 10:00:15] Failed login - brute force attempt detected
[2025-01-27 10:00:20] High connection rate - possible DDoS attack
[2025-01-27 10:00:25] SYN flood detected
[2025-01-27 10:00:30] Malware detected - suspicious file signature
[2025-01-27 10:00:35] SQL injection attempt blocked
[2025-01-27 10:00:40] Buffer overflow attempt detected
""")
    
    print("\n=== Analyzing Test Log File ===\n")
    results = analyzer.analyze_log_file(test_log)
    
    print(f"File: {results['file']}")
    print(f"Threats Detected: {results['statistics']['threat_count']}")
    print(f"Threat Types: {results['statistics']['threat_types']}")
    
    print("\n=== Threat Details ===")
    for threat in results['threats_detected'][:5]:
        print(f"  [{threat['type']}] Line {threat['line']}: {threat['context'][:60]}...")
    
    # Test IP geolocation
    print("\n=== IP Geolocation Test ===")
    test_ips = ["192.168.1.100", "8.8.8.8", "10.0.0.50"]
    for ip in test_ips:
        geo_info = analyzer.get_ip_geolocation_info(ip)
        print(f"  {ip}: {geo_info.get('type', 'unknown')} ({'private' if geo_info.get('is_private') else 'public'})")
    
    # Generate report
    print("\n=== Generating Report ===")
    report_msg = analyzer.generate_report(Path("test_forensic_report.json"))
    print(f"  {report_msg}")
    
    # Cleanup
    test_log.unlink(missing_ok=True)
    
    print("\n✓ Forensic analysis module test complete!")


if __name__ == "__main__":
    test_analyzer()
