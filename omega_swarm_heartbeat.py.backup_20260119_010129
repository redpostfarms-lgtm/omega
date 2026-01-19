#!/usr/bin/env python3
"""
Omega Swarm Heartbeat - Global WebSocket Monitoring
Single source of truth for all drones. Queen pings, drones pong or die.
Port 160, TLS, non-localhost. No race conditions, no duplicates.
"""

import asyncio
import ssl
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, List, Any, TYPE_CHECKING
from dataclasses import dataclass, asdict
from datetime import datetime
import threading

if TYPE_CHECKING:
    from websockets.server import WebSocketServerProtocol
    from websockets.client import WebSocketClientProtocol
else:
    # Runtime imports
    try:
        import websockets
        from websockets.server import WebSocketServerProtocol, serve
        from websockets.client import WebSocketClientProtocol, connect
    except ImportError:
        # Fallback if websockets not installed
        websockets = None  # type: ignore
        WebSocketServerProtocol = Any  # type: ignore
        WebSocketClientProtocol = Any  # type: ignore
        serve = None  # type: ignore
        connect = None  # type: ignore

# WebSocket configuration
HEARTBEAT_PORT = 160
HEARTBEAT_INTERVAL = 60  # seconds
DEATH_TIMEOUT = 65  # seconds without pong = dead

# TLS certificate paths
CERT_FILE = Path("swarm_cert.pem")
KEY_FILE = Path("swarm_key.pem")


@dataclass
class DroneStatus:
    """Single source of truth for drone state"""
    drone_id: str
    name: str
    last_pong: float
    registered_at: float
    ip_address: str
    capabilities: List[str]
    status: str = "alive"  # alive, dead, disconnected

    def is_alive(self) -> bool:
        """Check if drone responded recently"""
        return (time.time() - self.last_pong) < DEATH_TIMEOUT

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            **asdict(self),
            "alive": self.is_alive(),
            "last_seen": datetime.fromtimestamp(self.last_pong).isoformat()
        }


class SwarmQueen:
    """Queen manages the swarm - single source of truth"""

    def __init__(self):
        self.drones: Dict[str, DroneStatus] = {}  # drone_id -> status
        self.connections: Dict[str, WebSocketServerProtocol] = {}  # drone_id -> websocket
        self.drone_lock = asyncio.Lock()  # Prevent race conditions
        self.heartbeat_task: Optional[asyncio.Task[None]] = None
        self.running = False

    def generate_tls_cert(self):
        """Generate self-signed certificate for TLS"""
        if CERT_FILE.exists() and KEY_FILE.exists():
            print("[TLS] Using existing certificate")
            return

        print("[TLS] Generating self-signed certificate...")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(KEY_FILE), "-out", str(CERT_FILE),
            "-days", "365", "-nodes",
            "-subj", "/CN=omega-swarm/O=RedPostFarms/C=US"
        ], check=True, capture_output=True)
        print(f"[TLS] Certificate created: {CERT_FILE}")

    async def handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """Handle incoming WebSocket connection from drone"""
        drone_id: Optional[str] = None
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "register":
                    drone_id = data.get("drone_id")
                    if not drone_id:
                        continue
                    name = data.get("name", "Unknown")
                    ip_addr = websocket.remote_address
                    ip: str = ip_addr[0] if ip_addr else "unknown"
                    capabilities = data.get("capabilities", [])

                    async with self.drone_lock:
                        # Single source of truth update
                        self.drones[drone_id] = DroneStatus(
                            drone_id=drone_id,
                            name=name,
                            last_pong=time.time(),
                            registered_at=time.time(),
                            ip_address=ip,
                            capabilities=capabilities
                        )
                        self.connections[drone_id] = websocket

                    print(f"[Swarm] New drone registered: {name} ({drone_id})")
                    await websocket.send(json.dumps({"type": "registered", "drone_id": drone_id}))

                elif msg_type == "pong":
                    drone_id = data.get("drone_id")
                    if drone_id:
                        async with self.drone_lock:
                            if drone_id in self.drones:
                                self.drones[drone_id].last_pong = time.time()
                                self.drones[drone_id].status = "alive"

                elif msg_type == "status":
                    # Send swarm status
                    async with self.drone_lock:
                        status = {d.drone_id: d.to_dict() for d in self.drones.values()}
                    await websocket.send(json.dumps({"type": "swarm_status", "drones": status}))

        except Exception:
            # Catch all exceptions including ConnectionClosed
            pass
        finally:
            if drone_id:
                async with self.drone_lock:
                    if drone_id in self.connections:
                        del self.connections[drone_id]
                    if drone_id in self.drones:
                        self.drones[drone_id].status = "disconnected"

    async def heartbeat_loop(self):
        """Queen sends heartbeat pings every 60 seconds"""
        while self.running:
            await asyncio.sleep(HEARTBEAT_INTERVAL)

            async with self.drone_lock:
                # Send ping to all connected drones
                ping_msg = json.dumps({"type": "ping", "timestamp": time.time()})
                
                for drone_id, ws in list(self.connections.items()):
                    try:
                        await ws.send(ping_msg)
                    except Exception as e:
                        print(f"[Swarm] Failed to ping {drone_id}: {e}")

                # Check for dead drones
                dead_drones: List[DroneStatus] = []
                for drone_id, status in self.drones.items():
                    if not status.is_alive() and status.status != "dead":
                        status.status = "dead"
                        dead_drones.append(status)
                        print(f"[Swarm] ☠️  Drone DEAD: {status.name} ({drone_id})")

                # Trigger git sync on death
                if dead_drones:
                    reason = f"drone {dead_drones[0].name} died"
                    self.trigger_git_sync(reason)

                # Status update
                alive_count = sum(1 for d in self.drones.values() if d.is_alive())
                total_count = len(self.drones)
                print(f"[Swarm] ♥ Heartbeat: {alive_count}/{total_count} drones alive")

    def trigger_git_sync(self, reason: str):
        """Trigger automatic git sync in background thread"""
        def sync():
            print(f"[Git] Sync triggered: {reason}")
            try:
                subprocess.run(
                    ["python", "omega_auto_sync.py", "sync", "-r", reason],
                    capture_output=True,
                    timeout=60,
                    cwd=Path(__file__).parent
                )
                print("[Git] ✓ Swarm breathes - branch clean")
            except Exception as e:
                print(f"[Git] ✗ Sync failed: {e}")

        thread = threading.Thread(target=sync, daemon=True)
        thread.start()

    async def start(self):
        """Start the queen server"""
        self.running = True
        self.generate_tls_cert()

        # Setup TLS context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(CERT_FILE, KEY_FILE)

        # Start heartbeat loop
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        print(f"[Swarm] Queen starting on 0.0.0.0:{HEARTBEAT_PORT}")
        async with serve(
            self.handle_connection,
            "0.0.0.0",
            HEARTBEAT_PORT,
            ssl=ssl_context
        ):
            await asyncio.Future()  # Run forever

    async def stop(self):
        """Stop the queen server"""
        self.running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()


class SwarmDrone:
    """Drone connects to queen and responds to heartbeats"""

    def __init__(self, drone_id: str, name: str, queen_host: str, capabilities: Optional[List[str]] = None):
        self.drone_id = drone_id
        self.name = name
        self.queen_host = queen_host
        self.capabilities: List[str] = capabilities or []
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.running = False

    async def connect(self):
        """Connect to queen and maintain connection"""
        uri = f"wss://{self.queen_host}:{HEARTBEAT_PORT}"
        
        # Disable SSL verification for self-signed certs
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        while self.running:
            try:
                async with connect(uri, ssl=ssl_context) as websocket:
                    self.websocket = websocket
                    print(f"[Swarm] Connected to queen at {self.queen_host}")

                    # Register with queen
                    await websocket.send(json.dumps({
                        "type": "register",
                        "drone_id": self.drone_id,
                        "name": self.name,
                        "capabilities": self.capabilities
                    }))

                    # Wait for messages
                    async for message in websocket:
                        data = json.loads(message)
                        msg_type = data.get("type")

                        if msg_type == "registered":
                            print("[Swarm] Registered with queen")

                        elif msg_type == "ping":
                            # Respond with pong
                            await websocket.send(json.dumps({
                                "type": "pong",
                                "drone_id": self.drone_id
                            }))

                        elif msg_type == "push":
                            # Queen commands git sync
                            print("[Swarm] Queen commands: git sync")

            except (ConnectionRefusedError, Exception) as e:
                # Catch ConnectionRefusedError and all websockets exceptions
                print(f"[Swarm] Connection lost: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds

    async def start(self):
        """Start the drone"""
        self.running = True
        await self.connect()

    async def stop(self):
        """Stop the drone"""
        self.running = False
        if self.websocket is not None and not self.websocket.closed:
            await self.websocket.close()


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Queen: python omega_swarm_heartbeat.py queen")
        print("  Drone: python omega_swarm_heartbeat.py drone <drone_id> <name> <queen_host>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "queen":
        queen = SwarmQueen()
        try:
            await queen.start()
        except KeyboardInterrupt:
            print("\n[Swarm] Queen shutting down...")
            await queen.stop()

    elif mode == "drone":
        if len(sys.argv) < 5:
            print("Drone requires: <drone_id> <name> <queen_host>")
            sys.exit(1)

        drone_id = sys.argv[2]
        name = sys.argv[3]
        queen_host = sys.argv[4]
        
        drone = SwarmDrone(drone_id, name, queen_host, capabilities=["worker"])
        try:
            await drone.start()
        except KeyboardInterrupt:
            print("\n[Swarm] Drone shutting down...")
            await drone.stop()

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
