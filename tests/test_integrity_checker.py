"""
Tests for File Integrity Checker
=================================
"""

import pytest
import json
from pathlib import Path
from utils.integrity_checker import (
    IntegrityChecker,
    IntegrityError,
    verify_integrity
)


class TestIntegrityChecker:
    """Test file integrity verification"""

    def test_register_file(self, temp_dir):
        """Test file registration"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        record = checker.register_file(str(test_file))

        assert record.file_path == str(test_file.resolve())
        assert len(record.hash) == 64  # SHA-256 hex
        assert record.size > 0

    def test_verify_unchanged_file(self, temp_dir):
        """Test verification of unchanged file"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        checker.register_file(str(test_file))
        result = checker.verify_file(str(test_file), abort_on_mismatch=False)

        assert result['status'] == 'verified'

    def test_detect_file_modification(self, temp_dir):
        """Test detection of file modification"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))
        test_file = temp_dir / "test.txt"
        test_file.write_text("original content")

        checker.register_file(str(test_file))

        # Modify file
        test_file.write_text("modified content")

        result = checker.verify_file(str(test_file), abort_on_mismatch=False)

        assert result['status'] == 'corrupted'
        assert result['expected_hash'] != result['actual_hash']

    def test_abort_on_corruption(self, temp_dir):
        """Test abort behavior on corruption"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))
        test_file = temp_dir / "test.txt"
        test_file.write_text("original")

        checker.register_file(str(test_file))
        test_file.write_text("modified")

        with pytest.raises(IntegrityError):
            checker.verify_before_process(str(test_file))

    def test_batch_verify(self, temp_dir):
        """Test batch verification"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))

        # Create and register files
        files = []
        for i in range(5):
            test_file = temp_dir / f"file{i}.txt"
            test_file.write_text(f"content {i}")
            checker.register_file(str(test_file))
            files.append(str(test_file))

        # Corrupt one file
        (temp_dir / "file2.txt").write_text("corrupted")

        stats = checker.batch_verify(files, verbose=False)

        assert stats['total'] == 5
        assert stats['verified'] == 4
        assert stats['corrupted'] == 1

    def test_register_directory(self, temp_dir):
        """Test directory registration"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))

        # Create multiple files
        for i in range(3):
            (temp_dir / f"file{i}.txt").write_text(f"content {i}")

        count = checker.register_directory(str(temp_dir), "*.txt", recursive=False)

        assert count == 3

    def test_decorator_verify(self, temp_dir):
        """Test decorator-based verification"""
        checker = IntegrityChecker(str(temp_dir / ".integrity_db.json"))
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        checker.register_file(str(test_file))

        @verify_integrity(file_param='file_path')
        def process_file(file_path):
            return f"processed {file_path}"

        # Should work with valid file
        result = process_file(str(test_file))
        assert "processed" in result

        # Corrupt file
        test_file.write_text("corrupted")

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            process_file(str(test_file))

    def test_calculate_hash_consistency(self, temp_dir):
        """Test hash calculation consistency"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        hash1, size1 = IntegrityChecker.calculate_hash(str(test_file))
        hash2, size2 = IntegrityChecker.calculate_hash(str(test_file))

        assert hash1 == hash2
        assert size1 == size2

    def test_database_persistence(self, temp_dir):
        """Test that database persists across instances"""
        db_path = temp_dir / ".integrity_db.json"
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        # Register with first instance
        checker1 = IntegrityChecker(str(db_path))
        checker1.register_file(str(test_file))

        # Verify with second instance
        checker2 = IntegrityChecker(str(db_path))
        result = checker2.verify_file(str(test_file), abort_on_mismatch=False)

        assert result['status'] == 'verified'
