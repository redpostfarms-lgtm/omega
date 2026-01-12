#!/usr/bin/env python3
"""
Gatekeeper Wazuh Integration Module
====================================
Integrates Wazuh security monitoring platform with The Gatekeeper system.

This module provides:
- API client for querying Wazuh alerts and logs
- Custom rule integration for ROE alignment
- Real-time threat detection via Wazuh
- File integrity monitoring (FIM) integration
- Alert forwarding to Gatekeeper systems

Based on Wazuh open-source security monitoring platform.
"""

import json
import requests
import urllib3
from base64 import b64encode
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Disable SSL warnings (use proper certs in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class WazuhAlert:
    """Wazuh alert data structure."""
    timestamp: str
    rule_id: int
    rule_level: int
    rule_description: str
    agent_id: str
    agent_name: str
    full_log: str
    location: Optional[str] = None
    category: Optional[str] = None


@dataclass
class WazuhAgent:
    """Wazuh agent information."""
    agent_id: str
    agent_name: str
    status: str  # 'active', 'disconnected', 'never_connected'
    ip: Optional[str] = None
    last_keepalive: Optional[str] = None


class WazuhClient:
    """Wazuh API client for The Gatekeeper integration."""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 55000,
        protocol: str = 'https',
        username: str = 'wazuh-wui',
        password: Optional[str] = None,
        verify_ssl: bool = False
    ):
        """
        Initialize Wazuh API client.
        
        Args:
            host: Wazuh server hostname/IP
            port: Wazuh API port (default: 55000)
            protocol: Protocol ('https' or 'http')
            username: API username
            password: API password (if None, must be set via set_password)
            verify_ssl: Verify SSL certificates (default: False for self-signed)
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.base_url = f"{protocol}://{host}:{port}"
        
    def _authenticate(self) -> str:
        """Authenticate with Wazuh API and obtain JWT token."""
        if self.password is None:
            raise ValueError("Password must be set before authentication")
        
        auth_url = f"{self.base_url}/security/user/authenticate"
        basic_auth = f"{self.username}:{self.password}".encode()
        headers = {
            'Authorization': f'Basic {b64encode(basic_auth).decode()}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                auth_url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data['data']['token']
            # Wazuh tokens typically expire in 15 minutes
            self.token_expiry = datetime.now() + timedelta(minutes=14)
            return self.token
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Wazuh authentication failed: {e}")
    
    def _ensure_token(self) -> str:
        """Ensure we have a valid token, refreshing if needed."""
        if (self.token is None or 
            self.token_expiry is None or 
            datetime.now() >= self.token_expiry):
            return self._authenticate()
        return self.token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        token = self._ensure_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def set_password(self, password: str):
        """Set API password and invalidate existing token."""
        self.password = password
        self.token = None
        self.token_expiry = None
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """
        Get summary of all agents by status.
        
        Returns:
            Dictionary with agent counts by status
        """
        url = f"{self.base_url}/agents/summary/status"
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('data', {})
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get agent summary: {e}")
    
    def get_agents(
        self,
        status: Optional[str] = None,
        limit: int = 500,
        offset: int = 0
    ) -> List[WazuhAgent]:
        """
        Get list of agents.
        
        Args:
            status: Filter by status ('active', 'disconnected', 'never_connected')
            limit: Maximum number of agents to return
            offset: Offset for pagination
            
        Returns:
            List of WazuhAgent objects
        """
        url = f"{self.base_url}/agents"
        params = {'limit': limit, 'offset': offset}
        if status:
            params['status'] = status
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json().get('data', {})
            agents_data = data.get('affected_items', [])
            
            agents = []
            for agent_data in agents_data:
                agents.append(WazuhAgent(
                    agent_id=str(agent_data.get('id', '')),
                    agent_name=agent_data.get('name', 'unknown'),
                    status=agent_data.get('status', 'unknown'),
                    ip=agent_data.get('ip', None),
                    last_keepalive=agent_data.get('lastKeepAlive', None)
                ))
            return agents
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get agents: {e}")
    
    def get_alerts(
        self,
        rule_id: Optional[int] = None,
        rule_level: Optional[int] = None,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
        offset: int = 0,
        sort: str = '-timestamp'
    ) -> List[WazuhAlert]:
        """
        Get alerts from Wazuh.
        
        Args:
            rule_id: Filter by rule ID
            rule_level: Filter by rule level (minimum)
            agent_id: Filter by agent ID
            start_time: Start time for alert filtering
            end_time: End time for alert filtering
            limit: Maximum number of alerts to return
            offset: Offset for pagination
            sort: Sort order (default: '-timestamp' for newest first)
            
        Returns:
            List of WazuhAlert objects
        """
        url = f"{self.base_url}/alerts"
        params = {'limit': limit, 'offset': offset, 'sort': sort}
        
        if rule_id:
            params['rule.id'] = rule_id
        if rule_level:
            params['rule.level'] = rule_level
        if agent_id:
            params['agent.id'] = agent_id
        if start_time:
            params['timestamp'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        if end_time:
            # Wazuh uses range queries for time
            if start_time:
                params['timestamp'] = f"{start_time.strftime('%Y-%m-%dT%H:%M:%S')},{end_time.strftime('%Y-%m-%dT%H:%M:%S')}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json().get('data', {})
            alerts_data = data.get('affected_items', [])
            
            alerts = []
            for alert_data in alerts_data:
                rule_data = alert_data.get('rule', {})
                agent_data = alert_data.get('agent', {})
                
                alerts.append(WazuhAlert(
                    timestamp=alert_data.get('timestamp', ''),
                    rule_id=rule_data.get('id', 0),
                    rule_level=rule_data.get('level', 0),
                    rule_description=rule_data.get('description', ''),
                    agent_id=str(agent_data.get('id', '')),
                    agent_name=agent_data.get('name', 'unknown'),
                    full_log=alert_data.get('full_log', ''),
                    location=alert_data.get('location', None),
                    category=rule_data.get('category', None)
                ))
            return alerts
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get alerts: {e}")
    
    def get_fim_events(
        self,
        agent_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Get File Integrity Monitoring (FIM) events for an agent.
        
        Args:
            agent_id: Agent ID
            start_time: Start time for filtering
            end_time: End time for filtering
            limit: Maximum number of events to return
            
        Returns:
            List of FIM event dictionaries
        """
        url = f"{self.base_url}/syscheck/{agent_id}"
        params = {'limit': limit}
        
        if start_time:
            params['date'] = start_time.strftime('%Y-%m-%d')
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json().get('data', {})
            return data.get('affected_items', [])
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get FIM events: {e}")
    
    def search_threats(
        self,
        min_level: int = 7,
        time_range_hours: int = 24
    ) -> List[WazuhAlert]:
        """
        Search for high-level threats (convenience method).
        
        Args:
            min_level: Minimum rule level (default: 7 = medium-high)
            time_range_hours: Hours to look back (default: 24)
            
        Returns:
            List of high-level alerts
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        return self.get_alerts(
            rule_level=min_level,
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
    
    def test_connection(self) -> bool:
        """
        Test connection to Wazuh API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.get_agent_summary()
            return True
        except Exception:
            return False


class WazuhIntegration:
    """Integration class for connecting Wazuh with Gatekeeper systems."""
    
    def __init__(self, wazuh_client: WazuhClient):
        """
        Initialize Wazuh integration.
        
        Args:
            wazuh_client: Configured WazuhClient instance
        """
        self.client = wazuh_client
        self.last_check: Optional[datetime] = None
        
    def get_recent_threats(
        self,
        min_level: int = 7,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get recent threats for Gatekeeper ROE evaluation.
        
        Args:
            min_level: Minimum alert level
            hours: Hours to look back
            
        Returns:
            List of threat dictionaries formatted for Gatekeeper
        """
        alerts = self.client.search_threats(min_level=min_level, time_range_hours=hours)
        
        threats = []
        for alert in alerts:
            threats.append({
                'timestamp': alert.timestamp,
                'level': alert.rule_level,
                'description': alert.rule_description,
                'agent': alert.agent_name,
                'log': alert.full_log,
                'category': alert.category,
                'source': 'wazuh'
            })
        
        self.last_check = datetime.now()
        return threats
    
    def check_agent_status(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check status of agents.
        
        Args:
            agent_name: Specific agent name (None for all)
            
        Returns:
            Status information dictionary
        """
        summary = self.client.get_agent_summary()
        agents = self.client.get_agents()
        
        if agent_name:
            agent = next((a for a in agents if a.agent_name == agent_name), None)
            if agent:
                return {
                    'name': agent.agent_name,
                    'status': agent.status,
                    'id': agent.agent_id,
                    'ip': agent.ip,
                    'last_keepalive': agent.last_keepalive
                }
            return {'error': f'Agent {agent_name} not found'}
        
        return {
            'summary': summary,
            'total_agents': len(agents),
            'agents': [asdict(a) for a in agents[:10]]  # Limit to first 10
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Get comprehensive status report for Gatekeeper dashboard.
        
        Returns:
            Status report dictionary
        """
        try:
            summary = self.client.get_agent_summary()
            recent_threats = self.get_recent_threats(hours=1)
            
            return {
                'status': 'connected',
                'agents': summary,
                'recent_threats_count': len(recent_threats),
                'recent_threats': recent_threats[:10],  # Last 10 threats
                'last_check': self.last_check.isoformat() if self.last_check else None,
                'wazuh_server': f"{self.client.host}:{self.client.port}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': self.last_check.isoformat() if self.last_check else None
            }


# Example usage and integration function
def create_wazuh_client(config: Optional[Dict[str, Any]] = None) -> Optional[WazuhClient]:
    """
    Create and configure Wazuh client from config.
    
    Args:
        config: Configuration dictionary with Wazuh settings
                (host, port, username, password, etc.)
                
    Returns:
        Configured WazuhClient or None if config invalid
    """
    if config is None:
        # Try to load from environment or default config
        import os
        config = {
            'host': os.getenv('WAZUH_HOST', 'localhost'),
            'port': int(os.getenv('WAZUH_PORT', '55000')),
            'protocol': os.getenv('WAZUH_PROTOCOL', 'https'),
            'username': os.getenv('WAZUH_USERNAME', 'wazuh-wui'),
            'password': os.getenv('WAZUH_PASSWORD', None),
            'verify_ssl': os.getenv('WAZUH_VERIFY_SSL', 'false').lower() == 'true'
        }
    
    if not config.get('password'):
        return None  # Password required
    
    try:
        client = WazuhClient(
            host=config.get('host', 'localhost'),
            port=config.get('port', 55000),
            protocol=config.get('protocol', 'https'),
            username=config.get('username', 'wazuh-wui'),
            password=config.get('password'),
            verify_ssl=config.get('verify_ssl', False)
        )
        
        # Test connection
        if client.test_connection():
            return client
        return None
    except Exception:
        return None


if __name__ == "__main__":
    # Example usage
    print("Wazuh Integration Module")
    print("=" * 50)
    
    # Example: Create client (requires actual Wazuh server)
    # client = create_wazuh_client({
    #     'host': 'wazuh-server.local',
    #     'port': 55000,
    #     'username': 'wazuh-wui',
    #     'password': 'your-password',
    #     'verify_ssl': False
    # })
    # 
    # if client:
    #     integration = WazuhIntegration(client)
    #     status = integration.get_status_report()
    #     print(json.dumps(status, indent=2))
    # else:
    #     print("Failed to connect to Wazuh server")
    
    print("\nWazuh integration module loaded successfully.")
    print("Configure Wazuh server settings to use this module.")
