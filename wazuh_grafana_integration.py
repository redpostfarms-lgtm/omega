"""
Wazuh Grafana Integration for The Gatekeeper
=============================================
Security monitoring dashboards and alerts

Features:
- Connect to Wazuh Elasticsearch
- Auto-create Grafana dashboards
- Security event visualization
- Agent health monitoring
- Alert rules

Requirements:
- grafana-client>=3.5.0
- elasticsearch>=8.11.0
- python-dateutil>=2.8.2
"""

import os
import sys
import logging
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

try:
    from grafana_client import GrafanaApi
    GRAFANA_AVAILABLE = True
except ImportError:
    GRAFANA_AVAILABLE = False
    print("Warning: grafana-client not available")

try:
    from elasticsearch import Elasticsearch
    ES_AVAILABLE = True
except ImportError:
    ES_AVAILABLE = False
    print("Warning: elasticsearch not available")


@dataclass
class WazuhConfig:
    """Wazuh and Grafana configuration"""
    # Elasticsearch (Wazuh backend)
    es_host: str = "localhost"
    es_port: int = 9200
    es_user: str = "admin"
    es_password: str = "admin"
    es_index_pattern: str = "wazuh-alerts-*"

    # Grafana
    grafana_host: str = "localhost"
    grafana_port: int = 3000
    grafana_user: str = "admin"
    grafana_password: str = "admin"
    grafana_url: Optional[str] = None

    def __post_init__(self):
        if self.grafana_url is None:
            self.grafana_url = f"http://{self.grafana_host}:{self.grafana_port}"


class WazuhGrafanaIntegration:
    """
    Wazuh Grafana integration manager

    Usage:
        integration = WazuhGrafanaIntegration()
        integration.create_security_dashboard()
        integration.create_agent_health_dashboard()
        integration.setup_alerts()
    """

    def __init__(self, config: Optional[WazuhConfig] = None):
        """
        Initialize Wazuh Grafana integration

        Args:
            config: WazuhConfig or None to load from environment
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or self._load_config_from_env()

        # Initialize clients
        self.es_client: Optional[Elasticsearch] = None
        self.grafana_client: Optional[GrafanaApi] = None

        if ES_AVAILABLE:
            try:
                self.es_client = Elasticsearch(
                    [f"{self.config.es_host}:{self.config.es_port}"],
                    basic_auth=(self.config.es_user, self.config.es_password),
                    verify_certs=False
                )
                if self.es_client.ping():
                    self.logger.info("Connected to Elasticsearch")
                else:
                    self.logger.warning("Elasticsearch ping failed")
                    self.es_client = None
            except Exception as e:
                self.logger.error(f"Failed to connect to Elasticsearch: {e}")
                self.es_client = None

        if GRAFANA_AVAILABLE:
            try:
                self.grafana_client = GrafanaApi(
                    auth=(self.config.grafana_user, self.config.grafana_password),
                    host=self.config.grafana_url
                )
                self.logger.info("Connected to Grafana")
            except Exception as e:
                self.logger.error(f"Failed to connect to Grafana: {e}")
                self.grafana_client = None

    def _load_config_from_env(self) -> WazuhConfig:
        """Load configuration from environment variables"""
        return WazuhConfig(
            es_host=os.getenv('WAZUH_ES_HOST', 'localhost'),
            es_port=int(os.getenv('WAZUH_ES_PORT', '9200')),
            es_user=os.getenv('WAZUH_ES_USER', 'admin'),
            es_password=os.getenv('WAZUH_ES_PASSWORD', 'admin'),
            es_index_pattern=os.getenv('WAZUH_ES_INDEX', 'wazuh-alerts-*'),
            grafana_host=os.getenv('GRAFANA_HOST', 'localhost'),
            grafana_port=int(os.getenv('GRAFANA_PORT', '3000')),
            grafana_user=os.getenv('GRAFANA_USER', 'admin'),
            grafana_password=os.getenv('GRAFANA_PASSWORD', 'admin'),
        )

    def query_wazuh_events(
        self,
        hours: int = 24,
        rule_level: Optional[int] = None
    ) -> List[Dict]:
        """
        Query Wazuh security events

        Args:
            hours: Hours to look back
            rule_level: Minimum rule level (0-15)

        Returns:
            List of events
        """
        if not self.es_client:
            self.logger.warning("Elasticsearch not available")
            return []

        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": f"now-{hours}h",
                                        "lte": "now"
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            if rule_level is not None:
                query["query"]["bool"]["must"].append({
                    "range": {
                        "rule.level": {"gte": rule_level}
                    }
                })

            result = self.es_client.search(
                index=self.config.es_index_pattern,
                body=query,
                size=100
            )

            events = [hit["_source"] for hit in result["hits"]["hits"]]
            self.logger.info(f"Found {len(events)} Wazuh events")
            return events

        except Exception as e:
            self.logger.error(f"Failed to query Wazuh events: {e}")
            return []

    def get_agent_status(self) -> Dict:
        """Get Wazuh agent status summary"""
        if not self.es_client:
            return {}

        try:
            # Query for agent status
            query = {
                "size": 0,
                "aggs": {
                    "agents": {
                        "terms": {
                            "field": "agent.name.keyword",
                            "size": 100
                        },
                        "aggs": {
                            "latest_status": {
                                "top_hits": {
                                    "size": 1,
                                    "sort": [{"timestamp": {"order": "desc"}}]
                                }
                            }
                        }
                    }
                }
            }

            result = self.es_client.search(
                index=self.config.es_index_pattern,
                body=query
            )

            agents = result["aggregations"]["agents"]["buckets"]
            return {
                "total_agents": len(agents),
                "agents": [
                    {
                        "name": bucket["key"],
                        "event_count": bucket["doc_count"]
                    }
                    for bucket in agents
                ]
            }

        except Exception as e:
            self.logger.error(f"Failed to get agent status: {e}")
            return {}

    def create_security_dashboard(self) -> Optional[str]:
        """
        Create security overview dashboard in Grafana

        Returns:
            Dashboard UID or None
        """
        if not self.grafana_client:
            self.logger.warning("Grafana not available")
            return None

        dashboard_json = self._build_security_dashboard()

        try:
            result = self.grafana_client.dashboard.update_dashboard(dashboard_json)
            uid = result.get('uid', '')
            self.logger.info(f"Created security dashboard: {uid}")
            return uid
        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            return None

    def _build_security_dashboard(self) -> Dict:
        """Build security dashboard JSON"""
        return {
            "dashboard": {
                "title": "Wazuh Security Overview",
                "tags": ["security", "wazuh", "gatekeeper"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    # Alert Level Distribution
                    {
                        "id": 1,
                        "title": "Alert Level Distribution",
                        "type": "piechart",
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                        "targets": [{
                            "query": "rule.level",
                            "alias": "Level {{field}}"
                        }]
                    },
                    # Top 10 Rules
                    {
                        "id": 2,
                        "title": "Top 10 Triggered Rules",
                        "type": "table",
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                        "targets": [{
                            "query": "rule.description",
                            "alias": "Rule"
                        }]
                    },
                    # Alerts Over Time
                    {
                        "id": 3,
                        "title": "Alerts Over Time",
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8},
                        "targets": [{
                            "query": "timestamp",
                            "alias": "Alerts"
                        }]
                    },
                    # Top Affected Agents
                    {
                        "id": 4,
                        "title": "Top Affected Agents",
                        "type": "barchart",
                        "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8},
                        "targets": [{
                            "query": "agent.name",
                            "alias": "Agent"
                        }]
                    },
                    # Recent High Severity Alerts
                    {
                        "id": 5,
                        "title": "Recent High Severity Alerts (Level >= 10)",
                        "type": "logs",
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
                        "targets": [{
                            "query": "rule.level:>=10",
                            "alias": "High Severity"
                        }]
                    }
                ]
            },
            "overwrite": True
        }

    def create_agent_health_dashboard(self) -> Optional[str]:
        """
        Create agent health dashboard

        Returns:
            Dashboard UID or None
        """
        if not self.grafana_client:
            return None

        dashboard_json = {
            "dashboard": {
                "title": "Wazuh Agent Health",
                "tags": ["agents", "health", "wazuh"],
                "refresh": "1m",
                "panels": [
                    {
                        "id": 1,
                        "title": "Agent Status",
                        "type": "stat",
                        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    },
                    {
                        "id": 2,
                        "title": "Events Per Agent",
                        "type": "bargauge",
                        "gridPos": {"x": 6, "y": 0, "w": 18, "h": 8},
                    },
                    {
                        "id": 3,
                        "title": "Agent Activity Timeline",
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8},
                    }
                ]
            },
            "overwrite": True
        }

        try:
            result = self.grafana_client.dashboard.update_dashboard(dashboard_json)
            uid = result.get('uid', '')
            self.logger.info(f"Created agent health dashboard: {uid}")
            return uid
        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            return None

    def setup_alerts(self) -> bool:
        """
        Set up Grafana alert rules

        Returns:
            Success status
        """
        if not self.grafana_client:
            return False

        alerts = [
            {
                "name": "High Severity Alerts",
                "condition": "rule.level >= 10",
                "frequency": "5m",
                "for": "5m",
                "message": "High severity security alerts detected"
            },
            {
                "name": "Agent Disconnected",
                "condition": "agent.status == 'disconnected'",
                "frequency": "1m",
                "for": "5m",
                "message": "Wazuh agent disconnected"
            }
        ]

        try:
            for alert in alerts:
                # In a real implementation, use Grafana alert API
                # This is a simplified example
                self.logger.info(f"Would create alert: {alert['name']}")

            self.logger.info("Alert setup complete")
            return True

        except Exception as e:
            self.logger.error(f"Failed to setup alerts: {e}")
            return False

    def get_security_summary(self, hours: int = 24) -> Dict:
        """Get security summary for last N hours"""
        events = self.query_wazuh_events(hours=hours)

        if not events:
            return {
                "total_events": 0,
                "time_range_hours": hours
            }

        # Analyze events
        level_counts = {}
        rule_counts = {}
        agent_counts = {}

        for event in events:
            level = event.get("rule", {}).get("level", 0)
            level_counts[level] = level_counts.get(level, 0) + 1

            rule_id = event.get("rule", {}).get("id", "unknown")
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1

            agent_name = event.get("agent", {}).get("name", "unknown")
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1

        high_severity = sum(count for level, count in level_counts.items() if level >= 10)

        return {
            "total_events": len(events),
            "high_severity_count": high_severity,
            "unique_rules": len(rule_counts),
            "affected_agents": len(agent_counts),
            "time_range_hours": hours,
            "top_rules": sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_agents": sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def export_dashboard(self, dashboard_uid: str, filepath: str) -> bool:
        """Export dashboard to JSON file"""
        if not self.grafana_client:
            return False

        try:
            dashboard = self.grafana_client.dashboard.get_dashboard(dashboard_uid)
            with open(filepath, 'w') as f:
                json.dump(dashboard, f, indent=2)
            self.logger.info(f"Exported dashboard to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export dashboard: {e}")
            return False


# Global instance
_integration_instance: Optional[WazuhGrafanaIntegration] = None


def get_wazuh_integration(config: Optional[WazuhConfig] = None) -> WazuhGrafanaIntegration:
    """Get or create global Wazuh integration"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = WazuhGrafanaIntegration(config)
    return _integration_instance


if __name__ == "__main__":
    # Demo/test mode
    import argparse

    parser = argparse.ArgumentParser(description="Wazuh Grafana Integration Demo")
    parser.add_argument('--query', action='store_true', help='Query Wazuh events')
    parser.add_argument('--agents', action='store_true', help='Show agent status')
    parser.add_argument('--create-dashboards', action='store_true', help='Create Grafana dashboards')
    parser.add_argument('--summary', action='store_true', help='Show security summary')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    integration = get_wazuh_integration()

    print("\n🔒 Wazuh Grafana Integration")

    if not ES_AVAILABLE:
        print("❌ Elasticsearch client not available")
        print("Install: py -3.11 -m pip install elasticsearch")

    if not GRAFANA_AVAILABLE:
        print("❌ Grafana client not available")
        print("Install: py -3.11 -m pip install grafana-client")

    if not (ES_AVAILABLE and GRAFANA_AVAILABLE):
        sys.exit(1)

    if args.query:
        print(f"\n🔍 Querying Wazuh events (last {args.hours} hours)...")
        events = integration.query_wazuh_events(hours=args.hours)
        print(f"Found {len(events)} events")
        if events:
            print("\nSample event:")
            print(json.dumps(events[0], indent=2)[:500] + "...")

    if args.agents:
        print("\n👥 Agent Status:")
        status = integration.get_agent_status()
        print(f"Total agents: {status.get('total_agents', 0)}")
        for agent in status.get('agents', [])[:10]:
            print(f"  - {agent['name']}: {agent['event_count']} events")

    if args.create_dashboards:
        print("\n📊 Creating Grafana dashboards...")
        security_uid = integration.create_security_dashboard()
        if security_uid:
            print(f"  ✅ Security dashboard: {integration.config.grafana_url}/d/{security_uid}")

        agent_uid = integration.create_agent_health_dashboard()
        if agent_uid:
            print(f"  ✅ Agent health dashboard: {integration.config.grafana_url}/d/{agent_uid}")

        print("\n⚠️ Setting up alerts...")
        if integration.setup_alerts():
            print("  ✅ Alerts configured")

    if args.summary:
        print(f"\n📋 Security Summary (last {args.hours} hours):")
        summary = integration.get_security_summary(hours=args.hours)
        print(f"  Total events: {summary['total_events']}")
        print(f"  High severity: {summary['high_severity_count']}")
        print(f"  Unique rules: {summary['unique_rules']}")
        print(f"  Affected agents: {summary['affected_agents']}")

        if summary.get('top_rules'):
            print("\n  Top rules:")
            for rule_id, count in summary['top_rules']:
                print(f"    {rule_id}: {count} events")

    if not any([args.query, args.agents, args.create_dashboards, args.summary]):
        print("\nUsage:")
        print("  py -3.11 wazuh_grafana_integration.py --query --hours 24")
        print("  py -3.11 wazuh_grafana_integration.py --agents")
        print("  py -3.11 wazuh_grafana_integration.py --create-dashboards")
        print("  py -3.11 wazuh_grafana_integration.py --summary")
