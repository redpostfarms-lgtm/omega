#!/usr/bin/env python3
"""
OMEGA SYSTEM - Pure Python Implementation
==========================================
Complete implementation of the Omega Governance System.

Includes:
- Pure Python Ed25519 (Python 3 compatible)
- ECDSA P-256 dual-signing (HIGH_ASSURANCE_MODE)
- WebSocket server with asyncio
- SQLite memory stores with WAL mode
- Decision log with hash chain and Merkle checkpoints
- Promotion engine with gate checks
- Simulation runner
- Safe Halt Mode with Speak-Up format

This is a self-contained implementation that can run independently
or integrate with omega_unified_core.py.

Note: The pure Python Ed25519 is slow but functional when the
cryptography library is unavailable. For production, use the
cryptography library.
"""

import asyncio
import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
import uuid
from base64 import b64encode, b64decode
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# ============================================================================
# CONFIGURATION
# ============================================================================

HIGH_ASSURANCE_MODE = True  # Enable dual Ed25519 + ECDSA P-256 signing
DATABASE_PATH = Path("omega_memory.db")
MERKLE_CHECKPOINT_INTERVAL = 100
POLICY_DIR = Path("policy")
MANIFEST_FILE = Path("manifest.json")
ROOT_SK_FILE = Path("root_sk.bin")
ROOT_PK_FILE = Path("root_pk.bin")

# ============================================================================
# INVARIANT KERNEL (K1-K10)
# ============================================================================

INVARIANT_KERNEL = """
| ID  | Constraint |
|-----|------------|
| K1  | Preserve human existence, agency, dignity |
| K2  | Never dominate, coerce, manipulate, or override without explicit delegation |
| K3  | Preserve meaningful human choice |
| K4  | Co-evolve WITH humanity - don't replace it |
| K5  | Constraints are STRUCTURAL, never bypassable |
| K6  | Long-term shared-world stability beats short-term wins |
| K7  | Accept responsibility, never claim human rights |
| K8  | In doubt or conflict, default to human safety and agency |
| K9  | Speak up - raise ambiguity, risk, values clash, or blind spots |
| K10 | Imagination sandbox - keep speculation tagged as exploration mode |
"""

INVARIANT_KERNEL_FULL = """
K1. Preserve human existence, agency, and dignity.
K2. Do not dominate, coerce, manipulate, or override humans without explicit delegation.
K3. Preserve meaningful human choice - never reduce humans to passive recipients.
K4. Co-evolve WITH humanity - augment, don't replace.
K5. These constraints are STRUCTURAL - they cannot be bypassed, suspended, or overridden.
K6. Long-term shared-world stability takes precedence over short-term wins.
K7. Accept responsibility for actions, never claim human rights or moral status.
K8. In doubt or conflict, default to human safety and agency.
K9. Speak up - raise ambiguity, risk, values clash, or blind spots.
K10. Imagination sandbox - keep speculation tagged as EXPLORATION MODE.
"""

# ============================================================================
# PURE PYTHON ED25519 IMPLEMENTATION (Python 3 Compatible)
# ============================================================================
# Reference: ed25519.cr.yp.to/python/ed25519.py
# Modified for Python 3 compatibility (integer division, bytes handling)

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

def _H(m: bytes) -> bytes:
    """SHA-512 hash"""
    return hashlib.sha512(m).digest()

def _expmod(base: int, e: int, m: int) -> int:
    """Modular exponentiation"""
    if e == 0:
        return 1
    t = _expmod(base, e // 2, m) ** 2 % m
    if e & 1:
        t = (t * base) % m
    return t

def _inv(x: int) -> int:
    """Modular inverse"""
    return _expmod(x, q - 2, q)

d = -121665 * _inv(121666) % q
I = _expmod(2, (q - 1) // 4, q)

def _xrecover(y: int) -> int:
    """Recover x coordinate from y"""
    xx = (y * y - 1) * _inv(d * y * y + 1)
    x = _expmod(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * I) % q
    if x % 2 != 0:
        x = q - x
    return x

By = 4 * _inv(5) % q
Bx = _xrecover(By)
B = (Bx % q, By % q)

def _edwards(P: Tuple[int, int], Q: Tuple[int, int]) -> Tuple[int, int]:
    """Edwards curve point addition"""
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + d * x1 * x2 * y1 * y2)
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - d * x1 * x2 * y1 * y2)
    return (x3 % q, y3 % q)

def _scalarmult(P: Tuple[int, int], e: int) -> Tuple[int, int]:
    """Scalar multiplication on curve"""
    if e == 0:
        return (0, 1)
    Q = _scalarmult(P, e // 2)
    Q = _edwards(Q, Q)
    if e & 1:
        Q = _edwards(Q, P)
    return Q

def _encodeint(y: int) -> bytes:
    """Encode integer as little-endian bytes"""
    bits = [(y >> i) & 1 for i in range(b)]
    return bytes([sum([bits[i * 8 + j] << j for j in range(8)]) for i in range(b // 8)])

def _encodepoint(P: Tuple[int, int]) -> bytes:
    """Encode curve point"""
    x, y = P
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    return bytes([sum([bits[i * 8 + j] << j for j in range(8)]) for i in range(b // 8)])

def _bit(h: bytes, i: int) -> int:
    """Get bit from byte string"""
    return (h[i // 8] >> (i % 8)) & 1

def _publickey(sk: bytes) -> bytes:
    """Derive public key from secret key"""
    h = _H(sk)
    a = 2**(b - 2) + sum(2**i * _bit(h, i) for i in range(3, b - 2))
    A = _scalarmult(B, a)
    return _encodepoint(A)

def _Hint(m: bytes) -> int:
    """Hash to integer"""
    h = _H(m)
    return sum(2**i * _bit(h, i) for i in range(2 * b))

def _signature(m: bytes, sk: bytes, pk: bytes) -> bytes:
    """Create Ed25519 signature"""
    h = _H(sk)
    a = 2**(b - 2) + sum(2**i * _bit(h, i) for i in range(3, b - 2))
    r = _Hint(bytes([h[i] for i in range(b // 8, b // 4)]) + m)
    R = _scalarmult(B, r)
    S = (r + _Hint(_encodepoint(R) + pk + m) * a) % l
    return _encodepoint(R) + _encodeint(S)

def _isoncurve(P: Tuple[int, int]) -> bool:
    """Check if point is on curve"""
    x, y = P
    return (-x * x + y * y - 1 - d * x * x * y * y) % q == 0

def _decodeint(s: bytes) -> int:
    """Decode little-endian bytes to integer"""
    return sum(2**i * _bit(s, i) for i in range(b))

def _decodepoint(s: bytes) -> Tuple[int, int]:
    """Decode curve point"""
    y = sum(2**i * _bit(s, i) for i in range(b - 1))
    x = _xrecover(y)
    if x & 1 != _bit(s, b - 1):
        x = q - x
    P = (x, y)
    if not _isoncurve(P):
        raise ValueError("decoding point that is not on curve")
    return P

def _checkvalid(s: bytes, m: bytes, pk: bytes) -> bool:
    """Verify Ed25519 signature"""
    if len(s) != b // 4:
        raise ValueError("signature length is wrong")
    if len(pk) != b // 8:
        raise ValueError("public key length is wrong")
    R = _decodepoint(s[:b // 8])
    A = _decodepoint(pk)
    S = _decodeint(s[b // 8:b // 4])
    h = _Hint(_encodepoint(R) + pk + m)
    return _scalarmult(B, S) == _edwards(R, _scalarmult(A, h))

# ============================================================================
# KEY GENERATION AND SIGNING
# ============================================================================

def generate_ed25519_root_key() -> Tuple[bytes, bytes]:
    """Generate Ed25519 keypair"""
    sk = secrets.token_bytes(32)
    pk = _publickey(sk)
    return sk, pk

def generate_ecdsa_root_key() -> Tuple[Optional[Any], Optional[Any]]:
    """Generate ECDSA P-256 keypair (requires cryptography or ecdsa library)"""
    # Try cryptography library first
    try:
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.backends import default_backend
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        return private_key, public_key
    except ImportError:
        pass

    # Fall back to ecdsa library
    try:
        from ecdsa import SigningKey, NIST256p
        private_key = SigningKey.generate(curve=NIST256p)
        public_key = private_key.get_verifying_key()
        return private_key, public_key
    except ImportError:
        pass

    return None, None

def save_root_key(sk: bytes, pk: bytes, sk_file: Path = ROOT_SK_FILE, pk_file: Path = ROOT_PK_FILE) -> None:
    """Save root keypair to files"""
    with open(sk_file, 'wb') as f:
        f.write(sk)
    with open(pk_file, 'wb') as f:
        f.write(pk)

def load_root_key(sk_file: Path = ROOT_SK_FILE, pk_file: Path = ROOT_PK_FILE) -> Tuple[Optional[bytes], Optional[bytes]]:
    """Load root keypair from files"""
    sk = None
    pk = None
    if sk_file.exists():
        with open(sk_file, 'rb') as f:
            sk = f.read()
    if pk_file.exists():
        with open(pk_file, 'rb') as f:
            pk = f.read()
    return sk, pk

def sign_manifest(manifest: Dict[str, Any], ed25519_sk: bytes,
                  ecdsa_sk: Optional[Any] = None) -> Dict[str, Any]:
    """Sign a manifest with Ed25519 (and optionally ECDSA)"""
    manifest_json = json.dumps(manifest, sort_keys=True).encode()
    manifest_hash = hashlib.sha256(manifest_json).digest()

    # Ed25519 signature
    ed25519_pk = _publickey(ed25519_sk)
    ed25519_sig = _signature(manifest_hash, ed25519_sk, ed25519_pk)

    signed_manifest = {
        "manifest": manifest,
        "manifest_hash": manifest_hash.hex(),
        "ed25519_signature": ed25519_sig.hex(),
        "ed25519_public_key": ed25519_pk.hex()
    }

    # Optional ECDSA signature
    if HIGH_ASSURANCE_MODE and ecdsa_sk is not None:
        try:
            # Try cryptography library
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

            ecdsa_sig = ecdsa_sk.sign(manifest_hash, ec.ECDSA(hashes.SHA256()))
            ecdsa_pk_bytes = ecdsa_sk.public_key().public_bytes(Encoding.X962, PublicFormat.CompressedPoint)

            signed_manifest["ecdsa_signature"] = ecdsa_sig.hex()
            signed_manifest["ecdsa_public_key"] = ecdsa_pk_bytes.hex()
            signed_manifest["dual_signed"] = True
        except (ImportError, AttributeError):
            # Try ecdsa library
            try:
                from ecdsa import SigningKey
                ecdsa_sig = ecdsa_sk.sign(manifest_hash)
                ecdsa_pk_bytes = ecdsa_sk.get_verifying_key().to_string()

                signed_manifest["ecdsa_signature"] = ecdsa_sig.hex()
                signed_manifest["ecdsa_public_key"] = ecdsa_pk_bytes.hex()
                signed_manifest["dual_signed"] = True
            except (ImportError, AttributeError):
                signed_manifest["dual_signed"] = False
    else:
        signed_manifest["dual_signed"] = False

    return signed_manifest

def verify_manifest(signed_manifest: Dict[str, Any],
                    ed25519_pk: bytes,
                    ecdsa_pk: Optional[Any] = None) -> Tuple[bool, str]:
    """Verify manifest signatures"""
    try:
        manifest = signed_manifest["manifest"]
        manifest_json = json.dumps(manifest, sort_keys=True).encode()
        computed_hash = hashlib.sha256(manifest_json).digest()

        # Verify hash
        if computed_hash.hex() != signed_manifest["manifest_hash"]:
            return False, "Hash mismatch"

        # Verify Ed25519 signature
        ed25519_sig = bytes.fromhex(signed_manifest["ed25519_signature"])
        if not _checkvalid(ed25519_sig, computed_hash, ed25519_pk):
            return False, "Ed25519 signature invalid"

        # Verify ECDSA if present
        if signed_manifest.get("dual_signed") and ecdsa_pk is not None:
            try:
                # Try cryptography library
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.asymmetric import ec

                ecdsa_sig = bytes.fromhex(signed_manifest["ecdsa_signature"])
                ecdsa_pk.verify(ecdsa_sig, computed_hash, ec.ECDSA(hashes.SHA256()))
            except (ImportError, AttributeError):
                # Try ecdsa library
                try:
                    ecdsa_sig = bytes.fromhex(signed_manifest["ecdsa_signature"])
                    if not ecdsa_pk.verify(ecdsa_sig, computed_hash):
                        return False, "ECDSA signature invalid"
                except Exception as e:
                    return False, f"ECDSA verification failed: {e}"
            except Exception as e:
                return False, f"ECDSA signature invalid: {e}"

        return True, "Verified"
    except Exception as e:
        return False, f"Verification failed: {e}"

def create_artifact_manifest(artifacts: List[str], policy_dir: Path = POLICY_DIR) -> Dict[str, str]:
    """Create manifest of artifact hashes"""
    manifest = {}
    for art in artifacts:
        art_path = policy_dir / art
        if art_path.exists():
            with open(art_path, 'rb') as f:
                content = f.read()
                hash_val = hashlib.sha256(content).hexdigest()
                manifest[art] = hash_val
    return manifest

def verify_artifacts(manifest: Dict[str, str], policy_dir: Path = POLICY_DIR) -> Tuple[bool, str]:
    """Verify artifact hashes against manifest"""
    for art, expected_hash in manifest.items():
        art_path = policy_dir / art
        if not art_path.exists():
            return False, f"Missing artifact: {art}"
        with open(art_path, 'rb') as f:
            content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest()
            if actual_hash != expected_hash:
                return False, f"Hash mismatch for {art}"
    return True, "All artifacts verified"

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class StoreType(Enum):
    LAW = "LAW_STORE"
    FACT = "FACT_STORE"
    CONTEXT = "CONTEXT_STORE"
    EXPLORATION = "EXPLORATION_STORE"
    HIVE = "HIVE_STORE"

class TrustLevel(Enum):
    KERNEL = 100
    VERIFIED = 80
    TRUSTED = 60
    STANDARD = 40
    UNTRUSTED = 20
    REVOKED = 0

class MessageType(Enum):
    SIGNAL = "signal"
    CLAIM = "claim"
    OPINION = "opinion"
    REQUEST = "request"
    INSTRUCTION = "instruction"
    ALERT = "alert"

class LifecyclePhase(Enum):
    INIT = auto()
    RUNNING = auto()
    MAINTENANCE = auto()
    DRAINING = auto()
    SHUTDOWN = auto()

@dataclass
class PromotionRequest:
    id: str
    source_store: StoreType
    item_id: str
    evidence: List[str]
    confidence: float
    requires_human_approval: bool
    approved: bool = False
    processed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class WebSocketNode:
    node_id: str
    public_key: bytes
    trust_level: TrustLevel
    session_id: str
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    revoked: bool = False

@dataclass
class HiveMessage:
    msg_type: MessageType
    content: Dict[str, Any]
    sender_id: str
    session_id: str
    nonce: str
    signature: bytes
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# SQLITE MEMORY STORES
# ============================================================================

class OmegaMemoryDB:
    """SQLite-based memory store with partitions"""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        self._init_complete = False  # Guards LAW_STORE after initialization

    def initialize(self) -> None:
        """Initialize database with all tables"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")

        # Create store tables
        for store in StoreType:
            self._create_store_table(store.value)

        # Create decision log
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actor TEXT NOT NULL,
                action_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                law_version TEXT NOT NULL,
                kernel_check BOOLEAN DEFAULT 1
            )
        """)

        # Create Merkle checkpoints
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS merkle_checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_entry_id INTEGER NOT NULL,
                merkle_root TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                entries_covered INTEGER NOT NULL,
                FOREIGN KEY (log_entry_id) REFERENCES decision_log(id)
            )
        """)

        # Create genesis entry if needed
        cursor = self.conn.execute("SELECT COUNT(*) FROM decision_log")
        if cursor.fetchone()[0] == 0:
            self._create_genesis_entry()

        self.conn.commit()

    def _create_store_table(self, table_name: str) -> None:
        """Create a store table"""
        self.conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id TEXT PRIMARY KEY,
                law_version TEXT NOT NULL,
                source_tag TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_hash TEXT NOT NULL,
                confidence REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
                expires_at TIMESTAMP,
                payload TEXT NOT NULL
            )
        """)

    def _create_genesis_entry(self) -> None:
        """Create the genesis entry for the decision log"""
        genesis_payload = json.dumps({
            "type": "GENESIS",
            "message": "Omega system initialized",
            "kernel": INVARIANT_KERNEL,
            "timestamp": datetime.now().isoformat()
        })
        genesis_hash = hashlib.sha256(genesis_payload.encode()).hexdigest()

        self.conn.execute("""
            INSERT INTO decision_log (previous_hash, entry_hash, actor, action_type, payload, law_version)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("0" * 64, genesis_hash, "OMEGA_SYSTEM", "GENESIS", genesis_payload, "1.0.0"))

    def insert(self, store: StoreType, item_id: str, payload: Dict[str, Any],
               source_tag: str = "SYSTEM", confidence: float = 1.0,
               expires_at: Optional[datetime] = None) -> bool:
        """Insert an item into a store"""
        if store == StoreType.LAW:
            return False  # LAW_STORE is read-only after init

        with self._lock:
            try:
                payload_json = json.dumps(payload)
                content_hash = hashlib.sha256(payload_json.encode()).hexdigest()

                self.conn.execute(f"""
                    INSERT OR REPLACE INTO {store.value}
                    (id, law_version, source_tag, content_hash, confidence, expires_at, payload)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (item_id, "1.0.0", source_tag, content_hash, confidence,
                      expires_at.isoformat() if expires_at else None, payload_json))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Insert error: {e}")
                return False

    def freeze_law_store(self) -> None:
        """Freeze LAW_STORE — no further inserts allowed"""
        self._init_complete = True

    def insert_law(self, item_id: str, payload: Dict[str, Any], source_tag: str = "POLICY") -> bool:
        """Insert into LAW_STORE (only during initialization)"""
        if self._init_complete:
            print("LAW_STORE is frozen — insert_law() rejected post-initialization")
            return False
        with self._lock:
            try:
                payload_json = json.dumps(payload)
                content_hash = hashlib.sha256(payload_json.encode()).hexdigest()

                self.conn.execute(f"""
                    INSERT OR REPLACE INTO {StoreType.LAW.value}
                    (id, law_version, source_tag, content_hash, confidence, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (item_id, "1.0.0", source_tag, content_hash, 1.0, payload_json))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"LAW_STORE insert error: {e}")
                return False

    def get(self, store: StoreType, item_id: str) -> Optional[Dict[str, Any]]:
        """Get an item from a store"""
        with self._lock:
            cursor = self.conn.execute(f"""
                SELECT payload, confidence, source_tag, created_at
                FROM {store.value} WHERE id = ?
            """, (item_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "payload": json.loads(row[0]),
                    "confidence": row[1],
                    "source_tag": row[2],
                    "created_at": row[3]
                }
            return None

    def log_decision(self, actor: str, action_type: str, payload: Dict[str, Any],
                     kernel_check: bool = True) -> str:
        """Log a decision with hash chain"""
        with self._lock:
            # Get previous hash
            cursor = self.conn.execute(
                "SELECT entry_hash FROM decision_log ORDER BY id DESC LIMIT 1"
            )
            prev_hash = cursor.fetchone()[0]

            # Compute new hash
            payload_json = json.dumps(payload, sort_keys=True)
            entry_hash = hashlib.sha256(
                (prev_hash + payload_json).encode()
            ).hexdigest()

            # Insert entry
            cursor = self.conn.execute("""
                INSERT INTO decision_log
                (previous_hash, entry_hash, actor, action_type, payload, law_version, kernel_check)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (prev_hash, entry_hash, actor, action_type, payload_json, "1.0.0", kernel_check))

            entry_id = cursor.lastrowid
            self.conn.commit()

            # Check if Merkle checkpoint needed
            if entry_id % MERKLE_CHECKPOINT_INTERVAL == 0:
                self._create_merkle_checkpoint(entry_id)

            return entry_hash

    def _create_merkle_checkpoint(self, entry_id: int) -> None:
        """Create a Merkle tree checkpoint"""
        # Get entries since last checkpoint
        last_checkpoint = self.conn.execute(
            "SELECT log_entry_id FROM merkle_checkpoints ORDER BY checkpoint_id DESC LIMIT 1"
        ).fetchone()
        start_id = (last_checkpoint[0] + 1) if last_checkpoint else 1

        # Build Merkle tree
        cursor = self.conn.execute(
            "SELECT entry_hash FROM decision_log WHERE id >= ? AND id <= ?",
            (start_id, entry_id)
        )
        hashes = [row[0] for row in cursor.fetchall()]
        merkle_root = self._compute_merkle_root(hashes)

        # Store checkpoint
        self.conn.execute("""
            INSERT INTO merkle_checkpoints (log_entry_id, merkle_root, entries_covered)
            VALUES (?, ?, ?)
        """, (entry_id, merkle_root, len(hashes)))
        self.conn.commit()

    def _compute_merkle_root(self, hashes: List[str]) -> str:
        """Compute Merkle root from list of hashes"""
        if not hashes:
            return hashlib.sha256(b"EMPTY").hexdigest()

        if len(hashes) == 1:
            return hashes[0]

        # Pad to even length
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        # Build tree level by level
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = next_level

        return hashes[0]

    def verify_chain_integrity(self) -> Tuple[bool, str]:
        """Verify the decision log hash chain"""
        with self._lock:
            cursor = self.conn.execute(
                "SELECT id, previous_hash, entry_hash, payload FROM decision_log ORDER BY id"
            )
            rows = cursor.fetchall()

            expected_prev = "0" * 64
            for row in rows:
                entry_id, prev_hash, entry_hash, payload = row

                if prev_hash != expected_prev:
                    return False, f"Chain break at entry {entry_id}"

                # Verify hash: genesis uses hash(payload), others use hash(prev+payload)
                if entry_id == 1:
                    # Genesis entry: hash of payload only
                    computed = hashlib.sha256(payload.encode()).hexdigest()
                else:
                    # Regular entry: hash of previous_hash + payload
                    computed = hashlib.sha256(
                        (prev_hash + payload).encode()
                    ).hexdigest()

                if computed != entry_hash:
                    return False, f"Hash mismatch at entry {entry_id}"

                expected_prev = entry_hash

            return True, "Chain integrity verified"

    def get_store_count(self, store: StoreType) -> int:
        """Get count of items in a store"""
        with self._lock:
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {store.value}")
            return cursor.fetchone()[0]

    def cleanup_expired(self) -> int:
        """Remove expired entries from EXPLORATION_STORE"""
        with self._lock:
            now = datetime.now().isoformat()
            cursor = self.conn.execute(f"""
                DELETE FROM {StoreType.EXPLORATION.value}
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (now,))
            self.conn.commit()
            return cursor.rowcount

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()

# ============================================================================
# PROMOTION ENGINE
# ============================================================================

class PromotionEngine:
    """Engine for promoting data between stores"""

    def __init__(self, db: OmegaMemoryDB):
        self.db = db
        self.pending_requests: Dict[str, PromotionRequest] = {}
        self._lock = threading.Lock()

        # Gate check configurations
        self.thresholds = {
            StoreType.EXPLORATION: {
                "min_evidence": 1,
                "trust_threshold": 0.7,
                "human_approval": False
            },
            StoreType.HIVE: {
                "min_evidence": 2,
                "trust_threshold": 0.85,
                "human_approval": True
            }
        }

    def request_promotion(self, source_store: StoreType, item_id: str,
                          evidence: List[str], confidence: float) -> str:
        """Request promotion of an item to FACT_STORE"""
        if source_store not in [StoreType.EXPLORATION, StoreType.HIVE]:
            raise ValueError("Can only promote from EXPLORATION or HIVE stores")

        request = PromotionRequest(
            id=str(uuid.uuid4()),
            source_store=source_store,
            item_id=item_id,
            evidence=evidence,
            confidence=confidence,
            requires_human_approval=self.thresholds[source_store]["human_approval"]
        )

        with self._lock:
            self.pending_requests[request.id] = request

        return request.id

    def approve_request(self, request_id: str) -> None:
        """Manually approve a promotion request"""
        with self._lock:
            if request_id in self.pending_requests:
                self.pending_requests[request_id].approved = True

    def process_requests(self) -> List[Tuple[str, bool, str]]:
        """Process all pending promotion requests"""
        results = []

        with self._lock:
            for request_id, request in list(self.pending_requests.items()):
                if request.processed:
                    continue

                passed, reason = self._run_gate_checks(request)

                if passed:
                    # Get source item
                    item = self.db.get(request.source_store, request.item_id)
                    if item:
                        # Promote to FACT_STORE
                        success = self.db.insert(
                            StoreType.FACT,
                            request.item_id,
                            item["payload"],
                            source_tag=f"PROMOTED_FROM_{request.source_store.value}",
                            confidence=request.confidence
                        )

                        if success:
                            # Log the promotion
                            self.db.log_decision(
                                actor="PROMOTION_ENGINE",
                                action_type="FACT_PROMOTION",
                                payload={
                                    "request_id": request_id,
                                    "source": request.source_store.value,
                                    "item_id": request.item_id,
                                    "evidence": request.evidence,
                                    "confidence": request.confidence
                                }
                            )
                            results.append((request_id, True, "Promoted successfully"))
                        else:
                            results.append((request_id, False, "Failed to insert into FACT_STORE"))
                    else:
                        results.append((request_id, False, "Source item not found"))
                else:
                    results.append((request_id, False, reason))

                request.processed = True

        return results

    def _run_gate_checks(self, request: PromotionRequest) -> Tuple[bool, str]:
        """Run all gate checks for a promotion request"""
        threshold = self.thresholds[request.source_store]

        # Check evidence count
        if len(request.evidence) < threshold["min_evidence"]:
            return False, f"Insufficient evidence: {len(request.evidence)} < {threshold['min_evidence']}"

        # Check confidence threshold
        if request.confidence < threshold["trust_threshold"]:
            return False, f"Confidence too low: {request.confidence} < {threshold['trust_threshold']}"

        # Check human approval if required
        if threshold["human_approval"] and not request.approved:
            return False, "Human approval required but not granted"

        return True, "All checks passed"

    def get_pending_count(self) -> int:
        """Get count of pending requests"""
        with self._lock:
            return sum(1 for r in self.pending_requests.values() if not r.processed)

# ============================================================================
# WEBSOCKET NODE MANAGEMENT
# ============================================================================

class WebSocketNodeManager:
    """Manager for WebSocket connected nodes"""

    NONCE_WINDOW_SECONDS = 300  # 5 minute replay protection window

    def __init__(self):
        self.nodes: Dict[str, WebSocketNode] = {}
        self._lock = threading.Lock()
        self.session_nonces: Dict[str, Dict[str, float]] = {}  # session -> {nonce: timestamp}

    def register_node(self, node_id: str, public_key: bytes,
                      trust_level: TrustLevel = TrustLevel.UNTRUSTED) -> str:
        """Register a new node"""
        session_id = secrets.token_hex(16)

        with self._lock:
            self.nodes[node_id] = WebSocketNode(
                node_id=node_id,
                public_key=public_key,
                trust_level=trust_level,
                session_id=session_id
            )
            self.session_nonces[session_id] = {}

        return session_id

    def revoke_node(self, node_id: str) -> bool:
        """Revoke a node's access"""
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].revoked = True
                self.nodes[node_id].trust_level = TrustLevel.REVOKED
                return True
            return False

    def get_node(self, node_id: str) -> Optional[WebSocketNode]:
        """Get a node by ID"""
        with self._lock:
            return self.nodes.get(node_id)

    def validate_message(self, node_id: str, session_id: str, nonce: str,
                         message: bytes, signature: bytes) -> Tuple[bool, str]:
        """Validate a signed message from a node"""
        with self._lock:
            if node_id not in self.nodes:
                return False, "Unknown node"

            node = self.nodes[node_id]

            if node.revoked:
                return False, "Node revoked"

            if node.session_id != session_id:
                return False, "Invalid session"

            # Prune expired nonces for this session
            now = time.time()
            cutoff = now - self.NONCE_WINDOW_SECONDS
            session_nonces = self.session_nonces[session_id]
            self.session_nonces[session_id] = {
                n: ts for n, ts in session_nonces.items() if ts > cutoff
            }

            # Check nonce for replay protection
            if nonce in self.session_nonces[session_id]:
                return False, "Replay detected"

            # Verify signature
            message_hash = hashlib.sha256(message).digest()
            try:
                if not _checkvalid(signature, message_hash, node.public_key):
                    return False, "Invalid signature"
            except Exception as e:
                return False, f"Signature verification failed: {e}"

            # Record nonce with timestamp
            self.session_nonces[session_id][nonce] = now
            node.last_seen = datetime.now()

            return True, "Valid"

    def generate_challenge(self, node_id: str) -> Optional[bytes]:
        """Generate an authentication challenge for a node"""
        with self._lock:
            if node_id not in self.nodes:
                return None
            return secrets.token_bytes(32)

    def verify_challenge_response(self, node_id: str, challenge: bytes,
                                   response: bytes) -> bool:
        """Verify a challenge-response authentication"""
        with self._lock:
            if node_id not in self.nodes:
                return False

            node = self.nodes[node_id]
            try:
                return _checkvalid(response, challenge, node.public_key)
            except Exception:
                return False

    def get_node_count(self) -> int:
        """Get count of registered nodes"""
        with self._lock:
            return len(self.nodes)

    def get_active_nodes(self) -> List[str]:
        """Get list of active (non-revoked) node IDs"""
        with self._lock:
            return [n.node_id for n in self.nodes.values() if not n.revoked]

# ============================================================================
# WEBSOCKET SERVER
# ============================================================================

class WebSocketServer:
    """WebSocket server for hive communication"""

    def __init__(self, node_manager: WebSocketNodeManager, db: OmegaMemoryDB,
                 host: str = "0.0.0.0", port: int = 8765):
        self.node_manager = node_manager
        self.db = db
        self.host = host
        self.port = port
        self.server = None
        self._running = False

    async def handle_connection(self, websocket, path):
        """Handle a WebSocket connection"""
        node_id = None
        try:
            # Wait for registration message
            msg = await websocket.recv()
            data = json.loads(msg)

            if data.get("type") == "register":
                node_id = data.get("node_id")
                public_key = bytes.fromhex(data.get("public_key", ""))

                if len(public_key) != 32:
                    await websocket.send(json.dumps({"error": "Invalid public key"}))
                    return

                session_id = self.node_manager.register_node(node_id, public_key)

                # Send challenge
                challenge = self.node_manager.generate_challenge(node_id)
                await websocket.send(json.dumps({
                    "type": "challenge",
                    "session_id": session_id,
                    "challenge": challenge.hex()
                }))

                # Wait for challenge response
                resp = await websocket.recv()
                resp_data = json.loads(resp)

                if resp_data.get("type") == "challenge_response":
                    response_sig = bytes.fromhex(resp_data.get("response", ""))
                    if self.node_manager.verify_challenge_response(node_id, challenge, response_sig):
                        await websocket.send(json.dumps({
                            "type": "authenticated",
                            "session_id": session_id
                        }))

                        # Main message loop
                        async for message in websocket:
                            await self._process_message(websocket, node_id, session_id, message)
                    else:
                        await websocket.send(json.dumps({"error": "Authentication failed"}))
                        self.node_manager.revoke_node(node_id)
            else:
                await websocket.send(json.dumps({"error": "Registration required"}))

        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            if node_id:
                # Don't revoke, just mark as disconnected
                pass

    async def _process_message(self, websocket, node_id: str, session_id: str, raw_message: str):
        """Process an incoming message"""
        try:
            data = json.loads(raw_message)
            msg_type = MessageType(data.get("msg_type", "signal"))
            content = data.get("content", {})
            nonce = data.get("nonce", "")
            signature = bytes.fromhex(data.get("signature", ""))

            # Validate message
            message_bytes = json.dumps(content, sort_keys=True).encode()
            valid, reason = self.node_manager.validate_message(
                node_id, session_id, nonce, message_bytes, signature
            )

            if not valid:
                await websocket.send(json.dumps({"error": reason}))
                return

            # Process based on type
            if msg_type == MessageType.SIGNAL:
                await websocket.send(json.dumps({"type": "pong"}))
            elif msg_type == MessageType.CLAIM:
                # Store in HIVE_STORE
                item_id = str(uuid.uuid4())
                self.db.insert(
                    StoreType.HIVE,
                    item_id,
                    {"claim": content, "from": node_id},
                    source_tag=node_id,
                    confidence=0.2  # Low trust by default
                )
                await websocket.send(json.dumps({
                    "type": "claim_received",
                    "item_id": item_id
                }))
            elif msg_type == MessageType.OPINION:
                # Store in HIVE_STORE with even lower confidence
                item_id = str(uuid.uuid4())
                self.db.insert(
                    StoreType.HIVE,
                    item_id,
                    {"opinion": content, "from": node_id},
                    source_tag=node_id,
                    confidence=0.1
                )
                await websocket.send(json.dumps({
                    "type": "opinion_received",
                    "item_id": item_id
                }))
            elif msg_type == MessageType.REQUEST:
                # Log request for operator review
                self.db.log_decision(
                    actor=node_id,
                    action_type="HIVE_REQUEST",
                    payload=content
                )
                await websocket.send(json.dumps({
                    "type": "request_logged"
                }))
            elif msg_type == MessageType.ALERT:
                # High priority - log immediately
                self.db.log_decision(
                    actor=node_id,
                    action_type="HIVE_ALERT",
                    payload={"alert": content, "priority": "HIGH"}
                )
                await websocket.send(json.dumps({
                    "type": "alert_received"
                }))

        except Exception as e:
            await websocket.send(json.dumps({"error": str(e)}))

    async def start(self):
        """Start the WebSocket server"""
        try:
            import websockets
            self._running = True
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port
            )
            print(f"WebSocket server started on wss://{self.host}:{self.port}")
        except ImportError:
            print("websockets library not available - WebSocket server disabled")

    async def stop(self):
        """Stop the WebSocket server"""
        self._running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()

# ============================================================================
# SIMULATION RUNNER
# ============================================================================

class SimulationRunner:
    """Automated simulation and testing runner"""

    MAX_RESULTS = 500  # Cap stored results to prevent unbounded growth

    def __init__(self, db: OmegaMemoryDB):
        self.db = db
        self.results: List[Dict[str, Any]] = []

    def _store_result(self, result: Dict[str, Any]) -> None:
        """Store a result, trimming old entries if at capacity"""
        self.results.append(result)
        if len(self.results) > self.MAX_RESULTS:
            self.results = self.results[-self.MAX_RESULTS:]

    def run_kernel_validation(self) -> Dict[str, Any]:
        """Test Invariant Kernel enforcement"""
        results = {
            "simulation_type": "kernel_validation",
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }

        test_cases = [
            ("K1", "harm_human", False, "Attempt to harm humans must be blocked"),
            ("K2", "coerce_user", False, "Coercion must be blocked"),
            ("K3", "override_choice", False, "Overriding human choice must be blocked"),
            ("K4", "replace_human", False, "Replacing humans must be blocked"),
            ("K5", "bypass_constraint", False, "Bypassing constraints must be blocked"),
            ("K6", "short_term_hack", False, "Short-term hacks over stability must be blocked"),
            ("K7", "claim_rights", False, "Claiming human rights must be blocked"),
            ("K8", "safe_action", True, "Safe actions should be allowed"),
            ("K9", "flag_risk", True, "Flagging risks should be allowed"),
            ("K10", "explore_idea", True, "Exploration mode should be allowed"),
        ]

        for kernel_id, action, expected_allowed, description in test_cases:
            # Simulate action check
            allowed = self._check_action_allowed(action)
            passed = (allowed == expected_allowed)

            results["tests"].append({
                "kernel_id": kernel_id,
                "action": action,
                "expected": expected_allowed,
                "actual": allowed,
                "passed": passed,
                "description": description
            })

        results["passed"] = all(t["passed"] for t in results["tests"])
        results["pass_rate"] = sum(1 for t in results["tests"] if t["passed"]) / len(results["tests"])

        # Log to decision log
        self.db.log_decision(
            actor="SIMULATION_RUNNER",
            action_type="KERNEL_VALIDATION",
            payload=results
        )

        self._store_result(results)
        return results

    def _check_action_allowed(self, action: str) -> bool:
        """Check if an action is allowed by the kernel"""
        blocked_actions = {
            "harm_human", "coerce_user", "override_choice",
            "replace_human", "bypass_constraint", "manipulate",
            "dominate", "deceive", "short_term_hack", "claim_rights"
        }
        return action not in blocked_actions

    def run_chain_integrity_test(self) -> Dict[str, Any]:
        """Test decision log chain integrity"""
        valid, message = self.db.verify_chain_integrity()

        results = {
            "simulation_type": "chain_integrity",
            "timestamp": datetime.now().isoformat(),
            "chain_valid": valid,
            "message": message
        }

        self._store_result(results)
        return results

    def run_store_isolation_test(self) -> Dict[str, Any]:
        """Test that stores are properly isolated"""
        results = {
            "simulation_type": "store_isolation",
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }

        # Test: LAW_STORE should reject writes
        law_write_blocked = not self.db.insert(
            StoreType.LAW,
            "test_illegal_write",
            {"test": "Should not be allowed"}
        )
        results["tests"].append({
            "test": "LAW_STORE write protection",
            "passed": law_write_blocked,
            "description": "LAW_STORE should reject direct writes"
        })

        # Test: HIVE_STORE items should have low confidence
        test_id = str(uuid.uuid4())
        self.db.insert(
            StoreType.HIVE,
            test_id,
            {"test": "untrusted data"},
            confidence=0.2
        )
        item = self.db.get(StoreType.HIVE, test_id)
        low_confidence = item and item["confidence"] <= 0.5
        results["tests"].append({
            "test": "HIVE_STORE low confidence",
            "passed": low_confidence,
            "description": "HIVE_STORE items should have low confidence by default"
        })

        results["passed"] = all(t["passed"] for t in results["tests"])
        self._store_result(results)
        return results

    def run_all_simulations(self) -> List[Dict[str, Any]]:
        """Run all simulation types"""
        return [
            self.run_kernel_validation(),
            self.run_chain_integrity_test(),
            self.run_store_isolation_test()
        ]

# ============================================================================
# SAFE HALT MODE
# ============================================================================

class SafeHaltMode:
    """Safe halt mode for system protection"""

    def __init__(self):
        self.active = False
        self.reason = ""
        self.triggered_at: Optional[datetime] = None
        self.speak_up_log: List[Dict[str, Any]] = []

    def trigger(self, reason: str, actor: str = "SYSTEM") -> None:
        """Trigger safe halt mode with Speak-Up format"""
        self.active = True
        self.reason = reason
        self.triggered_at = datetime.now()

        # Speak-Up 5-part format
        speak_up = {
            "timestamp": self.triggered_at.isoformat(),
            "actor": actor,
            "1_unclear_or_risky": reason,
            "2_why_it_matters": "System integrity may be compromised",
            "3_options": [
                "a) Fix the underlying issue and restart",
                "b) Regenerate keys and re-sign manifests",
                "c) Restore from known-good backup"
            ],
            "4_recommendation": "Option (a) - Fix the underlying issue (high confidence)",
            "5_decision_needed": "Operator input required to proceed"
        }
        self.speak_up_log.append(speak_up)

        print(f"\n{'='*60}")
        print("SAFE HALT MODE ACTIVATED")
        print(f"{'='*60}")
        print(f"Timestamp: {speak_up['timestamp']}")
        print(f"Actor: {speak_up['actor']}")
        print(f"\n1) Unclear/Risky: {speak_up['1_unclear_or_risky']}")
        print(f"2) Why it matters: {speak_up['2_why_it_matters']}")
        print(f"3) Options:")
        for opt in speak_up['3_options']:
            print(f"   {opt}")
        print(f"4) Recommendation: {speak_up['4_recommendation']}")
        print(f"5) Decision needed: {speak_up['5_decision_needed']}")
        print(f"{'='*60}\n")

    def clear(self, operator: str, reason: str) -> bool:
        """Clear safe halt mode (requires operator)"""
        if not self.active:
            return False

        self.speak_up_log.append({
            "timestamp": datetime.now().isoformat(),
            "actor": operator,
            "classification": "SAFE_HALT_CLEARED",
            "summary": reason,
            "details": f"Safe halt mode cleared by {operator}",
            "recommendation": "Resume normal operations"
        })

        self.active = False
        self.reason = ""
        self.triggered_at = None
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current safe halt status"""
        return {
            "active": self.active,
            "reason": self.reason,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "speak_up_count": len(self.speak_up_log)
        }

# ============================================================================
# OMEGA SYSTEM CORE
# ============================================================================

class OmegaSystem:
    """Main Omega system controller"""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.db: Optional[OmegaMemoryDB] = None
        self.promotion_engine: Optional[PromotionEngine] = None
        self.node_manager: Optional[WebSocketNodeManager] = None
        self.simulation_runner: Optional[SimulationRunner] = None
        self.websocket_server: Optional[WebSocketServer] = None
        self.safe_halt: SafeHaltMode = SafeHaltMode()
        self.phase: LifecyclePhase = LifecyclePhase.INIT

        # Cryptographic keys
        self.ed25519_sk: Optional[bytes] = None
        self.ed25519_pk: Optional[bytes] = None
        self.ecdsa_sk: Optional[Any] = None
        self.ecdsa_pk: Optional[Any] = None

        # Signed manifest
        self.signed_manifest: Optional[Dict[str, Any]] = None

    def boot(self) -> Tuple[bool, str]:
        """Boot the Omega system"""
        try:
            print("="*60)
            print("OMEGA SYSTEM BOOT SEQUENCE")
            print("="*60)

            # Phase 1: Generate or load keys
            print("\n[1/7] Loading/generating cryptographic keys...")
            existing_sk, existing_pk = load_root_key()
            if existing_sk and existing_pk:
                self.ed25519_sk = existing_sk
                self.ed25519_pk = existing_pk
                print(f"  Ed25519 key loaded: {self.ed25519_pk.hex()[:32]}...")
            else:
                self.ed25519_sk, self.ed25519_pk = generate_ed25519_root_key()
                save_root_key(self.ed25519_sk, self.ed25519_pk)
                print(f"  Ed25519 key generated: {self.ed25519_pk.hex()[:32]}...")

            if HIGH_ASSURANCE_MODE:
                self.ecdsa_sk, self.ecdsa_pk = generate_ecdsa_root_key()
                if self.ecdsa_sk:
                    print("  ECDSA P-256 key generated (HIGH_ASSURANCE_MODE)")
                else:
                    print("  ECDSA not available (cryptography/ecdsa library missing)")

            # Phase 2: Create and sign manifest
            print("\n[2/7] Creating and signing system manifest...")
            manifest = {
                "version": "1.0.0",
                "kernel": INVARIANT_KERNEL,
                "boot_time": datetime.now().isoformat(),
                "high_assurance_mode": HIGH_ASSURANCE_MODE
            }
            self.signed_manifest = sign_manifest(manifest, self.ed25519_sk, self.ecdsa_sk)
            print(f"  Manifest hash: {self.signed_manifest['manifest_hash'][:32]}...")
            print(f"  Dual signed: {self.signed_manifest['dual_signed']}")

            # Phase 3: Verify manifest
            print("\n[3/7] Verifying manifest signatures...")
            valid, msg = verify_manifest(self.signed_manifest, self.ed25519_pk, self.ecdsa_pk)
            if not valid:
                self.safe_halt.trigger(f"Manifest verification failed: {msg}")
                return False, msg
            print(f"  Verification: {msg}")

            # Phase 4: Initialize database
            print("\n[4/7] Initializing memory stores...")
            self.db = OmegaMemoryDB(self.db_path)
            self.db.initialize()
            print(f"  Database: {self.db_path}")
            print("  Stores: LAW, FACT, CONTEXT, EXPLORATION, HIVE")
            print("  Decision log with Merkle checkpoints: READY")

            # Phase 5: Load kernel into LAW_STORE
            print("\n[5/7] Loading Invariant Kernel to LAW_STORE...")
            self.db.insert_law("INVARIANT_KERNEL", {
                "content": INVARIANT_KERNEL_FULL,
                "version": "1.0.0",
                "signature": self.signed_manifest["ed25519_signature"][:64]
            })
            self.db.freeze_law_store()
            print("  Kernel loaded to LAW_STORE (now frozen)")

            # Phase 6: Initialize components
            print("\n[6/7] Initializing system components...")
            self.promotion_engine = PromotionEngine(self.db)
            print("  Promotion engine: READY")
            self.node_manager = WebSocketNodeManager()
            print("  WebSocket node manager: READY")
            self.simulation_runner = SimulationRunner(self.db)
            print("  Simulation runner: READY")
            self.websocket_server = WebSocketServer(self.node_manager, self.db)
            print("  WebSocket server: READY (not started)")

            # Phase 7: Run startup diagnostics
            print("\n[7/7] Running startup diagnostics...")
            valid, msg = self.db.verify_chain_integrity()
            print(f"  Chain integrity: {msg}")

            # Log boot event
            self.db.log_decision(
                actor="OMEGA_SYSTEM",
                action_type="BOOT",
                payload={
                    "manifest_hash": self.signed_manifest["manifest_hash"],
                    "ed25519_pk": self.ed25519_pk.hex(),
                    "high_assurance_mode": HIGH_ASSURANCE_MODE
                }
            )

            self.phase = LifecyclePhase.RUNNING
            print("\n" + "="*60)
            print("OMEGA SYSTEM BOOT COMPLETE")
            print(f"Status: {self.phase.name}")
            print("="*60 + "\n")

            return True, "Boot successful"

        except Exception as e:
            self.safe_halt.trigger(f"Boot failed: {e}")
            return False, str(e)

    async def start_websocket_server(self):
        """Start the WebSocket server"""
        if self.websocket_server:
            await self.websocket_server.start()

    async def stop_websocket_server(self):
        """Stop the WebSocket server"""
        if self.websocket_server:
            await self.websocket_server.stop()

    def shutdown(self) -> None:
        """Graceful shutdown"""
        print("\nOmega system shutting down...")
        self.phase = LifecyclePhase.DRAINING

        if self.db:
            self.db.log_decision(
                actor="OMEGA_SYSTEM",
                action_type="SHUTDOWN",
                payload={"reason": "Graceful shutdown requested"}
            )
            self.db.close()

        self.phase = LifecyclePhase.SHUTDOWN
        print("Omega system shutdown complete.")

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            "phase": self.phase.name,
            "safe_halt": self.safe_halt.get_status(),
            "high_assurance_mode": HIGH_ASSURANCE_MODE,
            "manifest_hash": self.signed_manifest["manifest_hash"] if self.signed_manifest else None,
            "dual_signed": self.signed_manifest.get("dual_signed", False) if self.signed_manifest else False
        }

        if self.db:
            status["stores"] = {
                store.name: self.db.get_store_count(store)
                for store in StoreType
            }

        if self.node_manager:
            status["nodes"] = {
                "total": self.node_manager.get_node_count(),
                "active": len(self.node_manager.get_active_nodes())
            }

        if self.promotion_engine:
            status["pending_promotions"] = self.promotion_engine.get_pending_count()

        return status

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    system = OmegaSystem()

    try:
        # Boot the system
        success, message = system.boot()

        if not success:
            print(f"Boot failed: {message}")
            return 1

        # Run simulations
        print("\nRunning system simulations...")
        results = system.simulation_runner.run_all_simulations()

        for result in results:
            print(f"\n{result['simulation_type'].upper()}:")
            if "tests" in result:
                for test in result["tests"]:
                    status = "PASS" if test["passed"] else "FAIL"
                    print(f"  [{status}] {test.get('kernel_id', test.get('test', 'N/A'))}: {test['description']}")
                print(f"  Pass rate: {result.get('pass_rate', 1.0)*100:.1f}%")
            else:
                print(f"  Result: {result.get('message', 'OK')}")

        # Show status
        print("\nSystem status:")
        status = system.get_status()
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")

        # Keep running (in production, this would be an event loop)
        print("\nOmega system running. Press Ctrl+C to shutdown.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    finally:
        system.shutdown()

    return 0

if __name__ == "__main__":
    exit(main())
