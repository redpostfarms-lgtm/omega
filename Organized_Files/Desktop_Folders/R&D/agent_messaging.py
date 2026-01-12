# -*- coding: utf-8 -*-
# AGENT MESSAGING PROTOCOL - Real-time inter-agent communication
# Better than JSON files - real-time messaging system

import os
import sys
import json
import time
import socket
import threading
import queue
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Inter-agent message."""
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Any
    timestamp: float = 0.0
    message_id: str = ""
    reply_to: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.message_id:
            self.message_id = hashlib.md5(
                f"{self.from_agent}{self.to_agent}{self.timestamp}".encode()
            ).hexdigest()[:16]


class AgentMessaging:
    """
    Real-time messaging system for agents.
    
    Better than JSON files:
    - Real-time delivery
    - Async messaging
    - Message queues
    - Broadcast support
    """
    
    def __init__(self, agent_id: str, port: int = 9000):
        """Initialize messaging system."""
        self.agent_id = agent_id
        self.port = port
        self.connected_agents: Dict[str, int] = {}  # agent_id -> port
        self.message_queue: queue.Queue = queue.Queue()
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.running = False
        self.server_socket = None
        self.server_thread = None
        
    def start(self):
        """Start messaging server."""
        if self.running:
            return
        
        self.running = True
        self._start_server()
        self._start_message_processor()
        print(f"[Messaging] Agent {self.agent_id} started on port {self.port}")
    
    def stop(self):
        """Stop messaging server."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print(f"[Messaging] Agent {self.agent_id} stopped")
    
    def connect_agent(self, agent_id: str, host: str = 'localhost', port: int = None):
        """Connect to another agent."""
        if port is None:
            port = 9000 + len(self.connected_agents)
        
        self.connected_agents[agent_id] = {'host': host, 'port': port}
        print(f"[Messaging] Connected to agent {agent_id} at {host}:{port}")
    
    def send_message(self, to_agent: str, message_type: MessageType, 
                    content: Any, reply_to: Optional[str] = None) -> bool:
        """
        Send message to another agent.
        
        Args:
            to_agent: Target agent ID
            message_type: Type of message
            content: Message content
            reply_to: Optional message ID this is replying to
            
        Returns:
            True if sent successfully
        """
        if to_agent not in self.connected_agents:
            print(f"[Messaging] Agent {to_agent} not connected")
            return False
        
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            reply_to=reply_to
        )
        
        try:
            # Get agent connection info
            agent_info = self.connected_agents[to_agent]
            host = agent_info['host']
            port = agent_info['port']
            
            # Send via socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            # Serialize and send
            data = json.dumps(asdict(message)).encode('utf-8')
            sock.sendall(data)
            sock.close()
            
            return True
        
        except Exception as e:
            print(f"[Messaging] Send failed: {e}")
            return False
    
    def broadcast(self, message_type: MessageType, content: Any):
        """Broadcast message to all connected agents."""
        for agent_id in self.connected_agents:
            self.send_message(agent_id, message_type, content)
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register message handler."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def _start_server(self):
        """Start message receiving server."""
        def server_loop():
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                self.server_socket.bind(('localhost', self.port))
                self.server_socket.listen(5)
                
                while self.running:
                    try:
                        self.server_socket.settimeout(1.0)
                        conn, addr = self.server_socket.accept()
                        
                        # Receive message
                        data = conn.recv(4096)
                        if data:
                            message_dict = json.loads(data.decode('utf-8'))
                            message = AgentMessage(**message_dict)
                            self.message_queue.put(message)
                        
                        conn.close()
                    except socket.timeout:
                        continue
                    except Exception:
                        break
            except Exception as e:
                print(f"[Messaging] Server error: {e}")
        
        self.server_thread = threading.Thread(target=server_loop, daemon=True)
        self.server_thread.start()
    
    def _start_message_processor(self):
        """Start processing incoming messages."""
        def processor_loop():
            while self.running:
                try:
                    message = self.message_queue.get(timeout=1.0)
                    
                    # Handle message
                    handlers = self.message_handlers.get(message.message_type, [])
                    for handler in handlers:
                        try:
                            handler(message)
                        except Exception as e:
                            print(f"[Messaging] Handler error: {e}")
                    
                    self.message_queue.task_done()
                except queue.Empty:
                    continue
        
        processor_thread = threading.Thread(target=processor_loop, daemon=True)
        processor_thread.start()


# Global message bus (optional)
class MessageBus:
    """Central message bus for agent coordination."""
    
    def __init__(self, port: int = 8888):
        """Initialize message bus."""
        self.port = port
        self.agents: Dict[str, AgentMessaging] = {}
        self.running = False
    
    def register_agent(self, agent: AgentMessaging):
        """Register agent with bus."""
        self.agents[agent.agent_id] = agent
        agent.start()
    
    def broadcast(self, message_type: MessageType, content: Any, 
                  exclude: Optional[str] = None):
        """Broadcast to all agents."""
        for agent_id, agent in self.agents.items():
            if agent_id != exclude:
                agent.broadcast(message_type, content)


if __name__ == '__main__':
    print("=" * 60)
    print("AGENT MESSAGING - Test")
    print("=" * 60)
    
    # Create two agents
    agent1 = AgentMessaging("agent_001", port=9001)
    agent2 = AgentMessaging("agent_002", port=9002)
    
    # Connect
    agent1.connect_agent("agent_002", port=9002)
    agent2.connect_agent("agent_001", port=9001)
    
    # Start
    agent1.start()
    agent2.start()
    
    # Register handlers
    def handle_request(message: AgentMessage):
        print(f"[Agent {message.to_agent}] Received: {message.content}")
    
    agent2.register_handler(MessageType.REQUEST, handle_request)
    
    # Send message
    time.sleep(0.5)  # Wait for servers to start
    agent1.send_message("agent_002", MessageType.REQUEST, "Hello from agent 1!")
    
    time.sleep(1)
    
    agent1.stop()
    agent2.stop()
    
    print("\n[OK] Messaging system ready")

