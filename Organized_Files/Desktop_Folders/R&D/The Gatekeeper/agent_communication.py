# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Agent Communication System
Agent-to-agent messaging and communication framework
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
COMMUNICATION_DIR = ARCHIVED / 'agent_communication'
COMMUNICATION_DIR.mkdir(parents=True, exist_ok=True)

class AgentCommunication:
    """Agent-to-agent communication system."""
    
    def __init__(self):
        self.agents = set()
        self.channels = {}
        self.message_queue = defaultdict(list)
        self.message_history = []
    
    def register_agent(self, agent_id: str):
        """Register an agent in the communication system."""
        self.agents.add(agent_id)
        if agent_id not in self.channels:
            self.channels[agent_id] = {
                'messages': [],
                'subscriptions': set()
            }
    
    def send_message(self, from_agent: str, to_agent: str, message: Any, message_type: str = 'text') -> bool:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message: Message content
            message_type: Type of message ('text', 'data', 'request', 'response')
        
        Returns:
            True if message sent successfully
        """
        if from_agent not in self.agents:
            self.register_agent(from_agent)
        if to_agent not in self.agents:
            self.register_agent(to_agent)
        
        message_obj = {
            'id': f"msg_{int(time.time() * 1000)}",
            'from': from_agent,
            'to': to_agent,
            'message': message,
            'type': message_type,
            'timestamp': time.time(),
            'delivered': False
        }
        
        # Add to recipient's message queue
        self.message_queue[to_agent].append(message_obj)
        
        # Add to recipient's channel
        if to_agent in self.channels:
            self.channels[to_agent]['messages'].append(message_obj)
            # Keep last 1000 messages per channel
            if len(self.channels[to_agent]['messages']) > 1000:
                self.channels[to_agent]['messages'] = self.channels[to_agent]['messages'][-1000:]
        
        # Add to history
        self.message_history.append(message_obj)
        if len(self.message_history) > 10000:
            self.message_history = self.message_history[-10000:]
        
        # Save message
        self._save_message(message_obj)
        
        return True
    
    def broadcast(self, from_agent: str, message: Any, message_type: str = 'text', exclude: Optional[List[str]] = None) -> int:
        """
        Broadcast a message to all registered agents.
        
        Args:
            from_agent: Sender agent ID
            message: Message content
            message_type: Type of message
            exclude: List of agent IDs to exclude from broadcast
        
        Returns:
            Number of agents that received the message
        """
        exclude = exclude or []
        recipients = [agent for agent in self.agents if agent != from_agent and agent not in exclude]
        
        sent_count = 0
        for recipient in recipients:
            if self.send_message(from_agent, recipient, message, message_type):
                sent_count += 1
        
        return sent_count
    
    def create_channel(self, channel_id: str, agent_ids: List[str]):
        """
        Create a communication channel for multiple agents.
        
        Args:
            channel_id: Unique channel identifier
            agent_ids: List of agent IDs in the channel
        """
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                self.register_agent(agent_id)
            self.channels[agent_id]['subscriptions'].add(channel_id)
        
        self.channels[channel_id] = {
            'type': 'channel',
            'members': agent_ids,
            'messages': []
        }
    
    def send_to_channel(self, from_agent: str, channel_id: str, message: Any, message_type: str = 'text') -> int:
        """
        Send a message to all agents in a channel.
        
        Args:
            from_agent: Sender agent ID
            channel_id: Channel ID
            message: Message content
            message_type: Type of message
        
        Returns:
            Number of agents that received the message
        """
        if channel_id not in self.channels:
            raise ValueError(f"Channel {channel_id} not found")
        
        channel = self.channels[channel_id]
        if channel['type'] != 'channel':
            raise ValueError(f"{channel_id} is not a channel")
        
        members = channel.get('members', [])
        exclude = [from_agent]
        
        sent_count = 0
        for member in members:
            if member != from_agent:
                if self.send_message(from_agent, member, message, message_type):
                    sent_count += 1
        
        # Also add to channel message log
        message_obj = {
            'id': f"msg_{int(time.time() * 1000)}",
            'from': from_agent,
            'to': channel_id,
            'message': message,
            'type': message_type,
            'timestamp': time.time()
        }
        channel['messages'].append(message_obj)
        if len(channel['messages']) > 1000:
            channel['messages'] = channel['messages'][-1000:]
        
        return sent_count
    
    def get_messages(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages for an agent.
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of messages to return
        
        Returns:
            List of messages
        """
        if agent_id not in self.channels:
            return []
        
        messages = self.channels[agent_id]['messages']
        return messages[-limit:]
    
    def get_unread_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get unread messages for an agent."""
        unread = [msg for msg in self.message_queue[agent_id] if not msg.get('delivered', False)]
        return unread
    
    def mark_message_delivered(self, agent_id: str, message_id: str):
        """Mark a message as delivered."""
        for msg in self.message_queue[agent_id]:
            if msg['id'] == message_id:
                msg['delivered'] = True
                break
        
        # Also mark in channel messages
        if agent_id in self.channels:
            for msg in self.channels[agent_id]['messages']:
                if msg['id'] == message_id:
                    msg['delivered'] = True
                    break
    
    def _save_message(self, message: Dict[str, Any]):
        """Save message to disk."""
        timestamp = int(message['timestamp'])
        date_str = time.strftime('%Y%m%d', time.gmtime(timestamp))
        message_file = COMMUNICATION_DIR / f"messages_{date_str}.json"
        
        # Load existing messages for this date
        messages = []
        if message_file.exists():
            try:
                with open(message_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            except:
                messages = []
        
        messages.append(message)
        
        # Keep last 10000 messages per day
        messages = messages[-10000:]
        
        with open(message_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    
    def get_communication_statistics(self) -> Dict[str, Any]:
        """Get communication statistics."""
        total_messages = len(self.message_history)
        messages_by_agent = defaultdict(int)
        
        for msg in self.message_history:
            messages_by_agent[msg['from']] += 1
            messages_by_agent[msg['to']] += 1
        
        return {
            'total_agents': len(self.agents),
            'total_channels': sum(1 for ch in self.channels.values() if ch.get('type') == 'channel'),
            'total_messages': total_messages,
            'messages_by_agent': dict(messages_by_agent),
            'queued_messages': {agent: len(queue) for agent, queue in self.message_queue.items()}
        }

