"""
File Manager Web Interface for Gatekeeper System
Flask-based web UI for the advanced file manager
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from gatekeeper_file_manager import FileManager, SortBy


class FileManagerAPI:
    """API wrapper for file manager operations"""

    def __init__(self, root_path: str = "h:\\The Gatekeeper"):
        """Initialize API with file manager"""
        self.fm = FileManager(root_path=root_path, enable_checksums=False)
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "service": "File Manager",
                "version": "1.0",
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/api/browse', methods=['GET'])
        def browse():
            """List directory contents"""
            directory = request.args.get('directory', '.')
            include_hidden = request.args.get('include_hidden', 'false').lower() == 'true'
            sort_by = request.args.get('sort_by', 'name')
            recursive = request.args.get('recursive', 'false').lower() == 'true'

            try:
                sort_enum = SortBy[sort_by.upper()]
            except (KeyError, IndexError):
                sort_enum = SortBy.NAME

            files = self.fm.list_directory(
                directory=directory,
                include_hidden=include_hidden,
                sort_by=sort_enum,
                recursive=recursive
            )

            return jsonify({
                "success": True,
                "directory": directory,
                "total_items": len(files),
                "items": [f.to_dict() for f in files]
            })

        @self.app.route('/api/file-info', methods=['GET'])
        def file_info():
            """Get file information"""
            file_path = request.args.get('path', '')

            info = self.fm.get_file_info(file_path)
            if info:
                return jsonify({
                    "success": True,
                    "file": info.to_dict()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"File not found: {file_path}"
                }), 404

        @self.app.route('/api/stats', methods=['GET'])
        def stats():
            """Get directory statistics"""
            directory = request.args.get('directory', '.')

            stats_data = self.fm.get_directory_stats(directory)

            return jsonify({
                "success": True,
                "directory": directory,
                "stats": stats_data
            })

        @self.app.route('/api/search', methods=['GET'])
        def search():
            """Search for files"""
            pattern = request.args.get('pattern', '*')
            directory = request.args.get('directory', '.')
            search_content = request.args.get('content', 'false').lower() == 'true'

            results = self.fm.search(
                pattern=pattern,
                directory=directory,
                search_content=search_content
            )

            return jsonify({
                "success": True,
                "pattern": pattern,
                "total_results": len(results),
                "results": [f.to_dict() for f in results[:100]]  # Limit to 100 results
            })

        @self.app.route('/api/operations/copy', methods=['POST'])
        def copy_file():
            """Copy file"""
            data = request.get_json()
            source = data.get('source', '')
            destination = data.get('destination', '')
            overwrite = data.get('overwrite', False)

            success = self.fm.copy_file(
                source=source,
                destination=destination,
                overwrite=overwrite
            )

            return jsonify({
                "success": success,
                "source": source,
                "destination": destination,
                "message": "File copied successfully" if success else "Failed to copy file"
            })

        @self.app.route('/api/operations/move', methods=['POST'])
        def move_file():
            """Move file"""
            data = request.get_json()
            source = data.get('source', '')
            destination = data.get('destination', '')

            success = self.fm.move_file(source=source, destination=destination)

            return jsonify({
                "success": success,
                "source": source,
                "destination": destination,
                "message": "File moved successfully" if success else "Failed to move file"
            })

        @self.app.route('/api/operations/delete', methods=['POST'])
        def delete_file():
            """Delete file"""
            data = request.get_json()
            file_path = data.get('path', '')
            force = data.get('force', False)

            success = self.fm.delete_file(file_path=file_path, force=force)

            return jsonify({
                "success": success,
                "path": file_path,
                "message": "File deleted successfully" if success else "Failed to delete file"
            })

        @self.app.route('/api/operations/rename', methods=['POST'])
        def rename_file():
            """Rename file"""
            data = request.get_json()
            source = data.get('source', '')
            new_name = data.get('new_name', '')

            success = self.fm.rename_file(source=source, new_name=new_name)

            return jsonify({
                "success": success,
                "source": source,
                "new_name": new_name,
                "message": "File renamed successfully" if success else "Failed to rename file"
            })

        @self.app.route('/api/operations/mkdir', methods=['POST'])
        def mkdir():
            """Create directory"""
            data = request.get_json()
            directory = data.get('directory', '')
            parents = data.get('parents', True)

            success = self.fm.create_directory(dir_path=directory, parents=parents)

            return jsonify({
                "success": success,
                "directory": directory,
                "message": "Directory created successfully" if success else "Failed to create directory"
            })

        @self.app.route('/api/recent', methods=['GET'])
        def recent_files():
            """Get recently modified files"""
            directory = request.args.get('directory', '.')
            limit = int(request.args.get('limit', 10))

            files = self.fm.get_recent_files(directory=directory, limit=limit)

            return jsonify({
                "success": True,
                "directory": directory,
                "total_results": len(files),
                "files": [f.to_dict() for f in files]
            })

        @self.app.route('/api/favorites', methods=['GET'])
        def get_favorites():
            """Get favorites"""
            return jsonify({
                "success": True,
                "favorites": self.fm.get_favorites()
            })

        @self.app.route('/api/favorites', methods=['POST'])
        def add_favorite():
            """Add to favorites"""
            data = request.get_json()
            file_path = data.get('path', '')

            success = self.fm.add_favorite(file_path)

            return jsonify({
                "success": success,
                "path": file_path,
                "message": "Added to favorites" if success else "Failed to add to favorites"
            })

        @self.app.route('/api/export', methods=['POST'])
        def export_listing():
            """Export directory listing"""
            data = request.get_json()
            directory = data.get('directory', '.')
            output_file = data.get('output_file', 'file_listing.json')
            include_details = data.get('include_details', True)

            success = self.fm.export_listing(
                directory=directory,
                output_file=output_file,
                include_details=include_details
            )

            return jsonify({
                "success": success,
                "output_file": output_file,
                "message": "Listing exported successfully" if success else "Failed to export listing"
            })

        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors"""
            return jsonify({
                "success": False,
                "error": "Endpoint not found"
            }), 404

        @self.app.errorhandler(500)
        def server_error(error):
            """Handle 500 errors"""
            return jsonify({
                "success": False,
                "error": "Internal server error"
            }), 500

    def run(self, host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
        """Run the Flask app"""
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Factory function to create app"""
    api = FileManagerAPI()
    return api.app


if __name__ == '__main__':
    print("File Manager Web Interface")
    print("=" * 50)
    print("Starting on http://localhost:5001")
    print("=" * 50)
    
    api = FileManagerAPI()
    api.run(host='localhost', port=5001, debug=True)
