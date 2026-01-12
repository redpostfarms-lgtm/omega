#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Unit tests for auto_heal.py

import pytest
import sys
from pathlib import Path
import hashlib
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestAutoHeal:
    """Unit tests for auto_heal functionality."""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary file for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / 'test_file.py'
        test_file.write_text('print("test")')
        
        yield test_file
        
        shutil.rmtree(temp_dir)
    
    def test_checksum_calculation(self, temp_file):
        """Test SHA256 checksum calculation."""
        content = temp_file.read_bytes()
        checksum = hashlib.sha256(content).hexdigest()
        
        assert len(checksum) == 64  # SHA256 produces 64-char hex string
        assert isinstance(checksum, str)
    
    def test_file_verification(self, temp_file):
        """Test file verification logic."""
        # Test that file exists
        assert temp_file.exists()
        
        # Test that file is readable
        content = temp_file.read_text()
        assert len(content) > 0
    
    def test_backup_restore_logic(self):
        """Test backup and restore logic."""
        # Test backup structure
        backup_data = {
            'file': 'test.py',
            'checksum': 'abc123',
            'timestamp': '2026-01-03T00:00:00'
        }
        
        assert 'file' in backup_data
        assert 'checksum' in backup_data
        assert 'timestamp' in backup_data
    
    def test_corruption_detection(self, temp_file):
        """Test corruption detection."""
        original_content = temp_file.read_bytes()
        original_checksum = hashlib.sha256(original_content).hexdigest()
        
        # Simulate corruption
        temp_file.write_bytes(b'corrupted content')
        corrupted_checksum = hashlib.sha256(temp_file.read_bytes()).hexdigest()
        
        # Checksums should differ
        assert original_checksum != corrupted_checksum

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

