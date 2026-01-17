#!/usr/bin/env python3
"""
Omega Control Panel - Web Interface
====================================
Flask-based web interface for Omega Control Panel.
Provides remote access and modern web UI.

Usage:
    python omega_control_panel_web.py
    python omega_control_panel_web.py --port 8080
    python omega_control_panel_web.py --host 0.0.0.0  # Allow remote access
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from threading import Thread, Lock

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

# Flask availability
try:
    from flask import Flask, render_template_string, jsonify, request, session
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Install with: pip install flask flask-cors")

# Flask-Login availability
try:
    from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
    from werkzeug.security import generate_password_hash, check_password_hash
    LOGIN_AVAILABLE = True
except ImportError:
    LOGIN_AVAILABLE = False
    # Provide a fallback UserMixin for when flask-login is not available
    class UserMixin:
        """Fallback UserMixin when flask-login is not installed"""
        @property
        def is_authenticated(self):
            return True
        @property
        def is_active(self):
            return True
        @property
        def is_anonymous(self):
            return False
        def get_id(self):
            return str(self.id)
    print("Flask-Login not installed. Install with: pip install flask-login")

# Flask-SQLAlchemy availability
try:
    from flask_sqlalchemy import SQLAlchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("Flask-SQLAlchemy not installed. Install with: pip install flask-sqlalchemy")

# Flask-Migrate availability
try:
    from flask_migrate import Migrate
    MIGRATE_AVAILABLE = True
except ImportError:
    MIGRATE_AVAILABLE = False
    print("Flask-Migrate not installed. Install with: pip install flask-migrate")

# Import ControlPanel
try:
    from omega_control_panel import ControlPanel
    CONTROL_PANEL_AVAILABLE = True
except ImportError:
    CONTROL_PANEL_AVAILABLE = False
    print("omega_control_panel not available")

# WebSocket support (optional)
try:
    from flask_socketio import SocketIO, emit, disconnect
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False

# Requests for AI API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests not installed. Install with: pip install requests")

# User storage (persistent)
try:
    from omega_user_storage import get_user_storage
    USER_STORAGE_AVAILABLE = True
except ImportError:
    USER_STORAGE_AVAILABLE = False
    print("omega_user_storage not available - using demo users")

# User model for authentication
class User(UserMixin):
    """User model with role-based access control"""
    def __init__(self, id, username, password_hash='', role='viewer'):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'operator', 'viewer'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_operator(self):
        return self.role in ('admin', 'operator')
    
    def check_password(self, password):
        """Check password (simple comparison for demo - use hash in production)"""
        if LOGIN_AVAILABLE:
            return check_password_hash(self.password_hash, password)
        # Fallback: simple comparison (NOT SECURE - for demo only)
        return self.password_hash == password

# Role-based decorators
from functools import wraps

def role_required(*required_roles):
    """Decorator for Flask routes - requires authentication and specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not LOGIN_AVAILABLE:
                return f(*args, **kwargs)  # Skip if login not available
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            if current_user.role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def socketio_role_required(*required_roles):
    """Decorator for SocketIO events - requires authentication and specific role"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not LOGIN_AVAILABLE:
                return f(*args, **kwargs)  # Skip if login not available
            if not current_user.is_authenticated:
                if SOCKETIO_AVAILABLE:
                    disconnect()
                return False
            if current_user.role not in required_roles:
                if SOCKETIO_AVAILABLE:
                    emit('error', {'message': 'Insufficient permissions'})
                    disconnect()
                return False
            return f(*args, **kwargs)
        return wrapped
    return decorator

def authenticated_only(f):
    """Decorator for SocketIO events - requires authentication only"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not LOGIN_AVAILABLE:
            return f(*args, **kwargs)  # Skip if login not available
        if not current_user.is_authenticated:
            if SOCKETIO_AVAILABLE:
                disconnect()
            return False
        return f(*args, **kwargs)
    return wrapped


def calculate_balance_status(stats: Dict[str, Any], recommendations: List[str]) -> Dict[str, Any]:
    """Calculate overall system balance status from load balancer stats
    
    Args:
        stats: System statistics dictionary with cpu, ram, gpu metrics
        recommendations: List of active recommendations from load balancer
    
    Returns:
        Dictionary with balance status, health level, and action items
    """
    try:
        cpu = stats.get('cpu', {}).get('percent', 0)
        ram = stats.get('ram', {}).get('percent', 0)
        gpu = stats.get('gpu', {}).get('percent', 0)
        
        # Calculate overall stress level (0-100)
        stress_level = (cpu + ram + gpu) / 3
        
        # Determine health status
        if stress_level < 30:
            health = 'optimal'
            color = 'green'
        elif stress_level < 60:
            health = 'good'
            color = 'yellow'
        elif stress_level < 80:
            health = 'warning'
            color = 'orange'
        else:
            health = 'critical'
            color = 'red'
        
        # Check if balanced
        variance = max(cpu, ram, gpu) - min(cpu, ram, gpu)
        is_balanced = variance < 30  # Less than 30% difference between components
        
        # Determine bottleneck
        bottleneck = None
        if cpu > 80:
            bottleneck = 'CPU'
        elif ram > 75:
            bottleneck = 'RAM'
        elif gpu > 85:
            bottleneck = 'GPU'
        
        return {
            'status': 'balanced' if is_balanced else 'unbalanced',
            'health': health,
            'color': color,
            'stress_level': round(stress_level, 1),
            'bottleneck': bottleneck,
            'active_recommendations': len(recommendations),
            'recommendation_actions': recommendations[:3] if recommendations else []  # Top 3 actions
        }
    except Exception as e:
        return {
            'status': 'unknown',
            'health': 'error',
            'color': 'gray',
            'stress_level': 0,
            'bottleneck': None,
            'error': str(e)
        }


class MultiAIChatbot:
    """Multi-AI chatbot handler for Grok, DeepSeek, ChatGPT"""
    
    def __init__(self):
        self.enabled = False
        self.chat_history = []  # List of {role, content, ai_provider, timestamp}
        self.ai_configs = {
            'grok': {
                'api_url': os.getenv('GROK_API_URL', 'https://api.x.ai/v1/chat/completions'),
                'api_key': os.getenv('GROK_API_KEY', ''),
                'model': os.getenv('GROK_MODEL', 'grok-beta'),
                'enabled': False
            },
            'deepseek': {
                'api_url': os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions'),
                'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
                'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                'enabled': False
            },
            'chatgpt': {
                'api_url': os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions'),
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
                'enabled': False
            }
        }
        self.lock = Lock()
    
    def start(self):
        """Start chatbot"""
        with self.lock:
            self.enabled = True
    
    def stop(self):
        """Stop chatbot"""
        with self.lock:
            self.enabled = False
    
    def is_running(self):
        """Check if chatbot is running"""
        return self.enabled
    
    def query_ai(self, provider: str, message: str) -> Dict[str, Any]:
        """Query a specific AI provider"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests library not available'}
        
        if provider not in self.ai_configs:
            return {'error': f'Unknown AI provider: {provider}'}
        
        config = self.ai_configs[provider]
        if not config.get('enabled', False):
            return {'error': f'{provider} is not enabled or configured'}
        
        if not config.get('api_key'):
            return {'error': f'{provider} API key not configured'}
        
        try:
            headers = {
                'Authorization': f"Bearer {config['api_key']}",
                'Content-Type': 'application/json'
            }
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'user', 'content': message}
                ]
            }
            
            response = requests.post(config['api_url'], json=data, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ai_response = result['choices'][0]['message']['content']
            
            # Add to chat history
            with self.lock:
                self.chat_history.append({
                    'role': 'user',
                    'content': message,
                    'ai_provider': provider,
                    'timestamp': datetime.now().isoformat()
                })
                self.chat_history.append({
                    'role': 'assistant',
                    'content': ai_response,
                    'ai_provider': provider,
                    'timestamp': datetime.now().isoformat()
                })
                # Keep last 100 messages
                if len(self.chat_history) > 100:
                    self.chat_history = self.chat_history[-100:]
            
            return {'success': True, 'response': ai_response, 'provider': provider}
        except Exception as e:
            return {'error': str(e), 'provider': provider}
    
    def query_all(self, message: str) -> Dict[str, Any]:
        """Query all enabled AI providers"""
        results = {}
        for provider in self.ai_configs.keys():
            if self.ai_configs[provider].get('enabled', False):
                results[provider] = self.query_ai(provider, message)
        return results
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history"""
        with self.lock:
            return self.chat_history[-limit:] if limit else self.chat_history.copy()
    
    def clear_history(self):
        """Clear chat history"""
        with self.lock:
            self.chat_history = []
    
    def get_status(self) -> Dict[str, Any]:
        """Get chatbot status"""
        return {
            'enabled': self.enabled,
            'providers': {
                provider: {
                    'enabled': config.get('enabled', False),
                    'configured': bool(config.get('api_key'))
                }
                for provider, config in self.ai_configs.items()
            },
            'history_count': len(self.chat_history)
        }


class OmegaControlPanelWeb:
    """Web interface for Omega Control Panel"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug
        
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required. Install with: pip install flask flask-cors")
        
        if not CONTROL_PANEL_AVAILABLE:
            raise ImportError("omega_control_panel is required")
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'omega-secret-key-2026-change-in-production'  # Change in production!
        CORS(self.app)  # Enable CORS for API access
        
        # Initialize Flask-Login (if available)
        if LOGIN_AVAILABLE:
            self.login_manager = LoginManager()
            self.login_manager.init_app(self.app)
            self.login_manager.login_view = 'api_login'
            
            @self.login_manager.user_loader
            def load_user(user_id):
                # For demo: create user from stored credentials
                # In production: load from database
                return self._get_user_by_id(user_id)
        else:
            self.login_manager = None
        
        # WebSocket support (optional)
        if SOCKETIO_AVAILABLE:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        else:
            self.socketio = None
        
        # Background status emitter thread
        self.status_emitter_thread = None
        
        # ControlPanel instance (shared)
        self.control_panel = None
        self.control_panel_lock = Lock()
        
        # Update thread
        self.update_thread = None
        self.running = False
        
        # Multi-AI Chatbot
        self.chatbot = MultiAIChatbot()
        
        # User storage (persistent file-based storage)
        if USER_STORAGE_AVAILABLE:
            self.user_storage = get_user_storage()
            # Ensure admin user exists and is properly configured
            self.user_storage.ensure_admin_exists()
        else:
            self.user_storage = None
            self._init_demo_users()
        
        # Setup routes
        self._setup_routes()
        
        # Setup WebSocket events (if available)
        if self.socketio:
            self._setup_socketio()
    
    def _init_demo_users(self):
        """Initialize demo users (replace with database in production)"""
        if LOGIN_AVAILABLE:
            # Demo users - in production, load from database
            self.demo_users = {
                'admin': {'password': generate_password_hash('admin2026'), 'role': 'admin'},
                'operator': {'password': generate_password_hash('op2026'), 'role': 'operator'},
                'viewer': {'password': generate_password_hash('view2026'), 'role': 'viewer'}
            }
        else:
            self.demo_users = {}
    
    def _get_user_by_id(self, user_id):
        """Get user by ID (from persistent storage or demo)"""
        if not LOGIN_AVAILABLE:
            return None
        
        # Use persistent storage if available
        if USER_STORAGE_AVAILABLE and self.user_storage:
            user_data = self.user_storage.get_user(user_id)
            if user_data and user_data.get('active', True):
                return User(id=user_id, username=user_id, 
                          password_hash=user_data['password'], 
                          role=user_data.get('role', 'viewer'))
            return None
        
        # Fallback to demo users
        if hasattr(self, 'demo_users') and user_id in self.demo_users:
            user_data = self.demo_users[user_id]
            return User(id=user_id, username=user_id, password_hash=user_data['password'], role=user_data['role'])
        return None
    
    def _get_user_by_username(self, username):
        """Get user by username (from persistent storage or demo)"""
        if not LOGIN_AVAILABLE:
            return None
        
        # Use persistent storage if available
        if USER_STORAGE_AVAILABLE and self.user_storage:
            user_data = self.user_storage.get_user(username)
            if user_data and user_data.get('active', True):
                return User(id=username, username=username, 
                          password_hash=user_data['password'], 
                          role=user_data.get('role', 'viewer'))
            return None
        
        # Fallback to demo users
        if hasattr(self, 'demo_users') and username in self.demo_users:
            user_data = self.demo_users[username]
            return User(id=username, username=username, password_hash=user_data['password'], role=user_data['role'])
        return None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return self._get_dashboard_html()
        
        # Authentication routes
        @self.app.route('/api/login', methods=['POST'])
        def api_login():
            """Login endpoint"""
            if not LOGIN_AVAILABLE:
                return jsonify({'success': False, 'message': 'Authentication not available'}), 503
            
            try:
                data = request.get_json()
                username = data.get('username', '')
                password = data.get('password', '')
                
                user = self._get_user_by_username(username)
                if user and user.check_password(password):
                    login_user(user, remember=True)
                    return jsonify({
                        'success': True,
                        'message': 'Logged in',
                        'username': user.username,
                        'role': user.role
                    })
                
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/logout', methods=['POST'])
        @login_required if LOGIN_AVAILABLE else lambda f: f
        def api_logout():
            """Logout endpoint"""
            if LOGIN_AVAILABLE:
                logout_user()
            return jsonify({'success': True, 'message': 'Logged out'})
        
        @self.app.route('/api/current-user', methods=['GET'])
        def api_current_user():
            """Get current user info"""
            if not LOGIN_AVAILABLE:
                return jsonify({'authenticated': False})
            
            if current_user.is_authenticated:
                return jsonify({
                    'authenticated': True,
                    'username': current_user.username,
                    'role': current_user.role
                })
            return jsonify({'authenticated': False})
        
        @self.app.route('/api/status', methods=['GET'])
        def api_status():
            """Get overall status"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    status = {
                        'running': self.control_panel.running,
                        'timestamp': datetime.now().isoformat(),
                        'update_interval': self.control_panel.update_interval
                    }
                    return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/system', methods=['GET'])
        def api_system():
            """Get system information"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    system_data = self._get_system_data()
                    return jsonify(system_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/notifications', methods=['GET'])
        def api_notifications():
            """Get notifications"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    notifications = [
                        {
                            'message': n.message,
                            'level': n.level,
                            'timestamp': n.timestamp.isoformat()
                        }
                        for n in list(self.control_panel.notifications)
                    ]
                    return jsonify(notifications)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/integrated-systems', methods=['GET'])
        def api_integrated_systems():
            """Get integrated systems"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    systems = [
                        {
                            'name': s.name,
                            'status': s.status,
                            'cpu_usage': s.cpu_usage,
                            'temperature': s.temperature,
                            'processing_power': s.processing_power,
                            'last_update': s.last_update.isoformat()
                        }
                        for s in self.control_panel.integrated_systems
                    ]
                    return jsonify(systems)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/process-improvements', methods=['GET'])
        def api_process_improvements():
            """Get process improvements"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    improvements = [
                        {
                            'name': p.name,
                            'current_percentage': p.current_percentage,
                            'target_percentage': p.target_percentage,
                            'priority': p.priority,
                            'description': p.description
                        }
                        for p in self.control_panel.process_improvements
                    ]
                    return jsonify(improvements)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/optional-processes', methods=['GET'])
        def api_optional_processes():
            """Get optional processes"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    processes = [
                        {
                            'name': o.name,
                            'description': o.description,
                            'usefulness_score': o.usefulness_score,
                            'category': o.category,
                            'last_scanned': o.last_scanned.isoformat()
                        }
                        for o in self.control_panel.optional_processes
                    ]
                    return jsonify(processes)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/hardware', methods=['GET'])
        def api_hardware():
            """Get hardware information"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    hardware_data = self._get_hardware_data()
                    return jsonify(hardware_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/load-balance', methods=['GET'])
        def api_load_balance():
            """Get GPU load balancer metrics and recommendations"""
            try:
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    load_balancer = getattr(self.control_panel, 'load_balancer', None)
                    if not load_balancer:
                        return jsonify({
                            'error': 'Load balancer not available',
                            'gpu_available': False,
                            'status': 'Load balancer disabled'
                        }), 503
                    
                    # Get current load balancer data
                    config = load_balancer.get_balanced_config()
                    stats = load_balancer.get_system_stats()
                    recommendations = load_balancer.get_recommendations()
                    distribution = load_balancer.get_load_distribution()
                    
                    return jsonify({
                        'status': 'success',
                        'gpu_available': load_balancer.gpu_available,
                        'system_stats': {
                            'cpu_percent': stats.get('cpu', {}).get('percent', 0),
                            'ram_percent': stats.get('ram', {}).get('percent', 0),
                            'gpu_percent': stats.get('gpu', {}).get('percent', 0),
                            'gpu_available_gb': stats.get('gpu', {}).get('available_gb', 0),
                            'total_ram_gb': stats.get('ram', {}).get('total_gb', 0),
                            'used_ram_gb': stats.get('ram', {}).get('used_gb', 0)
                        },
                        'load_distribution': {
                            'cpu_utilization': distribution.get('cpu_utilization', 0.5),
                            'gpu_utilization': distribution.get('gpu_utilization', 0.5),
                            'recommended_cpu_percent': distribution.get('recommended_cpu_percent', 50),
                            'recommended_gpu_percent': distribution.get('recommended_gpu_percent', 50)
                        },
                        'configuration': {
                            'use_gpu': config.get('use_gpu', False),
                            'gpu_batch_size': config.get('gpu_batch_size', 32),
                            'cpu_batch_size': config.get('cpu_batch_size', 16),
                            'mixed_precision': config.get('mixed_precision', False),
                            'use_gradient_checkpointing': config.get('use_gradient_checkpointing', False)
                        },
                        'recommendations': recommendations,
                        'thresholds': {
                            'cpu_threshold': load_balancer.cpu_threshold,
                            'ram_threshold': load_balancer.ram_threshold,
                            'gpu_threshold': load_balancer.gpu_threshold
                        },
                        'balance_status': calculate_balance_status(stats, recommendations)
                    })
            except Exception as e:
                import traceback
                return jsonify({
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }), 500
        
        @self.app.route('/api/fan-speed', methods=['POST'])
        def api_set_fan_speed():
            """Set fan speed"""
            try:
                data = request.get_json()
                speed = data.get('speed', 50)
                
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    self.control_panel.set_fan_speed(speed)
                    return jsonify({'success': True, 'speed': speed})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/rgb', methods=['POST'])
        def api_set_rgb():
            """Set RGB lighting"""
            try:
                data = request.get_json()
                enabled = data.get('enabled')
                color = data.get('color')
                
                with self.control_panel_lock:
                    if not self.control_panel:
                        return jsonify({'error': 'Control panel not initialized'}), 503
                    
                    if enabled is not None:
                        self.control_panel.set_rgb_enabled(enabled)
                    if color:
                        self.control_panel.set_rgb_color(color)
                    
                    return jsonify({
                        'success': True,
                        'enabled': self.control_panel.rgb_enabled,
                        'color': self.control_panel.rgb_color
                    })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Chatbot routes
        @self.app.route('/api/chatbot/status', methods=['GET'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_status():
            """Get chatbot status"""
            try:
                return jsonify(self.chatbot.get_status())
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chatbot/start', methods=['POST'])
        @role_required('admin', 'operator') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_start():
            """Start chatbot"""
            try:
                self.chatbot.start()
                return jsonify({'success': True, 'message': 'Chatbot started'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chatbot/stop', methods=['POST'])
        @role_required('admin', 'operator') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_stop():
            """Stop chatbot"""
            try:
                self.chatbot.stop()
                return jsonify({'success': True, 'message': 'Chatbot stopped'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chatbot/message', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_message():
            """Send message to AI chatbot(s)"""
            try:
                if not self.chatbot.is_running():
                    return jsonify({'error': 'Chatbot is not running. Start it first.'}), 400
                
                data = request.get_json()
                message = data.get('message', '').strip()
                provider = data.get('provider', 'all')  # 'grok', 'deepseek', 'chatgpt', or 'all'
                
                if not message:
                    return jsonify({'error': 'Message cannot be empty'}), 400
                
                if provider == 'all':
                    results = self.chatbot.query_all(message)
                else:
                    result = self.chatbot.query_ai(provider, message)
                    results = {provider: result}
                
                return jsonify({'success': True, 'results': results})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chatbot/history', methods=['GET'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_history():
            """Get chat history"""
            try:
                limit = request.args.get('limit', 50, type=int)
                history = self.chatbot.get_history(limit=limit)
                return jsonify({'history': history})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chatbot/clear', methods=['POST'])
        @role_required('admin', 'operator') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_clear():
            """Clear chat history"""
            try:
                self.chatbot.clear_history()
                return jsonify({'success': True, 'message': 'Chat history cleared'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_socketio(self):
        """Setup WebSocket events (if SocketIO available)"""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        @authenticated_only if LOGIN_AVAILABLE else (lambda f: f)
        def handle_connect():
            """Handle WebSocket connection"""
            print('Client connected to SocketIO')
            # Send initial status on connect
            try:
                with self.control_panel_lock:
                    if self.control_panel:
                        system_data = self._get_system_data()
                        notifications = [
                            {
                                'message': n.message,
                                'level': n.level,
                                'timestamp': n.timestamp.isoformat()
                            }
                            for n in list(self.control_panel.notifications)
                        ]
                        integrated_systems = [
                            {
                                'name': s.name,
                                'status': s.status,
                                'cpu_usage': s.cpu_usage,
                                'temperature': s.temperature,
                                'processing_power': s.processing_power
                            }
                            for s in self.control_panel.integrated_systems
                        ]
                        emit('initial_status', {
                            'system': system_data,
                            'notifications': notifications,
                            'integrated_systems': integrated_systems
                        })
            except Exception as e:
                emit('error', {'message': str(e)})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle WebSocket disconnection"""
            print('Client disconnected from SocketIO')
        
        @self.socketio.on('set_fan_speed')
        @socketio_role_required('admin', 'operator') if LOGIN_AVAILABLE else (lambda f: f)
        def handle_fan_speed(data):
            """Handle fan speed change via SocketIO (requires admin or operator role)"""
            try:
                speed = int(data.get('speed', 0))
                with self.control_panel_lock:
                    if self.control_panel:
                        self.control_panel.set_fan_speed(speed)
                # Broadcast to all clients
                username = current_user.username if LOGIN_AVAILABLE and current_user.is_authenticated else 'anonymous'
                self.socketio.emit('fan_update', {
                    'success': True,
                    'speed': speed,
                    'changed_by': username,
                    'timestamp': datetime.now().isoformat()
                }, broadcast=True)
            except Exception as e:
                emit('fan_update', {'success': False, 'error': str(e)})
        
        @self.socketio.on('set_rgb')
        @socketio_role_required('admin', 'operator') if LOGIN_AVAILABLE else (lambda f: f)
        def handle_rgb(data):
            """Handle RGB control via SocketIO (requires admin or operator role)"""
            try:
                color = data.get('color')
                enabled = data.get('enabled')
                with self.control_panel_lock:
                    if self.control_panel:
                        if enabled is None:
                            # Toggle
                            self.control_panel.toggle_rgb()
                        elif color:
                            self.control_panel.set_rgb_color(color)
                        else:
                            self.control_panel.rgb_enabled = enabled
                # Broadcast to all clients
                username = current_user.username if LOGIN_AVAILABLE and current_user.is_authenticated else 'anonymous'
                self.socketio.emit('rgb_update', {
                    'success': True,
                    'color': self.control_panel.rgb_color,
                    'enabled': self.control_panel.rgb_enabled,
                    'changed_by': username,
                    'timestamp': datetime.now().isoformat()
                }, broadcast=True)
            except Exception as e:
                emit('rgb_update', {'success': False, 'error': str(e)})
        
        # Start background status emitter
        self._start_status_emitter()
    
    def _start_status_emitter(self):
        """Start background thread to emit system status via SocketIO"""
        if not self.socketio:
            return
        
        def background_emitter():
            """Emit system status to all connected clients every ~2 seconds"""
            import time
            while self.running:
                try:
                    if self.socketio and self.control_panel:
                        with self.control_panel_lock:
                            if self.control_panel:
                                system_data = self._get_system_data()
                                notifications = [
                                    {
                                        'message': n.message,
                                        'level': n.level,
                                        'timestamp': n.timestamp.isoformat()
                                    }
                                    for n in list(self.control_panel.notifications)
                                ]
                                integrated_systems = [
                                    {
                                        'name': s.name,
                                        'status': s.status,
                                        'cpu_usage': s.cpu_usage,
                                        'temperature': s.temperature,
                                        'processing_power': s.processing_power
                                    }
                                    for s in self.control_panel.integrated_systems
                                ]
                                self.socketio.emit('system_update', {
                                    'system': system_data,
                                    'notifications': notifications,
                                    'integrated_systems': integrated_systems,
                                    'timestamp': datetime.now().isoformat()
                                })
                except Exception as e:
                    print(f"Status emitter error: {e}")
                    if self.socketio:
                        self.socketio.emit('error', {'message': str(e)})
                
                time.sleep(2.0)  # Update every 2 seconds
        
        self.status_emitter_thread = Thread(target=background_emitter, daemon=True)
        self.status_emitter_thread.start()
    
    def _get_system_data(self) -> Dict[str, Any]:
        """Get system data from control panel"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1) if hasattr(psutil, 'cpu_percent') else 0.0
            memory = psutil.virtual_memory() if hasattr(psutil, 'virtual_memory') else None
            disk = psutil.disk_usage('/') if hasattr(psutil, 'disk_usage') else None
            cpu_temp = self.control_panel._get_cpu_temperature()
            
            return {
                'cpu_usage': cpu_percent,
                'cpu_temperature': cpu_temp or 0.0,
                'memory_usage': memory.percent if memory else 0.0,
                'memory_total': memory.total if memory else 0,
                'memory_available': memory.available if memory else 0,
                'disk_usage': disk.percent if disk else 0.0,
                'disk_total': disk.total if disk else 0,
                'disk_free': disk.free if disk else 0,
                'fan_speed': self.control_panel.fan_speed_percentage,
                'rgb_enabled': self.control_panel.rgb_enabled,
                'rgb_color': self.control_panel.rgb_color
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_hardware_data(self) -> Dict[str, Any]:
        """Get hardware data"""
        system_data = self._get_system_data()
        return system_data
    
    def _get_dashboard_html(self) -> str:
        """Get dashboard HTML"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omega Control Panel</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }
        .stat-unit {
            font-size: 16px;
            color: #666;
        }
        .section {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .notification {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .notification.info { background: #e3f2fd; border-color: #2196f3; }
        .notification.warning { background: #fff3e0; border-color: #ff9800; }
        .notification.error { background: #ffebee; border-color: #f44336; }
        .notification.success { background: #e8f5e9; border-color: #4caf50; }
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .control-group {
            flex: 1;
            min-width: 200px;
        }
        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="range"], input[type="color"], button {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            border-radius: 5px;
        }
        button:hover:not(:disabled) {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        button:active:not(:disabled) {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        .system-item {
            padding: 10px;
            margin-bottom: 10px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-active { background: #4caf50; color: white; }
        .status-inactive { background: #9e9e9e; color: white; }
        .status-error { background: #f44336; color: white; }
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            font-size: 16px;
            font-weight: bold;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OMEGA CONTROL PANEL</h1>
            <p>Web Interface - Real-time Monitoring & Control</p>
        </div>
        
        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be loaded here -->
        </div>
        
        <div class="section">
            <h2>System Status</h2>
            <div id="systemStatus">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Notifications</h2>
            <div id="notifications">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Integrated Systems</h2>
            <div id="integratedSystems">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Hardware Controls</h2>
            <div class="controls">
                <div class="control-group">
                    <label>🔧 Fan Speed: <span id="fanSpeedValue">50</span>%</label>
                    <input type="range" id="fanSpeed" min="0" max="100" value="50" oninput="updateFanSpeed(this.value)">
                    <small style="color: #666; margin-top: 5px; display: block;">Drag to adjust system fan speed</small>
                </div>
                <div class="control-group">
                    <label>🌈 RGB Color</label>
                    <input type="color" id="rgbColor" value="#FFD700" onchange="updateRGBColor(this.value)">
                    <small style="color: #666; margin-top: 5px; display: block;">Click to select color</small>
                </div>
                <div class="control-group">
                    <label>💡 RGB Lighting</label>
                    <button id="rgbToggleBtn" onclick="toggleRGB()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        Toggle RGB
                    </button>
                    <small style="color: #666; margin-top: 5px; display: block;">Click to enable/disable RGB</small>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>⚖️ GPU Load Balancer</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <div style="font-weight: bold; color: #667eea; margin-bottom: 10px;">System Balance</div>
                    <div id="balanceStatus" style="font-size: 24px; font-weight: bold; color: #333;">Loading...</div>
                    <div id="balanceHealth" style="font-size: 12px; color: #666; margin-top: 5px;">Stress Level: <span id="stressLevel">-</span>%</div>
                </div>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <div style="font-weight: bold; color: #667eea; margin-bottom: 10px;">GPU Available</div>
                    <div id="gpuAvailable" style="font-size: 24px; font-weight: bold; color: #f44336;">Checking...</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">GPU Memory: <span id="gpuMemory">-</span> GB</div>
                </div>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <div style="font-weight: bold; color: #667eea; margin-bottom: 10px;">Current Bottleneck</div>
                    <div id="bottleneck" style="font-size: 20px; font-weight: bold; color: #ff9800;">None</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">Active Recommendations: <span id="recommendationCount">0</span></div>
                </div>
            </div>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <div style="font-weight: bold; color: #667eea; margin-bottom: 10px;">System Resource Distribution</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                    <div>
                        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">CPU Usage</div>
                        <div style="position: relative; background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                            <div id="cpuBar" style="height: 100%; background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%); width: 0%; transition: width 0.3s ease;">
                            </div>
                        </div>
                        <div style="font-size: 12px; color: #333; margin-top: 5px;">
                            <span id="cpuPercent">0</span>%
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">RAM Usage</div>
                        <div style="position: relative; background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                            <div id="ramBar" style="height: 100%; background: linear-gradient(90deg, #4ecdc4 0%, #44a08d 100%); width: 0%; transition: width 0.3s ease;">
                            </div>
                        </div>
                        <div style="font-size: 12px; color: #333; margin-top: 5px;">
                            <span id="ramPercent">0</span>%
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">GPU Usage</div>
                        <div style="position: relative; background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                            <div id="gpuBar" style="height: 100%; background: linear-gradient(90deg, #ffd93d 0%, #f4d35e 100%); width: 0%; transition: width 0.3s ease;">
                            </div>
                        </div>
                        <div style="font-size: 12px; color: #333; margin-top: 5px;">
                            <span id="gpuPercent">0</span>%
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 5px;">
                <div style="font-weight: bold; color: #667eea; margin-bottom: 10px;">Active Recommendations</div>
                <div id="recommendations" style="list-style: none;">
                    <p style="color: #666; font-style: italic;">Optimizing system resources...</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>AI Council Chat</h2>
            <div style="margin-bottom: 15px;">
                <button id="chatbotStartBtn" onclick="startChatbot()" style="margin-right: 10px; width: auto; padding: 8px 16px;">Start Council</button>
                <button id="chatbotStopBtn" onclick="stopChatbot()" style="margin-right: 10px; width: auto; padding: 8px 16px; background: #f44336;">Stop Council</button>
                <button onclick="clearChatHistory()" style="width: auto; padding: 8px 16px; background: #ff9800;">Clear History</button>
                <span id="chatbotStatus" style="margin-left: 15px; font-weight: bold; color: #666;">Status: Stopped</span>
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Ask the Council:</label>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="chatMessage" placeholder="Type your question for the AI council..." 
                           style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;"
                           onkeypress="if(event.key === 'Enter') sendChatMessage()">
                    <button onclick="sendChatMessage()" style="width: auto; padding: 10px 20px; background: #667eea;">Send</button>
                </div>
            </div>
            <div style="margin-bottom: 15px;">
                <div id="chatHistory" style="min-height: 400px; max-height: 600px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9;">
                    <p style="color: #666; font-style: italic; text-align: center;">AI Council ready. Ask a question to see all responses side-by-side.</p>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">Refresh</button>
    </div>
    
    <script>
        function refreshData() {
            // Refresh all data
            loadStats();
            loadNotifications();
            loadIntegratedSystems();
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/system');
                const data = await response.json();
                
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <h3>CPU Usage</h3>
                        <div class="stat-value">${data.cpu_usage.toFixed(1)}<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>CPU Temperature</h3>
                        <div class="stat-value">${data.cpu_temperature.toFixed(1)}<span class="stat-unit">°C</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Memory Usage</h3>
                        <div class="stat-value">${data.memory_usage.toFixed(1)}<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Disk Usage</h3>
                        <div class="stat-value">${data.disk_usage.toFixed(1)}<span class="stat-unit">%</span></div>
                    </div>
                `;
                
                document.getElementById('systemStatus').innerHTML = `
                    <p>Status: Running</p>
                    <p>Fan Speed: ${data.fan_speed}%</p>
                    <p>RGB: ${data.rgb_enabled ? 'Enabled' : 'Disabled'} (${data.rgb_color})</p>
                `;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadNotifications() {
            try {
                const response = await fetch('/api/notifications');
                const notifications = await response.json();
                
                const container = document.getElementById('notifications');
                if (notifications.length === 0) {
                    container.innerHTML = '<p>No notifications</p>';
                    return;
                }
                
                container.innerHTML = notifications.slice(-10).reverse().map(n => `
                    <div class="notification ${n.level}">
                        <strong>${n.level.toUpperCase()}</strong>: ${n.message}
                        <small style="float: right;">${new Date(n.timestamp).toLocaleTimeString()}</small>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading notifications:', error);
            }
        }
        
        async function loadIntegratedSystems() {
            try {
                const response = await fetch('/api/integrated-systems');
                const systems = await response.json();
                
                const container = document.getElementById('integratedSystems');
                if (systems.length === 0) {
                    container.innerHTML = '<p>No integrated systems</p>';
                    return;
                }
                
                container.innerHTML = systems.map(s => `
                    <div class="system-item">
                        <strong>${s.name}</strong>
                        <span class="status-badge status-${s.status}">${s.status}</span>
                        <div style="margin-top: 5px;">
                            CPU: ${s.cpu_usage.toFixed(1)}% | 
                            Temp: ${s.temperature.toFixed(1)}°C | 
                            Power: ${s.processing_power.toFixed(1)}%
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading integrated systems:', error);
            }
        }
        
        function updateStats(data) {
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <h3>CPU Usage</h3>
                    <div class="stat-value">${data.cpu_usage.toFixed(1)}<span class="stat-unit">%</span></div>
                </div>
                <div class="stat-card">
                    <h3>CPU Temperature</h3>
                    <div class="stat-value">${data.cpu_temperature.toFixed(1)}<span class="stat-unit">°C</span></div>
                </div>
                <div class="stat-card">
                    <h3>Memory Usage</h3>
                    <div class="stat-value">${data.memory_usage.toFixed(1)}<span class="stat-unit">%</span></div>
                </div>
                <div class="stat-card">
                    <h3>Disk Usage</h3>
                    <div class="stat-value">${data.disk_usage.toFixed(1)}<span class="stat-unit">%</span></div>
                </div>
            `;
        }
        
        function updateNotifications(notifications) {
            const container = document.getElementById('notifications');
            if (notifications.length === 0) {
                container.innerHTML = '<p>No notifications</p>';
                return;
            }
            container.innerHTML = notifications.slice(-10).reverse().map(n => `
                <div class="notification ${n.level}">
                    <strong>${n.level.toUpperCase()}</strong>: ${n.message}
                    <small style="float: right;">${new Date(n.timestamp).toLocaleTimeString()}</small>
                </div>
            `).join('');
        }
        
        function updateIntegratedSystems(systems) {
            const container = document.getElementById('integratedSystems');
            if (systems.length === 0) {
                container.innerHTML = '<p>No integrated systems</p>';
                return;
            }
            container.innerHTML = systems.map(s => `
                <div class="system-item">
                    <strong>${s.name}</strong>
                    <span class="status-badge status-${s.status}">${s.status}</span>
                    <div style="margin-top: 5px;">
                        CPU: ${s.cpu_usage.toFixed(1)}% | 
                        Temp: ${s.temperature.toFixed(1)}°C | 
                        Power: ${s.processing_power.toFixed(1)}%
                    </div>
                </div>
            `).join('');
        }
        
        function updateSystemStatus(data) {
            const statusEl = document.getElementById('systemStatus');
            if (statusEl) {
                statusEl.innerHTML = `
                    <p><strong>Status:</strong> Running</p>
                    <p><strong>Fan Speed:</strong> ${data.fan_speed || 0}%</p>
                    <p><strong>RGB:</strong> ${data.rgb_enabled ? 'Enabled' : 'Disabled'} (${data.rgb_color || '#FFD700'})</p>
                `;
            }
        }
        
        // Legacy functions for polling fallback (if SocketIO not available)
        async function loadStats() {
            try {
                const response = await fetch('/api/system');
                const data = await response.json();
                updateStats(data);
                updateSystemStatus(data);
            } catch (error) {
                console.error('Error loading stats:', error);
                // Show error in UI
                document.getElementById('statsGrid').innerHTML = '<div class="stat-card" style="grid-column: 1/-1;"><p style="color: #f44336;">Error loading system data. Please refresh.</p></div>';
            }
        }
        
        async function loadNotifications() {
            try {
                const response = await fetch('/api/notifications');
                const notifications = await response.json();
                updateNotifications(notifications);
            } catch (error) {
                console.error('Error loading notifications:', error);
            }
        }
        
        async function loadIntegratedSystems() {
            try {
                const response = await fetch('/api/integrated-systems');
                const systems = await response.json();
                updateIntegratedSystems(systems);
            } catch (error) {
                console.error('Error loading integrated systems:', error);
            }
        }
        
        function updateFanSpeed(value) {
            const speedDisplay = document.getElementById('fanSpeedValue');
            if (speedDisplay) speedDisplay.textContent = value;
            
            fetch('/api/fan-speed', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({speed: parseInt(value)})
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    console.log(`✓ Fan speed set to ${value}%`);
                    showNotification(`Fan speed: ${value}%`, 'success');
                } else {
                    console.error('Error setting fan speed:', data.error);
                    showNotification(`Error: ${data.error}`, 'error');
                }
            })
            .catch(err => {
                console.error('Fan speed request failed:', err);
                showNotification(`Failed to set fan speed: ${err.message}`, 'error');
            });
        }
        
        function updateRGBColor(color) {
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({color: color})
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    console.log(`✓ RGB color set to ${color}`);
                    showNotification(`RGB color changed to ${color}`, 'success');
                } else {
                    console.error('Error setting RGB color:', data.error);
                    showNotification(`Error: ${data.error}`, 'error');
                }
            })
            .catch(err => {
                console.error('RGB color request failed:', err);
                showNotification(`Failed to set RGB color: ${err.message}`, 'error');
            });
        }
        
        function toggleRGB() {
            const btn = document.getElementById('rgbToggleBtn');
            if (btn) btn.disabled = true;
            
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: null})
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    const statusText = data.enabled ? 'enabled' : 'disabled';
                    console.log(`✓ RGB lighting ${statusText}`);
                    showNotification(`RGB ${statusText}`, 'success');
                    refreshData();
                } else {
                    console.error('Error toggling RGB:', data.error);
                    showNotification(`Error: ${data.error}`, 'error');
                }
            })
            .catch(err => {
                console.error('RGB toggle request failed:', err);
                showNotification(`Failed to toggle RGB: ${err.message}`, 'error');
            })
            .finally(() => {
                if (btn) btn.disabled = false;
            });
        }
        
        function showNotification(message, level = 'info') {
            console.log(`[${level.toUpperCase()}] ${message}`);
            // Create temporary notification
            const notif = document.createElement('div');
            notif.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                z-index: 9999;
                animation: slideIn 0.3s ease;
                ${level === 'success' ? 'background: #4caf50;' : 'background: #f44336;'}
            `;
            notif.textContent = message;
            document.body.appendChild(notif);
            setTimeout(() => notif.remove(), 3000);
        }
        
        // Chatbot functions
        async function loadChatbotStatus() {
            try {
                const response = await fetch('/api/chatbot/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('chatbotStatus');
                const startBtn = document.getElementById('chatbotStartBtn');
                const stopBtn = document.getElementById('chatbotStopBtn');
                
                if (status.enabled) {
                    statusEl.textContent = 'Status: Running';
                    statusEl.style.color = '#4caf50';
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                } else {
                    statusEl.textContent = 'Status: Stopped';
                    statusEl.style.color = '#f44336';
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                }
            } catch (error) {
                console.error('Error loading chatbot status:', error);
            }
        }
        
        async function startChatbot() {
            try {
                const response = await fetch('/api/chatbot/start', {method: 'POST'});
                const result = await response.json();
                if (result.success) {
                    loadChatbotStatus();
                    addChatMessage('system', 'AI Council started successfully');
                } else {
                    alert('Error: ' + (result.error || 'Failed to start chatbot'));
                }
            } catch (error) {
                console.error('Error starting chatbot:', error);
                alert('Error starting chatbot: ' + error.message);
            }
        }
        
        async function stopChatbot() {
            try {
                const response = await fetch('/api/chatbot/stop', {method: 'POST'});
                const result = await response.json();
                if (result.success) {
                    loadChatbotStatus();
                    addChatMessage('system', 'AI Council stopped');
                } else {
                    alert('Error: ' + (result.error || 'Failed to stop chatbot'));
                }
            } catch (error) {
                console.error('Error stopping chatbot:', error);
                alert('Error stopping chatbot: ' + error.message);
            }
        }
        
        async function sendChatMessage() {
            const messageInput = document.getElementById('chatMessage');
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            // Clear placeholder if exists
            const historyEl = document.getElementById('chatHistory');
            if (historyEl.querySelector('p[style*="italic"]')) {
                historyEl.innerHTML = '';
            }
            
            // Add user question to chat
            addUserQuestion(message);
            messageInput.value = '';
            
            // Query all AI providers simultaneously (council mode)
            try {
                const response = await fetch('/api/chatbot/message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, provider: 'all'})
                });
                const result = await response.json();
                
                if (result.success && result.results) {
                    // Display all responses in council format (side-by-side)
                    displayCouncilResponses(result.results);
                } else {
                    addErrorMessage('Error: ' + (result.error || 'Failed to send message'));
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addErrorMessage('Error: ' + error.message);
            }
        }
        
        // AI Council Chat Functions
        const AI_COLORS = {
            'grok': { bg: '#e8f5e9', border: '#4caf50', name: 'Grok' },
            'deepseek': { bg: '#e3f2fd', border: '#2196f3', name: 'DeepSeek' },
            'chatgpt': { bg: '#fff3e0', border: '#ff9800', name: 'ChatGPT' },
            'local': { bg: '#f3e5f5', border: '#9c27b0', name: 'Local AI' }
        };
        
        function addUserQuestion(message) {
            const historyEl = document.getElementById('chatHistory');
            const questionEl = document.createElement('div');
            questionEl.style.cssText = 'margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #667eea; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
            questionEl.innerHTML = `
                <div style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">You asked:</div>
                <div style="font-size: 14px; white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(message)}</div>
                <div style="font-size: 11px; opacity: 0.9; margin-top: 8px;">${new Date().toLocaleTimeString()}</div>
            `;
            historyEl.appendChild(questionEl);
            historyEl.scrollTop = historyEl.scrollHeight;
        }
        
        function displayCouncilResponses(results) {
            const historyEl = document.getElementById('chatHistory');
            const councilEl = document.createElement('div');
            councilEl.style.cssText = 'margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;';
            
            // Display each AI response in its own card
            for (const [provider, result] of Object.entries(results)) {
                const color = AI_COLORS[provider] || { bg: '#f5f5f5', border: '#9e9e9e', name: provider };
                const cardEl = document.createElement('div');
                cardEl.style.cssText = `padding: 15px; border-radius: 8px; background: ${color.bg}; border: 2px solid ${color.border}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);`;
                
                if (result.success) {
                    cardEl.innerHTML = `
                        <div style="font-weight: bold; font-size: 14px; color: ${color.border}; margin-bottom: 10px; text-transform: uppercase;">${color.name}</div>
                        <div style="color: #333; font-size: 13px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.5;">${escapeHtml(result.response)}</div>
                        <div style="font-size: 10px; color: #666; margin-top: 10px; border-top: 1px solid rgba(0,0,0,0.1); padding-top: 8px;">${new Date().toLocaleTimeString()}</div>
                    `;
                } else {
                    cardEl.innerHTML = `
                        <div style="font-weight: bold; font-size: 14px; color: #f44336; margin-bottom: 10px;">${color.name} - Error</div>
                        <div style="color: #666; font-size: 12px;">${escapeHtml(result.error || 'Unknown error')}</div>
                    `;
                }
                
                councilEl.appendChild(cardEl);
            }
            
            historyEl.appendChild(councilEl);
            historyEl.scrollTop = historyEl.scrollHeight;
        }
        
        function addErrorMessage(errorText) {
            const historyEl = document.getElementById('chatHistory');
            const errorEl = document.createElement('div');
            errorEl.style.cssText = 'margin-bottom: 15px; padding: 12px; border-radius: 5px; background: #ffebee; border: 2px solid #f44336;';
            errorEl.innerHTML = `
                <div style="font-weight: bold; color: #f44336; margin-bottom: 5px;">Error</div>
                <div style="color: #666; font-size: 13px;">${escapeHtml(errorText)}</div>
            `;
            historyEl.appendChild(errorEl);
            historyEl.scrollTop = historyEl.scrollHeight;
        }
        
        // Legacy function for compatibility
        function addChatMessage(role, content, provider = '') {
            const historyEl = document.getElementById('chatHistory');
            const messageEl = document.createElement('div');
            messageEl.style.cssText = 'margin-bottom: 10px; padding: 8px; border-radius: 5px; background: ' + 
                (role === 'user' ? '#e3f2fd' : role === 'assistant' ? '#f1f8e9' : role === 'error' ? '#ffebee' : '#fff3e0') + ';';
            
            const roleLabel = role === 'user' ? 'You' : role === 'assistant' ? (provider || 'AI') : role === 'error' ? 'Error' : 'System';
            messageEl.innerHTML = `
                <div style="font-weight: bold; color: #667eea; margin-bottom: 5px;">${roleLabel}</div>
                <div style="color: #333; white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(content)}</div>
                <div style="font-size: 11px; color: #666; margin-top: 5px;">${new Date().toLocaleTimeString()}</div>
            `;
            
            historyEl.appendChild(messageEl);
            historyEl.scrollTop = historyEl.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function loadChatHistory() {
            try {
                const response = await fetch('/api/chatbot/history?limit=50');
                const result = await response.json();
                const history = result.history || [];
                
                const historyEl = document.getElementById('chatHistory');
                historyEl.innerHTML = '';
                
                if (history.length === 0) {
                    historyEl.innerHTML = '<p style="color: #666; font-style: italic;">No chat history. Start a conversation!</p>';
                    return;
                }
                
                history.forEach(msg => {
                    const role = msg.role;
                    const content = msg.content;
                    const provider = msg.ai_provider || '';
                    const timestamp = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : '';
                    
                    const messageEl = document.createElement('div');
                    messageEl.style.cssText = 'margin-bottom: 10px; padding: 8px; border-radius: 5px; background: ' + 
                        (role === 'user' ? '#e3f2fd' : '#f1f8e9') + ';';
                    
                    const roleLabel = role === 'user' ? 'You' : (provider || 'AI');
                    messageEl.innerHTML = `
                        <div style="font-weight: bold; color: #667eea; margin-bottom: 5px;">${roleLabel}</div>
                        <div style="color: #333; white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(content)}</div>
                        ${timestamp ? '<div style="font-size: 11px; color: #666; margin-top: 5px;">' + timestamp + '</div>' : ''}
                    `;
                    
                    historyEl.appendChild(messageEl);
                });
                
                historyEl.scrollTop = historyEl.scrollHeight;
            } catch (error) {
                console.error('Error loading chat history:', error);
            }
        }
        
        async function clearChatHistory() {
            if (!confirm('Are you sure you want to clear the chat history?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/chatbot/clear', {method: 'POST'});
                const result = await response.json();
                if (result.success) {
                    const historyEl = document.getElementById('chatHistory');
                    historyEl.innerHTML = '<p style="color: #666; font-style: italic; text-align: center;">AI Council ready. Ask a question to see all responses side-by-side.</p>';
                } else {
                    alert('Error: ' + (result.error || 'Failed to clear history'));
                }
            } catch (error) {
                console.error('Error clearing chat history:', error);
                alert('Error clearing history: ' + error.message);
            }
        }
        
        // GPU Load Balancer Functions
        async function loadLoadBalancerData() {
            try {
                const response = await fetch('/api/load-balance');
                const data = await response.json();
                
                if (data.error && data.status === 'Load balancer disabled') {
                    // Load balancer not available
                    document.getElementById('gpuAvailable').textContent = 'Not Available';
                    document.getElementById('gpuAvailable').style.color = '#999';
                    return;
                }
                
                // Update GPU availability
                const gpuStatus = data.gpu_available ? '✓ Available' : '✗ Not Available';
                const gpuColor = data.gpu_available ? '#4caf50' : '#f44336';
                document.getElementById('gpuAvailable').textContent = gpuStatus;
                document.getElementById('gpuAvailable').style.color = gpuColor;
                
                // Update system stats and bars
                const stats = data.system_stats || {};
                const cpuPercent = stats.cpu_percent || 0;
                const ramPercent = stats.ram_percent || 0;
                const gpuPercent = stats.gpu_percent || 0;
                
                document.getElementById('cpuPercent').textContent = Math.round(cpuPercent);
                document.getElementById('ramPercent').textContent = Math.round(ramPercent);
                document.getElementById('gpuPercent').textContent = Math.round(gpuPercent);
                document.getElementById('cpuBar').style.width = Math.min(cpuPercent, 100) + '%';
                document.getElementById('ramBar').style.width = Math.min(ramPercent, 100) + '%';
                document.getElementById('gpuBar').style.width = Math.min(gpuPercent, 100) + '%';
                
                // Update GPU memory info
                const gpuMemory = (stats.gpu_available_gb || 0).toFixed(1);
                document.getElementById('gpuMemory').textContent = gpuMemory;
                
                // Update balance status
                const balance = data.balance_status || {};
                const statusColor = balance.color || 'gray';
                const statusHealth = balance.health || 'unknown';
                document.getElementById('balanceStatus').textContent = balance.status ? balance.status.toUpperCase() : 'UNKNOWN';
                document.getElementById('balanceStatus').style.color = getStatusColor(statusColor);
                
                document.getElementById('stressLevel').textContent = Math.round(balance.stress_level || 0);
                
                // Update bottleneck
                const bottleneck = balance.bottleneck || 'None';
                document.getElementById('bottleneck').textContent = bottleneck;
                
                // Update bottleneck color based on which component is stressed
                if (bottleneck === 'CPU') {
                    document.getElementById('bottleneck').style.color = '#ff6b6b';
                } else if (bottleneck === 'RAM') {
                    document.getElementById('bottleneck').style.color = '#4ecdc4';
                } else if (bottleneck === 'GPU') {
                    document.getElementById('bottleneck').style.color = '#ffd93d';
                } else {
                    document.getElementById('bottleneck').style.color = '#4caf50';
                }
                
                // Update recommendation count
                const recommendations = data.recommendations || [];
                document.getElementById('recommendationCount').textContent = recommendations.length;
                
                // Display recommendations
                const recContainer = document.getElementById('recommendations');
                if (recommendations.length > 0) {
                    recContainer.innerHTML = recommendations.slice(0, 5).map((rec, idx) => `
                        <div style="padding: 10px; margin-bottom: 8px; background: white; border-left: 4px solid #667eea; border-radius: 3px;">
                            <div style="font-weight: bold; color: #333; font-size: 13px; margin-bottom: 3px;">💡 Recommendation ${idx + 1}</div>
                            <div style="color: #666; font-size: 12px;">${escapeHtml(rec)}</div>
                        </div>
                    `).join('');
                } else {
                    recContainer.innerHTML = '<p style="color: #666; font-style: italic;">System is operating optimally</p>';
                }
            } catch (error) {
                console.error('Error loading load balancer data:', error);
                document.getElementById('gpuAvailable').textContent = 'Error';
                document.getElementById('gpuAvailable').style.color = '#f44336';
            }
        }
        
        function getStatusColor(colorName) {
            const colors = {
                'green': '#4caf50',
                'yellow': '#ffc107',
                'orange': '#ff9800',
                'red': '#f44336',
                'gray': '#999'
            };
            return colors[colorName] || '#999';
        }
        
        // Initialize all data on page load
        window.addEventListener('DOMContentLoaded', () => {
            // Load main dashboard data
            loadStats();
            loadNotifications();
            loadIntegratedSystems();
            loadLoadBalancerData();
            
            // Load chatbot data
            loadChatbotStatus();
            loadChatHistory();
            
            // Set up auto-refresh every 5 seconds
            setInterval(() => {
                loadStats();
                loadNotifications();
                loadIntegratedSystems();
                loadLoadBalancerData();
            }, 5000);
        });
    </script>
</body>
</html>'''
    
    def initialize_control_panel(self):
        """Initialize ControlPanel instance"""
        with self.control_panel_lock:
            if not self.control_panel:
                self.control_panel = ControlPanel(use_gradual_loading=False)
                # Start background updates (without GUI)
                self.control_panel.running = True
                # Don't call run() - we just need the data updates
                # Instead, manually update in background thread
                self._start_update_thread()
    
    def _start_update_thread(self):
        """Start background update thread"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        def update_loop():
            while self.running:
                try:
                    with self.control_panel_lock:
                        if self.control_panel:
                            # Trigger updates
                            self.control_panel._update_integrated_systems()
                            self.control_panel._scan_process_improvements()
                    import time
                    time.sleep(2.0)  # Update every 2 seconds
                except Exception as e:
                    print(f"Update thread error: {e}")
                    import time
                    time.sleep(2.0)
        
        self.running = True
        self.update_thread = Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def run(self):
        """Run the web server"""
        # Initialize control panel
        self.initialize_control_panel()
        
        # Start status emitter if SocketIO is available
        if self.socketio and not self.status_emitter_thread:
            self._start_status_emitter()
        
        print("=" * 80)
        print(" " * 20 + "OMEGA CONTROL PANEL - WEB INTERFACE")
        print("=" * 80)
        print()
        print(f"[WEB] Server running at: http://{self.host}:{self.port}")
        print(f"[WEB] Access the dashboard in your browser")
        print()
        print("Press Ctrl+C to stop")
        print()
        
        try:
            if self.socketio:
                self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug)
            else:
                self.app.run(host=self.host, port=self.port, debug=self.debug)
        except KeyboardInterrupt:
            print("\n[INFO] Server stopped by user")
            self.running = False
        except Exception as e:
            print(f"\n[ERROR] Server error: {e}")
            self.running = False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Omega Control Panel Web Interface')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    if not FLASK_AVAILABLE:
        print("ERROR: Flask is required. Install with: pip install flask flask-cors")
        sys.exit(1)
    
    if not CONTROL_PANEL_AVAILABLE:
        print("ERROR: omega_control_panel is required")
        sys.exit(1)
    
    try:
        web_interface = OmegaControlPanelWeb(host=args.host, port=args.port, debug=args.debug)
        web_interface.run()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
