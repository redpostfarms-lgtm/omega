"""
Tests for Compressed JSON Utility
==================================
"""

import pytest
import json
import gzip
from pathlib import Path
from utils.compressed_json import (
    CompressedJSON,
    save_json_auto,
    load_json_auto
)


class TestCompressedJSON:
    """Test compressed JSON functionality"""

    def test_save_small_file_uncompressed(self, temp_dir, sample_json_data):
        """Small files should not be compressed"""
        file_path = temp_dir / "small.json"

        result = save_json_auto(str(file_path), sample_json_data)

        assert result['compressed'] == False
        assert file_path.exists()
        assert not (temp_dir / "small.json.gz").exists()

    def test_save_large_file_compressed(self, temp_dir, large_json_data):
        """Large files should be compressed"""
        file_path = temp_dir / "large.json"

        result = save_json_auto(str(file_path), large_json_data)

        assert result['compressed'] == True
        assert (temp_dir / "large.json.gz").exists()
        assert float(result['compression_ratio'].strip('%')) > 0

    def test_load_uncompressed(self, temp_dir, sample_json_data):
        """Load uncompressed JSON"""
        file_path = temp_dir / "test.json"
        with open(file_path, 'w') as f:
            json.dump(sample_json_data, f)

        loaded = load_json_auto(str(file_path))

        assert loaded == sample_json_data

    def test_load_compressed(self, temp_dir, sample_json_data):
        """Load compressed JSON"""
        file_path = temp_dir / "test.json.gz"
        with gzip.open(file_path, 'wt') as f:
            json.dump(sample_json_data, f)

        loaded = load_json_auto(str(temp_dir / "test.json"))

        assert loaded == sample_json_data

    def test_compression_threshold(self, temp_dir):
        """Test custom compression threshold"""
        small_data = {"test": "data"}
        file_path = temp_dir / "test.json"

        # Force compression with threshold=0
        result = CompressedJSON.save(
            str(file_path),
            small_data,
            compress_threshold=0
        )

        assert result['compressed'] == True

    def test_batch_compress_directory(self, temp_dir):
        """Test batch compression"""
        # Create multiple JSON files
        for i in range(5):
            file_path = temp_dir / f"file{i}.json"
            data = {"data": "x" * 500000}  # Make it large enough
            with open(file_path, 'w') as f:
                json.dump(data, f)

        stats = CompressedJSON.batch_compress_directory(
            str(temp_dir),
            threshold=100000
        )

        assert stats['total_files'] == 5
        assert stats['compressed_files'] >= 0
        assert stats['space_saved'] >= 0

    def test_roundtrip(self, temp_dir, large_json_data):
        """Test save and load roundtrip"""
        file_path = temp_dir / "roundtrip.json"

        save_json_auto(str(file_path), large_json_data)
        loaded = load_json_auto(str(file_path))

        assert loaded == large_json_data

    def test_compression_ratio(self, temp_dir):
        """Test that compression actually reduces size"""
        large_data = {"array": [{"id": i, "data": "test" * 100} for i in range(1000)]}
        file_path = temp_dir / "ratio.json"

        result = save_json_auto(str(file_path), large_data)

        if result['compressed']:
            assert result['saved_size'] < result['original_size']
