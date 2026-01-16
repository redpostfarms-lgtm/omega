"""
Quantum-Enhanced File Manager Web API
Flask server with quantum-inspired file operations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from gatekeeper_file_manager import FileManager
from gatekeeper_quantum_file_manager import QuantumFileManager


class QuantumFileManagerAPI:
    """API wrapper for quantum file manager operations"""

    def __init__(self, root_path: str = "h:\\The Gatekeeper"):
        """Initialize quantum API with file manager"""
        self.fm = FileManager(root_path=root_path, enable_checksums=False)
        self.qfm = QuantumFileManager(self.fm)
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check with quantum status"""
            return jsonify({
                "status": "healthy",
                "service": "Quantum File Manager",
                "version": "2.0",
                "quantum_enhanced": True,
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/api/quantum/optimize', methods=['GET'])
        def quantum_optimize():
            """Optimize directory using quantum annealing"""
            directory = request.args.get('directory', '.')
            method = request.args.get('method', 'access_speed')

            try:
                optimized = self.qfm.optimize_directory(directory=directory, method=method)
                
                return jsonify({
                    "success": True,
                    "method": method,
                    "directory": directory,
                    "optimized_files": len(optimized),
                    "files": optimized[:100]  # Limit to 100
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.route('/api/quantum/search', methods=['GET'])
        def quantum_search():
            """Fast search using Grover's algorithm"""
            pattern = request.args.get('pattern', '*')
            directory = request.args.get('directory', '.')

            try:
                results = self.qfm.fast_search(pattern=pattern, directory=directory)
                
                return jsonify({
                    "success": True,
                    "search_type": "grover",
                    "pattern": pattern,
                    "directory": directory,
                    "total_results": len(results),
                    "results": results[:100]  # Limit to 100
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.route('/api/quantum/semantic-search', methods=['GET'])
        def quantum_semantic_search():
            """Semantic search with quantum relevance ranking"""
            query = request.args.get('query', '')
            directory = request.args.get('directory', '.')

            if not query:
                return jsonify({
                    "success": False,
                    "error": "Query parameter required"
                }), 400

            try:
                results = self.qfm.intelligent_search(query=query, directory=directory)
                
                return jsonify({
                    "success": True,
                    "search_type": "semantic",
                    "query": query,
                    "directory": directory,
                    "total_results": len(results),
                    "results": results[:100]  # Limit to 100
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.route('/api/quantum/dedup', methods=['GET'])
        def quantum_dedup():
            """Find duplicate files using quantum hashing"""
            directory = request.args.get('directory', '.')

            try:
                duplicates = self.qfm.find_duplicates(directory=directory)
                
                # Convert to list format for JSON
                dup_list = []
                for hash_val, paths in list(duplicates.items())[:100]:
                    dup_list.append({
                        "hash": hash_val,
                        "file_count": len(paths),
                        "files": paths
                    })
                
                return jsonify({
                    "success": True,
                    "directory": directory,
                    "duplicate_groups": len(duplicates),
                    "duplicates": dup_list
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.route('/api/quantum/stats', methods=['GET'])
        def quantum_stats():
            """Get quantum optimization statistics"""
            try:
                stats = self.qfm.get_quantum_stats()
                
                return jsonify({
                    "success": True,
                    "quantum_stats": stats,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.route('/api/quantum/info', methods=['GET'])
        def quantum_info():
            """Get quantum file manager information"""
            return jsonify({
                "success": True,
                "quantum_features": {
                    "grover_search": {
                        "description": "Fast quantum-inspired file search",
                        "endpoint": "/api/quantum/search?pattern=*.py",
                        "speedup": "Square root of N (dataset size)"
                    },
                    "quantum_annealing": {
                        "description": "Optimize file arrangement",
                        "endpoint": "/api/quantum/optimize?method=access_speed",
                        "methods": ["access_speed", "storage_efficiency", "listing_speed"]
                    },
                    "quantum_dedup": {
                        "description": "Find duplicate files via quantum hashing",
                        "endpoint": "/api/quantum/dedup?directory=.",
                        "algorithm": "Quantum-inspired hash matching"
                    },
                    "semantic_search": {
                        "description": "Semantic search with relevance ranking",
                        "endpoint": "/api/quantum/semantic-search?query=config",
                        "ranking": "Quantum amplitude amplification"
                    }
                }
            })

        @self.app.route('/api/browse', methods=['GET'])
        def browse():
            """List directory contents (standard)"""
            directory = request.args.get('directory', '.')

            try:
                files = self.fm.list_directory(directory=directory)
                
                return jsonify({
                    "success": True,
                    "directory": directory,
                    "total_items": len(files),
                    "items": [f.to_dict() for f in files]
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors"""
            return jsonify({
                "success": False,
                "error": "Endpoint not found",
                "available_quantum_endpoints": [
                    "/api/quantum/optimize",
                    "/api/quantum/search",
                    "/api/quantum/semantic-search",
                    "/api/quantum/dedup",
                    "/api/quantum/stats",
                    "/api/quantum/info"
                ]
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
    api = QuantumFileManagerAPI()
    return api.app


if __name__ == '__main__':
    print("Quantum-Enhanced File Manager Web API")
    print("=" * 60)
    print("Quantum Features Enabled:")
    print("  - Grover's Search Algorithm")
    print("  - Quantum Annealing Optimization")
    print("  - Quantum Hashing & Deduplication")
    print("  - Semantic Search with Quantum Ranking")
    print("=" * 60)
    print("\nStarting on http://localhost:5001")
    print("Quantum Endpoints:")
    print("  GET /api/quantum/optimize?method=access_speed")
    print("  GET /api/quantum/search?pattern=*.py")
    print("  GET /api/quantum/semantic-search?query=config")
    print("  GET /api/quantum/dedup?directory=.")
    print("  GET /api/quantum/stats")
    print("  GET /api/quantum/info")
    print()
    
    api = QuantumFileManagerAPI()
    api.run(host='localhost', port=5001, debug=False)
