"""
Agent Observability System
Logs, monitors, and tracks agent execution metrics.
Provides dashboard and debugging tools.

Red Post Farms, LLC - 2026
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
LOG_DIR = BRAIN_DIR / "Archived" / "agent_logs"
METRICS_DIR = BRAIN_DIR / "Archived" / "agent_metrics"
LOG_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

class AgentObservability:
    def __init__(self):
        self.execution_logs = []
        self.metrics = defaultdict(list)
        self._load_metrics()
    
    def _load_metrics(self):
        """Load historical metrics."""
        metrics_file = METRICS_DIR / "metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = defaultdict(list, data)
            except: pass
    
    def _save_metrics(self):
        """Save metrics to disk."""
        metrics_file = METRICS_DIR / "metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(dict(self.metrics), f, indent=2)
    
    def log_execution(self, agent_name: str, task: str, result: str, duration: float, success: bool = True):
        """Log agent execution."""
        log_entry = {
            "timestamp": int(time.time()),
            "agent": agent_name,
            "task": task,
            "result": result[:500],  # Truncate long results
            "duration_seconds": duration,
            "success": success
        }
        self.execution_logs.append(log_entry)
        
        # Keep last 1000 logs in memory
        if len(self.execution_logs) > 1000:
            self.execution_logs = self.execution_logs[-1000:]
        
        # Save to file
        log_file = LOG_DIR / f"agent_{agent_name}_{datetime.now().strftime('%Y%m%d')}.json"
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except: pass
        logs.append(log_entry)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-1000:], f, indent=2)
        
        # Track metrics
        self.metrics[f"{agent_name}_executions"].append({
            "timestamp": int(time.time()),
            "duration": duration,
            "success": success
        })
        self.metrics[f"{agent_name}_success_rate"].append({
            "timestamp": int(time.time()),
            "rate": sum(1 for e in self.execution_logs[-100:] if e.get("success", False)) / min(100, len(self.execution_logs))
        })
        self._save_metrics()
    
    def create_dashboard(self) -> Dict:
        """Create agent execution dashboard."""
        agents = set(e["agent"] for e in self.execution_logs)
        dashboard = {
            "total_executions": len(self.execution_logs),
            "agents": {},
            "recent_activity": self.execution_logs[-10:],
            "success_rate": sum(1 for e in self.execution_logs if e.get("success", False)) / max(1, len(self.execution_logs))
        }
        
        for agent in agents:
            agent_logs = [e for e in self.execution_logs if e["agent"] == agent]
            dashboard["agents"][agent] = {
                "total_executions": len(agent_logs),
                "success_rate": sum(1 for e in agent_logs if e.get("success", False)) / max(1, len(agent_logs)),
                "avg_duration": sum(e["duration_seconds"] for e in agent_logs) / max(1, len(agent_logs)),
                "last_execution": max((e["timestamp"] for e in agent_logs), default=0)
            }
        
        return dashboard
    
    def track_metrics(self, agent_name: str, metric_name: str, value: float):
        """Track custom metrics."""
        self.metrics[f"{agent_name}_{metric_name}"].append({
            "timestamp": int(time.time()),
            "value": value
        })
        if len(self.metrics[f"{agent_name}_{metric_name}"]) > 1000:
            self.metrics[f"{agent_name}_{metric_name}"] = self.metrics[f"{agent_name}_{metric_name}"][-1000:]
        self._save_metrics()
    
    def get_metrics(self, agent_name: Optional[str] = None) -> Dict:
        """Get metrics for agent(s)."""
        if agent_name:
            return {k: v for k, v in self.metrics.items() if k.startswith(f"{agent_name}_")}
        return dict(self.metrics)

def main():
    obs = AgentObservability()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agent_observability.py <command> [args...]")
        print("Commands: dashboard, metrics [agent_name], log <agent> <task> <result>")
        return
    cmd = sys.argv[1].lower()
    if cmd == "dashboard":
        dashboard = obs.create_dashboard()
        print("Agent Dashboard:")
        print(f"Total Executions: {dashboard['total_executions']}")
        print(f"Success Rate: {dashboard['success_rate']*100:.1f}%")
        print("\nAgents:")
        for agent, stats in dashboard['agents'].items():
            print(f"  {agent}: {stats['total_executions']} executions, {stats['success_rate']*100:.1f}% success, {stats['avg_duration']:.2f}s avg")
    elif cmd == "metrics":
        agent = sys.argv[2] if len(sys.argv) > 2 else None
        metrics = obs.get_metrics(agent)
        print(f"Metrics{' for ' + agent if agent else ''}:")
        for name, values in list(metrics.items())[:10]:
            print(f"  {name}: {len(values)} data points")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

