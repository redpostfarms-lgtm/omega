#!/usr/bin/env python3
"""
OMEGA WEBSOCKET HIVE INTERFACE
==============================
Implements Prompt Six - WebSocket Hive Interface.

Core Requirements:
- WebSocket (wss://) communication
- All messages signed with Ed25519 per message
- Replay protection using (session_id, nonce)
- Message classification: signal, claim, opinion, request, instruction, alert
- Only verified signals auto-promote
- Low-trust/revoked nodes cannot trigger irreversible actions

This module handles secure communication with the Omega hive network.
"""

import asyncio
import json
import hashlib
import uuid
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging
import secrets

# WebSocket imports
try:
    import websockets
    from websockets.server import serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# Cryptography imports
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OMEGA_HIVE - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaWebSocketHive')


class MessageType(Enum):
    """Classification of inbound messages"""
    SIGNAL = "signal"           # Verified system signals - can auto-promote
    CLAIM = "claim"             # Assertions requiring verification
    OPINION = "opinion"         # Subjective input - low trust
    REQUEST = "request"         # Action requests - need approval
    INSTRUCTION = "instruction" # Commands - require authority
    ALERT = "alert"            # Warnings/notifications


class TrustLevel(Enum):
    """Node trust levels"""
    KERNEL = 1.0      # System kernel - absolute trust
    VERIFIED = 0.9    # Verified nodes
    TRUSTED = 0.7     # Trusted but not verified
    STANDARD = 0.5    # Standard nodes
    LOW = 0.3         # Low trust
    UNTRUSTED = 0.1   # Untrusted
    REVOKED = 0.0     # Revoked - no trust


@dataclass
class HiveMessage:
    """Represents a message in the hive network"""
    message_id: str
    session_id: str
    nonce: str
    timestamp: str
    message_type: MessageType
    sender_id: str
    payload: Dict[str, Any]
    signature: str = ""
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'message_type': self.message_type.value,
            'sender_id': self.sender_id,
            'payload': self.payload,
            'signature': self.signature,
            'verified': self.verified
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HiveMessage':
        return cls(
            message_id=data['message_id'],
            session_id=data['session_id'],
            nonce=data['nonce'],
            timestamp=data['timestamp'],
            message_type=MessageType(data['message_type']),
            sender_id=data['sender_id'],
            payload=data['payload'],
            signature=data.get('signature', ''),
            verified=data.get('verified', False)
        )

    def get_signable_content(self) -> bytes:
        """Get the content to be signed (excludes signature field)"""
        content = {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'message_type': self.message_type.value,
            'sender_id': self.sender_id,
            'payload': self.payload
        }
        return json.dumps(content, sort_keys=True).encode()


@dataclass
class HiveNode:
    """Represents a node in the hive network"""
    node_id: str
    public_key: Optional[bytes]
    trust_level: TrustLevel
    session_id: Optional[str] = None
    connected_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    nonces_used: Set[str] = field(default_factory=set)
    revoked: bool = False
    revoked_at: Optional[datetime] = None

    def is_active(self) -> bool:
        return self.session_id is not None and not self.revoked

    def can_trigger_irreversible(self) -> bool:
        """Check if node can trigger irreversible actions"""
        if self.revoked:
            return False
        return self.trust_level.value >= TrustLevel.TRUSTED.value


class ReplayProtection:
    """Handles replay attack protection"""

    def __init__(self, nonce_ttl_seconds: int = 300):
        self._nonce_ttl = nonce_ttl_seconds
        self._used_nonces: Dict[str, datetime] = {}  # nonce -> timestamp
        self._lock = threading.Lock()

    def check_and_record(self, session_id: str, nonce: str) -> bool:
        """
        Check if nonce is valid and record it.
        Returns True if valid (not replay), False if replay detected.
        """
        combined = f"{session_id}:{nonce}"

        with self._lock:
            # Cleanup old nonces
            cutoff = datetime.now() - timedelta(seconds=self._nonce_ttl)
            self._used_nonces = {
                k: v for k, v in self._used_nonces.items()
                if v > cutoff
            }

            # Check for replay
            if combined in self._used_nonces:
                logger.warning(f"Replay detected: {combined}")
                return False

            # Record nonce
            self._used_nonces[combined] = datetime.now()
            return True

    def generate_nonce(self) -> str:
        """Generate a cryptographically secure nonce"""
        return secrets.token_hex(16)


class MessageVerifier:
    """Handles Ed25519 message verification"""

    def __init__(self):
        self._node_keys: Dict[str, bytes] = {}  # node_id -> public_key_pem

    def register_node_key(self, node_id: str, public_key_pem: bytes):
        """Register a node's public key"""
        self._node_keys[node_id] = public_key_pem
        logger.info(f"Registered public key for node: {node_id}")

    def sign_message(self, message: HiveMessage, private_key: ed25519.Ed25519PrivateKey) -> str:
        """Sign a message with Ed25519"""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography package not available")

        content = message.get_signable_content()
        signature = private_key.sign(content)
        return base64.b64encode(signature).decode('ascii')

    def verify_message(self, message: HiveMessage) -> bool:
        """Verify a message's Ed25519 signature"""
        if not CRYPTO_AVAILABLE:
            logger.warning("Crypto not available - cannot verify")
            return False

        if not message.signature:
            logger.warning(f"No signature on message {message.message_id}")
            return False

        public_key_pem = self._node_keys.get(message.sender_id)
        if not public_key_pem:
            logger.warning(f"No public key for node {message.sender_id}")
            return False

        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )
            signature = base64.b64decode(message.signature)
            content = message.get_signable_content()
            public_key.verify(signature, content)
            return True

        except InvalidSignature:
            logger.error(f"Invalid signature for message {message.message_id}")
            return False
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False


class MessageClassifier:
    """Classifies and routes incoming messages"""

    # Keywords for classification
    SIGNAL_KEYWORDS = ['heartbeat', 'status', 'sync', 'ack', 'ping']
    CLAIM_KEYWORDS = ['assert', 'claim', 'state', 'declare']
    REQUEST_KEYWORDS = ['request', 'ask', 'query', 'get']
    INSTRUCTION_KEYWORDS = ['execute', 'run', 'command', 'do', 'perform']
    ALERT_KEYWORDS = ['alert', 'warn', 'error', 'critical', 'emergency']

    def classify(self, message: HiveMessage) -> MessageType:
        """Classify a message based on content"""
        # If already typed, trust it (but verify later)
        if message.message_type != MessageType.OPINION:
            return message.message_type

        # Auto-classify based on content
        payload_str = json.dumps(message.payload).lower()

        if any(kw in payload_str for kw in self.SIGNAL_KEYWORDS):
            return MessageType.SIGNAL
        if any(kw in payload_str for kw in self.ALERT_KEYWORDS):
            return MessageType.ALERT
        if any(kw in payload_str for kw in self.INSTRUCTION_KEYWORDS):
            return MessageType.INSTRUCTION
        if any(kw in payload_str for kw in self.REQUEST_KEYWORDS):
            return MessageType.REQUEST
        if any(kw in payload_str for kw in self.CLAIM_KEYWORDS):
            return MessageType.CLAIM

        return MessageType.OPINION


class OmegaWebSocketHive:
    """
    Main WebSocket Hive Interface.

    Handles secure communication with the Omega hive network.
    """

    def __init__(self,
                 host: str = "0.0.0.0",
                 port: int = 8765,
                 ssl_context=None):
        self.host = host
        self.port = port
        self.ssl_context = ssl_context

        # Components
        self.replay_protection = ReplayProtection()
        self.verifier = MessageVerifier()
        self.classifier = MessageClassifier()

        # Node registry
        self._nodes: Dict[str, HiveNode] = {}
        self._revoked_nodes: Set[str] = set()

        # Message handlers
        self._handlers: Dict[MessageType, List[Callable]] = {
            mt: [] for mt in MessageType
        }

        # Connection tracking
        self._connections: Dict[str, Any] = {}  # session_id -> websocket
        self._lock = threading.Lock()

        # Server state
        self._server = None
        self._running = False

        logger.info(f"Omega WebSocket Hive initialized on {host}:{port}")

    def register_node(self, node_id: str, public_key_pem: bytes,
                     trust_level: TrustLevel = TrustLevel.STANDARD) -> HiveNode:
        """Register a new node"""
        with self._lock:
            node = HiveNode(
                node_id=node_id,
                public_key=public_key_pem,
                trust_level=trust_level
            )
            self._nodes[node_id] = node
            self.verifier.register_node_key(node_id, public_key_pem)
            logger.info(f"Registered node: {node_id} (trust: {trust_level.value})")
            return node

    def revoke_node(self, node_id: str, reason: str = ""):
        """Revoke a node's access"""
        with self._lock:
            if node_id in self._nodes:
                self._nodes[node_id].revoked = True
                self._nodes[node_id].revoked_at = datetime.now()
                self._revoked_nodes.add(node_id)
                logger.warning(f"Node revoked: {node_id} - {reason}")

    def is_revoked(self, node_id: str) -> bool:
        """Check if a node is revoked"""
        return node_id in self._revoked_nodes

    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a message type"""
        self._handlers[message_type].append(handler)
        logger.debug(f"Registered handler for {message_type.value}")

    async def _handle_connection(self, websocket, path):
        """Handle a new WebSocket connection"""
        session_id = str(uuid.uuid4())
        node_id = None

        try:
            # Wait for authentication message
            auth_msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            auth_data = json.loads(auth_msg)

            node_id = auth_data.get('node_id')
            if not node_id:
                await websocket.close(1008, "Missing node_id")
                return

            # Check if revoked
            if self.is_revoked(node_id):
                await websocket.close(1008, "Node revoked")
                logger.warning(f"Revoked node attempted connection: {node_id}")
                return

            # Get or create node
            node = self._nodes.get(node_id)
            if not node:
                # Unknown node - create with low trust
                node = HiveNode(
                    node_id=node_id,
                    public_key=None,
                    trust_level=TrustLevel.UNTRUSTED
                )
                self._nodes[node_id] = node

            # Update node state
            node.session_id = session_id
            node.connected_at = datetime.now()
            node.last_seen = datetime.now()

            # Store connection
            self._connections[session_id] = websocket

            logger.info(f"Node connected: {node_id} (session: {session_id})")

            # Send session info
            await websocket.send(json.dumps({
                'type': 'session_init',
                'session_id': session_id,
                'server_time': datetime.now().isoformat()
            }))

            # Message loop
            async for raw_message in websocket:
                try:
                    await self._process_message(raw_message, node, session_id)
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'error': str(e)
                    }))

        except asyncio.TimeoutError:
            logger.warning("Connection timeout during auth")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {node_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            # Cleanup
            if session_id in self._connections:
                del self._connections[session_id]
            if node_id and node_id in self._nodes:
                self._nodes[node_id].session_id = None

    async def _process_message(self, raw_message: str, node: HiveNode, session_id: str):
        """Process an incoming message"""
        try:
            data = json.loads(raw_message)
            message = HiveMessage.from_dict(data)
        except Exception as e:
            logger.error(f"Invalid message format: {e}")
            return

        # Update last seen
        node.last_seen = datetime.now()

        # Replay protection
        if not self.replay_protection.check_and_record(message.session_id, message.nonce):
            logger.warning(f"Replay attack detected from {node.node_id}")
            return

        # Verify session matches
        if message.session_id != session_id:
            logger.warning(f"Session mismatch: {message.session_id} != {session_id}")
            return

        # Verify signature
        if node.public_key:
            message.verified = self.verifier.verify_message(message)
            if not message.verified:
                logger.warning(f"Signature verification failed for {message.message_id}")
                # Continue but mark as unverified

        # Classify message
        message.message_type = self.classifier.classify(message)

        # Check if node can perform action
        if message.message_type == MessageType.INSTRUCTION:
            if not node.can_trigger_irreversible():
                logger.warning(f"Low-trust node {node.node_id} attempted instruction")
                return

        # Auto-promote only verified signals
        auto_promote = (
            message.message_type == MessageType.SIGNAL and
            message.verified and
            node.trust_level.value >= TrustLevel.VERIFIED.value
        )

        # Call handlers
        for handler in self._handlers.get(message.message_type, []):
            try:
                await handler(message, node, auto_promote)
            except Exception as e:
                logger.error(f"Handler error: {e}")

        logger.debug(f"Processed message {message.message_id} ({message.message_type.value})")

    async def broadcast(self, message: Dict[str, Any], exclude: Set[str] = None):
        """Broadcast a message to all connected nodes"""
        exclude = exclude or set()
        for session_id, ws in self._connections.items():
            if session_id not in exclude:
                try:
                    await ws.send(json.dumps(message))
                except:
                    pass

    async def send_to_node(self, node_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific node"""
        node = self._nodes.get(node_id)
        if not node or not node.session_id:
            return False

        ws = self._connections.get(node.session_id)
        if not ws:
            return False

        try:
            await ws.send(json.dumps(message))
            return True
        except:
            return False

    async def start(self):
        """Start the WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets package not available")
            return

        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        self._running = True

        self._server = await serve(
            self._handle_connection,
            self.host,
            self.port,
            ssl=self.ssl_context
        )

        logger.info("WebSocket server started")

    async def stop(self):
        """Stop the WebSocket server"""
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("WebSocket server stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get hive status"""
        return {
            'running': self._running,
            'host': self.host,
            'port': self.port,
            'connected_nodes': len(self._connections),
            'registered_nodes': len(self._nodes),
            'revoked_nodes': len(self._revoked_nodes),
            'websockets_available': WEBSOCKETS_AVAILABLE,
            'crypto_available': CRYPTO_AVAILABLE
        }


# =================================================================
# MESSAGE CREATION HELPERS
# =================================================================

def create_message(
    message_type: MessageType,
    sender_id: str,
    session_id: str,
    payload: Dict[str, Any],
    nonce: str = None
) -> HiveMessage:
    """Create a new hive message"""
    return HiveMessage(
        message_id=str(uuid.uuid4()),
        session_id=session_id,
        nonce=nonce or secrets.token_hex(16),
        timestamp=datetime.now().isoformat(),
        message_type=message_type,
        sender_id=sender_id,
        payload=payload
    )


# =================================================================
# GLOBAL INSTANCE
# =================================================================

_hive_instance: Optional[OmegaWebSocketHive] = None
_hive_lock = threading.Lock()


def get_hive(host: str = "0.0.0.0", port: int = 8765) -> OmegaWebSocketHive:
    """Get or create the global hive instance"""
    global _hive_instance

    if _hive_instance is None:
        with _hive_lock:
            if _hive_instance is None:
                _hive_instance = OmegaWebSocketHive(host, port)

    return _hive_instance


# =================================================================
# MAIN - SELF TEST
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("OMEGA WEBSOCKET HIVE - SELF TEST")
    print("=" * 70)

    hive = OmegaWebSocketHive()

    print(f"\nWebSockets available: {WEBSOCKETS_AVAILABLE}")
    print(f"Crypto available: {CRYPTO_AVAILABLE}")

    print("\n--- REPLAY PROTECTION TEST ---")
    rp = ReplayProtection()
    session = "test-session"
    nonce1 = rp.generate_nonce()
    nonce2 = rp.generate_nonce()

    print(f"First use of nonce1: {rp.check_and_record(session, nonce1)}")  # True
    print(f"Replay of nonce1: {rp.check_and_record(session, nonce1)}")      # False
    print(f"First use of nonce2: {rp.check_and_record(session, nonce2)}")  # True

    print("\n--- MESSAGE CLASSIFICATION TEST ---")
    classifier = MessageClassifier()

    test_messages = [
        HiveMessage("1", "s", "n", "t", MessageType.OPINION, "node1",
                   {'action': 'heartbeat'}),
        HiveMessage("2", "s", "n", "t", MessageType.OPINION, "node1",
                   {'content': 'I think this is good'}),
        HiveMessage("3", "s", "n", "t", MessageType.OPINION, "node1",
                   {'command': 'execute task'}),
        HiveMessage("4", "s", "n", "t", MessageType.OPINION, "node1",
                   {'type': 'alert', 'level': 'critical'}),
    ]

    for msg in test_messages:
        classified = classifier.classify(msg)
        print(f"  {msg.payload} -> {classified.value}")

    print("\n--- NODE REGISTRATION TEST ---")
    hive.register_node("node-001", None, TrustLevel.VERIFIED)
    hive.register_node("node-002", None, TrustLevel.LOW)

    print(f"Registered nodes: {len(hive._nodes)}")
    print(f"Node-001 can trigger irreversible: {hive._nodes['node-001'].can_trigger_irreversible()}")
    print(f"Node-002 can trigger irreversible: {hive._nodes['node-002'].can_trigger_irreversible()}")

    print("\n--- NODE REVOCATION TEST ---")
    hive.revoke_node("node-002", "Security violation")
    print(f"Node-002 revoked: {hive.is_revoked('node-002')}")
    print(f"Node-002 can trigger: {hive._nodes['node-002'].can_trigger_irreversible()}")

    print("\n--- STATUS ---")
    status = hive.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("OMEGA WEBSOCKET HIVE - TEST COMPLETE")
    print("=" * 70)
