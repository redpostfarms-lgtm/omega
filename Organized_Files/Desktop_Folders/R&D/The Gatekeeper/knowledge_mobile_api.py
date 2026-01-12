# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Knowledge Mobile API
Mobile app integration API for knowledge management
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
MOBILE_API_DIR = ARCHIVED / 'knowledge_mobile'
MOBILE_API_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeMobileAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for mobile API."""
    
    def __init__(self, api_server, *args, **kwargs):
        self.api_server = api_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        endpoint = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if endpoint == '/mobile/api/notes':
            notes = self.api_server.get_notes(limit=int(query_params.get('limit', [100])[0]))
            self._send_response(200, {'notes': notes})
        elif endpoint == '/mobile/api/search':
            query = query_params.get('q', [''])[0]
            results = self.api_server.search_notes(query)
            self._send_response(200, {'results': results})
        else:
            self._send_response(404, {'error': 'Endpoint not found'})
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        endpoint = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            self._send_response(400, {'error': 'Invalid JSON'})
            return
        
        if endpoint == '/mobile/api/notes':
            result = self.api_server.create_note(data)
            self._send_response(201, result)
        else:
            self._send_response(404, {'error': 'Endpoint not found'})
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to suppress default logging."""
        pass

class KnowledgeMobileAPI:
    """Mobile API for knowledge management."""
    
    def __init__(self, host: str = 'localhost', port: int = 8081):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        self.data_file = MOBILE_API_DIR / 'mobile_data.json'
        self._load_data()
    
    def _load_data(self):
        """Load data from disk."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {'notes': []}
        else:
            self.data = {'notes': []}
    
    def _save_data(self):
        """Save data to disk."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def create_api_endpoint(self) -> HTTPServer:
        """Create API endpoint."""
        def handler(*args, **kwargs):
            return KnowledgeMobileAPIHandler(self, *args, **kwargs)
        
        server = HTTPServer((self.host, self.port), handler)
        return server
    
    def sync_mobile(self, mobile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync data with mobile app.
        
        Args:
            mobile_data: Data from mobile app
        
        Returns:
            Sync result
        """
        # Merge mobile data with local data
        if 'notes' in mobile_data:
            for note in mobile_data['notes']:
                # Update or add note
                existing = next((n for n in self.data['notes'] if n.get('id') == note.get('id')), None)
                if existing:
                    existing.update(note)
                    existing['updated_at'] = time.time()
                else:
                    note['id'] = note.get('id', f"note_{int(time.time())}")
                    note['created_at'] = time.time()
                    self.data['notes'].append(note)
        
        self._save_data()
        
        return {
            'status': 'synced',
            'timestamp': time.time(),
            'local_data': self.data
        }
    
    def handle_mobile_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle mobile request programmatically."""
        if method == 'GET':
            if endpoint == '/mobile/api/notes':
                return {'notes': self.get_notes()}
            elif endpoint == '/mobile/api/search':
                query = data.get('q', '') if data else ''
                return {'results': self.search_notes(query)}
        elif method == 'POST':
            if endpoint == '/mobile/api/notes' and data:
                return self.create_note(data)
        
        return {'error': 'Invalid request'}
    
    def get_notes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notes."""
        return self.data.get('notes', [])[-limit:]
    
    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a note."""
        note_data['id'] = f"note_{int(time.time())}"
        note_data['created_at'] = time.time()
        self.data['notes'].append(note_data)
        self._save_data()
        return note_data
    
    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes."""
        query_lower = query.lower()
        notes = self.data.get('notes', [])
        
        results = []
        for note in notes:
            content = json.dumps(note).lower()
            if query_lower in content:
                results.append(note)
        
        return results

