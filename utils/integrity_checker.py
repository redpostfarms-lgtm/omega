"""
File Integrity Checker
======================
SHA-256 hash-based integrity verification
Prevents corruption and detects unauthorized modifications
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FileIntegrityRecord:
    """Record of file integrity"""
    file_path: str
    hash: str
    size: int
    modified: str
    verified_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IntegrityChecker:
    """SHA-256 file integrity verification system"""

    def __init__(self, database_path: str = ".integrity_db.json"):
        """
        Initialize integrity checker

        Args:
            database_path: Path to integrity database
        """
        self.db_path = Path(database_path)
        self.records: Dict[str, FileIntegrityRecord] = {}
        self._load_database()

    def _load_database(self) -> None:
        """Load integrity database"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for file_path, record_data in data.items():
                        self.records[file_path] = FileIntegrityRecord(**record_data)
            except Exception as e:
                print(f"[Integrity] Warning: Could not load database: {e}")
                self.records = {}

    def _save_database(self) -> None:
        """Save integrity database"""
        try:
            data = {path: record.to_dict() for path, record in self.records.items()}
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Integrity] Error saving database: {e}")

    @staticmethod
    def calculate_hash(file_path: str) -> Tuple[str, int]:
        """
        Calculate SHA-256 hash of file

        Args:
            file_path: Path to file

        Returns:
            (hash_hex, file_size)
        """
        sha256 = hashlib.sha256()
        file_size = 0

        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
                    file_size += len(chunk)

            return sha256.hexdigest(), file_size
        except Exception as e:
            raise IOError(f"Cannot hash {file_path}: {e}")

    def register_file(self, file_path: str, force: bool = False) -> FileIntegrityRecord:
        """
        Register file and calculate its hash

        Args:
            file_path: Path to file
            force: Force re-registration even if exists

        Returns:
            Integrity record
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        abs_path = str(path.resolve())

        # Skip if already registered and not forcing
        if abs_path in self.records and not force:
            return self.records[abs_path]

        # Calculate hash
        file_hash, file_size = self.calculate_hash(abs_path)

        # Get modification time
        mod_time = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

        # Create record
        record = FileIntegrityRecord(
            file_path=abs_path,
            hash=file_hash,
            size=file_size,
            modified=mod_time,
            verified_at=datetime.now().isoformat()
        )

        self.records[abs_path] = record
        self._save_database()

        return record

    def verify_file(self, file_path: str, abort_on_mismatch: bool = True) -> Dict[str, Any]:
        """
        Verify file integrity against stored hash

        Args:
            file_path: Path to file
            abort_on_mismatch: Raise exception on integrity failure

        Returns:
            Verification result dictionary
        """
        path = Path(file_path)
        abs_path = str(path.resolve())

        # Check if file is registered
        if abs_path not in self.records:
            return {
                'status': 'not_registered',
                'file': abs_path,
                'message': 'File not in integrity database'
            }

        # Check if file exists
        if not path.exists():
            return {
                'status': 'missing',
                'file': abs_path,
                'message': 'File has been deleted'
            }

        # Calculate current hash
        try:
            current_hash, current_size = self.calculate_hash(abs_path)
        except Exception as e:
            return {
                'status': 'error',
                'file': abs_path,
                'message': f'Cannot read file: {e}'
            }

        # Compare with stored hash
        stored_record = self.records[abs_path]

        if current_hash == stored_record.hash:
            # Update verification timestamp
            stored_record.verified_at = datetime.now().isoformat()
            self._save_database()

            return {
                'status': 'verified',
                'file': abs_path,
                'hash': current_hash,
                'size': current_size,
                'message': 'Integrity verified'
            }
        else:
            # INTEGRITY FAILURE
            result = {
                'status': 'corrupted',
                'file': abs_path,
                'expected_hash': stored_record.hash,
                'actual_hash': current_hash,
                'expected_size': stored_record.size,
                'actual_size': current_size,
                'message': 'INTEGRITY FAILURE - File has been modified or corrupted'
            }

            if abort_on_mismatch:
                raise IntegrityError(
                    f"Integrity check failed for {abs_path}\n"
                    f"Expected: {stored_record.hash}\n"
                    f"Actual: {current_hash}\n"
                    f"File may be corrupted or tampered with!"
                )

            return result

    def verify_before_process(self, file_path: str) -> bool:
        """
        Verify file before processing (convenience method)

        Args:
            file_path: Path to file

        Returns:
            True if verified, raises IntegrityError if not

        Raises:
            IntegrityError: If file integrity check fails
        """
        result = self.verify_file(file_path, abort_on_mismatch=True)
        return result['status'] == 'verified'

    def batch_verify(self, file_paths: List[str], verbose: bool = True) -> Dict[str, Any]:
        """
        Verify multiple files

        Args:
            file_paths: List of file paths
            verbose: Print progress

        Returns:
            Verification statistics
        """
        stats = {
            'total': len(file_paths),
            'verified': 0,
            'corrupted': 0,
            'missing': 0,
            'not_registered': 0,
            'errors': 0,
            'failed_files': []
        }

        for file_path in file_paths:
            try:
                result = self.verify_file(file_path, abort_on_mismatch=False)
                status = result['status']

                if status == 'verified':
                    stats['verified'] += 1
                    if verbose:
                        print(f"✓ {file_path}")
                elif status == 'corrupted':
                    stats['corrupted'] += 1
                    stats['failed_files'].append(result)
                    if verbose:
                        print(f"✗ CORRUPTED: {file_path}")
                elif status == 'missing':
                    stats['missing'] += 1
                    if verbose:
                        print(f"? MISSING: {file_path}")
                elif status == 'not_registered':
                    stats['not_registered'] += 1
                else:
                    stats['errors'] += 1
            except Exception as e:
                stats['errors'] += 1
                if verbose:
                    print(f"✗ ERROR: {file_path} - {e}")

        return stats

    def register_directory(self, directory: str, pattern: str = "*",
                          recursive: bool = True) -> int:
        """
        Register all files in directory

        Args:
            directory: Directory path
            pattern: File pattern to match
            recursive: Recursive scan

        Returns:
            Number of files registered
        """
        dir_path = Path(directory)
        count = 0

        if recursive:
            files = dir_path.rglob(pattern)
        else:
            files = dir_path.glob(pattern)

        for file_path in files:
            if file_path.is_file():
                try:
                    self.register_file(str(file_path))
                    count += 1
                except Exception as e:
                    print(f"[Integrity] Error registering {file_path}: {e}")

        return count

    def remove_record(self, file_path: str) -> bool:
        """Remove file from integrity database"""
        abs_path = str(Path(file_path).resolve())
        if abs_path in self.records:
            del self.records[abs_path]
            self._save_database()
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get integrity database statistics"""
        return {
            'total_files': len(self.records),
            'database_path': str(self.db_path),
            'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0
        }


class IntegrityError(Exception):
    """Raised when file integrity check fails"""
    pass


# Decorator for automatic integrity checking
def verify_integrity(file_param: str = 'file_path'):
    """
    Decorator to verify file integrity before function execution

    Args:
        file_param: Name of parameter containing file path
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get file path from parameters
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            file_path = bound.arguments.get(file_param)
            if file_path:
                checker = IntegrityChecker()
                checker.verify_before_process(file_path)

            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    print("=" * 70)
    print("  FILE INTEGRITY CHECKER")
    print("=" * 70)
    print()
    print("Example usage:")
    print()
    print("  from utils.integrity_checker import IntegrityChecker")
    print()
    print("  # Initialize")
    print("  checker = IntegrityChecker()")
    print()
    print("  # Register file")
    print("  checker.register_file('important_data.json')")
    print()
    print("  # Verify before processing")
    print("  if checker.verify_before_process('important_data.json'):")
    print("      # Safe to process")
    print("      process_file('important_data.json')")
    print()
    print("  # Register entire directory")
    print("  count = checker.register_directory('conversations', '*.json')")
    print("  print(f'Registered {count} files')")
    print()
    print("  # Batch verify")
    print("  stats = checker.batch_verify(['file1.json', 'file2.json'])")
    print("  print(f'Verified: {stats[\"verified\"]} / {stats[\"total\"]}')")
    print()
    print("=" * 70)
