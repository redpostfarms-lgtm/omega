# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Farm API Access
REST API for farm data access
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
API_DIR = ARCHIVED / 'farm_api'
API_DIR.mkdir(parents=True, exist_ok=True)

class FarmAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for farm API."""
    
    def __init__(self, api_server, *args, **kwargs):
        self.api_server = api_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        endpoint = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if endpoint == '/api/status':
            self._send_response(200, {'status': 'ok', 'version': '1.0'})
        elif endpoint == '/api/crops':
            crops = self.api_server.get_crops()
            self._send_response(200, {'crops': crops})
        elif endpoint == '/api/inventory':
            inventory = self.api_server.get_inventory()
            self._send_response(200, {'inventory': inventory})
        elif endpoint == '/api/financial':
            financial = self.api_server.get_financial()
            self._send_response(200, {'financial': financial})
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
        
        if endpoint == '/api/crops':
            result = self.api_server.add_crop(data)
            self._send_response(201, result)
        elif endpoint == '/api/inventory':
            result = self.api_server.add_inventory_item(data)
            self._send_response(201, result)
        elif endpoint == '/api/financial':
            result = self.api_server.add_transaction(data)
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

class FarmAPIServer:
    """REST API server for farm data."""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        self.endpoints = {}
        self.data_store = API_DIR / 'api_data.json'
        self._load_data()
    
    def _load_data(self):
        """Load data from disk."""
        if self.data_store.exists():
            try:
                with open(self.data_store, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {'crops': [], 'inventory': [], 'financial': []}
        else:
            self.data = {'crops': [], 'inventory': [], 'financial': []}
    
    def _save_data(self):
        """Save data to disk."""
        with open(self.data_store, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def create_api_server(self) -> HTTPServer:
        """Create and configure API server."""
        def handler(*args, **kwargs):
            return FarmAPIHandler(self, *args, **kwargs)
        
        server = HTTPServer((self.host, self.port), handler)
        return server
    
    def register_endpoint(self, endpoint: str, handler: callable):
        """Register a custom endpoint."""
        self.endpoints[endpoint] = handler
    
    def start(self):
        """Start the API server."""
        if self.running:
            return
        
        self.server = self.create_api_server()
        self.running = True
        
        def run_server():
            self.server.serve_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def stop(self):
        """Stop the API server."""
        if self.server:
            self.server.shutdown()
            self.running = False
    
    def get_crops(self) -> List[Dict[str, Any]]:
        """Get all crops."""
        return self.data.get('crops', [])
    
    def get_inventory(self) -> List[Dict[str, Any]]:
        """Get all inventory items."""
        return self.data.get('inventory', [])
    
    def get_financial(self) -> List[Dict[str, Any]]:
        """Get all financial transactions."""
        return self.data.get('financial', [])
    
    def add_crop(self, crop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a crop."""
        crop_data['id'] = f"crop_{int(time.time())}"
        crop_data['created_at'] = time.time()
        self.data['crops'].append(crop_data)
        self._save_data()
        return crop_data
    
    def add_inventory_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add an inventory item."""
        item_data['id'] = f"item_{int(time.time())}"
        item_data['created_at'] = time.time()
        self.data['inventory'].append(item_data)
        self._save_data()
        return item_data
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a financial transaction."""
        transaction_data['id'] = f"trans_{int(time.time())}"
        transaction_data['created_at'] = time.time()
        self.data['financial'].append(transaction_data)
        self._save_data()
        return transaction_data
    
    def handle_api_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle API request programmatically."""
        if method == 'GET':
            if endpoint == '/api/crops':
                return {'crops': self.get_crops()}
            elif endpoint == '/api/inventory':
                return {'inventory': self.get_inventory()}
            elif endpoint == '/api/financial':
                return {'financial': self.get_financial()}
        elif method == 'POST':
            if endpoint == '/api/crops' and data:
                return self.add_crop(data)
            elif endpoint == '/api/inventory' and data:
                return self.add_inventory_item(data)
            elif endpoint == '/api/financial' and data:
                return self.add_transaction(data)
        
        return {'error': 'Invalid request'}

