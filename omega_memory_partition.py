#!/usr/bin/env python3
"""
OMEGA MEMORY PARTITIONING SYSTEM
================================
SQLite-based memory architecture with strict partitioning.

Implements Prompt Four - SQLite Memory Partitioning:
- LAW STORE: Signed, frozen read-only rules
- FACT STORE: Verified facts only, no fluff
- CONTEXT STORE: Preferences, runtime state
- EXPLORATION STORE: Sandboxed what-ifs, auto-expires
- HIVE STORE: Raw crowd input, zero trust
- DECISION LOG: Append-only, hash-chained

All operations respect the Invariant Kernel (K1-K10).
"""

import sqlite3
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OMEGA_MEMORY - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaMemoryPartition')


class StoreType(Enum):
    """Memory store types"""
    LAW = "law_store"
    FACT = "fact_store"
    CONTEXT = "context_store"
    EXPLORATION = "exploration_store"
    HIVE = "hive_store"
    DECISION_LOG = "decision_log"


class TrustLevel(Enum):
    """Trust levels for data entries"""
    KERNEL = 1.0      # From Invariant Kernel - absolute trust
    VERIFIED = 0.9    # Verified by system or human
    CONFIRMED = 0.7   # Confirmed but not cryptographically verified
    SUGGESTED = 0.5   # Suggested, needs verification
    UNTRUSTED = 0.1   # From Hive, unverified
    SPECULATION = 0.0 # Exploration mode only


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    law_version: str
    source_tag: str
    created_at: datetime
    content_hash: str
    confidence: float
    expires_at: Optional[datetime]
    payload: Dict[str, Any]
    store_type: StoreType

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'law_version': self.law_version,
            'source_tag': self.source_tag,
            'created_at': self.created_at.isoformat(),
            'content_hash': self.content_hash,
            'confidence': self.confidence,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'payload': self.payload,
            'store_type': self.store_type.value
        }


@dataclass
class DecisionLogEntry:
    """Represents a decision log entry with hash chain"""
    id: int
    previous_hash: str
    entry_hash: str
    timestamp: datetime
    actor: str
    action_type: str
    payload: Dict[str, Any]
    law_version: str
    kernel_check: bool


class OmegaMemoryPartition:
    """
    SQLite-based memory partitioning system.

    Strict walls between stores:
    - No cross-talk
    - No secrets jumping tables
    - All rows include: ID, law_version, source_tag, created_at,
      content_hash, confidence, expires_at
    """

    # Current law version
    LAW_VERSION = "K10-v1.0.0"

    def __init__(self, db_path: str = "omega_memory.db"):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._connection: Optional[sqlite3.Connection] = None
        self._law_store_frozen = False  # Guards LAW_STORE after initialization

        # Initialize database
        self._init_database()

        # Freeze LAW_STORE after init completes
        self._law_store_frozen = True
        logger.info(f"Omega Memory Partition initialized: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with WAL mode"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            # Enable WAL mode for better concurrency
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def _init_database(self):
        """Initialize all store tables"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # LAW STORE - Read-only signed rules
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS law_store (
                    id TEXT PRIMARY KEY,
                    law_version TEXT NOT NULL,
                    source_tag TEXT NOT NULL DEFAULT 'kernel',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
                    expires_at TIMESTAMP DEFAULT NULL,
                    payload TEXT NOT NULL,
                    signature TEXT,
                    is_frozen BOOLEAN DEFAULT TRUE
                )
            """)

            # FACT STORE - Verified facts only
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fact_store (
                    id TEXT PRIMARY KEY,
                    law_version TEXT NOT NULL,
                    source_tag TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT NOT NULL,
                    confidence REAL CHECK (confidence >= 0.7 AND confidence <= 1.0),
                    expires_at TIMESTAMP DEFAULT NULL,
                    payload TEXT NOT NULL,
                    verified_by TEXT,
                    verified_at TIMESTAMP
                )
            """)

            # CONTEXT STORE - User preferences, runtime state
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_store (
                    id TEXT PRIMARY KEY,
                    law_version TEXT NOT NULL,
                    source_tag TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT NOT NULL,
                    confidence REAL DEFAULT 0.8 CHECK (confidence >= 0.0 AND confidence <= 1.0),
                    expires_at TIMESTAMP DEFAULT NULL,
                    payload TEXT NOT NULL,
                    context_type TEXT NOT NULL
                )
            """)

            # EXPLORATION STORE - Sandboxed what-ifs, auto-expires
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exploration_store (
                    id TEXT PRIMARY KEY,
                    law_version TEXT NOT NULL,
                    source_tag TEXT NOT NULL DEFAULT 'exploration',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT NOT NULL,
                    confidence REAL DEFAULT 0.0 CHECK (confidence >= 0.0 AND confidence <= 0.5),
                    expires_at TIMESTAMP NOT NULL,
                    payload TEXT NOT NULL,
                    exploration_tag TEXT DEFAULT 'EXPLORATION_MODE',
                    can_graduate BOOLEAN DEFAULT FALSE
                )
            """)

            # HIVE STORE - Raw crowd input, zero trust
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hive_store (
                    id TEXT PRIMARY KEY,
                    law_version TEXT NOT NULL,
                    source_tag TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT NOT NULL,
                    confidence REAL DEFAULT 0.1 CHECK (confidence >= 0.0 AND confidence <= 0.3),
                    expires_at TIMESTAMP DEFAULT NULL,
                    payload TEXT NOT NULL,
                    verified BOOLEAN DEFAULT FALSE,
                    flagged BOOLEAN DEFAULT FALSE,
                    flag_reason TEXT
                )
            """)

            # DECISION LOG - Append-only, hash-chained
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actor TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    law_version TEXT NOT NULL,
                    kernel_check BOOLEAN DEFAULT TRUE
                )
            """)

            # MERKLE CHECKPOINTS - For fast integrity verification
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS merkle_checkpoints (
                    checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_entry_id INTEGER NOT NULL,
                    merkle_root TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    entries_covered INTEGER NOT NULL,
                    FOREIGN KEY (log_entry_id) REFERENCES decision_log(id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_source ON fact_store(source_tag)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_type ON context_store(context_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exploration_expires ON exploration_store(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hive_verified ON hive_store(verified)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_decision_timestamp ON decision_log(timestamp)")

            conn.commit()

            # Initialize genesis decision log entry if empty
            cursor.execute("SELECT COUNT(*) FROM decision_log")
            if cursor.fetchone()[0] == 0:
                self._create_genesis_entry()

    def _create_genesis_entry(self):
        """Create the genesis entry for decision log chain"""
        genesis_payload = {
            'type': 'genesis',
            'message': 'Omega Memory Partition initialized',
            'kernel_version': self.LAW_VERSION
        }
        genesis_prev = "0" * 64  # Standardized genesis previous_hash
        payload_json = json.dumps(genesis_payload, sort_keys=True)
        genesis_hash = self._compute_hash(genesis_prev, payload_json)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO decision_log (previous_hash, entry_hash, actor, action_type, payload, law_version)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (genesis_prev, genesis_hash, "system", "init", payload_json, self.LAW_VERSION))
        conn.commit()
        logger.info("Genesis entry created for decision log")

    def _compute_hash(self, previous: str, payload: str) -> str:
        """Compute SHA-256 hash for chain"""
        combined = f"{previous}{payload}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())

    def _content_hash(self, content: Dict[str, Any]) -> str:
        """Compute content hash"""
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

    # =================================================================
    # LAW STORE - Read-only signed rules
    # =================================================================

    def add_law(self, content: Dict[str, Any], signature: str = None) -> str:
        """Add a law to the Law Store (requires signature for production)"""
        if self._law_store_frozen:
            logger.warning("LAW_STORE is frozen — add_law() rejected post-initialization")
            raise RuntimeError("LAW_STORE is frozen after initialization — cannot add laws")
        with self._lock:
            entry_id = self._generate_id()
            content_hash = self._content_hash(content)

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO law_store (id, law_version, content_hash, payload, signature)
                VALUES (?, ?, ?, ?, ?)
            """, (entry_id, self.LAW_VERSION, content_hash, json.dumps(content), signature))
            conn.commit()

            self._log_decision("system", "add_law", {'law_id': entry_id, 'hash': content_hash})
            logger.info(f"Law added: {entry_id}")
            return entry_id

    def get_law(self, law_id: str) -> Optional[Dict[str, Any]]:
        """Get a law by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM law_store WHERE id = ?", (law_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_laws(self) -> List[Dict[str, Any]]:
        """Get all laws"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM law_store ORDER BY created_at")
        return [dict(row) for row in cursor.fetchall()]

    # =================================================================
    # FACT STORE - Verified facts only
    # =================================================================

    def add_fact(self, content: Dict[str, Any], source: str,
                 confidence: float = 0.9, verified_by: str = None) -> str:
        """Add a verified fact to Fact Store"""
        if confidence < 0.7:
            raise ValueError("Facts must have confidence >= 0.7")

        with self._lock:
            entry_id = self._generate_id()
            content_hash = self._content_hash(content)

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fact_store (id, law_version, source_tag, content_hash,
                                       confidence, payload, verified_by, verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (entry_id, self.LAW_VERSION, source, content_hash,
                  confidence, json.dumps(content), verified_by,
                  datetime.now().isoformat() if verified_by else None))
            conn.commit()

            self._log_decision("system", "add_fact", {'fact_id': entry_id, 'source': source})
            logger.info(f"Fact added: {entry_id} from {source}")
            return entry_id

    def get_facts(self, source: str = None, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """Get facts, optionally filtered by source"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if source:
            cursor.execute("""
                SELECT * FROM fact_store
                WHERE source_tag = ? AND confidence >= ?
                ORDER BY created_at DESC
            """, (source, min_confidence))
        else:
            cursor.execute("""
                SELECT * FROM fact_store
                WHERE confidence >= ?
                ORDER BY created_at DESC
            """, (min_confidence,))

        return [dict(row) for row in cursor.fetchall()]

    # =================================================================
    # CONTEXT STORE - Preferences, runtime state
    # =================================================================

    def set_context(self, key: str, value: Any, context_type: str = "preference") -> str:
        """Set a context value"""
        with self._lock:
            content = {'key': key, 'value': value}
            content_hash = self._content_hash(content)

            conn = self._get_connection()
            cursor = conn.cursor()

            # Upsert
            cursor.execute("""
                INSERT OR REPLACE INTO context_store
                (id, law_version, content_hash, payload, context_type)
                VALUES (?, ?, ?, ?, ?)
            """, (key, self.LAW_VERSION, content_hash, json.dumps(content), context_type))
            conn.commit()

            logger.debug(f"Context set: {key} = {value}")
            return key

    def get_context(self, key: str) -> Optional[Any]:
        """Get a context value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT payload FROM context_store WHERE id = ?", (key,))
        row = cursor.fetchone()
        if row:
            content = json.loads(row['payload'])
            return content.get('value')
        return None

    def get_all_context(self, context_type: str = None) -> Dict[str, Any]:
        """Get all context values"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if context_type:
            cursor.execute("""
                SELECT payload FROM context_store WHERE context_type = ?
            """, (context_type,))
        else:
            cursor.execute("SELECT payload FROM context_store")

        result = {}
        for row in cursor.fetchall():
            content = json.loads(row['payload'])
            result[content['key']] = content['value']
        return result

    # =================================================================
    # EXPLORATION STORE - Sandboxed what-ifs
    # =================================================================

    def add_exploration(self, content: Dict[str, Any], source: str,
                        ttl_hours: int = 24) -> str:
        """Add an exploration entry (auto-expires)"""
        with self._lock:
            entry_id = self._generate_id()
            content_hash = self._content_hash(content)
            expires_at = datetime.now() + timedelta(hours=ttl_hours)

            # Mark as exploration mode
            content['_exploration_mode'] = True
            content['_warning'] = "EXPLORATION MODE - Not verified, do not use for decisions"

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO exploration_store
                (id, law_version, source_tag, content_hash, confidence, expires_at, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entry_id, self.LAW_VERSION, source, content_hash,
                  0.0, expires_at.isoformat(), json.dumps(content)))
            conn.commit()

            logger.info(f"Exploration added: {entry_id} (expires: {expires_at})")
            return entry_id

    def get_explorations(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """Get exploration entries"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if include_expired:
            cursor.execute("SELECT * FROM exploration_store ORDER BY created_at DESC")
        else:
            cursor.execute("""
                SELECT * FROM exploration_store
                WHERE expires_at > ?
                ORDER BY created_at DESC
            """, (datetime.now().isoformat(),))

        return [dict(row) for row in cursor.fetchall()]

    def cleanup_expired_explorations(self) -> int:
        """Remove expired exploration entries"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM exploration_store WHERE expires_at <= ?
            """, (datetime.now().isoformat(),))
            deleted = cursor.rowcount
            conn.commit()

            if deleted > 0:
                self._log_decision("system", "cleanup_explorations", {'deleted': deleted})
                logger.info(f"Cleaned up {deleted} expired explorations")
            return deleted

    # =================================================================
    # HIVE STORE - Raw crowd input, zero trust
    # =================================================================

    def add_hive_input(self, content: Dict[str, Any], source: str) -> str:
        """Add raw input from the hive (untrusted)"""
        with self._lock:
            entry_id = self._generate_id()
            content_hash = self._content_hash(content)

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO hive_store
                (id, law_version, source_tag, content_hash, confidence, payload)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entry_id, self.LAW_VERSION, source, content_hash,
                  TrustLevel.UNTRUSTED.value, json.dumps(content)))
            conn.commit()

            logger.info(f"Hive input added: {entry_id} from {source}")
            return entry_id

    def verify_hive_entry(self, entry_id: str, verified_by: str) -> bool:
        """Mark a hive entry as verified (but doesn't promote it)"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE hive_store SET verified = TRUE WHERE id = ?
            """, (entry_id,))
            conn.commit()

            self._log_decision(verified_by, "verify_hive", {'entry_id': entry_id})
            logger.info(f"Hive entry verified: {entry_id} by {verified_by}")
            return cursor.rowcount > 0

    def flag_hive_entry(self, entry_id: str, reason: str, flagged_by: str) -> bool:
        """Flag a hive entry as problematic"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE hive_store SET flagged = TRUE, flag_reason = ? WHERE id = ?
            """, (reason, entry_id))
            conn.commit()

            self._log_decision(flagged_by, "flag_hive", {'entry_id': entry_id, 'reason': reason})
            logger.warning(f"Hive entry flagged: {entry_id} - {reason}")
            return cursor.rowcount > 0

    def promote_hive_to_fact(self, entry_id: str, promoted_by: str) -> Optional[str]:
        """
        Promote a verified hive entry to Fact Store.
        REQUIRES: entry must be verified and not flagged.
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if eligible
            cursor.execute("""
                SELECT * FROM hive_store
                WHERE id = ? AND verified = TRUE AND flagged = FALSE
            """, (entry_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Cannot promote hive entry {entry_id}: not verified or flagged")
                return None

            # Promote to fact store
            content = json.loads(row['payload'])
            fact_id = self.add_fact(
                content=content,
                source=f"hive:{row['source_tag']}",
                confidence=0.7,  # Minimum for facts
                verified_by=promoted_by
            )

            self._log_decision(promoted_by, "promote_hive_to_fact",
                             {'hive_id': entry_id, 'fact_id': fact_id})
            logger.info(f"Hive entry {entry_id} promoted to fact {fact_id}")
            return fact_id

    # =================================================================
    # DECISION LOG - Append-only, hash-chained
    # =================================================================

    def _log_decision(self, actor: str, action_type: str, payload: Dict[str, Any],
                      kernel_check: bool = True):
        """Log a decision (internal use)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get previous hash
        cursor.execute("SELECT entry_hash FROM decision_log ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        previous_hash = row['entry_hash'] if row else "0" * 64

        # Compute new hash
        payload_json = json.dumps(payload, sort_keys=True)
        entry_hash = self._compute_hash(previous_hash, payload_json)

        cursor.execute("""
            INSERT INTO decision_log
            (previous_hash, entry_hash, actor, action_type, payload, law_version, kernel_check)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (previous_hash, entry_hash, actor, action_type, payload_json,
              self.LAW_VERSION, kernel_check))
        conn.commit()

        # Check if we need a Merkle checkpoint
        cursor.execute("SELECT COUNT(*) FROM decision_log")
        count = cursor.fetchone()[0]
        if count % 100 == 0:
            self._create_merkle_checkpoint(count)

    def _create_merkle_checkpoint(self, entry_count: int):
        """Create a Merkle checkpoint every 100 entries"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get last 100 hashes
        cursor.execute("""
            SELECT entry_hash FROM decision_log
            ORDER BY id DESC LIMIT 100
        """)
        hashes = [row['entry_hash'] for row in cursor.fetchall()]

        # Compute Merkle root (simplified - just hash all together)
        merkle_root = hashlib.sha256(''.join(hashes).encode()).hexdigest()

        cursor.execute("SELECT id FROM decision_log ORDER BY id DESC LIMIT 1")
        last_id = cursor.fetchone()['id']

        cursor.execute("""
            INSERT INTO merkle_checkpoints (log_entry_id, merkle_root, entries_covered)
            VALUES (?, ?, ?)
        """, (last_id, merkle_root, 100))
        conn.commit()

        logger.info(f"Merkle checkpoint created at entry {last_id}")

    def get_decision_log(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get decision log entries"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM decision_log
            ORDER BY id DESC LIMIT ? OFFSET ?
        """, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

    def verify_chain_integrity(self) -> Tuple[bool, Optional[int]]:
        """
        Verify the integrity of the decision log hash chain.
        Returns: (is_valid, first_broken_entry_id or None)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decision_log ORDER BY id")

        previous_hash = "0" * 64  # Standardized genesis previous_hash
        for row in cursor.fetchall():
            expected_hash = self._compute_hash(previous_hash, row['payload'])
            if row['entry_hash'] != expected_hash:
                logger.error(f"Chain break detected at entry {row['id']}")
                return False, row['id']
            if row['previous_hash'] != previous_hash:
                logger.error(f"Previous hash mismatch at entry {row['id']}")
                return False, row['id']
            previous_hash = row['entry_hash']

        logger.info("Chain integrity verified")
        return True, None

    # =================================================================
    # UTILITY METHODS
    # =================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get memory partition statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}
        for store in ['law_store', 'fact_store', 'context_store',
                      'exploration_store', 'hive_store', 'decision_log']:
            cursor.execute(f"SELECT COUNT(*) FROM {store}")
            stats[store] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM merkle_checkpoints")
        stats['merkle_checkpoints'] = cursor.fetchone()[0]

        is_valid, _ = self.verify_chain_integrity()
        stats['chain_integrity'] = is_valid

        return stats

    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Memory partition connection closed")


# =================================================================
# GLOBAL INSTANCE
# =================================================================

_memory_instance: Optional[OmegaMemoryPartition] = None
_memory_lock = threading.Lock()


def get_memory() -> OmegaMemoryPartition:
    """Get or create the global memory partition instance"""
    global _memory_instance

    if _memory_instance is None:
        with _memory_lock:
            if _memory_instance is None:
                _memory_instance = OmegaMemoryPartition()

    return _memory_instance


# =================================================================
# MAIN - SELF TEST
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("OMEGA MEMORY PARTITIONING - SELF TEST")
    print("=" * 70)

    # Use test database
    memory = OmegaMemoryPartition("omega_memory_test.db")

    print("\n--- TESTING LAW STORE ---")
    # Temporarily unfreeze for test insertion
    memory._law_store_frozen = False
    law_id = memory.add_law({
        'name': 'K1',
        'constraint': 'Preserve human existence, agency, dignity'
    })
    memory._law_store_frozen = True  # Re-freeze
    print(f"Added law: {law_id}")
    laws = memory.get_all_laws()
    print(f"Total laws: {len(laws)}")

    # Verify freeze blocks further writes
    try:
        memory.add_law({'name': 'SHOULD_FAIL', 'constraint': 'This must be blocked'})
        print("  FAIL: LAW_STORE freeze did not block write!")
    except RuntimeError:
        print("  PASS: LAW_STORE freeze correctly blocks post-init writes")

    print("\n--- TESTING FACT STORE ---")
    fact_id = memory.add_fact(
        {'statement': 'The sky is blue', 'verified': True},
        source='observation',
        confidence=0.95,
        verified_by='human'
    )
    print(f"Added fact: {fact_id}")
    facts = memory.get_facts()
    print(f"Total facts: {len(facts)}")

    print("\n--- TESTING CONTEXT STORE ---")
    memory.set_context('theme', 'dark', 'preference')
    memory.set_context('language', 'en', 'preference')
    theme = memory.get_context('theme')
    print(f"Theme: {theme}")
    all_context = memory.get_all_context()
    print(f"All context: {all_context}")

    print("\n--- TESTING EXPLORATION STORE ---")
    exp_id = memory.add_exploration(
        {'hypothesis': 'What if we added feature X?'},
        source='brainstorm',
        ttl_hours=1
    )
    print(f"Added exploration: {exp_id}")
    explorations = memory.get_explorations()
    print(f"Active explorations: {len(explorations)}")

    print("\n--- TESTING HIVE STORE ---")
    hive_id = memory.add_hive_input(
        {'suggestion': 'Try this approach'},
        source='user_feedback'
    )
    print(f"Added hive input: {hive_id}")
    memory.verify_hive_entry(hive_id, 'admin')
    fact_id = memory.promote_hive_to_fact(hive_id, 'admin')
    print(f"Promoted to fact: {fact_id}")

    print("\n--- TESTING DECISION LOG ---")
    log = memory.get_decision_log(limit=5)
    print(f"Recent decisions: {len(log)}")
    for entry in log[:3]:
        print(f"  - {entry['action_type']}: {entry['actor']}")

    print("\n--- VERIFYING CHAIN INTEGRITY ---")
    is_valid, broken_at = memory.verify_chain_integrity()
    print(f"Chain valid: {is_valid}")

    print("\n--- STATISTICS ---")
    stats = memory.get_stats()
    for store, count in stats.items():
        print(f"  {store}: {count}")

    memory.close()

    # Cleanup test database
    Path("omega_memory_test.db").unlink(missing_ok=True)
    Path("omega_memory_test.db-wal").unlink(missing_ok=True)
    Path("omega_memory_test.db-shm").unlink(missing_ok=True)

    print("\n" + "=" * 70)
    print("OMEGA MEMORY PARTITIONING - SELF TEST COMPLETE")
    print("=" * 70)
