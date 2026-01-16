"""
Advanced File Manager for Gatekeeper System
Provides comprehensive file operations, browsing, searching, and management capabilities
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import mimetypes


class FileType(Enum):
    """File type classifications"""
    DIRECTORY = "directory"
    FILE = "file"
    SYMLINK = "symlink"
    UNKNOWN = "unknown"


class SortBy(Enum):
    """Sorting options"""
    NAME = "name"
    SIZE = "size"
    DATE_MODIFIED = "date_modified"
    TYPE = "type"
    DATE_CREATED = "date_created"


@dataclass
class FileInfo:
    """File information container"""
    path: str
    name: str
    type: str
    size: int
    size_human: str
    created: str
    modified: str
    is_hidden: bool
    permissions: str
    mime_type: Optional[str]
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class FileManager:
    """Advanced file manager with comprehensive operations"""

    def __init__(self, root_path: str = ".", enable_checksums: bool = False):
        """
        Initialize file manager
        
        Args:
            root_path: Root directory for operations
            enable_checksums: Enable MD5 checksums for files
        """
        self.root_path = Path(root_path).resolve()
        self.enable_checksums = enable_checksums
        self.cache = {}
        self.favorites = []

    def _get_file_type(self, path: Path) -> FileType:
        """Determine file type"""
        if path.is_symlink():
            return FileType.SYMLINK
        elif path.is_dir():
            return FileType.DIRECTORY
        elif path.is_file():
            return FileType.FILE
        return FileType.UNKNOWN

    def _humanize_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def _get_permissions(self, path: Path) -> str:
        """Get file permissions as string"""
        try:
            mode = path.stat().st_mode
            return oct(mode)[-3:]
        except Exception:
            return "---"

    def _calculate_checksum(self, file_path: Path) -> Optional[str]:
        """Calculate MD5 checksum for file"""
        if not self.enable_checksums or not file_path.is_file():
            return None
        
        try:
            md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception:
            return None

    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """Get detailed information about a file"""
        try:
            path = (self.root_path / file_path).resolve()
            
            if not path.exists():
                return None
            
            stat = path.stat()
            file_type = self._get_file_type(path)
            
            created = datetime.fromtimestamp(stat.st_ctime).isoformat()
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            mime_type, _ = mimetypes.guess_type(str(path))
            
            return FileInfo(
                path=str(path),
                name=path.name,
                type=file_type.value,
                size=stat.st_size,
                size_human=self._humanize_size(stat.st_size),
                created=created,
                modified=modified,
                is_hidden=path.name.startswith('.'),
                permissions=self._get_permissions(path),
                mime_type=mime_type,
                checksum=self._calculate_checksum(path)
            )
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None

    def list_directory(self, directory: str = ".", include_hidden: bool = False,
                      sort_by: SortBy = SortBy.NAME, reverse: bool = False,
                      recursive: bool = False) -> List[FileInfo]:
        """
        List directory contents
        
        Args:
            directory: Directory path to list
            include_hidden: Include hidden files
            sort_by: Sort criteria
            reverse: Reverse sort order
            recursive: Recursive directory listing
        """
        try:
            dir_path = (self.root_path / directory).resolve()
            
            if not dir_path.is_dir():
                print(f"Not a directory: {directory}")
                return []
            
            files = []
            
            if recursive:
                for path in dir_path.rglob("*"):
                    if not include_hidden and any(part.startswith('.') for part in path.parts):
                        continue
                    file_info = self.get_file_info(str(path.relative_to(self.root_path)))
                    if file_info:
                        files.append(file_info)
            else:
                for path in dir_path.iterdir():
                    if not include_hidden and path.name.startswith('.'):
                        continue
                    file_info = self.get_file_info(str(path.relative_to(self.root_path)))
                    if file_info:
                        files.append(file_info)
            
            # Sort files
            if sort_by == SortBy.NAME:
                files.sort(key=lambda x: x.name.lower(), reverse=reverse)
            elif sort_by == SortBy.SIZE:
                files.sort(key=lambda x: x.size, reverse=reverse)
            elif sort_by == SortBy.DATE_MODIFIED:
                files.sort(key=lambda x: x.modified, reverse=reverse)
            elif sort_by == SortBy.TYPE:
                files.sort(key=lambda x: x.type, reverse=reverse)
            
            return files
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []

    def search(self, pattern: str, directory: str = ".", search_content: bool = False) -> List[FileInfo]:
        """
        Search for files by name or content
        
        Args:
            pattern: Search pattern (supports wildcards and regex)
            directory: Search directory
            search_content: Also search file contents
        """
        import fnmatch
        import re
        
        try:
            dir_path = (self.root_path / directory).resolve()
            results = []
            
            # Try as regex first, fall back to wildcard
            try:
                regex = re.compile(pattern)
                match_func = lambda name: regex.search(name) is not None
            except:
                match_func = lambda name: fnmatch.fnmatch(name.lower(), pattern.lower())
            
            for path in dir_path.rglob("*"):
                if match_func(path.name):
                    file_info = self.get_file_info(str(path.relative_to(self.root_path)))
                    if file_info:
                        results.append(file_info)
                
                # Search content if enabled
                if search_content and path.is_file():
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                file_info = self.get_file_info(str(path.relative_to(self.root_path)))
                                if file_info and file_info not in results:
                                    results.append(file_info)
                    except:
                        pass
            
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """Copy file to destination"""
        try:
            src_path = (self.root_path / source).resolve()
            dst_path = (self.root_path / destination).resolve()
            
            if not src_path.exists():
                print(f"Source not found: {source}")
                return False
            
            if dst_path.exists() and not overwrite:
                print(f"Destination exists: {destination}")
                return False
            
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path, dirs_exist_ok=overwrite)
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
            
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False

    def move_file(self, source: str, destination: str) -> bool:
        """Move file to destination"""
        try:
            src_path = (self.root_path / source).resolve()
            dst_path = (self.root_path / destination).resolve()
            
            if not src_path.exists():
                print(f"Source not found: {source}")
                return False
            
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    def delete_file(self, file_path: str, force: bool = False) -> bool:
        """Delete file or directory"""
        try:
            path = (self.root_path / file_path).resolve()
            
            if not path.exists():
                print(f"Path not found: {file_path}")
                return False
            
            if path.is_dir():
                if force:
                    shutil.rmtree(path)
                else:
                    path.rmdir()
            else:
                path.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def create_directory(self, dir_path: str, parents: bool = True) -> bool:
        """Create directory"""
        try:
            path = (self.root_path / dir_path).resolve()
            path.mkdir(parents=parents, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False

    def rename_file(self, source: str, new_name: str) -> bool:
        """Rename file or directory"""
        try:
            src_path = (self.root_path / source).resolve()
            
            if not src_path.exists():
                print(f"Path not found: {source}")
                return False
            
            dst_path = src_path.parent / new_name
            src_path.rename(dst_path)
            
            return True
        except Exception as e:
            print(f"Error renaming file: {e}")
            return False

    def get_directory_size(self, directory: str = ".") -> int:
        """Calculate total directory size"""
        try:
            dir_path = (self.root_path / directory).resolve()
            
            if not dir_path.is_dir():
                return 0
            
            total_size = 0
            for path in dir_path.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
            
            return total_size
        except Exception as e:
            print(f"Error calculating directory size: {e}")
            return 0

    def get_directory_stats(self, directory: str = ".") -> Dict[str, Any]:
        """Get directory statistics"""
        try:
            dir_path = (self.root_path / directory).resolve()
            
            if not dir_path.is_dir():
                return {}
            
            files = []
            dirs = []
            total_size = 0
            
            for path in dir_path.rglob("*"):
                if path.is_file():
                    files.append(path.name)
                    total_size += path.stat().st_size
                elif path.is_dir():
                    dirs.append(path.name)
            
            return {
                "total_files": len(files),
                "total_directories": len(dirs),
                "total_size": total_size,
                "total_size_human": self._humanize_size(total_size),
                "path": str(dir_path)
            }
        except Exception as e:
            print(f"Error getting directory stats: {e}")
            return {}

    def batch_operation(self, operation: str, files: List[str], **kwargs) -> Dict[str, Any]:
        """
        Perform batch operations on files
        
        Args:
            operation: Operation type (copy, move, delete, etc.)
            files: List of file paths
            **kwargs: Additional arguments for the operation
        """
        results = {
            "operation": operation,
            "total": len(files),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for file_path in files:
            try:
                if operation == "delete":
                    success = self.delete_file(file_path, **kwargs)
                elif operation == "copy":
                    destination = kwargs.get("destination", "")
                    success = self.copy_file(file_path, destination, **kwargs)
                elif operation == "move":
                    destination = kwargs.get("destination", "")
                    success = self.move_file(file_path, destination)
                else:
                    success = False
                
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to {operation}: {file_path}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error in {operation}: {file_path} - {str(e)}")
        
        return results

    def add_favorite(self, file_path: str) -> bool:
        """Add file to favorites"""
        try:
            path = (self.root_path / file_path).resolve()
            if path.exists() and str(path) not in self.favorites:
                self.favorites.append(str(path))
                return True
        except Exception as e:
            print(f"Error adding favorite: {e}")
        return False

    def get_favorites(self) -> List[str]:
        """Get list of favorite paths"""
        return self.favorites

    def export_listing(self, directory: str = ".", output_file: str = "file_listing.json",
                       include_details: bool = True) -> bool:
        """Export directory listing to JSON"""
        try:
            files = self.list_directory(directory, include_hidden=True, recursive=True)
            
            data = {
                "export_time": datetime.now().isoformat(),
                "directory": directory,
                "total_files": len(files),
                "files": [f.to_dict() if include_details else f.name for f in files]
            }
            
            output_path = self.root_path / output_file
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting listing: {e}")
            return False

    def get_recent_files(self, directory: str = ".", limit: int = 10) -> List[FileInfo]:
        """Get recently modified files"""
        try:
            files = self.list_directory(directory, include_hidden=True, recursive=True)
            files.sort(key=lambda x: x.modified, reverse=True)
            return files[:limit]
        except Exception as e:
            print(f"Error getting recent files: {e}")
            return []


def main():
    """Demonstrate file manager functionality"""
    print("Gatekeeper File Manager v1.0")
    print("=" * 50)
    
    # Initialize file manager
    fm = FileManager(root_path="h:\\The Gatekeeper", enable_checksums=False)
    
    # Example: List root directory
    print("\n[Listing Root Directory]")
    files = fm.list_directory(".", include_hidden=False, sort_by=SortBy.NAME)
    for f in files[:10]:
        print(f"  {f.name:30} | {f.size_human:12} | {f.type:10}")
    
    # Example: Directory statistics
    print("\n[Directory Statistics]")
    stats = fm.get_directory_stats(".")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Example: Search for Python files
    print("\n[Searching for Python Files]")
    results = fm.search("*.py", ".")
    print(f"  Found {len(results)} Python files")
    for f in results[:5]:
        print(f"    - {f.name}")
    
    # Example: Get file information
    print("\n[File Information]")
    file_info = fm.get_file_info("gatekeeper_integration_module.py")
    if file_info:
        print(f"  Name: {file_info.name}")
        print(f"  Size: {file_info.size_human}")
        print(f"  Type: {file_info.type}")
        print(f"  Modified: {file_info.modified}")
    
    print("\n" + "=" * 50)
    print("File Manager Ready")


if __name__ == "__main__":
    main()
