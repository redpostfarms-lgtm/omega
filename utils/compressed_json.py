"""
Compressed JSON Utilities
=========================
Automatic gzip compression for large JSON files (>2MB)
Prevents conversation folder bloat and improves I/O performance
"""

import json
import gzip
import os
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib


class CompressedJSON:
    """Handle JSON with automatic compression for files >2MB"""

    COMPRESSION_THRESHOLD = 2 * 1024 * 1024  # 2MB

    @staticmethod
    def calculate_size(data: Any) -> int:
        """Estimate JSON size before writing"""
        return len(json.dumps(data, separators=(',', ':')))

    @staticmethod
    def save(file_path: str, data: Any, compress_threshold: int = COMPRESSION_THRESHOLD,
             indent: Optional[int] = 2) -> Dict[str, Any]:
        """
        Save JSON with automatic compression if size exceeds threshold

        Args:
            file_path: Path to save file
            data: Data to save
            compress_threshold: Size threshold for compression (bytes)
            indent: JSON indentation (None for compact)

        Returns:
            Dict with save stats (compressed, original_size, saved_size, compression_ratio)
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Estimate size
        json_str = json.dumps(data, indent=indent, default=str)
        original_size = len(json_str.encode('utf-8'))

        # Decide whether to compress
        should_compress = original_size >= compress_threshold

        if should_compress:
            # Save compressed with .gz extension
            compressed_path = str(path) + '.gz'
            with gzip.open(compressed_path, 'wt', encoding='utf-8') as f:
                f.write(json_str)

            saved_size = os.path.getsize(compressed_path)
            compression_ratio = (1 - saved_size / original_size) * 100

            # Remove uncompressed version if exists
            if path.exists():
                os.remove(path)

            return {
                'compressed': True,
                'path': compressed_path,
                'original_size': original_size,
                'saved_size': saved_size,
                'compression_ratio': f'{compression_ratio:.1f}%'
            }
        else:
            # Save uncompressed
            with open(path, 'w', encoding='utf-8') as f:
                f.write(json_str)

            # Remove compressed version if exists
            compressed_path = str(path) + '.gz'
            if os.path.exists(compressed_path):
                os.remove(compressed_path)

            return {
                'compressed': False,
                'path': str(path),
                'original_size': original_size,
                'saved_size': original_size,
                'compression_ratio': '0%'
            }

    @staticmethod
    def load(file_path: str, auto_detect: bool = True) -> Any:
        """
        Load JSON with automatic decompression detection

        Args:
            file_path: Path to JSON file (with or without .gz)
            auto_detect: Automatically detect .gz files

        Returns:
            Loaded data
        """
        path = Path(file_path)

        # Try compressed version first
        if auto_detect:
            compressed_path = Path(str(path) + '.gz')
            if compressed_path.exists():
                with gzip.open(compressed_path, 'rt', encoding='utf-8') as f:
                    return json.load(f)

        # Check if file itself is gzipped
        if path.suffix == '.gz':
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                return json.load(f)

        # Load uncompressed
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

        raise FileNotFoundError(f"No JSON file found at {file_path}")

    @staticmethod
    def batch_compress_directory(directory: str, threshold: int = COMPRESSION_THRESHOLD,
                                  pattern: str = "*.json") -> Dict[str, Any]:
        """
        Batch compress all JSON files in directory

        Args:
            directory: Directory to scan
            threshold: Size threshold
            pattern: File pattern to match

        Returns:
            Compression statistics
        """
        dir_path = Path(directory)
        stats = {
            'total_files': 0,
            'compressed_files': 0,
            'space_saved': 0,
            'files': []
        }

        for json_file in dir_path.rglob(pattern):
            if json_file.suffix == '.gz':
                continue  # Skip already compressed

            file_size = json_file.stat().st_size
            stats['total_files'] += 1

            if file_size >= threshold:
                try:
                    # Load and re-save with compression
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    result = CompressedJSON.save(str(json_file), data, threshold)

                    if result['compressed']:
                        space_saved = result['original_size'] - result['saved_size']
                        stats['compressed_files'] += 1
                        stats['space_saved'] += space_saved
                        stats['files'].append({
                            'file': str(json_file),
                            'saved': space_saved,
                            'ratio': result['compression_ratio']
                        })
                except Exception as e:
                    print(f"Error compressing {json_file}: {e}")

        return stats


def save_json_auto(file_path: str, data: Any, **kwargs) -> Dict[str, Any]:
    """Convenience function - drop-in replacement for json.dump"""
    return CompressedJSON.save(file_path, data, **kwargs)


def load_json_auto(file_path: str) -> Any:
    """Convenience function - drop-in replacement for json.load"""
    return CompressedJSON.load(file_path)


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("  COMPRESSED JSON UTILITY")
    print("=" * 70)
    print()
    print("Example usage:")
    print()
    print("  from utils.compressed_json import save_json_auto, load_json_auto")
    print()
    print("  # Save (auto-compresses if >2MB)")
    print("  stats = save_json_auto('large_data.json', my_data)")
    print("  print(f'Saved {stats[\"compression_ratio\"]} space')")
    print()
    print("  # Load (auto-detects compression)")
    print("  data = load_json_auto('large_data.json')")
    print()
    print("  # Batch compress directory")
    print("  from utils.compressed_json import CompressedJSON")
    print("  stats = CompressedJSON.batch_compress_directory('conversations')")
    print("  print(f'Compressed {stats[\"compressed_files\"]} files')")
    print("  print(f'Saved {stats[\"space_saved\"] / 1024 / 1024:.1f}MB')")
    print()
    print("=" * 70)
