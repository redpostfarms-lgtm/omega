"""
Omega Mesh Network - Distributed Computing Fleet Controller
- Queen node (main device) at full power
- Worker nodes (phones 1-5) contribute 20% CPU when idle
- Screen-black idle detection
- Silent background processing
- No snooping, no feedback, pure compute power
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import psutil

@dataclass
class WorkerNode:
    """Worker bee node in the mesh"""
    id: int
    name: str
    status: str  # "active", "idle", "offline", "disabled"
    cpu_contribution: float  # 0.0 to 0.20 (20% max)
    screen_state: str  # "on", "off"
    last_heartbeat: str
    enabled: bool
    tasks_completed: int
    total_compute_time: float

class OmegaMeshNetwork:
    """
    Distributed computing mesh coordinator
    Queen + 4 worker bees processing network
    """
    
    def __init__(self):
        self.queen_node = {
            "id": 0,
            "name": "QUEEN",
            "status": "active",
            "cpu_contribution": 1.0,  # Full throttle
            "role": "coordinator"
        }
        
        self.worker_nodes: Dict[int, WorkerNode] = {
            i: WorkerNode(
                id=i,
                name=f"WORKER-{i}",
                status="offline",
                cpu_contribution=0.0,
                screen_state="on",
                last_heartbeat=datetime.now().isoformat(),
                enabled=True,
                tasks_completed=0,
                total_compute_time=0.0
            )
            for i in range(1, 6)  # Workers 1-5
        }
        
        self.mesh_active = False
        self.total_fleet_power = 0.0
        self.task_queue = []
        
    def initialize_mesh(self):
        """Seed the mesh - deploy to fleet"""
        print("[MESH] Initializing Omega Fleet Mesh Network...")
        print(f"[MESH] Queen node: {self.queen_node['name']} - Full throttle active")
        print(f"[MESH] Worker nodes: {len(self.worker_nodes)} devices")
        print("[MESH] Configuration: 20% CPU cap when screen black & idle")
        print("[MESH] No snooping, no feedback - silent compute only")
        self.mesh_active = True
        return True
    
    def toggle_worker(self, worker_id: int, enabled: bool) -> bool:
        """Toggle individual worker on/off"""
        if worker_id not in self.worker_nodes:
            return False
        
        worker = self.worker_nodes[worker_id]
        worker.enabled = enabled
        
        if not enabled:
            worker.status = "disabled"
            worker.cpu_contribution = 0.0
            print(f"[MESH] Worker {worker_id} disabled")
        else:
            worker.status = "offline"  # Will activate when conditions met
            print(f"[MESH] Worker {worker_id} enabled - awaiting idle state")
        
        self._update_fleet_power()
        return True
    
    def check_worker_idle_state(self, worker_id: int, screen_on: bool, user_active: bool) -> bool:
        """
        Check if worker should contribute compute power
        Conditions: Screen OFF and user IDLE
        """
        if worker_id not in self.worker_nodes:
            return False
        
        worker = self.worker_nodes[worker_id]
        
        if not worker.enabled:
            return False
        
        if not screen_on and not user_active:
            worker.screen_state = "off"
            worker.status = "active"
            worker.cpu_contribution = 0.20  # Cap at 20%
            print(f"[MESH] Worker {worker_id} contributing compute power (20% cap)")
            return True
        else:
            worker.screen_state = "on"
            worker.status = "idle"
            worker.cpu_contribution = 0.0
            return False
    
    def assign_task_to_worker(self, worker_id: int, task_data: Dict) -> bool:
        """
        Assign compute task to worker node
        Silent background processing only
        """
        if worker_id not in self.worker_nodes:
            return False
        
        worker = self.worker_nodes[worker_id]
        
        if worker.status != "active" or not worker.enabled:
            return False
        
        task = {
            "task_id": task_data.get("id"),
            "type": task_data.get("type", "compute"),
            "data": task_data.get("data"),
            "worker_id": worker_id,
            "assigned_at": datetime.now().isoformat(),
            "silent_mode": True  # No user notification
        }
        
        print(f"[MESH] Task assigned to Worker {worker_id} (silent mode)")
        return True
    
    def get_fleet_status(self) -> Dict:
        """Get complete fleet status"""
        workers_status = {
            worker_id: {
                "name": worker.name,
                "status": worker.status,
                "enabled": worker.enabled,
                "cpu_contribution": worker.cpu_contribution,
                "screen_state": worker.screen_state,
                "tasks_completed": worker.tasks_completed,
                "compute_time": worker.total_compute_time
            }
            for worker_id, worker in self.worker_nodes.items()
        }
        
        active_workers = sum(1 for w in self.worker_nodes.values() if w.status == "active")
        total_contribution = sum(w.cpu_contribution for w in self.worker_nodes.values())
        
        return {
            "queen": self.queen_node,
            "workers": workers_status,
            "mesh_active": self.mesh_active,
            "active_workers": active_workers,
            "total_workers": len(self.worker_nodes),
            "total_cpu_contribution": total_contribution,
            "fleet_power": self.queen_node["cpu_contribution"] + total_contribution
        }
    
    def _update_fleet_power(self):
        """Calculate total fleet compute power"""
        worker_power = sum(w.cpu_contribution for w in self.worker_nodes.values())
        self.total_fleet_power = self.queen_node["cpu_contribution"] + worker_power
        return self.total_fleet_power
    
    def get_worker_labels(self) -> List[str]:
        """Get labeled list of all workers (1-5)"""
        return [f"Worker-{i}" for i in range(1, 6)]
    
    async def monitor_fleet(self):
        """Continuous fleet monitoring loop"""
        while self.mesh_active:
            for worker_id, worker in self.worker_nodes.items():
                if worker.status == "active":
                    worker.last_heartbeat = datetime.now().isoformat()
            
            self._update_fleet_power()
            
            await asyncio.sleep(5)  # Check every 5 seconds

mesh_network = OmegaMeshNetwork()

if __name__ == "__main__":
    print("=" * 70)
    print("         OMEGA MESH NETWORK - Distributed Fleet Controller")
    print("=" * 70)
    print()
    
    mesh_network.initialize_mesh()
    
    print()
    print("Fleet Configuration:")
    print("  🔴 QUEEN: Full throttle (100% CPU)")
    print("  🐝 WORKER-1: 20% CPU cap (idle only)")
    print("  🐝 WORKER-2: 20% CPU cap (idle only)")
    print("  🐝 WORKER-3: 20% CPU cap (idle only)")
    print("  🐝 WORKER-4: 20% CPU cap (idle only)")
    print("  🐝 WORKER-5: 20% CPU cap (idle only)")
    print()
    print("Mesh Status: ACTIVE")
    print("Silent Mode: ENABLED (no snooping, no talking back)")
    print("=" * 70)
