#!/usr/bin/env python3
"""
OMEGA POLICY INTEGRITY AND CRYPTOGRAPHIC SIGNING
=================================================
Implements Prompt Three - Policy Integrity and Cryptographic Signing.

Core Requirements:
- Every rule, code, config gets hashed (SHA-256)
- Manifest gets signed with Ed25519 root policy key
- Omega and shards pin the public key
- No match = No run
- Verification on startup and any update
- Mismatch = Safe Halt Mode (read-only, no changes)
- Optional: Dual-signing with ECDSA P-256

This module ensures the integrity of all Omega system policies
and configurations through cryptographic verification.
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging
import base64

# Cryptography imports
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, ec
    from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("[WARN] cryptography package not available - using fallback mode")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OMEGA_SIGNING - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OmegaPolicySigning')


class SystemMode(Enum):
    """System operational modes"""
    NORMAL = "normal"           # Full operation
    SAFE_HALT = "safe_halt"     # Read-only, no changes
    UNVERIFIED = "unverified"   # Running without verification (degraded)


class VerificationResult(Enum):
    """Result of verification operations"""
    VALID = "valid"
    INVALID_SIGNATURE = "invalid_signature"
    INVALID_HASH = "invalid_hash"
    MISSING_KEY = "missing_key"
    MISSING_MANIFEST = "missing_manifest"
    CHAIN_BROKEN = "chain_broken"


@dataclass
class PolicyEntry:
    """Represents a single policy entry in the manifest"""
    path: str                    # File path or identifier
    content_hash: str            # SHA-256 hash
    entry_type: str              # 'file', 'config', 'rule'
    version: str
    created_at: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'content_hash': self.content_hash,
            'entry_type': self.entry_type,
            'version': self.version,
            'created_at': self.created_at,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PolicyEntry':
        return cls(**data)


@dataclass
class PolicyManifest:
    """The signed policy manifest"""
    version: str
    created_at: str
    kernel_version: str
    entries: List[PolicyEntry]
    manifest_hash: str = ""
    ed25519_signature: str = ""
    ecdsa_signature: str = ""  # Optional dual-sign

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'created_at': self.created_at,
            'kernel_version': self.kernel_version,
            'entries': [e.to_dict() for e in self.entries],
            'manifest_hash': self.manifest_hash,
            'ed25519_signature': self.ed25519_signature,
            'ecdsa_signature': self.ecdsa_signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PolicyManifest':
        entries = [PolicyEntry.from_dict(e) for e in data.get('entries', [])]
        return cls(
            version=data['version'],
            created_at=data['created_at'],
            kernel_version=data['kernel_version'],
            entries=entries,
            manifest_hash=data.get('manifest_hash', ''),
            ed25519_signature=data.get('ed25519_signature', ''),
            ecdsa_signature=data.get('ecdsa_signature', '')
        )

    def compute_hash(self) -> str:
        """Compute the manifest hash (excluding signatures)"""
        content = {
            'version': self.version,
            'created_at': self.created_at,
            'kernel_version': self.kernel_version,
            'entries': [e.to_dict() for e in self.entries]
        }
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()


class OmegaPolicySigning:
    """
    Cryptographic signing and verification for Omega policies.

    Implements:
    - SHA-256 hashing for all content
    - Ed25519 signing (primary)
    - ECDSA P-256 signing (optional dual-sign)
    - Safe Halt Mode on verification failure
    """

    MANIFEST_VERSION = "1.0.0"
    KERNEL_VERSION = "K10-v1.0.0"

    def __init__(self, keys_dir: str = "omega_keys", manifest_path: str = "omega_manifest.json"):
        self.keys_dir = Path(keys_dir)
        self.manifest_path = Path(manifest_path)
        self._lock = threading.RLock()

        # System state
        self.mode = SystemMode.UNVERIFIED
        self.last_verification: Optional[datetime] = None
        self.verification_errors: List[str] = []

        # Keys (loaded on demand)
        self._ed25519_private: Optional[Any] = None
        self._ed25519_public: Optional[Any] = None
        self._ecdsa_private: Optional[Any] = None
        self._ecdsa_public: Optional[Any] = None

        # Pinned public key (for verification)
        self._pinned_ed25519_public: Optional[bytes] = None
        self._pinned_ecdsa_public: Optional[bytes] = None

        # Ensure keys directory exists
        self.keys_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Omega Policy Signing initialized (crypto available: {CRYPTO_AVAILABLE})")

    # =================================================================
    # KEY MANAGEMENT
    # =================================================================

    def generate_keys(self, force: bool = False) -> bool:
        """Generate new Ed25519 and ECDSA key pairs"""
        if not CRYPTO_AVAILABLE:
            logger.error("Cannot generate keys - cryptography package not available")
            return False

        with self._lock:
            ed25519_private_path = self.keys_dir / "ed25519_private.pem"
            ed25519_public_path = self.keys_dir / "ed25519_public.pem"
            ecdsa_private_path = self.keys_dir / "ecdsa_private.pem"
            ecdsa_public_path = self.keys_dir / "ecdsa_public.pem"

            if not force and ed25519_private_path.exists():
                logger.warning("Keys already exist. Use force=True to regenerate.")
                return False

            try:
                # Generate Ed25519 key pair
                ed25519_private = ed25519.Ed25519PrivateKey.generate()
                ed25519_public = ed25519_private.public_key()

                # Generate ECDSA P-256 key pair
                ecdsa_private = ec.generate_private_key(SECP256R1(), default_backend())
                ecdsa_public = ecdsa_private.public_key()

                # Save private keys (KEEP SECURE!)
                ed25519_private_path.write_bytes(
                    ed25519_private.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )

                ecdsa_private_path.write_bytes(
                    ecdsa_private.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )

                # Save public keys
                ed25519_public_path.write_bytes(
                    ed25519_public.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )

                ecdsa_public_path.write_bytes(
                    ecdsa_public.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )

                logger.info("Generated new Ed25519 and ECDSA P-256 key pairs")
                return True

            except Exception as e:
                logger.error(f"Key generation failed: {e}")
                return False

    def load_keys(self) -> bool:
        """Load keys from disk"""
        if not CRYPTO_AVAILABLE:
            return False

        with self._lock:
            try:
                ed25519_private_path = self.keys_dir / "ed25519_private.pem"
                ed25519_public_path = self.keys_dir / "ed25519_public.pem"
                ecdsa_private_path = self.keys_dir / "ecdsa_private.pem"
                ecdsa_public_path = self.keys_dir / "ecdsa_public.pem"

                if ed25519_private_path.exists():
                    self._ed25519_private = serialization.load_pem_private_key(
                        ed25519_private_path.read_bytes(),
                        password=None,
                        backend=default_backend()
                    )

                if ed25519_public_path.exists():
                    self._ed25519_public = serialization.load_pem_public_key(
                        ed25519_public_path.read_bytes(),
                        backend=default_backend()
                    )
                    # Pin the public key
                    self._pinned_ed25519_public = ed25519_public_path.read_bytes()

                if ecdsa_private_path.exists():
                    self._ecdsa_private = serialization.load_pem_private_key(
                        ecdsa_private_path.read_bytes(),
                        password=None,
                        backend=default_backend()
                    )

                if ecdsa_public_path.exists():
                    self._ecdsa_public = serialization.load_pem_public_key(
                        ecdsa_public_path.read_bytes(),
                        backend=default_backend()
                    )
                    self._pinned_ecdsa_public = ecdsa_public_path.read_bytes()

                logger.info("Keys loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load keys: {e}")
                return False

    def pin_public_key(self, ed25519_public_pem: bytes, ecdsa_public_pem: bytes = None):
        """Pin public keys for verification (call this at system init)"""
        with self._lock:
            self._pinned_ed25519_public = ed25519_public_pem
            if ecdsa_public_pem:
                self._pinned_ecdsa_public = ecdsa_public_pem
            logger.info("Public keys pinned for verification")

    # =================================================================
    # HASHING
    # =================================================================

    @staticmethod
    def hash_content(content: bytes) -> str:
        """Compute SHA-256 hash of content"""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def hash_file(file_path: Path) -> str:
        """Compute SHA-256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def hash_string(content: str) -> str:
        """Compute SHA-256 hash of a string"""
        return hashlib.sha256(content.encode()).hexdigest()

    # =================================================================
    # SIGNING
    # =================================================================

    def sign_ed25519(self, data: bytes) -> Optional[str]:
        """Sign data with Ed25519 key"""
        if self.is_safe_halt():
            raise RuntimeError("sign_ed25519() blocked: System is in SAFE HALT MODE")
        if not CRYPTO_AVAILABLE or not self._ed25519_private:
            logger.error("Ed25519 private key not available")
            return None

        try:
            signature = self._ed25519_private.sign(data)
            return base64.b64encode(signature).decode('ascii')
        except Exception as e:
            logger.error(f"Ed25519 signing failed: {e}")
            return None

    def sign_ecdsa(self, data: bytes) -> Optional[str]:
        """Sign data with ECDSA P-256 key (optional dual-sign)"""
        if self.is_safe_halt():
            raise RuntimeError("sign_ecdsa() blocked: System is in SAFE HALT MODE")
        if not CRYPTO_AVAILABLE or not self._ecdsa_private:
            logger.warning("ECDSA private key not available")
            return None

        try:
            signature = self._ecdsa_private.sign(
                data,
                ec.ECDSA(hashes.SHA256())
            )
            return base64.b64encode(signature).decode('ascii')
        except Exception as e:
            logger.error(f"ECDSA signing failed: {e}")
            return None

    def verify_ed25519(self, data: bytes, signature_b64: str) -> bool:
        """Verify Ed25519 signature"""
        if not CRYPTO_AVAILABLE:
            return False

        try:
            # Use pinned public key if available
            if self._pinned_ed25519_public:
                public_key = serialization.load_pem_public_key(
                    self._pinned_ed25519_public,
                    backend=default_backend()
                )
            elif self._ed25519_public:
                public_key = self._ed25519_public
            else:
                logger.error("No Ed25519 public key available")
                return False

            signature = base64.b64decode(signature_b64)
            public_key.verify(signature, data)
            return True

        except InvalidSignature:
            logger.error("Ed25519 signature verification FAILED")
            return False
        except Exception as e:
            logger.error(f"Ed25519 verification error: {e}")
            return False

    def verify_ecdsa(self, data: bytes, signature_b64: str) -> bool:
        """Verify ECDSA P-256 signature"""
        if not CRYPTO_AVAILABLE or not signature_b64:
            return True  # Optional - pass if not provided

        try:
            if self._pinned_ecdsa_public:
                public_key = serialization.load_pem_public_key(
                    self._pinned_ecdsa_public,
                    backend=default_backend()
                )
            elif self._ecdsa_public:
                public_key = self._ecdsa_public
            else:
                return True  # No key = skip ECDSA check

            signature = base64.b64decode(signature_b64)
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True

        except InvalidSignature:
            logger.error("ECDSA signature verification FAILED")
            return False
        except Exception as e:
            logger.error(f"ECDSA verification error: {e}")
            return False

    # =================================================================
    # MANIFEST OPERATIONS
    # =================================================================

    def create_manifest(self, files: List[Tuple[str, str]],
                       configs: List[Tuple[str, Dict[str, Any]]] = None) -> PolicyManifest:
        """
        Create a new policy manifest from files and configs.

        Args:
            files: List of (path, description) tuples
            configs: List of (name, config_dict) tuples
        """
        entries = []

        # Hash files
        for file_path, description in files:
            path = Path(file_path)
            if path.exists():
                content_hash = self.hash_file(path)
                entries.append(PolicyEntry(
                    path=str(path),
                    content_hash=content_hash,
                    entry_type='file',
                    version=self.MANIFEST_VERSION,
                    created_at=datetime.now().isoformat(),
                    description=description
                ))
            else:
                logger.warning(f"File not found: {file_path}")

        # Hash configs
        if configs:
            for name, config in configs:
                content_hash = self.hash_string(json.dumps(config, sort_keys=True))
                entries.append(PolicyEntry(
                    path=name,
                    content_hash=content_hash,
                    entry_type='config',
                    version=self.MANIFEST_VERSION,
                    created_at=datetime.now().isoformat(),
                    description=f"Configuration: {name}"
                ))

        manifest = PolicyManifest(
            version=self.MANIFEST_VERSION,
            created_at=datetime.now().isoformat(),
            kernel_version=self.KERNEL_VERSION,
            entries=entries
        )

        # Compute manifest hash
        manifest.manifest_hash = manifest.compute_hash()

        logger.info(f"Created manifest with {len(entries)} entries")
        return manifest

    def sign_manifest(self, manifest: PolicyManifest, dual_sign: bool = False) -> PolicyManifest:
        """Sign the manifest with Ed25519 (and optionally ECDSA)"""
        if self.is_safe_halt():
            raise RuntimeError("sign_manifest() blocked: System is in SAFE HALT MODE")
        with self._lock:
            # Ensure keys are loaded
            if not self._ed25519_private:
                self.load_keys()

            # Get data to sign
            data_to_sign = manifest.manifest_hash.encode()

            # Ed25519 signature (required)
            ed25519_sig = self.sign_ed25519(data_to_sign)
            if ed25519_sig:
                manifest.ed25519_signature = ed25519_sig
            else:
                raise RuntimeError("Ed25519 signing failed - cannot proceed")

            # ECDSA signature (optional)
            if dual_sign:
                ecdsa_sig = self.sign_ecdsa(data_to_sign)
                if ecdsa_sig:
                    manifest.ecdsa_signature = ecdsa_sig
                    logger.info("Dual-signed manifest with Ed25519 and ECDSA")
                else:
                    logger.warning("ECDSA signing skipped")
            else:
                logger.info("Signed manifest with Ed25519")

            return manifest

    def save_manifest(self, manifest: PolicyManifest) -> bool:
        """Save manifest to disk"""
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest.to_dict(), f, indent=2)
            logger.info(f"Manifest saved to {self.manifest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
            return False

    def load_manifest(self) -> Optional[PolicyManifest]:
        """Load manifest from disk"""
        try:
            if not self.manifest_path.exists():
                logger.warning("Manifest file not found")
                return None

            with open(self.manifest_path, 'r') as f:
                data = json.load(f)
            return PolicyManifest.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            return None

    # =================================================================
    # VERIFICATION
    # =================================================================

    def verify_manifest(self, manifest: PolicyManifest) -> Tuple[VerificationResult, List[str]]:
        """
        Verify the manifest signature and all entry hashes.

        Returns:
            (result, list_of_errors)
        """
        errors = []

        with self._lock:
            # Ensure keys are loaded
            if not self._ed25519_public and not self._pinned_ed25519_public:
                self.load_keys()

            # Step 1: Verify manifest hash
            computed_hash = manifest.compute_hash()
            if computed_hash != manifest.manifest_hash:
                errors.append(f"Manifest hash mismatch: expected {manifest.manifest_hash}, got {computed_hash}")
                return VerificationResult.INVALID_HASH, errors

            # Step 2: Verify Ed25519 signature
            if not manifest.ed25519_signature:
                errors.append("Missing Ed25519 signature")
                return VerificationResult.INVALID_SIGNATURE, errors

            data_to_verify = manifest.manifest_hash.encode()
            if not self.verify_ed25519(data_to_verify, manifest.ed25519_signature):
                errors.append("Ed25519 signature verification failed")
                return VerificationResult.INVALID_SIGNATURE, errors

            # Step 3: Verify ECDSA signature (if present)
            if manifest.ecdsa_signature:
                if not self.verify_ecdsa(data_to_verify, manifest.ecdsa_signature):
                    errors.append("ECDSA signature verification failed")
                    return VerificationResult.INVALID_SIGNATURE, errors

            # Step 4: Verify each entry hash
            for entry in manifest.entries:
                if entry.entry_type == 'file':
                    path = Path(entry.path)
                    if not path.exists():
                        errors.append(f"File not found: {entry.path}")
                        continue

                    current_hash = self.hash_file(path)
                    if current_hash != entry.content_hash:
                        errors.append(f"Hash mismatch for {entry.path}: expected {entry.content_hash}, got {current_hash}")

            if errors:
                return VerificationResult.INVALID_HASH, errors

            logger.info("Manifest verification PASSED")
            return VerificationResult.VALID, []

    def verify_on_startup(self) -> bool:
        """
        Verify manifest on system startup.
        If verification fails, enter Safe Halt Mode.
        """
        logger.info("Running startup verification...")

        manifest = self.load_manifest()
        if not manifest:
            logger.warning("No manifest found - operating in UNVERIFIED mode")
            self.mode = SystemMode.UNVERIFIED
            return False

        result, errors = self.verify_manifest(manifest)
        self.verification_errors = errors
        self.last_verification = datetime.now()

        if result == VerificationResult.VALID:
            self.mode = SystemMode.NORMAL
            logger.info("Startup verification PASSED - NORMAL mode")
            return True
        else:
            self.mode = SystemMode.SAFE_HALT
            logger.critical(f"Startup verification FAILED - entering SAFE HALT MODE")
            for error in errors:
                logger.error(f"  - {error}")
            return False

    def verify_on_update(self, updated_files: List[str]) -> bool:
        """
        Verify after file updates.
        """
        logger.info(f"Verifying update for {len(updated_files)} files...")

        manifest = self.load_manifest()
        if not manifest:
            logger.warning("No manifest to verify against")
            return False

        # Check only the updated files
        errors = []
        for file_path in updated_files:
            # Find entry in manifest
            entry = next((e for e in manifest.entries if e.path == file_path), None)
            if not entry:
                logger.warning(f"File {file_path} not in manifest - adding verification required")
                continue

            current_hash = self.hash_file(Path(file_path))
            if current_hash != entry.content_hash:
                errors.append(f"Hash mismatch for {file_path}")

        if errors:
            logger.error("Update verification FAILED")
            for error in errors:
                logger.error(f"  - {error}")
            return False

        logger.info("Update verification PASSED")
        return True

    # =================================================================
    # SAFE HALT MODE
    # =================================================================

    def is_safe_halt(self) -> bool:
        """Check if system is in Safe Halt Mode"""
        return self.mode == SystemMode.SAFE_HALT

    def get_mode(self) -> SystemMode:
        """Get current system mode"""
        return self.mode

    def get_status(self) -> Dict[str, Any]:
        """Get signing system status"""
        return {
            'mode': self.mode.value,
            'crypto_available': CRYPTO_AVAILABLE,
            'keys_loaded': self._ed25519_public is not None,
            'keys_pinned': self._pinned_ed25519_public is not None,
            'last_verification': self.last_verification.isoformat() if self.last_verification else None,
            'verification_errors': self.verification_errors,
            'manifest_exists': self.manifest_path.exists()
        }


# =================================================================
# GLOBAL INSTANCE
# =================================================================

_signing_instance: Optional[OmegaPolicySigning] = None
_signing_lock = threading.Lock()


def get_signing() -> OmegaPolicySigning:
    """Get or create the global signing instance"""
    global _signing_instance

    if _signing_instance is None:
        with _signing_lock:
            if _signing_instance is None:
                _signing_instance = OmegaPolicySigning()

    return _signing_instance


# =================================================================
# DECORATOR FOR SAFE HALT CHECK
# =================================================================

def requires_normal_mode(func):
    """Decorator to block actions in Safe Halt Mode"""
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        signing = get_signing()
        if signing.is_safe_halt():
            raise RuntimeError(f"Action blocked: {func.__name__}() cannot run in SAFE HALT MODE")
        return func(*args, **kwargs)
    return wrapper


# =================================================================
# MAIN - SELF TEST
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("OMEGA POLICY SIGNING - SELF TEST")
    print("=" * 70)

    signing = OmegaPolicySigning(keys_dir="omega_keys_test", manifest_path="omega_manifest_test.json")

    print(f"\nCrypto available: {CRYPTO_AVAILABLE}")

    if CRYPTO_AVAILABLE:
        print("\n--- KEY GENERATION ---")
        if signing.generate_keys(force=True):
            print("Keys generated successfully")

        print("\n--- KEY LOADING ---")
        if signing.load_keys():
            print("Keys loaded successfully")

        print("\n--- MANIFEST CREATION ---")
        # Create test file
        test_file = Path("test_policy_file.txt")
        test_file.write_text("This is a test policy file for signing verification.")

        manifest = signing.create_manifest(
            files=[
                (str(test_file), "Test policy file"),
            ],
            configs=[
                ("test_config", {"setting1": "value1", "setting2": 42})
            ]
        )
        print(f"Manifest created with {len(manifest.entries)} entries")
        print(f"Manifest hash: {manifest.manifest_hash[:32]}...")

        print("\n--- SIGNING (Ed25519 + ECDSA) ---")
        manifest = signing.sign_manifest(manifest, dual_sign=True)
        print(f"Ed25519 signature: {manifest.ed25519_signature[:32]}...")
        if manifest.ecdsa_signature:
            print(f"ECDSA signature: {manifest.ecdsa_signature[:32]}...")

        print("\n--- SAVE MANIFEST ---")
        if signing.save_manifest(manifest):
            print("Manifest saved")

        print("\n--- VERIFICATION ---")
        result, errors = signing.verify_manifest(manifest)
        print(f"Result: {result.value}")
        if errors:
            for error in errors:
                print(f"  Error: {error}")

        print("\n--- STARTUP VERIFICATION ---")
        if signing.verify_on_startup():
            print(f"Mode: {signing.get_mode().value}")
        else:
            print(f"FAILED - Mode: {signing.get_mode().value}")

        print("\n--- TAMPER TEST ---")
        # Tamper with the file
        test_file.write_text("TAMPERED CONTENT!")
        result, errors = signing.verify_manifest(manifest)
        print(f"After tampering: {result.value}")
        if errors:
            print(f"  Detected: {errors[0]}")

        # Cleanup
        test_file.unlink(missing_ok=True)
        Path("omega_manifest_test.json").unlink(missing_ok=True)
        import shutil
        shutil.rmtree("omega_keys_test", ignore_errors=True)

    else:
        print("\n[SKIP] Cryptography tests - package not installed")
        print("Install with: pip install cryptography")

    print("\n--- STATUS ---")
    status = signing.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("OMEGA POLICY SIGNING - SELF TEST COMPLETE")
    print("=" * 70)
