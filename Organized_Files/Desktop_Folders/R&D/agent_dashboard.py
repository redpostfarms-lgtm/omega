# -*- coding: utf-8 -*-
# AGENT DASHBOARD - Monitors .skills folder for agent improvements
# Watches agent skill logs and reports when agents level up

import os
import json
import sys
import io
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass


class AgentDashboard:
    """
    Dashboard that monitors agent skill logs and reports improvements.
    Watches .skills folder for changes and notifies when agents level up.
    """
    
    def __init__(self, skills_dir: str = './.skills', watch_interval: float = 5.0):
        """
        Initialize dashboard.
        
        Args:
            skills_dir: Directory containing agent skill logs
            watch_interval: How often to check for changes (seconds)
        """
        self.skills_dir = Path(skills_dir)
        self.watch_interval = watch_interval
        self.known_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_snapshots: Dict[str, Dict[str, Any]] = {}
        
    def scan_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan skills directory for all agent logs.
        
        Returns:
            Dictionary mapping agent names to their current stats
        """
        agents = {}
        
        if not self.skills_dir.exists():
            return agents
        
        for skill_file in self.skills_dir.glob('*.json'):
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                agent_name = data.get('name', skill_file.stem)
                
                # Calculate stats
                total_runs = data.get('runs', 0)
                successful_runs = data.get('successful_runs', 0)
                failed_runs = data.get('failed_runs', 0)
                
                agents[agent_name] = {
                    'name': agent_name,
                    'birth': data.get('birth', 'unknown'),
                    'goal': data.get('initial_goal', 'unknown'),
                    'total_runs': total_runs,
                    'successful_runs': successful_runs,
                    'failed_runs': failed_runs,
                    'success_rate': (successful_runs / max(total_runs, 1)) * 100,
                    'improvement_notes_count': len(data.get('improve_notes', [])),
                    'last_update': self._get_file_mtime(skill_file),
                    'file_path': str(skill_file)
                }
                
            except (IOError, json.JSONDecodeError) as e:
                continue
        
        return agents
    
    def _get_file_mtime(self, file_path: Path) -> str:
        """Get file modification time as string."""
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).isoformat()
        except OSError:
            return 'unknown'
    
    def detect_improvements(self, old_snapshot: Dict[str, Dict[str, Any]], 
                          new_snapshot: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect improvements between two snapshots.
        
        Args:
            old_snapshot: Previous agent state
            new_snapshot: Current agent state
            
        Returns:
            List of improvement notifications
        """
        improvements = []
        
        # Check for new agents
        for agent_name, agent_data in new_snapshot.items():
            if agent_name not in old_snapshot:
                improvements.append({
                    'type': 'new_agent',
                    'agent': agent_name,
                    'message': f"🎉 New agent born: {agent_name}",
                    'data': agent_data
                })
        
        # Check for improvements in existing agents
        for agent_name, new_data in new_snapshot.items():
            if agent_name not in old_snapshot:
                continue
            
            old_data = old_snapshot[agent_name]
            
            # Check for more runs
            old_runs = old_data.get('total_runs', 0)
            new_runs = new_data.get('total_runs', 0)
            if new_runs > old_runs:
                improvements.append({
                    'type': 'more_experience',
                    'agent': agent_name,
                    'message': f"📈 {agent_name} gained experience: {old_runs} → {new_runs} runs",
                    'data': {'old_runs': old_runs, 'new_runs': new_runs}
                })
            
            # Check for improved success rate
            old_rate = old_data.get('success_rate', 0)
            new_rate = new_data.get('success_rate', 0)
            if new_rate > old_rate + 5:  # At least 5% improvement
                improvements.append({
                    'type': 'level_up',
                    'agent': agent_name,
                    'message': f"⭐ {agent_name} leveled up! Success rate: {old_rate:.1f}% → {new_rate:.1f}%",
                    'data': {'old_rate': old_rate, 'new_rate': new_rate}
                })
            
            # Check for milestone (100% success rate, 10+ successful runs, etc.)
            if new_data.get('successful_runs', 0) >= 10 and old_data.get('successful_runs', 0) < 10:
                improvements.append({
                    'type': 'milestone',
                    'agent': agent_name,
                    'message': f"🏆 {agent_name} hit milestone: 10+ successful runs!",
                    'data': {'successful_runs': new_data.get('successful_runs', 0)}
                })
            
            # Check for learning (more improvement notes)
            old_notes = old_data.get('improvement_notes_count', 0)
            new_notes = new_data.get('improvement_notes_count', 0)
            if new_notes > old_notes:
                improvements.append({
                    'type': 'learning',
                    'agent': agent_name,
                    'message': f"🧠 {agent_name} learned something new ({new_notes - old_notes} new improvements)",
                    'data': {'old_notes': old_notes, 'new_notes': new_notes}
                })
        
        return improvements
    
    def display_status(self, agents: Dict[str, Dict[str, Any]]):
        """
        Display current status of all agents.
        
        Args:
            agents: Dictionary of agent data
        """
        if not agents:
            print("📊 No agents found in .skills directory")
            return
        
        print("\n" + "=" * 70)
        print("AGENT DASHBOARD - Current Status")
        print("=" * 70)
        print(f"Total agents: {len(agents)}")
        print(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Sort by success rate (descending)
        sorted_agents = sorted(agents.items(), 
                              key=lambda x: x[1].get('success_rate', 0), 
                              reverse=True)
        
        for agent_name, data in sorted_agents:
            success_rate = data.get('success_rate', 0)
            total_runs = data.get('total_runs', 0)
            successful_runs = data.get('successful_runs', 0)
            
            # Status icon
            if success_rate >= 90 and total_runs >= 5:
                icon = "🌟"  # Expert
            elif success_rate >= 75:
                icon = "⭐"  # Good
            elif total_runs == 0:
                icon = "🆕"  # New
            else:
                icon = "🔧"  # Learning
            
            print(f"\n{icon} {agent_name}")
            print(f"   Goal: {data.get('goal', 'unknown')[:50]}")
            print(f"   Runs: {total_runs} (✅ {successful_runs} | ❌ {data.get('failed_runs', 0)})")
            print(f"   Success rate: {success_rate:.1f}%")
            print(f"   Improvements logged: {data.get('improvement_notes_count', 0)}")
        
        print("\n" + "=" * 70)
    
    def watch(self, max_iterations: Optional[int] = None):
        """
        Watch for changes and report improvements.
        
        Args:
            max_iterations: Maximum number of iterations (None = infinite)
        """
        print("🔍 Agent Dashboard - Watching for improvements...")
        print(f"📁 Monitoring: {self.skills_dir}")
        print(f"⏱️  Check interval: {self.watch_interval}s")
        print("\nPress Ctrl+C to stop\n")
        
        iteration = 0
        
        try:
            while max_iterations is None or iteration < max_iterations:
                # Scan current state
                current_agents = self.scan_agents()
                
                # Detect improvements
                if self.agent_snapshots:
                    improvements = self.detect_improvements(
                        self.agent_snapshots,
                        current_agents
                    )
                    
                    if improvements:
                        print(f"\n🔔 [{datetime.now().strftime('%H:%M:%S')}] Updates detected:")
                        for improvement in improvements:
                            print(f"   {improvement['message']}")
                
                # Update snapshot
                self.agent_snapshots = current_agents.copy()
                
                # Display status every 5 iterations or on first run
                if iteration == 0 or iteration % 5 == 0:
                    self.display_status(current_agents)
                
                iteration += 1
                time.sleep(self.watch_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped by user")
            self.display_status(self.scan_agents())
    
    def recommend_agent(self, task_type: str = None) -> Optional[str]:
        """
        Recommend best agent for a task type.
        
        Args:
            task_type: Optional task type hint
            
        Returns:
            Recommended agent name or None
        """
        agents = self.scan_agents()
        
        if not agents:
            return None
        
        # Filter by task type if provided
        if task_type:
            filtered = {
                name: data for name, data in agents.items()
                if task_type.lower() in data.get('goal', '').lower()
            }
            if filtered:
                agents = filtered
        
        # Find agent with highest success rate and enough experience
        best = None
        best_score = -1
        
        for name, data in agents.items():
            runs = data.get('total_runs', 0)
            rate = data.get('success_rate', 0)
            
            # Score: success rate weighted by experience (min 3 runs)
            if runs >= 3:
                score = rate * (1 + min(runs / 20, 0.5))  # Bonus for experience
                if score > best_score:
                    best_score = score
                    best = name
        
        return best


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Dashboard - Monitor agent improvements')
    parser.add_argument('--skills-dir', default='./.skills', help='Skills directory to monitor')
    parser.add_argument('--watch', action='store_true', help='Watch for changes continuously')
    parser.add_argument('--interval', type=float, default=5.0, help='Watch interval in seconds')
    parser.add_argument('--recommend', type=str, help='Recommend agent for task type')
    parser.add_argument('--status', action='store_true', help='Show current status and exit')
    
    args = parser.parse_args()
    
    dashboard = AgentDashboard(
        skills_dir=args.skills_dir,
        watch_interval=args.interval
    )
    
    if args.recommend:
        agent = dashboard.recommend_agent(args.recommend)
        if agent:
            print(f"💡 Recommended agent for '{args.recommend}': {agent}")
        else:
            print(f"❌ No suitable agent found for '{args.recommend}'")
    elif args.status or not args.watch:
        # Single scan
        agents = dashboard.scan_agents()
        dashboard.display_status(agents)
        
        # Show recommendations
        best_overall = dashboard.recommend_agent()
        if best_overall:
            print(f"\n💡 Best overall agent: {best_overall}")
    else:
        # Watch mode
        dashboard.watch()

