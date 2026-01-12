#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# KNOWLEDGE BASE WEB INTERFACE
# Web dashboard for semantic search, visualization, and query interface
# Uses Flask for web server, integrates with ChromaDB and Sentence Transformers

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
WEB_DIR = BRAIN / 'Archived' / 'knowledge_web'
WEB_DIR.mkdir(parents=True, exist_ok=True)

# Try to import Flask
try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[WARNING] Flask not installed. Install with: pip install flask")

# Try to import ChromaDB and Sentence Transformers
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("[WARNING] ChromaDB or Sentence Transformers not installed.")

class KnowledgeWebUI:
    """Web interface for knowledge base."""
    
    def __init__(self, port: int = 5000):
        """Initialize web UI."""
        self.port = port
        self.app = None
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.websocket_clients = []  # For real-time updates
        self.last_update_time = datetime.now()
        
        if FLASK_AVAILABLE:
            self.app = Flask(__name__, template_folder=str(WEB_DIR))
            self.setup_routes()
            self.setup_websocket()  # Real-time updates
        
        # Initialize ChromaDB if available
        if CHROMADB_AVAILABLE:
            try:
                chroma_db_path = BRAIN / 'Archived' / 'chroma_db'
                self.chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))
                try:
                    self.collection = self.chroma_client.get_or_create_collection(
                        name="gatekeeper_knowledge"
                    )
                except:
                    pass
                
                # Load embedding model
                try:
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                except:
                    pass
            except Exception as e:
                print(f"[WARNING] ChromaDB initialization error: {e}")
    
    def load_knowledge_json(self) -> List[Dict]:
        """Load knowledge from JSON file."""
        knowledge_db = BRAIN / 'Archived' / 'gatekeeper_knowledge.json'
        if knowledge_db.exists():
            try:
                with open(knowledge_db, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'knowledge' in data:
                        return data['knowledge']
            except Exception as e:
                print(f"[ERROR] Failed to load knowledge: {e}")
        return []
    
    def search_knowledge(self, query: str, n_results: int = 10) -> List[Dict]:
        """Search knowledge base."""
        results = []
        
        # Try ChromaDB semantic search first
        if self.collection and self.embedding_model:
            try:
                # Generate query embedding
                query_embedding = self.embedding_model.encode([query])[0]
                
                # Search ChromaDB
                search_results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=n_results
                )
                
                # Format results
                if search_results['ids'] and len(search_results['ids'][0]) > 0:
                    for i, doc_id in enumerate(search_results['ids'][0]):
                        results.append({
                            'id': doc_id,
                            'text': search_results['documents'][0][i] if search_results['documents'] else '',
                            'metadata': search_results['metadatas'][0][i] if search_results['metadatas'] else {},
                            'distance': search_results['distances'][0][i] if search_results['distances'] else 0.0,
                            'source': 'chromadb'
                        })
                    return results
            except Exception as e:
                print(f"[WARNING] ChromaDB search error: {e}")
        
        # Fallback to keyword search in JSON
        knowledge = self.load_knowledge_json()
        query_lower = query.lower()
        
        for item in knowledge:
            text = ""
            if isinstance(item, dict):
                text = json.dumps(item).lower()
            else:
                text = str(item).lower()
            
            if query_lower in text:
                results.append({
                    'id': str(len(results)),
                    'text': str(item),
                    'metadata': {},
                    'distance': 0.0,
                    'source': 'json'
                })
                if len(results) >= n_results:
                    break
        
        return results
    
    def get_knowledge_stats(self) -> Dict:
        """Get knowledge base statistics."""
        stats = {
            'total_entries': 0,
            'chromadb_entries': 0,
            'json_entries': 0,
            'last_updated': 'Unknown'
        }
        
        # Count JSON entries
        knowledge = self.load_knowledge_json()
        stats['json_entries'] = len(knowledge)
        stats['total_entries'] = len(knowledge)
        
        # Count ChromaDB entries
        if self.collection:
            try:
                count = self.collection.count()
                stats['chromadb_entries'] = count
                if count > stats['total_entries']:
                    stats['total_entries'] = count
            except:
                pass
        
        return stats
    
    def setup_websocket(self):
        """Setup WebSocket for real-time updates."""
        try:
            from flask_socketio import SocketIO, emit
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")
            self.websocket_enabled = True
            
            @self.socketio.on('connect')
            def handle_connect():
                self.websocket_clients.append(request.sid)
                emit('connected', {'status': 'connected'})
            
            @self.socketio.on('disconnect')
            def handle_disconnect():
                if request.sid in self.websocket_clients:
                    self.websocket_clients.remove(request.sid)
            
            print("[OK] WebSocket support enabled")
        except ImportError:
            self.websocket_enabled = False
            print("[WARNING] flask-socketio not installed. Real-time updates disabled.")
    
    def broadcast_update(self, data: Dict):
        """Broadcast update to all WebSocket clients."""
        if self.websocket_enabled and hasattr(self, 'socketio'):
            self.socketio.emit('knowledge_update', data, broadcast=True)
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gatekeeper Knowledge Base</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .search-box {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            width: 70%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #4CAF50;
            border-radius: 4px;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        button {
            padding: 12px 24px;
            font-size: 16px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        button:hover {
            background: #45a049;
        }
        .stats {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .results {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
        }
        .result-item {
            background: #1a1a1a;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }
        .result-meta {
            color: #888;
            font-size: 12px;
            margin-top: 10px;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Gatekeeper Knowledge Base</h1>
        <p>Red Post Farms, LLC | Semantic Search Interface</p>
        
        <div class="stats">
            <strong>Knowledge Base Statistics:</strong><br>
            Total Entries: {{ stats.total_entries }}<br>
            ChromaDB Entries: {{ stats.chromadb_entries }}<br>
            JSON Entries: {{ stats.json_entries }}
        </div>
        
        <div class="search-box">
            <form method="POST" action="/search">
                <input type="text" name="query" placeholder="Search knowledge base..." value="{{ query }}" required>
                <button type="submit">Search</button>
            </form>
        </div>
        
        {% if results %}
        <div class="results">
            <h2>Search Results ({{ results|length }})</h2>
            {% for result in results %}
            <div class="result-item">
                <div>{{ result.text[:500] }}{% if result.text|length > 500 %}...{% endif %}</div>
                <div class="result-meta">
                    Source: {{ result.source }} | 
                    Distance: {{ "%.3f"|format(result.distance) if result.distance else "N/A" }}
                </div>
            </div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="no-results">
            <p>No results found for "{{ query }}"</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
        """
        
        @self.app.route('/')
        def index():
            """Main page."""
            stats = self.get_knowledge_stats()
            return render_template_string(HTML_TEMPLATE, stats=stats, query='', results=None)
        
        @self.app.route('/search', methods=['POST'])
        def search():
            """Search endpoint."""
            query = request.form.get('query', '')
            stats = self.get_knowledge_stats()
            results = []
            
            if query:
                results = self.search_knowledge(query, n_results=20)
            
            return render_template_string(HTML_TEMPLATE, stats=stats, query=query, results=results)
        
        @self.app.route('/api/search', methods=['GET'])
        def api_search():
            """API search endpoint."""
            query = request.args.get('q', '')
            n_results = int(request.args.get('n', 10))
            
            if not query:
                return jsonify({'error': 'Query parameter required'}), 400
            
            results = self.search_knowledge(query, n_results=n_results)
            return jsonify({'query': query, 'results': results, 'count': len(results)})
        
        @self.app.route('/api/stats', methods=['GET'])
        def api_stats():
            """API stats endpoint."""
            stats = self.get_knowledge_stats()
            return jsonify(stats)
    
    def run(self, debug: bool = False):
        """Run web server."""
        if not FLASK_AVAILABLE:
            print("[ERROR] Flask not installed. Install with: pip install flask")
            return
        
        if not self.app:
            print("[ERROR] Flask app not initialized")
            return
        
        print("=" * 60)
        print("KNOWLEDGE BASE WEB INTERFACE")
        print("Red Post Farms, LLC | Copyright (c) 2025-2026")
        print("=" * 60)
        print()
        print("The doors of knowledge opens.")
        print("Starting web server...\n")
        print(f"🌐 Server running at: http://localhost:{self.port}")
        print(f"📊 Knowledge Base: {self.get_knowledge_stats()['total_entries']} entries")
        print()
        print("Press Ctrl+C to stop\n")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=debug)
        except KeyboardInterrupt:
            print("\n[INFO] Server stopped by user")
        except Exception as e:
            print(f"\n[ERROR] Server error: {e}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Base Web Interface')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    ui = KnowledgeWebUI(port=args.port)
    ui.run(debug=args.debug)

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

