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
import secrets
import argparse
import subprocess
import platform
import shutil
import glob
import webbrowser
import re
import wave
import random
from urllib.parse import unquote
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from threading import Thread, Lock

base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

try:
    from flask import Flask, render_template_string, jsonify, request, session
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Install with: pip install flask flask-cors")

try:
    from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
    from werkzeug.security import generate_password_hash, check_password_hash
    LOGIN_AVAILABLE = True
except ImportError:
    LOGIN_AVAILABLE = False
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

try:
    from flask_sqlalchemy import SQLAlchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("Flask-SQLAlchemy not installed. Install with: pip install flask-sqlalchemy")

try:
    from flask_migrate import Migrate
    MIGRATE_AVAILABLE = True
except ImportError:
    MIGRATE_AVAILABLE = False
    print("Flask-Migrate not installed. Install with: pip install flask-migrate")

try:
    from omega_control_panel import ControlPanel
    CONTROL_PANEL_AVAILABLE = True
except ImportError:
    CONTROL_PANEL_AVAILABLE = False
    print("omega_control_panel not available")

try:
    from flask_socketio import SocketIO, emit, disconnect
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests not installed. Install with: pip install requests")

try:
    from omega_user_storage import get_user_storage
    USER_STORAGE_AVAILABLE = True
except ImportError:
    USER_STORAGE_AVAILABLE = False
    print("omega_user_storage not available - using secure local fallback users")

try:
    from unified_agent_framework import get_agent_registry, LANGCHAIN_AVAILABLE
    from unified_agent_framework import GatekeeperBrainAccess
    sys.path.insert(0, str(base_dir / "agents"))
    from development_agent import DevelopmentAgent
    from communication_agent import CommunicationAgent
    from creative_agent import CreativeAgent
    from harriet_agent import HarrietAgent
    from bob_agent import BobAgent
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    LANGCHAIN_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from omega_ai_mirror_orchestrator import AIMirrorOrchestrator
    MIRROR_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    MIRROR_ORCHESTRATOR_AVAILABLE = False

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
        return self.password_hash == password

from functools import wraps

def role_required(*required_roles):
    """Decorator for Flask routes - requires authentication and specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.remote_addr in ("127.0.0.1", "::1"):
                return f(*args, **kwargs)
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
        
        stress_level = (cpu + ram + gpu) / 3
        
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
        
        variance = max(cpu, ram, gpu) - min(cpu, ram, gpu)
        is_balanced = variance < 30  # Less than 30% difference between components
        
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
        self.ai_configs = {}
        self.mirror = AIMirrorOrchestrator() if MIRROR_ORCHESTRATOR_AVAILABLE else None
        if self.mirror:
            self.ai_configs = self.mirror.providers
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
        if self.mirror:
            result = self.mirror.query_provider(provider, message)
            with self.lock:
                self.chat_history.append({
                    'role': 'user',
                    'content': message,
                    'ai_provider': provider,
                    'timestamp': datetime.now().isoformat()
                })
                self.chat_history.append({
                    'role': 'assistant',
                    'content': result.get('response', result.get('error', '')),
                    'ai_provider': provider,
                    'timestamp': datetime.now().isoformat()
                })
                if len(self.chat_history) > 100:
                    self.chat_history = self.chat_history[-100:]
            return result
        return {'success': False, 'error': 'Mirror orchestrator unavailable', 'provider': provider}
    
    def query_all(self, message: str) -> Dict[str, Any]:
        """Query all enabled AI providers"""
        if self.mirror:
            return self.mirror.query_all(message)
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
        if self.mirror:
            mirror_status = self.mirror.get_status()
        else:
            mirror_status = {}
        return {
            'enabled': self.enabled,
            'providers': {
                provider: {
                    'enabled': config.get('enabled', False),
                    'configured': bool(config.get('api_key'))
                }
                for provider, config in self.ai_configs.items()
            },
            'history_count': len(self.chat_history),
            'mirror': mirror_status
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
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.getenv('OMEGA_SECRET_KEY', secrets.token_hex(32))
        CORS(self.app)  # Enable CORS for API access
        
        if LOGIN_AVAILABLE:
            self.login_manager = LoginManager()
            self.login_manager.init_app(self.app)
            self.login_manager.login_view = 'api_login'
            
            @self.login_manager.user_loader
            def load_user(user_id):
                return self._get_user_by_id(user_id)
        else:
            self.login_manager = None
        
        if SOCKETIO_AVAILABLE:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        else:
            self.socketio = None
        
        self.status_emitter_thread = None
        
        self.control_panel = None
        self.control_panel_lock = Lock()
        
        self.update_thread = None
        self.running = False
        
        self.chatbot = MultiAIChatbot()
        self._conversation_memory: Dict[str, List[Dict[str, str]]] = {
            'omega': [],
            'agents': [],
        }
        self._conversation_memory_file = base_dir / "logs" / "conversation_memory.json"
        self._load_conversation_memory()
        self.agent_registry = None
        self._init_agent_framework()
        
        if USER_STORAGE_AVAILABLE:
            self.user_storage = get_user_storage()
            self.user_storage.ensure_admin_exists()
        else:
            self.user_storage = None
            self._init_fallback_users()
        
        self._setup_routes()
        
        try:
            from omega_voice_screenshot_extension import register_voice_screenshot_extension
            register_voice_screenshot_extension(self.app)
        except ImportError:
            print("[OMEGA] Voice & Screenshot Extension not available")
        
        if self.socketio:
            self._setup_socketio()

    def _load_conversation_memory(self):
        """Load persisted conversation memory across sessions."""
        try:
            if self._conversation_memory_file.exists():
                with open(self._conversation_memory_file, "r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict):
                    for key in ("omega", "agents"):
                        if isinstance(payload.get(key), list):
                            self._conversation_memory[key] = payload[key][-20:]
        except Exception:
            pass

    def _save_conversation_memory(self):
        """Persist conversation memory so Omega/agents can grow between runs."""
        try:
            self._conversation_memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._conversation_memory_file, "w", encoding="utf-8") as handle:
                json.dump(self._conversation_memory, handle, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _is_ui_safe_message(self, text: str) -> Dict[str, Any]:
        """Reject direct code/script/command payloads in UI conversation endpoints."""
        if not text:
            return {'safe': False, 'reason': 'Message cannot be empty'}
        suspicious_patterns = [
            r'```',
            r'\b(eval|exec|subprocess|powershell|cmd\.exe|bash|sh)\b',
            r'(^|\s)(rm\s+-rf|del\s+/[sqf]|format\s+[a-z]:|shutdown\s+/s)\b',
            r'<script\b',
            r'\bfunction\s+\w+\s*\(',
            r'\b(import|require)\s+[a-zA-Z0-9_"\']+',
        ]
        lowered = text.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, lowered, flags=re.IGNORECASE | re.MULTILINE):
                return {
                    'safe': False,
                    'reason': 'UI chat accepts conversational prompts only. Remove code/commands and retry.'
                }
        return {'safe': True}

    def _strip_code_blocks(self, text: str) -> str:
        """Remove fenced/inline code so UI remains conversation-focused."""
        if not isinstance(text, str):
            return ''
        cleaned = re.sub(r'```[\s\S]*?```', '[code omitted for UI safety]', text)
        cleaned = re.sub(r'`[^`]+`', '[inline code omitted]', cleaned)
        return cleaned.strip()

    def _remember_turn(self, channel: str, role: str, content: str):
        """Track short rolling conversation memory per channel."""
        safe_channel = channel if channel in self._conversation_memory else 'omega'
        turns = self._conversation_memory[safe_channel]
        turns.append({
            'role': role,
            'content': content[:1200],
            'timestamp': datetime.now().isoformat()
        })
        if len(turns) > 20:
            self._conversation_memory[safe_channel] = turns[-20:]
        self._save_conversation_memory()

    def _recent_context(self, channel: str, limit: int = 8) -> List[Dict[str, str]]:
        safe_channel = channel if channel in self._conversation_memory else 'omega'
        turns = self._conversation_memory.get(safe_channel, [])
        return turns[-max(1, min(limit, 20)):]

    def _build_suggestions(self, user_message: str, response_texts: List[str]) -> List[str]:
        """Generate practical next-step suggestions that fit the current conversation."""
        msg = (user_message or '').lower()
        corpus = ' '.join(response_texts).lower()
        suggestions: List[str] = []

        if any(word in msg for word in ['simulate', 'scenario', 'path', 'branch', 'decision']):
            suggestions.append('Run a second scenario with one variable changed and compare outcomes.')
        if any(word in msg for word in ['drone', 'flight']):
            suggestions.append('Add weather and battery constraints, then rerun the same route.')
        if any(word in msg for word in ['chess', 'game']):
            suggestions.append('Test two opening strategies and track evaluation after move 10.')
        if 'risk' in msg or 'risk' in corpus:
            suggestions.append('Rank options by impact and likelihood before choosing a final path.')
        if 'agent' in msg or 'omega' in msg:
            suggestions.append('Ask a second agent to challenge assumptions and propose an alternative.')

        if not suggestions:
            suggestions = [
                'Define two alternative paths, then compare cost, time, and risk.',
                'List assumptions explicitly and test the weakest assumption first.',
                'Request one conservative and one aggressive recommendation before deciding.'
            ]
        return suggestions[:3]

    def _query_external_ai_targets(
        self,
        message: str,
        context: List[Dict[str, str]],
        targets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Query user-provided external AI endpoints for group conversation."""
        if not REQUESTS_AVAILABLE or not targets:
            return []
        outputs: List[Dict[str, Any]] = []
        for idx, target in enumerate(targets):
            url = str(target.get('url', '')).strip()
            name = str(target.get('name', f'external_{idx + 1}')).strip() or f'external_{idx + 1}'
            api_key = str(target.get('api_key', '')).strip()
            if not url:
                continue
            headers = {'Content-Type': 'application/json'}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            payload = {
                'message': message,
                'context': context,
                'conversation_mode': True
            }
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=20)
                body = {}
                try:
                    body = resp.json() if resp.content else {}
                except Exception:
                    body = {'text': resp.text[:2000]}
                text = body.get('response') or body.get('result') or body.get('text') or ''
                outputs.append({
                    'target': name,
                    'url': url,
                    'success': resp.ok,
                    'status': resp.status_code,
                    'response': self._strip_code_blocks(str(text)) if text else '',
                    'error': '' if resp.ok else str(body.get('error') or resp.reason)
                })
            except Exception as exc:
                outputs.append({
                    'target': name,
                    'url': url,
                    'success': False,
                    'status': None,
                    'response': '',
                    'error': str(exc)
                })
        return outputs

    def _desktop_app_catalog(self) -> List[Dict[str, Any]]:
        """Catalog of desktop apps to verify and launch from UI."""
        return [
            {
                'id': 'autocad',
                'name': 'AutoCAD',
                'vendor': 'Autodesk',
                'capabilities': ['CAD editing', 'DWG workflows'],
                'executables': ['acad.exe'],
                'path_patterns': [
                    r'C:\Program Files\Autodesk\AutoCAD *\acad.exe',
                    r'C:\Program Files\Autodesk\*\acad.exe',
                ],
            },
            {
                'id': 'adobe_acrobat',
                'name': 'Adobe Acrobat',
                'vendor': 'Adobe',
                'capabilities': ['Sign PDFs', 'Fill forms', 'Edit PDFs'],
                'executables': ['Acrobat.exe'],
                'path_patterns': [
                    r'C:\Program Files\Adobe\Acrobat*\Acrobat\Acrobat.exe',
                    r'C:\Program Files (x86)\Adobe\Acrobat*\Acrobat\Acrobat.exe',
                ],
            },
            {
                'id': 'adobe_reader',
                'name': 'Adobe Reader',
                'vendor': 'Adobe',
                'capabilities': ['Open PDFs', 'Fill/sign supported PDFs'],
                'executables': ['AcroRd32.exe'],
                'path_patterns': [
                    r'C:\Program Files\Adobe\Acrobat Reader*\Reader\AcroRd32.exe',
                    r'C:\Program Files (x86)\Adobe\Acrobat Reader*\Reader\AcroRd32.exe',
                ],
            },
            {
                'id': 'adobe_creative_cloud',
                'name': 'Adobe Creative Cloud',
                'vendor': 'Adobe',
                'capabilities': ['Manage Adobe subscriptions/apps'],
                'executables': ['Creative Cloud.exe'],
                'path_patterns': [
                    r'C:\Program Files\Adobe\Adobe Creative Cloud\ACC\Creative Cloud.exe',
                ],
            },
            {
                'id': 'windows_remote_desktop',
                'name': 'Windows Remote Desktop',
                'vendor': 'Microsoft',
                'capabilities': ['RDP access', 'Cloud/remote Windows sessions'],
                'executables': ['mstsc.exe', 'msrdcw.exe'],
                'path_patterns': [],
            },
            {
                'id': 'windows_365_cloud_pc',
                'name': 'Windows 365 Cloud PC',
                'vendor': 'Microsoft',
                'capabilities': ['Windows 365 browser portal access'],
                'executables': [],
                'path_patterns': [],
                'launch_url': 'https://windows365.microsoft.com/',
            },
        ]

    def _extract_version_hints(self, paths: List[str]) -> List[str]:
        """Extract readable version hints from discovered install paths."""
        versions: List[str] = []
        for path in paths:
            match = re.search(r'(\d{4}(?:\.\d+)?)', path)
            if match:
                value = match.group(1)
                if value not in versions:
                    versions.append(value)
        return versions

    def _resolve_desktop_app(self, app_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve whether app is installed and where it can be launched from."""
        resolved_paths: List[str] = []
        launch_url = app_entry.get('launch_url')

        for exe_name in app_entry.get('executables', []):
            detected = shutil.which(exe_name)
            if detected and detected not in resolved_paths:
                resolved_paths.append(detected)

        for pattern in app_entry.get('path_patterns', []):
            for candidate in glob.glob(pattern):
                if candidate not in resolved_paths:
                    resolved_paths.append(candidate)

        primary_path = resolved_paths[0] if resolved_paths else None
        versions = self._extract_version_hints(resolved_paths)
        installed = bool(primary_path or launch_url)
        return {
            'id': app_entry['id'],
            'name': app_entry['name'],
            'vendor': app_entry['vendor'],
            'capabilities': app_entry.get('capabilities', []),
            'installed': installed,
            'launch_path': primary_path,
            'detected_paths': resolved_paths,
            'launch_url': launch_url,
            'versions': versions,
            'platform_supported': platform.system().lower() == 'windows',
        }

    def _get_desktop_apps_status(self) -> List[Dict[str, Any]]:
        """Return status for all supported desktop app integrations."""
        return [self._resolve_desktop_app(entry) for entry in self._desktop_app_catalog()]

    def _launch_desktop_app(self, app_id: str, launch_target: str = '') -> Dict[str, Any]:
        """Launch a supported desktop app by id."""
        apps_by_id = {app['id']: app for app in self._get_desktop_apps_status()}
        app = apps_by_id.get(app_id)
        if not app:
            return {'success': False, 'error': f'Unknown app id: {app_id}'}

        if not app['platform_supported']:
            return {'success': False, 'error': 'Desktop launch is only supported on Windows hosts'}

        if app.get('launch_url') and (not launch_target or launch_target == app.get('launch_url')):
            try:
                webbrowser.open(app['launch_url'])
                return {'success': True, 'app': app['name'], 'launch_url': app['launch_url']}
            except Exception as exc:
                return {'success': False, 'error': f'Failed to open {app["name"]}: {exc}'}

        allowed_paths = set(app.get('detected_paths') or [])
        default_path = app.get('launch_path')
        selected_target = launch_target if launch_target in allowed_paths else default_path
        if not selected_target:
            return {'success': False, 'error': f"{app['name']} not detected on this machine"}

        try:
            os.startfile(selected_target)  # type: ignore[attr-defined]
            return {'success': True, 'app': app['name'], 'launch_path': selected_target}
        except Exception as exc:
            return {'success': False, 'error': f'Failed to launch {app["name"]}: {exc}'}

    def _allowed_pdf_roots(self) -> List[Path]:
        """Allowed roots for PDF operations."""
        home = Path.home()
        return [
            home / "Documents",
            home / "Downloads",
            home / "Desktop",
        ]

    def _is_allowed_pdf_path(self, file_path: Path) -> bool:
        """Check if a PDF path is inside allowed roots."""
        try:
            resolved = file_path.resolve()
        except Exception:
            return False

        for root in self._allowed_pdf_roots():
            try:
                resolved.relative_to(root.resolve())
                return True
            except Exception:
                continue
        return False

    def _scan_pdf_hints(self, file_path: Path) -> Dict[str, Any]:
        """Best-effort PDF form/signature hints without external dependencies."""
        hints = {
            'likely_fillable': False,
            'likely_signable': False,
        }
        try:
            with open(file_path, 'rb') as f:
                blob = f.read(400000)
            hints['likely_fillable'] = b'/AcroForm' in blob or b'/NeedAppearances' in blob
            hints['likely_signable'] = b'/Sig' in blob or b'/Signature' in blob
        except Exception:
            pass
        return hints

    def _list_recent_pdfs(self, limit: int = 30) -> List[Dict[str, Any]]:
        """List recent PDFs from common user folders."""
        files: List[Path] = []
        for root in self._allowed_pdf_roots():
            if not root.exists():
                continue
            try:
                files.extend(root.rglob("*.pdf"))
            except Exception:
                continue

        unique_files = {}
        for file in files:
            unique_files[str(file)] = file

        sorted_files = sorted(
            unique_files.values(),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )[:max(1, min(limit, 100))]

        results = []
        for file in sorted_files:
            try:
                hints = self._scan_pdf_hints(file)
                results.append({
                    'path': str(file),
                    'name': file.name,
                    'folder': str(file.parent),
                    'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    'size_bytes': file.stat().st_size,
                    **hints
                })
            except Exception:
                continue
        return results

    def _open_pdf(self, file_path: str, app_id: str = '', launch_target: str = '') -> Dict[str, Any]:
        """Open PDF with chosen app (if available) or system default."""
        try:
            decoded = unquote(file_path).strip()
            target = Path(decoded)
            if not target.exists() or target.suffix.lower() != '.pdf':
                return {'success': False, 'error': 'PDF file not found or invalid type'}
            if not self._is_allowed_pdf_path(target):
                return {'success': False, 'error': 'PDF path is outside allowed folders'}

            app_result = None
            if app_id:
                app_result = self._launch_desktop_app(app_id, launch_target=launch_target)
                if not app_result.get('success'):
                    return app_result

            os.startfile(str(target))  # type: ignore[attr-defined]
            return {
                'success': True,
                'file': str(target),
                'app': app_result.get('app') if app_result else 'System default PDF app'
            }
        except Exception as exc:
            return {'success': False, 'error': f'Failed to open PDF: {exc}'}

    def _allowed_audio_roots(self) -> List[Path]:
        home = Path.home()
        return [home / "Desktop", home / "Documents", home / "Downloads", base_dir]

    def _is_allowed_audio_path(self, file_path: Path) -> bool:
        try:
            resolved = file_path.resolve()
        except Exception:
            return False
        for root in self._allowed_audio_roots():
            try:
                resolved.relative_to(root.resolve())
                return True
            except Exception:
                continue
        return False

    def _list_recent_audio(self, limit: int = 40) -> List[Dict[str, Any]]:
        exts = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
        files: List[Path] = []
        for root in self._allowed_audio_roots():
            if not root.exists():
                continue
            try:
                for p in root.rglob("*"):
                    if p.is_file() and p.suffix.lower() in exts:
                        files.append(p)
            except Exception:
                continue
        dedup = {}
        for f in files:
            dedup[str(f)] = f
        sorted_files = sorted(
            dedup.values(),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )[:max(1, min(limit, 100))]
        output = []
        for f in sorted_files:
            try:
                output.append({
                    "path": str(f),
                    "name": f.name,
                    "folder": str(f.parent),
                    "size_bytes": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
            except Exception:
                continue
        return output

    def _copy_audio_file(self, source_path: str, suffix: str = "_copy") -> Dict[str, Any]:
        source = Path(unquote(source_path).strip())
        if not source.exists() or not source.is_file():
            return {"success": False, "error": "Audio file not found"}
        if not self._is_allowed_audio_path(source):
            return {"success": False, "error": "Path outside allowed audio roots"}
        target = source.with_name(f"{source.stem}{suffix}{source.suffix}")
        try:
            shutil.copy2(source, target)
            return {"success": True, "source": str(source), "target": str(target)}
        except Exception as exc:
            return {"success": False, "error": f"Copy failed: {exc}"}

    def _apply_audio_effect(self, source_path: str, effect: str) -> Dict[str, Any]:
        source = Path(unquote(source_path).strip())
        if not source.exists() or not source.is_file():
            return {"success": False, "error": "Audio file not found"}
        if not self._is_allowed_audio_path(source):
            return {"success": False, "error": "Path outside allowed audio roots"}
        if source.suffix.lower() != ".wav":
            return {"success": False, "error": "Current effect engine supports WAV files only"}
        if effect != "reverse":
            return {"success": False, "error": f"Unsupported effect: {effect}"}

        target = source.with_name(f"{source.stem}_{effect}{source.suffix}")
        try:
            with wave.open(str(source), "rb") as in_wav:
                params = in_wav.getparams()
                frames = in_wav.readframes(in_wav.getnframes())
            frame_width = params.sampwidth * params.nchannels
            chunks = [frames[i:i + frame_width] for i in range(0, len(frames), frame_width)]
            chunks.reverse()
            reversed_bytes = b"".join(chunks)
            with wave.open(str(target), "wb") as out_wav:
                out_wav.setparams(params)
                out_wav.writeframes(reversed_bytes)
            return {"success": True, "source": str(source), "target": str(target), "effect": effect}
        except Exception as exc:
            return {"success": False, "error": f"Effect processing failed: {exc}"}

    def _allowed_image_roots(self) -> List[Path]:
        home = Path.home()
        return [home / "Desktop", home / "Documents", home / "Downloads", base_dir]

    def _is_allowed_image_path(self, file_path: Path) -> bool:
        try:
            resolved = file_path.resolve()
        except Exception:
            return False
        for root in self._allowed_image_roots():
            try:
                resolved.relative_to(root.resolve())
                return True
            except Exception:
                continue
        return False

    def _list_recent_images(self, limit: int = 40) -> List[Dict[str, Any]]:
        exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        files: List[Path] = []
        for root in self._allowed_image_roots():
            if not root.exists():
                continue
            try:
                for p in root.rglob("*"):
                    if p.is_file() and p.suffix.lower() in exts:
                        files.append(p)
            except Exception:
                continue
        dedup = {str(f): f for f in files}
        sorted_files = sorted(
            dedup.values(),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True
        )[:max(1, min(limit, 100))]
        output = []
        for f in sorted_files:
            try:
                output.append({
                    "path": str(f),
                    "name": f.name,
                    "folder": str(f.parent),
                    "size_bytes": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
            except Exception:
                continue
        return output

    def _create_image_from_prompt(self, prompt: str, width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        if not PIL_AVAILABLE:
            return {"success": False, "error": "Pillow is required: pip install pillow"}
        width = max(256, min(width, 2048))
        height = max(256, min(height, 2048))
        safe_prompt = (prompt or "Omega image").strip()[:160]
        out_dir = Path.home() / "Desktop" / "OmegaMediaLab"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = out_dir / f"omega_generated_{stamp}.png"
        try:
            color_a = (random.randint(20, 120), random.randint(20, 120), random.randint(80, 180))
            color_b = (random.randint(120, 220), random.randint(80, 220), random.randint(20, 180))
            img = Image.new("RGB", (width, height), color_a)
            draw = ImageDraw.Draw(img)
            for y in range(height):
                ratio = y / max(1, height - 1)
                r = int(color_a[0] * (1 - ratio) + color_b[0] * ratio)
                g = int(color_a[1] * (1 - ratio) + color_b[1] * ratio)
                b = int(color_a[2] * (1 - ratio) + color_b[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            font = ImageFont.load_default()
            draw.rectangle([(20, height - 130), (width - 20, height - 20)], fill=(0, 0, 0, 160))
            draw.text((35, height - 110), f"Prompt: {safe_prompt}", fill=(255, 255, 255), font=font)
            img.save(out_file, format="PNG")
            return {"success": True, "path": str(out_file), "prompt": safe_prompt}
        except Exception as exc:
            return {"success": False, "error": f"Image creation failed: {exc}"}

    def _edit_image(self, source_path: str, operation: str) -> Dict[str, Any]:
        if not PIL_AVAILABLE:
            return {"success": False, "error": "Pillow is required: pip install pillow"}
        src = Path(unquote(source_path).strip())
        if not src.exists() or not src.is_file():
            return {"success": False, "error": "Image file not found"}
        if not self._is_allowed_image_path(src):
            return {"success": False, "error": "Path outside allowed image roots"}
        operation = operation.strip().lower()
        supported = {"grayscale", "mirror", "rotate90", "contrast_plus"}
        if operation not in supported:
            return {"success": False, "error": f"Unsupported operation: {operation}"}
        out = src.with_name(f"{src.stem}_{operation}{src.suffix}")
        try:
            img = Image.open(src)
            if operation == "grayscale":
                out_img = ImageOps.grayscale(img).convert("RGB")
            elif operation == "mirror":
                out_img = ImageOps.mirror(img)
            elif operation == "rotate90":
                out_img = img.rotate(90, expand=True)
            else:
                out_img = ImageEnhance.Contrast(img).enhance(1.35)
            out_img.save(out)
            return {"success": True, "source": str(src), "target": str(out), "operation": operation}
        except Exception as exc:
            return {"success": False, "error": f"Image edit failed: {exc}"}

    def _init_agent_framework(self):
        """Initialize and activate core agents for Omega routing."""
        if not AGENT_FRAMEWORK_AVAILABLE:
            return
        try:
            self.agent_registry = get_agent_registry()
            existing = {agent.agent_id for agent in self.agent_registry.agents.values()}
            if "development_agent" not in existing:
                self.agent_registry.register_agent(DevelopmentAgent())
            if "communication_agent" not in existing:
                self.agent_registry.register_agent(CommunicationAgent())
            if "creative_agent" not in existing:
                self.agent_registry.register_agent(CreativeAgent())
            if "harriet_agent" not in existing:
                self.agent_registry.register_agent(HarrietAgent())
            if "bob_agent" not in existing:
                self.agent_registry.register_agent(BobAgent())
            self.agent_registry.activate_all()
        except Exception as exc:
            print(f"[OMEGA] Agent framework init failed: {exc}")

    def _emit_realtime_event(self, event_name: str, payload: Dict[str, Any]):
        """Emit realtime Socket.IO event safely."""
        if not self.socketio:
            return
        try:
            self.socketio.emit(event_name, payload, broadcast=True)
        except Exception as exc:
            print(f"[OMEGA] Socket emit failed for {event_name}: {exc}")
    
    def _init_fallback_users(self):
        """Initialize secure local fallback users when persistent storage is unavailable."""
        if not LOGIN_AVAILABLE:
            self.fallback_users = {}
            return
        users_file = base_dir / "runtime_fallback_users.json"
        if users_file.exists():
            try:
                with open(users_file, "r", encoding="utf-8") as handle:
                    raw = json.load(handle)
                    if isinstance(raw, dict):
                        self.fallback_users = raw
                        return
            except Exception:
                pass

        generated_passwords = {
            "admin": secrets.token_urlsafe(18),
            "operator": secrets.token_urlsafe(16),
            "viewer": secrets.token_urlsafe(14),
        }
        self.fallback_users = {
            username: {"password": generate_password_hash(password), "role": username if username != "admin" else "admin"}
            for username, password in generated_passwords.items()
        }
        try:
            with open(users_file, "w", encoding="utf-8") as handle:
                json.dump(self.fallback_users, handle, indent=2)
            print("[OMEGA] Created secure fallback users at runtime_fallback_users.json")
            print("[OMEGA] Set persistent omega_user_storage to avoid fallback mode.")
        except Exception as exc:
            print(f"[OMEGA] Failed to persist fallback users: {exc}")
    
    def _get_user_by_id(self, user_id):
        """Get user by ID (from persistent storage or fallback users)."""
        if not LOGIN_AVAILABLE:
            return None
        
        if USER_STORAGE_AVAILABLE and self.user_storage:
            user_data = self.user_storage.get_user(user_id)
            if user_data and user_data.get('active', True):
                return User(id=user_id, username=user_id, 
                          password_hash=user_data['password'], 
                          role=user_data.get('role', 'viewer'))
            return None
        
        if hasattr(self, 'fallback_users') and user_id in self.fallback_users:
            user_data = self.fallback_users[user_id]
            return User(id=user_id, username=user_id, password_hash=user_data['password'], role=user_data['role'])
        return None
    
    def _get_user_by_username(self, username):
        """Get user by username (from persistent storage or fallback users)."""
        if not LOGIN_AVAILABLE:
            return None
        
        if USER_STORAGE_AVAILABLE and self.user_storage:
            user_data = self.user_storage.get_user(username)
            if user_data and user_data.get('active', True):
                return User(id=username, username=username, 
                          password_hash=user_data['password'], 
                          role=user_data.get('role', 'viewer'))
            return None
        
        if hasattr(self, 'fallback_users') and username in self.fallback_users:
            user_data = self.fallback_users[username]
            return User(id=username, username=username, password_hash=user_data['password'], role=user_data['role'])
        return None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return self._get_dashboard_html()
        
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

        @self.app.route('/api/desktop-apps', methods=['GET'])
        def api_desktop_apps():
            """Get desktop app integration status (AutoCAD/Adobe/Windows tools)."""
            try:
                apps = self._get_desktop_apps_status()
                return jsonify({'apps': apps, 'timestamp': datetime.now().isoformat()})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/desktop-apps/launch', methods=['POST'])
        @role_required('admin', 'operator')
        def api_launch_desktop_app():
            """Launch desktop application by app id."""
            data = request.get_json(silent=True) or {}
            app_id = data.get('app_id', '')
            launch_target = data.get('launch_target', '')
            if not app_id:
                return jsonify({'success': False, 'error': 'app_id is required'}), 400

            result = self._launch_desktop_app(app_id, launch_target=launch_target)
            status_code = 200 if result.get('success') else 400
            return jsonify(result), status_code

        @self.app.route('/api/pdf-actions/list', methods=['GET'])
        def api_pdf_list():
            """List recent PDFs and quick fill/sign hints."""
            try:
                limit = int(request.args.get('limit', '30'))
                items = self._list_recent_pdfs(limit=limit)
                return jsonify({'pdfs': items, 'count': len(items)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/pdf-actions/open', methods=['POST'])
        @role_required('admin', 'operator')
        def api_pdf_open():
            """Open selected PDF in preferred app or system default."""
            data = request.get_json(silent=True) or {}
            file_path = data.get('file_path', '')
            app_id = data.get('app_id', '')
            launch_target = data.get('launch_target', '')
            if not file_path:
                return jsonify({'success': False, 'error': 'file_path is required'}), 400

            result = self._open_pdf(file_path, app_id=app_id, launch_target=launch_target)
            status_code = 200 if result.get('success') else 400
            return jsonify(result), status_code
        
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
        
        @self.app.route('/api/hardware/enhanced', methods=['GET'])
        def api_hardware_enhanced():
            """Get enhanced hardware information from LibreHardwareMonitor"""
            try:
                from omega_hardware_monitor_enhanced import OmegaHardwareMonitor
                
                monitor = OmegaHardwareMonitor()
                try:
                    data = monitor.get_all_hardware_data()
                    return jsonify(data)
                finally:
                    monitor.close()
            except Exception as e:
                return jsonify({'error': str(e), 'available': False}), 500
        
        @self.app.route('/api/hardware/fan-control', methods=['POST'])
        def api_fan_control():
            """Control fan speeds (requires LibreHardwareMonitor and admin rights)"""
            try:
                from omega_hardware_monitor_enhanced import OmegaHardwareMonitor
                
                data = request.get_json()
                fan_name = data.get('fan_name')
                speed_percent = data.get('speed_percent')
                
                if not fan_name or speed_percent is None:
                    return jsonify({'error': 'Missing fan_name or speed_percent'}), 400
                
                monitor = OmegaHardwareMonitor()
                try:
                    success = monitor.set_fan_speed(fan_name, speed_percent)
                    return jsonify({'success': success})
                finally:
                    monitor.close()
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/hardware/rgb', methods=['GET', 'POST'])
        def api_hardware_rgb():
            """Get or set RGB lighting configuration"""
            try:
                from omega_hardware_monitor_enhanced import OmegaHardwareMonitor
                
                monitor = OmegaHardwareMonitor()
                try:
                    if request.method == 'GET':
                        rgb_info = monitor.get_rgb_info()
                        return jsonify(rgb_info)
                    
                    elif request.method == 'POST':
                        data = request.get_json()
                        action = data.get('action')
                        
                        if action == 'set_brightness':
                            brightness = data.get('brightness', 100)
                            success = monitor.set_rgb_brightness(brightness)
                            return jsonify({'success': success, 'brightness': monitor.rgb_info.brightness})
                        
                        elif action == 'set_color':
                            r = data.get('r', 255)
                            g = data.get('g', 215)
                            b = data.get('b', 0)
                            success = monitor.set_rgb_color(r, g, b)
                            return jsonify({'success': success, 'color_hex': monitor.rgb_info.color_hex})
                        
                        elif action == 'set_mode':
                            mode = data.get('mode', 'static')
                            success = monitor.set_rgb_mode(mode)
                            return jsonify({'success': success, 'mode': monitor.rgb_info.mode})
                        
                        elif action == 'toggle':
                            success = monitor.toggle_rgb()
                            return jsonify({'success': success, 'enabled': monitor.rgb_info.enabled})
                        
                        else:
                            return jsonify({'error': 'Invalid action'}), 400
                
                finally:
                    monitor.close()
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
                self._emit_realtime_event('chatbot_event', {
                    'type': 'status',
                    'status': 'started',
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'success': True, 'message': 'Chatbot started'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chatbot/stop', methods=['POST'])
        @role_required('admin', 'operator') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_stop():
            """Stop chatbot"""
            try:
                self.chatbot.stop()
                self._emit_realtime_event('chatbot_event', {
                    'type': 'status',
                    'status': 'stopped',
                    'timestamp': datetime.now().isoformat()
                })
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
                
                data = request.get_json() or {}
                message = data.get('message', '').strip()
                provider = data.get('provider', 'all')  # 'grok', 'deepseek', 'chatgpt', or 'all'
                
                if not message:
                    return jsonify({'error': 'Message cannot be empty'}), 400
                safety = self._is_ui_safe_message(message)
                if not safety.get('safe'):
                    return jsonify({'error': safety.get('reason', 'Unsafe request')}), 400

                self._remember_turn('omega', 'user', message)
                recent_context = self._recent_context('omega')
                context_prefix = "\n".join([
                    f"{item.get('role', 'user')}: {item.get('content', '')}" for item in recent_context[:-1]
                ])
                contextual_message = message
                if context_prefix:
                    contextual_message = (
                        "Conversation context:\n"
                        f"{context_prefix}\n\n"
                        f"Current user request: {message}\n"
                        "Respond conversationally with practical suggestions."
                    )
                
                if provider == 'all':
                    results = self.chatbot.query_all(contextual_message)
                else:
                    result = self.chatbot.query_ai(provider, contextual_message)
                    results = {provider: result}

                response_texts = []
                for result_key, result_value in results.items():
                    if isinstance(result_value, dict):
                        if result_value.get('response'):
                            sanitized = self._strip_code_blocks(str(result_value.get('response', '')))
                            results[result_key]['response'] = sanitized
                            response_texts.append(sanitized)
                        if result_value.get('error'):
                            response_texts.append(str(result_value.get('error', '')))
                suggestions = self._build_suggestions(message, response_texts)
                if response_texts:
                    self._remember_turn('omega', 'assistant', " | ".join(response_texts)[:1200])

                self._emit_realtime_event('chatbot_event', {
                    'type': 'message',
                    'provider': provider,
                    'user_message': message,
                    'results': results,
                    'suggestions': suggestions,
                    'timestamp': datetime.now().isoformat()
                })
                
                return jsonify({'success': True, 'results': results, 'suggestions': suggestions})
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
                self._emit_realtime_event('chatbot_event', {
                    'type': 'clear',
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'success': True, 'message': 'Chat history cleared'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/chatbot/provider', methods=['POST'])
        @role_required('admin', 'operator') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_provider():
            """Enable/disable a provider."""
            try:
                data = request.get_json() or {}
                provider = str(data.get('provider', '')).strip().lower()
                enabled = bool(data.get('enabled', True))
                if provider not in self.chatbot.ai_configs:
                    return jsonify({'error': f'Unknown provider: {provider}'}), 400
                self.chatbot.ai_configs[provider]['enabled'] = enabled
                self._emit_realtime_event('chatbot_event', {
                    'type': 'provider_toggle',
                    'provider': provider,
                    'enabled': enabled,
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({
                    'success': True,
                    'provider': provider,
                    'enabled': self.chatbot.ai_configs[provider]['enabled']
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/chatbot/mirror-summary', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_chatbot_mirror_summary():
            """Query mirror providers and return merged overlap summary."""
            try:
                if not self.chatbot.is_running():
                    return jsonify({'error': 'Chatbot is not running. Start it first.'}), 400
                data = request.get_json() or {}
                message = str(data.get('message', '')).strip()
                if not message:
                    return jsonify({'error': 'Message cannot be empty'}), 400
                results = self.chatbot.query_all(message)
                if self.chatbot.mirror:
                    summary = self.chatbot.mirror.mirror_summary(message, results)
                else:
                    summary = {
                        'query': message,
                        'successful_count': 0,
                        'failed_count': 0,
                        'successful': [],
                        'failed': [],
                        'merged_response': '',
                        'timestamp': datetime.now().isoformat()
                    }
                self._emit_realtime_event('chatbot_event', {
                    'type': 'mirror_summary',
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'success': True, 'summary': summary, 'results': results})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/agents/status', methods=['GET'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_agents_status():
            """Get unified agent framework status."""
            if not self.agent_registry:
                return jsonify({
                    'available': False,
                    'error': 'Agent framework unavailable',
                    'langchain_routing': False
                }), 503
            return jsonify({
                'available': True,
                'status': self.agent_registry.get_system_status(),
                'langchain_routing': LANGCHAIN_AVAILABLE
            })

        @self.app.route('/api/agents/message', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_agents_message():
            """Route Omega request through unified agent framework."""
            if not self.agent_registry:
                return jsonify({'error': 'Agent framework unavailable'}), 503
            try:
                data = request.get_json() or {}
                request_text = data.get('request', '').strip()
                payload = data.get('payload', {}) or {}
                if not request_text:
                    return jsonify({'error': 'request is required'}), 400
                safety = self._is_ui_safe_message(request_text)
                if not safety.get('safe'):
                    return jsonify({'error': safety.get('reason', 'Unsafe request')}), 400

                self._remember_turn('agents', 'user', request_text)
                payload['conversation_context'] = self._recent_context('agents')
                payload['conversation_mode'] = True
                result = self.agent_registry.route_task(request_text, payload)
                response_text = self._strip_code_blocks(json.dumps(result.get('result', result), ensure_ascii=False))
                suggestions = self._build_suggestions(request_text, [response_text])
                self._remember_turn('agents', 'assistant', response_text)
                self._emit_realtime_event('agent_event', {
                    'type': 'route',
                    'request': request_text,
                    'payload': payload,
                    'result': result,
                    'suggestions': suggestions,
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({
                    **result,
                    'response_text': response_text,
                    'suggestions': suggestions
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/agents/group-message', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_agents_group_message():
            """Send one prompt to a selected group of agents (and optional external AIs)."""
            if not self.agent_registry:
                return jsonify({'error': 'Agent framework unavailable'}), 503
            try:
                data = request.get_json() or {}
                request_text = str(data.get('request', '')).strip()
                selected_agents = data.get('agents', []) or []
                payload = data.get('payload', {}) or {}
                external_targets = data.get('external_targets', []) or []
                if not request_text:
                    return jsonify({'error': 'request is required'}), 400
                safety = self._is_ui_safe_message(request_text)
                if not safety.get('safe'):
                    return jsonify({'error': safety.get('reason', 'Unsafe request')}), 400

                self._remember_turn('agents', 'user', request_text)
                context = self._recent_context('agents')
                payload['conversation_context'] = context
                payload['conversation_mode'] = True

                active_ids = {agent.agent_id for agent in self.agent_registry.agents.values() if agent.active}
                requested = [str(agent_id).strip() for agent_id in selected_agents if str(agent_id).strip()]
                if not requested:
                    requested = sorted(active_ids)

                results: List[Dict[str, Any]] = []
                for agent_id in requested:
                    if agent_id not in active_ids:
                        results.append({
                            'agent_id': agent_id,
                            'success': False,
                            'error': 'Agent not active or not found'
                        })
                        continue
                    agent = self.agent_registry.get_agent(agent_id)
                    if not agent:
                        results.append({'agent_id': agent_id, 'success': False, 'error': 'Agent not found'})
                        continue
                    task = {
                        'type': payload.get('type', 'compose_message'),
                        'data': {'request': request_text, **payload},
                        'priority': payload.get('priority', 5),
                        'metadata': {'conversation_mode': True, 'group_chat': True}
                    }
                    self.agent_registry.bus.send('omega', agent_id, request_text, {'group_chat': True})
                    raw_result = agent.execute_task(task)
                    response_text = self._strip_code_blocks(json.dumps(raw_result, ensure_ascii=False))
                    self.agent_registry.bus.send(agent_id, 'omega', response_text[:2000], {'group_chat': True, 'result': True})
                    results.append({
                        'agent_id': agent_id,
                        'agent_name': agent.name,
                        'success': True,
                        'result': raw_result,
                        'response_text': response_text
                    })

                external_results = self._query_external_ai_targets(request_text, context, external_targets)
                response_texts = [entry.get('response_text', '') for entry in results if entry.get('response_text')]
                response_texts.extend([entry.get('response', '') for entry in external_results if entry.get('response')])
                suggestions = self._build_suggestions(request_text, response_texts)
                if response_texts:
                    self._remember_turn('agents', 'assistant', ' | '.join(response_texts)[:1200])

                payload_view = {
                    'selected_agents': requested,
                    'external_count': len(external_targets),
                    'conversation_mode': True
                }
                self._emit_realtime_event('agent_event', {
                    'type': 'group_route',
                    'request': request_text,
                    'payload': payload_view,
                    'results_count': len(results),
                    'external_results_count': len(external_results),
                    'suggestions': suggestions,
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({
                    'success': True,
                    'request': request_text,
                    'selected_agents': requested,
                    'results': results,
                    'external_results': external_results,
                    'suggestions': suggestions
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/agents/messages', methods=['GET'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_agents_messages():
            """Get recent inter-agent messages."""
            if not self.agent_registry:
                return jsonify({'history': []})
            limit = request.args.get('limit', 100, type=int)
            return jsonify({'history': self.agent_registry.get_message_history(limit=limit)})

        @self.app.route('/api/brain/search', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_brain_search():
            """Search shared Gatekeeper/Omega brain sources directly."""
            try:
                data = request.get_json() or {}
                query = str(data.get('query', '')).strip()
                limit = int(data.get('limit', 10))
                if not query:
                    return jsonify({'error': 'query is required'}), 400
                limit = max(1, min(limit, 25))
                brain = GatekeeperBrainAccess()
                hits = brain.search(query, limit=limit)
                return jsonify({
                    'success': True,
                    'query': query,
                    'limit': limit,
                    'sources': brain.available_sources(),
                    'hits': hits
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/voice/speak', methods=['POST'])
        def api_voice_speak():
            """Trigger Omega voice"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                voice_type = data.get('type', 'status')  # status, alert, command
                
                subprocess.Popen(
                    [sys.executable, 'speak_omega_voice.py'],
                    cwd=str(base_dir),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Omega voice activated',
                    'type': voice_type
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/voice/status', methods=['GET'])
        def api_voice_status():
            """Get voice system status"""
            try:
                voice_files = []
                for f in ['clip_0001.wav', 'omega_downloaded.wav']:
                    if os.path.exists(f):
                        voice_files.append({
                            'name': f,
                            'size': os.path.getsize(f)
                        })
                
                return jsonify({
                    'available': len(voice_files) > 0,
                    'files': voice_files,
                    'tts_installed': True
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/audio/list', methods=['GET'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_audio_list():
            try:
                limit = request.args.get('limit', 40, type=int)
                return jsonify({'success': True, 'files': self._list_recent_audio(limit=limit)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/audio/copy', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_audio_copy():
            try:
                data = request.get_json() or {}
                source = str(data.get('source_path', '')).strip()
                suffix = str(data.get('suffix', '_copy')).strip() or '_copy'
                if not source:
                    return jsonify({'error': 'source_path is required'}), 400
                result = self._copy_audio_file(source, suffix=suffix)
                code = 200 if result.get('success') else 400
                return jsonify(result), code
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/audio/effect', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_audio_effect():
            try:
                data = request.get_json() or {}
                source = str(data.get('source_path', '')).strip()
                effect = str(data.get('effect', 'reverse')).strip().lower()
                if not source:
                    return jsonify({'error': 'source_path is required'}), 400
                result = self._apply_audio_effect(source, effect=effect)
                code = 200 if result.get('success') else 400
                return jsonify(result), code
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/images/list', methods=['GET'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_images_list():
            try:
                limit = request.args.get('limit', 40, type=int)
                return jsonify({'success': True, 'files': self._list_recent_images(limit=limit)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/images/create', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_images_create():
            try:
                data = request.get_json() or {}
                prompt = str(data.get('prompt', '')).strip()
                width = int(data.get('width', 1024))
                height = int(data.get('height', 1024))
                if not prompt:
                    return jsonify({'error': 'prompt is required'}), 400
                result = self._create_image_from_prompt(prompt, width=width, height=height)
                code = 200 if result.get('success') else 400
                return jsonify(result), code
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/images/edit', methods=['POST'])
        @role_required('admin', 'operator', 'viewer') if LOGIN_AVAILABLE else lambda f: f
        def api_images_edit():
            try:
                data = request.get_json() or {}
                source = str(data.get('source_path', '')).strip()
                operation = str(data.get('operation', 'grayscale')).strip().lower()
                if not source:
                    return jsonify({'error': 'source_path is required'}), 400
                result = self._edit_image(source, operation=operation)
                code = 200 if result.get('success') else 400
                return jsonify(result), code
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile')
        def mobile_interface():
            """Mobile-optimized interface"""
            return self._get_mobile_html()
    
    def _setup_socketio(self):
        """Setup WebSocket events (if SocketIO available)"""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        @authenticated_only if LOGIN_AVAILABLE else (lambda f: f)
        def handle_connect():
            """Handle WebSocket connection"""
            print('Client connected to SocketIO')
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
                            self.control_panel.toggle_rgb()
                        elif color:
                            self.control_panel.set_rgb_color(color)
                        else:
                            self.control_panel.rgb_enabled = enabled
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
            
            cpu_temp = self.control_panel._get_cpu_temperature() if self.control_panel else 0.0
            gpu_temp = self.control_panel._get_gpu_temperature() if self.control_panel else 0.0
            gpu_usage = self.control_panel._get_gpu_usage() if self.control_panel else 0.0
            fan_speed = self.control_panel.fan_speed_percentage if self.control_panel else 50
            rgb_enabled = self.control_panel.rgb_enabled if self.control_panel else False
            rgb_color = self.control_panel.rgb_color if self.control_panel else '#FFD700'
            
            gpu_memory_used = 0.0
            gpu_memory_total = 0.0
            gpu_name = 'Unknown'
            gpu_power_draw = None
            gpu_power_limit = None
            gpu_fan_speed = None
            gpu_clock = None
            gpu_memory_clock = None
            
            try:
                from omega_hardware_sensors import get_gpu_info_nvidia
                gpu_info = get_gpu_info_nvidia()
                if gpu_info:
                    gpu_name = gpu_info.get('name', 'Unknown')
                    gpu_memory_used = gpu_info.get('memory_used_gb', 0.0)
                    gpu_memory_total = gpu_info.get('memory_total_gb', 0.0)
                    gpu_power_draw = gpu_info.get('power_draw')
                    gpu_power_limit = gpu_info.get('power_limit')
                    gpu_fan_speed = gpu_info.get('fan_speed')
                    gpu_clock = gpu_info.get('clock_graphics')
                    gpu_memory_clock = gpu_info.get('clock_memory')
            except Exception:
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        mem_data = result.stdout.strip().split(',')
                        if len(mem_data) >= 2:
                            gpu_memory_used = float(mem_data[0].strip()) / 1024  # Convert MB to GB
                            gpu_memory_total = float(mem_data[1].strip()) / 1024
                except Exception:
                    pass
            
            return {
                'cpu_usage': cpu_percent,
                'cpu_temperature': cpu_temp or 0.0,
                'gpu_name': gpu_name,
                'gpu_temperature': gpu_temp or 0.0,
                'gpu_usage': gpu_usage or 0.0,
                'gpu_memory_used': gpu_memory_used,
                'gpu_memory_total': gpu_memory_total,
                'gpu_power_draw': gpu_power_draw,
                'gpu_power_limit': gpu_power_limit,
                'gpu_fan_speed': gpu_fan_speed,
                'gpu_clock': gpu_clock,
                'gpu_memory_clock': gpu_memory_clock,
                'gpu_available': gpu_temp is not None or gpu_usage is not None,
                'memory_usage': memory.percent if memory else 0.0,
                'memory_total': memory.total if memory else 0,
                'memory_available': memory.available if memory else 0,
                'disk_usage': disk.percent if disk else 0.0,
                'disk_total': disk.total if disk else 0,
                'disk_free': disk.free if disk else 0,
                'fan_speed': fan_speed,
                'rgb_enabled': rgb_enabled,
                'rgb_color': rgb_color
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_hardware_data(self) -> Dict[str, Any]:
        """Get hardware data"""
        system_data = self._get_system_data()
        return system_data
    
    def _get_mobile_html(self) -> str:
        """Generate mobile-optimized HTML interface"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Omega Mobile Control</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1e 100%);
            color: #fff;
            overflow-x: hidden;
            height: 100vh;
        }
        .mobile-header {
            background: rgba(255,0,0,0.1);
            border-bottom: 2px solid #ff0000;
            padding: 15px;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        .mobile-header h1 {
            font-size: 24px;
            color: #ff0000;
            text-shadow: 0 0 10px rgba(255,0,0,0.5);
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 12px;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #0f0;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .mobile-content {
            padding: 15px;
            padding-bottom: 100px;
        }
        .voice-control {
            background: linear-gradient(135deg, rgba(255,0,0,0.2), rgba(255,0,0,0.05));
            border: 2px solid #ff0000;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        .voice-btn {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff0000, #cc0000);
            border: none;
            font-size: 48px;
            color: #fff;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(255,0,0,0.5);
            transition: all 0.3s;
            margin: 20px auto;
            display: block;
        }
        .voice-btn:active {
            transform: scale(0.95);
            box-shadow: 0 5px 15px rgba(255,0,0,0.5);
        }
        .voice-btn.listening {
            animation: voicePulse 1s infinite;
        }
        @keyframes voicePulse {
            0%, 100% { box-shadow: 0 10px 30px rgba(255,0,0,0.5); }
            50% { box-shadow: 0 10px 50px rgba(255,0,0,1); }
        }
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .action-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .action-card:active {
            background: rgba(255,255,255,0.1);
            transform: scale(0.98);
        }
        .action-icon {
            font-size: 36px;
            margin-bottom: 10px;
        }
        .action-label {
            font-size: 14px;
            font-weight: 600;
        }
        .system-stats {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.7;
        }
        .stat-value {
            font-size: 18px;
            font-weight: 700;
            color: #0f0;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #0f0, #0a0);
            transition: width 0.3s;
        }
        .voice-status {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.9);
            border: 1px solid #ff0000;
            border-radius: 25px;
            padding: 10px 20px;
            font-size: 14px;
            display: none;
            animation: slideUp 0.3s;
        }
        @keyframes slideUp {
            from { bottom: 60px; opacity: 0; }
            to { bottom: 80px; opacity: 1; }
        }
        .nav-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.95);
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            backdrop-filter: blur(10px);
        }
        .nav-btn {
            background: none;
            border: none;
            color: rgba(255,255,255,0.5);
            font-size: 24px;
            padding: 10px 20px;
            cursor: pointer;
            transition: color 0.3s;
        }
        .nav-btn.active {
            color: #ff0000;
        }
    </style>
</head>
<body>
    <div class="mobile-header">
        <h1>âš¡ OMEGA CONTROL</h1>
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>Online</span>
            </div>
            <div class="status-item">
                <span id="time">--:--</span>
            </div>
        </div>
    </div>

    <div class="mobile-content">
        <div class="voice-control">
            <h2>ðŸŽ¤ Omega Voice</h2>
            <button class="voice-btn" id="voiceBtn">ðŸ”´</button>
            <p id="voiceText">Tap to activate Omega</p>
        </div>

        <div class="quick-actions">
            <div class="action-card" onclick="quickAction('status')">
                <div class="action-icon">ðŸ“Š</div>
                <div class="action-label">Status</div>
            </div>
            <div class="action-card" onclick="quickAction('voice')">
                <div class="action-icon">ðŸ”Š</div>
                <div class="action-label">Speak</div>
            </div>
            <div class="action-card" onclick="quickAction('hardware')">
                <div class="action-icon">ðŸ’»</div>
                <div class="action-label">Hardware</div>
            </div>
            <div class="action-card" onclick="quickAction('optimize')">
                <div class="action-icon">âš¡</div>
                <div class="action-label">Optimize</div>
            </div>
        </div>

        <div class="system-stats">
            <h3 style="margin-bottom: 15px;">System Status</h3>
            
            <div class="stat-row">
                <span class="stat-label">CPU</span>
                <span class="stat-value" id="cpu">--</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="cpuBar"></div>
            </div>

            <div class="stat-row">
                <span class="stat-label">RAM</span>
                <span class="stat-value" id="ram">--</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="ramBar"></div>
            </div>

            <div class="stat-row">
                <span class="stat-label">GPU</span>
                <span class="stat-value" id="gpu">--</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="gpuBar"></div>
            </div>
        </div>
    </div>

    <div class="voice-status" id="voiceStatus">Omega speaking...</div>

    <div class="nav-bar">
        <button class="nav-btn active">ðŸ </button>
        <button class="nav-btn">ðŸ“Š</button>
        <button class="nav-btn">âš™ï¸</button>
        <button class="nav-btn">ðŸ‘¤</button>
    </div>

    <script>
        function updateTime() {
            const now = new Date();
            document.getElementById('time').textContent = now.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        }
        setInterval(updateTime, 1000);
        updateTime();

        const voiceBtn = document.getElementById('voiceBtn');
        const voiceText = document.getElementById('voiceText');
        const voiceStatus = document.getElementById('voiceStatus');
        let isListening = false;

        voiceBtn.onclick = function() {
            if (!isListening) {
                isListening = true;
                voiceBtn.classList.add('listening');
                voiceText.textContent = 'Omega activating...';
                
                fetch('/api/voice/speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: 'System status', type: 'status'})
                })
                .then(r => r.json())
                .then(data => {
                    voiceStatus.textContent = 'Omega online';
                    voiceStatus.style.display = 'block';
                    setTimeout(() => {
                        voiceStatus.style.display = 'none';
                        isListening = false;
                        voiceBtn.classList.remove('listening');
                        voiceText.textContent = 'Tap to activate Omega';
                    }, 3000);
                })
                .catch(err => {
                    console.error(err);
                    isListening = false;
                    voiceBtn.classList.remove('listening');
                    voiceText.textContent = 'Error - Tap to retry';
                });
            }
        };

        function quickAction(action) {
            switch(action) {
                case 'voice':
                    voiceBtn.click();
                    break;
                case 'status':
                    updateStats();
                    break;
                case 'hardware':
                    window.location.href = '/';
                    break;
                case 'optimize':
                    alert('System optimization initiated');
                    break;
            }
        }

        function updateStats() {
            fetch('/api/system')
                .then(r => r.json())
                .then(data => {
                    const cpu = data.cpu_percent || 0;
                    const ram = data.ram_percent || 0;
                    const gpu = data.gpu_percent || 0;

                    document.getElementById('cpu').textContent = cpu.toFixed(1) + '%';
                    document.getElementById('ram').textContent = ram.toFixed(1) + '%';
                    document.getElementById('gpu').textContent = gpu.toFixed(1) + '%';

                    document.getElementById('cpuBar').style.width = cpu + '%';
                    document.getElementById('ramBar').style.width = ram + '%';
                    document.getElementById('gpuBar').style.width = gpu + '%';
                })
                .catch(err => console.error(err));
        }

        setInterval(updateStats, 1000);  // Update every 1 second
        updateStats();
    </script>
</body>
</html>''';
    
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
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(26, 26, 46, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 0, 0, 0.2);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(255, 0, 0, 0.1);
        }
        .header h1 {
            color: #ff0000;
            margin-bottom: 10px;
            font-size: 36px;
            font-weight: 700;
            text-shadow: 0 0 20px rgba(255,0,0,0.5);
            letter-spacing: 3px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(26, 26, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 0, 0, 0.2);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(255, 0, 0, 0.3);
            border-color: rgba(255, 0, 0, 0.5);
        }
        .stat-card h3 {
            color: #ff4444;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #fff;
            text-shadow: 0 2px 10px rgba(255,255,255,0.3);
        }
        .stat-unit {
            font-size: 16px;
            color: #aaa;
        }
        .section {
            background: rgba(26, 26, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 0, 0, 0.2);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        .section h2 {
            color: #ff4444;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: 600;
            border-bottom: 2px solid rgba(255,68,68,0.3);
            padding-bottom: 10px;
        }
        .notification {
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 10px;
            border-left: 4px solid;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(5px);
        }
        .notification.info { border-color: #2196f3; color: #64b5f6; }
        .notification.warning { border-color: #ff9800; color: #ffb74d; }
        .notification.error { border-color: #f44336; color: #e57373; }
        .notification.success { border-color: #4caf50; color: #81c784; }
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
            padding: 8px 16px;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            font-size: 12px;
            font-weight: bold;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        /* KITT Voice Box */
        .kitt-voice-box {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #000;
            padding: 20px 30px;
            border-radius: 8px;
            border: 2px solid #1a1a1a;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 4px 10px rgba(0,0,0,0.5);
            margin: 20px 0;
        }
        
        .kitt-bars {
            display: flex;
            gap: 6px;
            align-items: flex-end;
        }
        
        .kitt-bar {
            width: 8px;
            background: rgba(80,0,0,0.3);
            border-radius: 2px;
            transition: all 0.3s ease;
            box-shadow: inset 0 -2px 4px rgba(0,0,0,0.5);
        }
        
        .kitt-bar.active {
            background: linear-gradient(to top, #ff0000, #ff6666);
            box-shadow: 
                0 0 10px #ff0000,
                0 0 20px rgba(255,0,0,0.6),
                inset 0 -2px 8px rgba(255,100,100,0.8);
        }
        
        .kitt-bar.dim {
            background: rgba(255,0,0,0.2);
            box-shadow: 0 0 5px rgba(255,0,0,0.2);
        }
        
        /* Header Section (Light Blue) */
        .omega-header-section {
            background: linear-gradient(135deg, #4a90e2, #5ba3f5);
            padding: 20px 30px;
            border-radius: 8px 8px 0 0;
            border: 2px solid rgba(74, 144, 226, 0.5);
            text-align: center;
            box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        }
        
        .omega-header-section h1 {
            margin: 0;
            color: #ffffff;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .omega-header-section p {
            margin: 5px 0 0 0;
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* KITT Section (Purple Background) */
        .kitt-section {
            background: linear-gradient(135deg, #6a1b9a, #8e24aa);
            padding: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-left: 2px solid rgba(142, 36, 170, 0.5);
            border-right: 2px solid rgba(142, 36, 170, 0.5);
            box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.3);
        }
        
        /* Voice Status Section (Orange/Yellow Box) */
        .voice-status-section {
            background: linear-gradient(135deg, #ff9800, #ffc107);
            padding: 20px 30px;
            border-radius: 0 0 8px 8px;
            border: 2px solid rgba(255, 152, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        }
        
        .voice-status-box {
            display: inline-flex;
            align-items: center;
            gap: 15px;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid rgba(255, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        
        .status-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #666;
            box-shadow: 0 0 10px rgba(102, 102, 102, 0.5);
            transition: all 0.3s ease;
        }
        
        .status-indicator.active {
            background: #ff0000;
            box-shadow: 
                0 0 15px #ff0000,
                0 0 30px rgba(255, 0, 0, 0.8);
            animation: statusPulse 1.5s infinite;
        }
        
        @keyframes statusPulse {
            0%, 100% { 
                opacity: 1;
                transform: scale(1);
            }
            50% { 
                opacity: 0.7;
                transform: scale(1.1);
            }
        }
        
        .status-text {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .status-title {
            font-size: 16px;
            font-weight: 700;
            color: #ff0000;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .status-subtitle {
            font-size: 12px;
            color: #aaa;
            opacity: 0.8;
        }
        
        /* Tab System */
        .tab-btn {
            transition: all 0.3s ease;
        }
        .tab-btn:hover {
            color: #ff8888 !important;
        }
        .tab-btn.active {
            color: #ff0000 !important;
            border-bottom-color: #ff0000 !important;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
    <script src="https://cdn.rawgit.com/davidshimjs/qrcodejs/gh-pages/qrcode.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <!-- Header Section (Light Blue) - OMEGA Name -->
            <div class="omega-header-section">
                <h1>ðŸ”´ OMEGA CONTROL PANEL</h1>
                <p>Web Interface - Real-time Monitoring & Control</p>
            </div>
            
            <!-- KITT Voice Section (Purple Background) -->
            <div class="kitt-section">
                <!-- Simplified layout - bars saved for later -->
            </div>
            
            <!-- Voice Status Section (Orange/Yellow Box) -->
            <div class="voice-status-section">
                <div class="voice-status-box" id="voiceStatusBox">
                    <div class="status-indicator" id="statusIndicator"></div>
                    <div class="status-text">
                        <div class="status-title" id="statusTitle">OMEGA READY</div>
                        <div class="status-subtitle" id="statusSubtitle">Click button to activate</div>
                    </div>
                </div>
            </div>
            
            <!-- Tab Navigation -->
            <div style="margin-top: 20px; display: flex; gap: 10px; border-bottom: 2px solid rgba(255,0,0,0.2); padding-bottom: 10px;">
                <button onclick="switchTab('desktop')" id="tabDesktop" class="tab-btn active" style="background: transparent; border: none; color: #ff4444; padding: 10px 20px; cursor: pointer; border-bottom: 3px solid #ff0000; font-weight: bold;">
                    ðŸ’» Desktop
                </button>
                <button onclick="switchTab('mobile')" id="tabMobile" class="tab-btn" style="background: transparent; border: none; color: #aaa; padding: 10px 20px; cursor: pointer; border-bottom: 3px solid transparent; font-weight: bold;">
                    ðŸ“± Mobile
                </button>
                <button onclick="switchTab('qr')" id="tabQR" class="tab-btn" style="background: transparent; border: none; color: #aaa; padding: 10px 20px; cursor: pointer; border-bottom: 3px solid transparent; font-weight: bold;">
                    ðŸ“· QR Code
                </button>
                <button onclick="switchTab('audio')" id="tabAudio" class="tab-btn" style="background: transparent; border: none; color: #aaa; padding: 10px 20px; cursor: pointer; border-bottom: 3px solid transparent; font-weight: bold;">
                    🔊 Audio Lab
                </button>
            </div>
            
            <div style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
                <button onclick="activateOmegaVoice()" style="background: #ff0000; width: auto; padding: 12px 24px; font-weight: bold; box-shadow: 0 0 20px rgba(255,0,0,0.3);">
                    ðŸŽ¤ Activate Omega Voice
                </button>
                <button onclick="refreshData()" style="background: #4caf50; width: auto; padding: 12px 24px; font-weight: bold;">
                    ðŸ”„ Refresh Data
                </button>
                <button onclick="toggleRGB()" id="rgbToggleBtn" style="background: #9c27b0; width: auto; padding: 12px 24px; font-weight: bold;">
                    ðŸŒˆ Toggle RGB
                </button>
            </div>
        </div>
        
        <!-- Tab Content -->
        <div id="tabContentDesktop" class="tab-content active">
        
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
            <h2>Desktop App Integrations</h2>
            <p style="color: #666; margin-bottom: 10px;">AutoCAD, Adobe, and Windows access tools detected on this machine.</p>
            <div id="desktopApps">Loading...</div>
        </div>

        <div class="section">
            <h2>PDF Actions</h2>
            <p style="color: #666; margin-bottom: 10px;">Open, fill, sign, or edit recent PDFs using your Adobe tools.</p>
            <div style="display:flex; gap:8px; margin-bottom:10px; flex-wrap:wrap;">
                <button onclick="loadPdfActions()" style="width:auto; padding: 8px 12px; background:#2e7d32;">Refresh PDFs</button>
            </div>
            <div id="pdfActionsList">Loading...</div>
        </div>
        
        <div class="section">
            <h2>ðŸŒ¡ï¸ Enhanced Hardware Monitor</h2>
            <div id="enhancedHardwareMonitor" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <!-- CPU Section -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <h3 style="margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">ðŸ–¥ï¸</span>
                        <span>CPU Monitor</span>
                    </h3>
                    <div id="cpuMonitor" style="font-size: 14px;">
                        <div style="margin-bottom: 10px;">
                            <strong>Temperature:</strong> <span id="cpuTemp">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Package:</strong> <span id="cpuPackageTemp">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Core Temps:</strong><br>
                            <span id="cpuCoreTemps" style="font-size: 12px;">--</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Clock:</strong> <span id="cpuClock">--</span> MHz
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Power:</strong> <span id="cpuPower">--</span>W
                        </div>
                        <div>
                            <strong>Usage:</strong> <span id="cpuUsageDetailed">--</span>%
                        </div>
                    </div>
                </div>

                <!-- GPU Section -->
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <h3 style="margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">ðŸŽ®</span>
                        <span>GPU Monitor</span>
                    </h3>
                    <div id="gpuMonitor" style="font-size: 14px;">
                        <div style="margin-bottom: 10px;">
                            <strong>Name:</strong> <span id="gpuNameDetailed">--</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Temperature:</strong> <span id="gpuTempDetailed">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Hot Spot:</strong> <span id="gpuHotSpot">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Memory Temp:</strong> <span id="gpuMemoryTemp">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Usage:</strong> <span id="gpuUsageDetailed">--</span>%
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Memory:</strong> <span id="gpuMemoryDetailed">--</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Power:</strong> <span id="gpuPowerDetailed">--</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Fan:</strong> <span id="gpuFanDetailed">--</span>%
                        </div>
                        <div>
                            <strong>Clocks:</strong> <span id="gpuClocksDetailed">--</span>
                        </div>
                    </div>
                </div>

                <!-- Motherboard Section -->
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <h3 style="margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">âš¡</span>
                        <span>Motherboard</span>
                    </h3>
                    <div id="motherboardMonitor" style="font-size: 14px;">
                        <div style="margin-bottom: 10px;">
                            <strong>Name:</strong><br>
                            <span id="mbName" style="font-size: 12px;">--</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Chipset:</strong> <span id="mbChipsetTemp">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>VRM:</strong> <span id="mbVrmTemp">--</span>Â°C
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Fans:</strong><br>
                            <span id="mbFans" style="font-size: 12px;">--</span>
                        </div>
                        <div>
                            <strong>Status:</strong> <span id="mbStatus">--</span>
                        </div>
                    </div>
                </div>

                <!-- Memory Section -->
                <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <h3 style="margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">ðŸ’¾</span>
                        <span>Memory</span>
                    </h3>
                    <div id="memoryMonitor" style="font-size: 14px;">
                        <div style="margin-bottom: 10px;">
                            <strong>Usage:</strong> <span id="memUsage">--</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Temperature:</strong> <span id="memTemp">--</span>Â°C
                        </div>
                        <div>
                            <strong>Speed:</strong> <span id="memSpeed">--</span> MHz
                        </div>
                    </div>
                </div>

                <!-- Storage Section -->
                <div style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <h3 style="margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">ðŸ’¿</span>
                        <span>Storage</span>
                    </h3>
                    <div id="storageMonitor" style="font-size: 12px;">
                        <div id="storageDevices">No storage data available</div>
                    </div>
                </div>

                <!-- LibreHardwareMonitor Status -->
                <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 20px; border-radius: 10px; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <h3 style="margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">ðŸ“Š</span>
                        <span>Monitor Status</span>
                    </h3>
                    <div id="monitorStatus" style="font-size: 14px;">
                        <div style="margin-bottom: 10px;">
                            <strong>LibreHardwareMonitor:</strong> <span id="libreHwStatus">Checking...</span>
                        </div>
                        <div style="margin-bottom: 10px; font-size: 12px; line-height: 1.5;">
                            <strong>Installation:</strong><br>
                            Download from <a href="https://github.com/LibreHardwareMonitor/LibreHardwareMonitor" target="_blank" style="color: #667eea;">GitHub</a><br>
                            Run as Administrator for full access
                        </div>
                        <div style="font-size: 12px;">
                            <strong>Last Update:</strong> <span id="hwLastUpdate">--</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Controls -->
            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 15px 0; color: #333;">âš™ï¸ Performance Controls</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">ðŸŒ¡ï¸ CPU Boost Mode</label>
                        <select id="cpuBoostMode" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ddd; background: white;">
                            <option value="auto">Auto (Default)</option>
                            <option value="conservative">Conservative</option>
                            <option value="performance">High Performance</option>
                            <option value="aggressive">Aggressive Boost</option>
                        </select>
                        <small style="color: #666; display: block; margin-top: 5px;">Adjust CPU turbo behavior</small>
                    </div>
                    
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">ðŸŽ® GPU Power Limit</label>
                        <select id="gpuPowerLimit" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ddd; background: white;">
                            <option value="default">Default (Stock)</option>
                            <option value="eco">Eco Mode (70W)</option>
                            <option value="balanced">Balanced (90W)</option>
                            <option value="performance">Performance (110W)</option>
                        </select>
                        <small style="color: #666; display: block; margin-top: 5px;">Adjust GPU power target</small>
                    </div>
                    
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">ðŸ’¨ Fan Profile</label>
                        <select id="fanProfile" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ddd; background: white;">
                            <option value="auto">Auto (Temperature-based)</option>
                            <option value="silent">Silent (30-50%)</option>
                            <option value="balanced">Balanced (50-70%)</option>
                            <option value="performance">Performance (70-100%)</option>
                            <option value="manual">Manual Control</option>
                        </select>
                        <small style="color: #666; display: block; margin-top: 5px;">Fan speed behavior</small>
                    </div>
                </div>
                
                <div style="margin-top: 20px; text-align: center;">
                    <button onclick="applyPerformanceSettings()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                        âœ“ Apply Settings
                    </button>
                    <small style="display: block; margin-top: 10px; color: #999;">âš ï¸ Requires administrator rights for some settings</small>
                </div>
            </div>
        </div>
        
        <!-- RGB Lighting Control -->
        <div class="section">
            <h2>ðŸŒˆ RGB Lighting Control</h2>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <!-- RGB Brightness -->
                    <div>
                        <label style="display: block; margin-bottom: 10px; font-weight: bold; font-size: 16px;">
                            ðŸ’¡ Brightness: <span id="rgbBrightnessValue">100</span>%
                        </label>
                        <input type="range" id="rgbBrightness" min="0" max="100" value="100" 
                               style="width: 100%; height: 8px; border-radius: 5px; background: rgba(255,255,255,0.3); cursor: pointer;"
                               oninput="updateRGBBrightness(this.value)">
                        <small style="color: rgba(255,255,255,0.8); display: block; margin-top: 5px;">Adjust RGB LED brightness</small>
                    </div>
                    
                    <!-- RGB Color Picker -->
                    <div>
                        <label style="display: block; margin-bottom: 10px; font-weight: bold; font-size: 16px;">ðŸŽ¨ Color</label>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <input type="color" id="rgbColorPicker" value="#FFD700" 
                                   style="width: 80px; height: 50px; border: 3px solid white; border-radius: 5px; cursor: pointer;"
                                   onchange="updateRGBColorPicker(this.value)">
                            <div style="flex: 1;">
                                <div id="rgbColorHex" style="font-family: monospace; font-size: 18px; font-weight: bold;">#FFD700</div>
                                <div id="rgbColorRGB" style="font-size: 12px; opacity: 0.8; margin-top: 5px;">RGB(255, 215, 0)</div>
                            </div>
                        </div>
                        <small style="color: rgba(255,255,255,0.8); display: block; margin-top: 5px;">Click to choose RGB color</small>
                    </div>
                    
                    <!-- RGB Mode -->
                    <div>
                        <label style="display: block; margin-bottom: 10px; font-weight: bold; font-size: 16px;">âœ¨ Mode</label>
                        <select id="rgbMode" style="width: 100%; padding: 12px; border-radius: 5px; border: none; background: white; color: #333; font-size: 14px; font-weight: bold; cursor: pointer;"
                                onchange="updateRGBMode(this.value)">
                            <option value="static">ðŸ”´ Static (Solid Color)</option>
                            <option value="breathing">ðŸ’¨ Breathing (Fade In/Out)</option>
                            <option value="rainbow">ðŸŒˆ Rainbow (Cycle Colors)</option>
                            <option value="reactive">ðŸŽµ Reactive (Audio Sync)</option>
                        </select>
                        <small style="color: rgba(255,255,255,0.8); display: block; margin-top: 5px;">Select lighting effect</small>
                    </div>
                </div>
                
                <!-- RGB Status Display -->
                <div style="margin-top: 25px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 5px; text-align: center;">
                    <div style="display: inline-block; padding: 8px 20px; background: rgba(255,255,255,0.2); border-radius: 20px; font-weight: bold; margin-bottom: 10px;">
                        RGB Status: <span id="rgbStatus">ENABLED</span>
                    </div>
                    <br>
                    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 10px;">
                        <button onclick="applyRGBSettings()" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                            âœ“ Apply RGB Settings
                        </button>
                        <button onclick="toggleRGBLighting()" id="rgbPowerBtn" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                            ðŸ”˜ Toggle ON/OFF
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Hardware Controls</h2>
            <div class="controls">
                <div class="control-group">
                    <label>ðŸ”§ Fan Speed: <span id="fanSpeedValue">50</span>%</label>
                    <input type="range" id="fanSpeed" min="0" max="100" value="50" oninput="updateFanSpeed(this.value)">
                    <small style="color: #666; margin-top: 5px; display: block;">Drag to adjust system fan speed</small>
                </div>
                <div class="control-group">
                    <label>ðŸŒˆ RGB Color</label>
                    <input type="color" id="rgbColor" value="#FFD700" onchange="updateRGBColor(this.value)">
                    <small style="color: #666; margin-top: 5px; display: block;">Click to select color</small>
                </div>
                <div class="control-group">
                    <label>ðŸ’¡ RGB Lighting</label>
                    <button id="rgbToggleBtn" onclick="toggleRGB()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        Toggle RGB
                    </button>
                    <small style="color: #666; margin-top: 5px; display: block;">Click to enable/disable RGB</small>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>âš–ï¸ GPU Load Balancer</h2>
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
                    <input type="text" id="chatMessage" 
                           style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;"
                           onkeypress="if(event.key === 'Enter') sendChatMessage()">
                    <button id="chatMicBtn" onclick="toggleChatMic()" style="width: auto; padding: 10px 16px; background: #4caf50;">Mic</button>
                    <button onclick="sendChatMessage()" style="width: auto; padding: 10px 20px; background: #667eea;">Send</button>
                </div>
                <div id="chatMicStatus" style="margin-top: 6px; color: #666; font-size: 12px;">Mic idle</div>
            </div>
            <div style="margin-bottom: 15px; background: #f5f5f5; border: 1px solid #ddd; border-radius: 6px; padding: 10px;">
                <label style="display: block; margin-bottom: 6px; font-weight: bold;">Route to Omega Agent Framework</label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="agentRouteInput"
                           style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 5px; font-size: 13px;">
                    <button onclick="routeToAgentFramework()" style="width: auto; padding: 8px 16px; background: #3f51b5;">Route</button>
                </div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                        <label style="font-weight: bold;">Select Agents (group conversation)</label>
                        <div>
                            <button onclick="selectAllAgents(true)" style="width: auto; padding: 4px 8px; font-size: 11px; background: #5c6bc0;">All</button>
                            <button onclick="selectAllAgents(false)" style="width: auto; padding: 4px 8px; font-size: 11px; background: #9e9e9e; margin-left: 4px;">None</button>
                        </div>
                    </div>
                    <div id="agentSelectionBox" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 6px; background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 8px;">
                        <div style="color: #777; font-size: 12px;">Loading agents...</div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <label style="display: block; margin-bottom: 6px; font-weight: bold;">External AI Systems (optional)</label>
                    <textarea id="externalAiTargets" rows="3"
                              placeholder='[{"name":"My Local LLM","url":"http://localhost:8000/chat","api_key":""}]'
                              style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px; font-size: 12px; font-family: Consolas, monospace; resize: vertical;"></textarea>
                    <div style="font-size: 11px; color: #666; margin-top: 4px;">JSON array format: name, url, api_key.</div>
                </div>
            </div>
            <div style="margin-bottom: 15px;">
                <div id="chatHistory" style="min-height: 400px; max-height: 600px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9;">
                    <p style="color: #666; font-style: italic; text-align: center;">AI Council ready. Ask a question to see all responses side-by-side.</p>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">ðŸ”„ Refresh</button>
        </div>
        
        <!-- Mobile Tab Content -->
        <div id="tabContentMobile" class="tab-content" style="display: none;">
            <div class="section">
                <h2>ðŸ“± Mobile Access</h2>
                <p style="color: #aaa; margin-bottom: 20px;">Access Omega Control Panel on your mobile device</p>
                <div style="text-align: center;">
                    <a href="/mobile" style="display: inline-block; padding: 15px 30px; background: #ff0000; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; box-shadow: 0 0 20px rgba(255,0,0,0.3);">
                        ðŸ“± Open Mobile Interface
                    </a>
                </div>
            </div>
        </div>
        
        <!-- QR Code Tab Content -->
        <div id="tabContentQR" class="tab-content" style="display: none;">
            <div class="section">
                <h2>ðŸ“· QR Code Access</h2>
                <p style="color: #aaa; margin-bottom: 20px;">Scan to access on your phone</p>
                <div style="text-align: center; padding: 40px;">
                    <div id="qrcode" style="display: inline-block; padding: 20px; background: white; border-radius: 15px;">
                        <!-- QR Code will be generated here -->
                    </div>
                    <p style="margin-top: 20px; font-size: 18px; font-weight: bold; color: #ff4444;" id="qrURL">http://localhost:5000/mobile</p>
                    <p style="margin-top: 10px; color: #aaa;">Scan with your phone camera</p>
                </div>
            </div>
        </div>

        <div id="tabContentAudio" class="tab-content" style="display: none;">
            <div class="section">
                <h2>Media Lab</h2>
                <p style="color: #aaa; margin-bottom: 12px;">Audio + image creation/editing with AI-assisted suggestions.</p>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
                    <input id="mediaIdeaInput" type="text" placeholder="Describe what you want to create..." style="flex:1; min-width:260px; padding:8px; border:1px solid #ddd; border-radius:5px;">
                    <button onclick="askCreativeAgent()" style="width:auto; padding:8px 14px; background:#37474f;">Ask Creative Agent</button>
                </div>
                <div id="mediaAgentOutput" style="font-size:12px; color:#666; margin-bottom:10px;">Creative suggestions will appear here.</div>
                <hr style="border:none; border-top:1px solid #ddd; margin:14px 0;">
                <h3 style="margin-top:0;">Audio Tools</h3>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                    <button onclick="loadAudioLab()" style="width: auto; padding: 8px 14px; background: #2e7d32;">Refresh Audio</button>
                    <button onclick="copySelectedAudio()" style="width: auto; padding: 8px 14px; background: #1565c0;">Copy Selected</button>
                    <button onclick="reverseSelectedAudio()" style="width: auto; padding: 8px 14px; background: #6a1b9a;">Create Reverse FX</button>
                </div>
                <div id="audioLabStatus" style="font-size: 12px; color: #666; margin-bottom: 8px;">Select an audio file from the list.</div>
                <div id="audioLabList" style="max-height: 500px; overflow-y: auto; border: 1px solid #ddd; border-radius: 6px; padding: 10px; background: #fafafa;">
                    <p style="color: #666; font-style: italic;">Loading audio files...</p>
                </div>
                <hr style="border:none; border-top:1px solid #ddd; margin:14px 0;">
                <h3>Image Tools</h3>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
                    <input id="imagePromptInput" type="text" placeholder="Image prompt..." style="flex:1; min-width:280px; padding:8px; border:1px solid #ddd; border-radius:5px;">
                    <button onclick="createImageFromPrompt()" style="width:auto; padding:8px 14px; background:#8e24aa;">Create Image</button>
                    <button onclick="loadImageLab()" style="width:auto; padding:8px 14px; background:#2e7d32;">Refresh Images</button>
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px;">
                    <button onclick="editSelectedImage('grayscale')" style="width:auto; padding:8px 12px; background:#546e7a;">Grayscale</button>
                    <button onclick="editSelectedImage('mirror')" style="width:auto; padding:8px 12px; background:#546e7a;">Mirror</button>
                    <button onclick="editSelectedImage('rotate90')" style="width:auto; padding:8px 12px; background:#546e7a;">Rotate 90</button>
                    <button onclick="editSelectedImage('contrast_plus')" style="width:auto; padding:8px 12px; background:#546e7a;">Boost Contrast</button>
                </div>
                <div id="imageLabStatus" style="font-size:12px; color:#666; margin-bottom:8px;">Select an image file from the list.</div>
                <div id="imageLabList" style="max-height: 420px; overflow-y: auto; border: 1px solid #ddd; border-radius: 6px; padding: 10px; background: #fafafa;">
                    <p style="color: #666; font-style: italic;">Loading image files...</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab Switching
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.style.color = '#aaa';
                btn.style.borderBottomColor = 'transparent';
            });
            
            // Show selected tab
            const contentId = 'tabContent' + tabName.charAt(0).toUpperCase() + tabName.slice(1);
            const tabContent = document.getElementById(contentId);
            const tabBtn = document.getElementById('tab' + tabName.charAt(0).toUpperCase() + tabName.slice(1));
            
            if (tabContent) {
                tabContent.style.display = 'block';
                tabContent.classList.add('active');
            }
            if (tabBtn) {
                tabBtn.classList.add('active');
                tabBtn.style.color = '#ff0000';
                tabBtn.style.borderBottomColor = '#ff0000';
            }
            
            // Generate QR code if switching to QR tab
            if (tabName === 'qr') {
                generateQRCode();
            }
        }
        
        // Voice status updates (KITT/Spectrum animations saved for later)
        function updateVoiceStatus(isActive) {
            const indicator = document.getElementById('statusIndicator');
            const title = document.getElementById('statusTitle');
            const subtitle = document.getElementById('statusSubtitle');
            
            if (isActive) {
                indicator.classList.add('active');
                title.textContent = 'OMEGA SPEAKING';
                subtitle.textContent = 'Voice system active...';
            } else {
                indicator.classList.remove('active');
                title.textContent = 'OMEGA READY';
                subtitle.textContent = 'Click button to activate';
            }
        }
        
        // QR Code Generation
        function generateQRCode() {
            const qrContainer = document.getElementById('qrcode');
            if (!qrContainer) return;
            
            // Clear existing QR code
            qrContainer.innerHTML = '';
            
            // Get current URL for mobile interface
            const hostname = window.location.hostname;
            const port = window.location.port;
            const mobileURL = `http://${hostname}:${port}/mobile`;
            
            // Update URL display
            const urlDisplay = document.getElementById('qrURL');
            if (urlDisplay) {
                urlDisplay.textContent = mobileURL;
            }
            
            // Generate QR code
            new QRCode(qrContainer, {
                text: mobileURL,
                width: 256,
                height: 256,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            setInterval(refreshData, 2000); // Faster refresh - 2 seconds
            
            // Start enhanced hardware monitoring
            loadEnhancedHardwareData();
            setInterval(loadEnhancedHardwareData, 3000); // Update every 3 seconds
        });
        
        function refreshData() {
            // Refresh all data
            loadStats();
            loadNotifications();
            loadIntegratedSystems();
            loadDesktopApps();
            loadPdfActions();
        }
        
        async function loadEnhancedHardwareData() {
            try {
                const response = await fetch('/api/hardware/enhanced');
                const data = await response.json();
                
                if (data.error) {
                    // LibreHardwareMonitor not available
                    document.getElementById('libreHwStatus').innerHTML = `<span style="color: #f44336;">âœ— Not Available</span>`;
                    document.getElementById('mbStatus').textContent = 'Not Available';
                    return;
                }
                
                // Update CPU Monitor
                const cpu = data.cpu;
                document.getElementById('cpuTemp').textContent = cpu.temperature !== null ? cpu.temperature.toFixed(1) : 'N/A';
                document.getElementById('cpuPackageTemp').textContent = cpu.package_temp !== null ? cpu.package_temp.toFixed(1) : 'N/A';
                
                if (cpu.core_temps && cpu.core_temps.length > 0) {
                    const coreTemps = cpu.core_temps.map((t, i) => `Core ${i}: ${t.toFixed(1)}Â°C`).join(', ');
                    document.getElementById('cpuCoreTemps').textContent = coreTemps;
                } else {
                    document.getElementById('cpuCoreTemps').textContent = 'N/A';
                }
                
                document.getElementById('cpuClock').textContent = cpu.current_clock > 0 ? cpu.current_clock.toFixed(0) : 'N/A';
                document.getElementById('cpuPower').textContent = cpu.power_draw !== null ? cpu.power_draw.toFixed(1) : 'N/A';
                document.getElementById('cpuUsageDetailed').textContent = cpu.usage.toFixed(1);
                
                // Update GPU Monitor
                const gpu = data.gpu;
                document.getElementById('gpuNameDetailed').textContent = gpu.name;
                document.getElementById('gpuTempDetailed').textContent = gpu.temperature !== null ? gpu.temperature.toFixed(1) : 'N/A';
                document.getElementById('gpuHotSpot').textContent = gpu.hot_spot_temp !== null ? gpu.hot_spot_temp.toFixed(1) : 'N/A';
                document.getElementById('gpuMemoryTemp').textContent = gpu.memory_temp !== null ? gpu.memory_temp.toFixed(1) : 'N/A';
                document.getElementById('gpuUsageDetailed').textContent = gpu.usage !== null ? gpu.usage.toFixed(1) : 'N/A';
                document.getElementById('gpuMemoryDetailed').textContent = 
                    `${gpu.memory_used.toFixed(2)} GB / ${gpu.memory_total.toFixed(2)} GB`;
                
                if (gpu.power_draw !== null && gpu.power_limit !== null) {
                    document.getElementById('gpuPowerDetailed').textContent = 
                        `${gpu.power_draw.toFixed(1)}W / ${gpu.power_limit.toFixed(0)}W`;
                } else {
                    document.getElementById('gpuPowerDetailed').textContent = 'N/A';
                }
                
                document.getElementById('gpuFanDetailed').textContent = gpu.fan_speed !== null ? gpu.fan_speed.toFixed(0) : 'N/A';
                document.getElementById('gpuClocksDetailed').textContent = 
                    `${gpu.core_clock || 'N/A'}MHz / ${gpu.memory_clock || 'N/A'}MHz`;
                
                // Update Motherboard Monitor
                const mb = data.motherboard;
                document.getElementById('mbName').textContent = mb.name;
                document.getElementById('mbChipsetTemp').textContent = mb.chipset_temp !== null ? mb.chipset_temp.toFixed(1) : 'N/A';
                document.getElementById('mbVrmTemp').textContent = mb.vrm_temp !== null ? mb.vrm_temp.toFixed(1) : 'N/A';
                
                if (mb.system_fans && Object.keys(mb.system_fans).length > 0) {
                    const fans = Object.entries(mb.system_fans).map(([name, rpm]) => 
                        `${name}: ${rpm.toFixed(0)} RPM`
                    ).join('<br>');
                    document.getElementById('mbFans').innerHTML = fans;
                    document.getElementById('mbStatus').innerHTML = '<span style="color: #4caf50;">âœ“ All sensors active</span>';
                } else {
                    document.getElementById('mbFans').textContent = 'No fan data';
                    document.getElementById('mbStatus').innerHTML = '<span style="color: #ff9800;">âš  Limited data</span>';
                }
                
                // Update Memory Monitor
                const mem = data.memory;
                document.getElementById('memUsage').textContent = 
                    `${mem.used_gb.toFixed(1)} GB / ${mem.total_gb.toFixed(1)} GB (${mem.usage_percent.toFixed(1)}%)`;
                document.getElementById('memTemp').textContent = mem.temperature !== null ? mem.temperature.toFixed(1) : 'N/A';
                document.getElementById('memSpeed').textContent = mem.speed_mhz !== null ? mem.speed_mhz : 'N/A';
                
                // Update Storage Monitor
                const storage = data.storage;
                if (storage && storage.length > 0) {
                    const storageHTML = storage.map(s => `
                        <div style="margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                            <strong>${s.name}</strong> (${s.type})<br>
                            Temp: ${s.temperature !== null ? s.temperature.toFixed(1) + 'Â°C' : 'N/A'}<br>
                            ${s.health !== null ? 'Health: ' + s.health + '%' : ''}
                        </div>
                    `).join('');
                    document.getElementById('storageDevices').innerHTML = storageHTML;
                } else {
                    document.getElementById('storageDevices').textContent = 'No storage data available';
                }
                
                // Update LibreHardwareMonitor Status
                if (data.libre_hw_available) {
                    document.getElementById('libreHwStatus').innerHTML = '<span style="color: #4caf50;">âœ“ Active</span>';
                } else {
                    document.getElementById('libreHwStatus').innerHTML = '<span style="color: #f44336;">âœ— Not Running</span>';
                }
                
                document.getElementById('hwLastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
                
            } catch (error) {
                console.error('Enhanced hardware monitor error:', error);
                document.getElementById('libreHwStatus').innerHTML = '<span style="color: #f44336;">âœ— Error</span>';
            }
        }
        
        function applyPerformanceSettings() {
            const cpuBoost = document.getElementById('cpuBoostMode').value;
            const gpuPower = document.getElementById('gpuPowerLimit').value;
            const fanProfile = document.getElementById('fanProfile').value;
            
            alert(`Performance settings applied:\n\nCPU Boost: ${cpuBoost}\nGPU Power: ${gpuPower}\nFan Profile: ${fanProfile}\n\nâš ï¸ Note: Some settings require administrator rights and hardware support.`);
            
            // In a real implementation, these would call backend APIs to adjust settings
            // For now, this is a UI demonstration
        }
        
        // RGB Control Functions
        async function updateRGBBrightness(value) {
            document.getElementById('rgbBrightnessValue').textContent = value;
        }
        
        async function updateRGBColorPicker(hexColor) {
            document.getElementById('rgbColorHex').textContent = hexColor.toUpperCase();
            
            // Convert hex to RGB
            const r = parseInt(hexColor.slice(1, 3), 16);
            const g = parseInt(hexColor.slice(3, 5), 16);
            const b = parseInt(hexColor.slice(5, 7), 16);
            document.getElementById('rgbColorRGB').textContent = `RGB(${r}, ${g}, ${b})`;
        }
        
        async function updateRGBMode(mode) {
            console.log('RGB mode changed to:', mode);
        }
        
        async function applyRGBSettings() {
            const brightness = document.getElementById('rgbBrightness').value;
            const color = document.getElementById('rgbColorPicker').value;
            const mode = document.getElementById('rgbMode').value;
            
            try {
                // Set brightness
                await fetch('/api/hardware/rgb', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        action: 'set_brightness',
                        brightness: parseInt(brightness)
                    })
                });
                
                // Set color
                const r = parseInt(color.slice(1, 3), 16);
                const g = parseInt(color.slice(3, 5), 16);
                const b = parseInt(color.slice(5, 7), 16);
                
                await fetch('/api/hardware/rgb', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        action: 'set_color',
                        r: r,
                        g: g,
                        b: b
                    })
                });
                
                // Set mode
                await fetch('/api/hardware/rgb', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        action: 'set_mode',
                        mode: mode
                    })
                });
                
                alert(`âœ“ RGB Settings Applied!\n\nBrightness: ${brightness}%\nColor: ${color}\nMode: ${mode}`);
                
                // Refresh RGB status
                await loadRGBStatus();
                
            } catch (error) {
                console.error('RGB settings error:', error);
                alert('âŒ Failed to apply RGB settings');
            }
        }
        
        async function toggleRGBLighting() {
            try {
                const response = await fetch('/api/hardware/rgb', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'toggle'})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const status = data.enabled ? 'ENABLED' : 'DISABLED';
                    document.getElementById('rgbStatus').textContent = status;
                    
                    const btn = document.getElementById('rgbPowerBtn');
                    if (data.enabled) {
                        btn.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                        btn.innerHTML = 'ðŸ”˜ Toggle ON/OFF';
                    } else {
                        btn.style.background = 'linear-gradient(135deg, #666 0%, #999 100%)';
                        btn.innerHTML = 'âšª Toggle ON/OFF';
                    }
                    
                    alert(`RGB Lighting: ${status}`);
                }
            } catch (error) {
                console.error('RGB toggle error:', error);
                alert('âŒ Failed to toggle RGB');
            }
        }
        
        async function loadRGBStatus() {
            try {
                const response = await fetch('/api/hardware/rgb');
                const data = await response.json();
                
                // Update RGB controls with current values
                document.getElementById('rgbBrightness').value = data.brightness;
                document.getElementById('rgbBrightnessValue').textContent = data.brightness;
                
                document.getElementById('rgbColorPicker').value = data.color_hex;
                document.getElementById('rgbColorHex').textContent = data.color_hex.toUpperCase();
                document.getElementById('rgbColorRGB').textContent = `RGB(${data.color_r}, ${data.color_g}, ${data.color_b})`;
                
                document.getElementById('rgbMode').value = data.mode;
                
                const status = data.enabled ? 'ENABLED' : 'DISABLED';
                document.getElementById('rgbStatus').textContent = status;
                
                const btn = document.getElementById('rgbPowerBtn');
                if (data.enabled) {
                    btn.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                } else {
                    btn.style.background = 'linear-gradient(135deg, #666 0%, #999 100%)';
                }
                
            } catch (error) {
                console.error('Load RGB status error:', error);
            }
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            setInterval(refreshData, 2000); // Faster refresh - 2 seconds
            
            // Load RGB status
            loadRGBStatus();
            setInterval(loadRGBStatus, 5000); // Refresh RGB status every 5 seconds
        });
        
        async function loadStats() {
            try {
                const response = await fetch('/api/system');
                const data = await response.json();
                
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <h3>CPU Usage</h3>
                        <div class="stat-value">${data.cpu_usage ? data.cpu_usage.toFixed(1) : '0.0'}<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>CPU Temperature</h3>
                        <div class="stat-value">${data.cpu_temperature !== undefined ? data.cpu_temperature.toFixed(1) : 'N/A'}<span class="stat-unit">${data.cpu_temperature !== undefined ? 'Â°C' : ''}</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>GPU Temperature</h3>
                        <div class="stat-value">${data.gpu_temperature ? data.gpu_temperature.toFixed(1) : 'N/A'}<span class="stat-unit">${data.gpu_temperature ? 'Â°C' : ''}</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>GPU Usage</h3>
                        <div class="stat-value">${data.gpu_usage ? data.gpu_usage.toFixed(1) : 'N/A'}<span class="stat-unit">${data.gpu_usage ? '%' : ''}</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Memory Usage</h3>
                        <div class="stat-value">${data.memory_usage ? data.memory_usage.toFixed(1) : '0.0'}<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>GPU Memory</h3>
                        <div class="stat-value">${data.gpu_memory_used ? data.gpu_memory_used.toFixed(1) : 'N/A'}<span class="stat-unit">${data.gpu_memory_used ? ' GB' : ''}</span></div>
                    </div>
                `;
                
                // Update fan speed slider and value
                const fanSlider = document.getElementById('fanSpeed');
                const fanValue = document.getElementById('fanSpeedValue');
                if (fanSlider && fanValue) {
                    fanSlider.value = data.fan_speed || 50;
                    fanValue.textContent = data.fan_speed || 50;
                }
                
                // Update RGB color picker
                const rgbColor = document.getElementById('rgbColor');
                if (rgbColor && data.rgb_color) {
                    rgbColor.value = data.rgb_color;
                }
                
                document.getElementById('systemStatus').innerHTML = `
                    <p>Status: Running</p>
                    <p>Fan Speed: ${data.fan_speed || 50}%</p>
                    <p>RGB: ${data.rgb_enabled ? 'Enabled' : 'Disabled'}</p>
                    <p style="display: flex; align-items: center; gap: 10px;">Color: <span style="display: inline-block; width: 20px; height: 20px; background: ${data.rgb_color}; border: 1px solid #ccc; border-radius: 3px;"></span> ${data.rgb_color}</p>
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
                
                // Separate active and inactive systems
                const activeSystems = systems.filter(s => s.status === 'active');
                const inactiveSystems = systems.filter(s => s.status !== 'active');
                
                let html = '';
                
                // Show only active systems prominently
                if (activeSystems.length > 0) {
                    html += '<div style="margin-bottom: 15px;"><strong style="color: #4caf50;">âœ“ Active Systems (' + activeSystems.length + ')</strong></div>';
                    html += activeSystems.map(s => `
                        <div class="system-item" style="background: rgba(76, 175, 80, 0.05); border-left: 3px solid #4caf50;">
                            <strong>${s.name}</strong>
                            <span class="status-badge status-${s.status}">${s.status}</span>
                            <div style="margin-top: 5px; font-size: 12px;">
                                ${s.cpu_usage > 0 ? 'CPU: ' + s.cpu_usage.toFixed(1) + '% | ' : ''}
                                ${s.temperature > 0 ? 'Temp: ' + s.temperature.toFixed(1) + 'Â°C | ' : ''}
                                Power: ${s.processing_power.toFixed(1)}%
                            </div>
                        </div>
                    `).join('');
                } else {
                    html += '<div style="padding: 20px; text-align: center; color: #666;">No active systems detected</div>';
                }
                
                // Hide inactive systems in separate collapsible section
                if (inactiveSystems.length > 0) {
                    html += `
                        <div style="margin-top: 25px; padding-top: 15px; border-top: 1px solid rgba(158, 158, 158, 0.2);">
                            <details style="cursor: pointer;">
                                <summary style="padding: 12px; background: rgba(158, 158, 158, 0.05); border-radius: 8px; user-select: none; border: 1px solid rgba(158, 158, 158, 0.2);">
                                    <strong style="color: #9e9e9e;">âŠ™ Inactive Systems (${inactiveSystems.length})</strong>
                                    <span style="font-size: 11px; color: #999; margin-left: 10px;">â–¼ Click to view</span>
                                </summary>
                                <div style="margin-top: 10px; padding: 10px; background: rgba(0,0,0,0.02); border-radius: 5px;">
                                    ${inactiveSystems.map(s => `
                                        <div class="system-item" style="opacity: 0.5; background: rgba(158, 158, 158, 0.03); border-left: 2px solid #9e9e9e;">
                                            <strong style="font-size: 13px;">${s.name}</strong>
                                            <span class="status-badge status-${s.status}" style="font-size: 10px;">${s.status}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </details>
                        </div>
                    `;
                }
                
                container.innerHTML = html;
            } catch (error) {
                console.error('Error loading integrated systems:', error);
            }
        }

        async function loadDesktopApps() {
            try {
                const response = await fetch('/api/desktop-apps');
                const result = await response.json();
                const apps = result.apps || [];
                const container = document.getElementById('desktopApps');

                if (!container) return;
                if (apps.length === 0) {
                    container.innerHTML = '<p>No desktop app integrations configured.</p>';
                    return;
                }

                container.innerHTML = apps.map(app => {
                    const status = app.installed ? 'Installed' : 'Not Detected';
                    const statusColor = app.installed ? '#4caf50' : '#f44336';
                    const caps = (app.capabilities || []).join(', ');
                    const versions = (app.versions || []).length ? app.versions.join(', ') : 'N/A';
                    const paths = app.detected_paths || [];
                    const versionLaunchUI = paths.length > 1 ? `
                        <div style="margin-top: 6px;">
                            <select id="launchTarget_${app.id}" style="padding: 6px; border: 1px solid #ccc; border-radius: 4px; width: 100%;">
                                ${paths.map(p => `<option value="${p.replace(/"/g, '&quot;')}">${p}</option>`).join('')}
                            </select>
                            <div style="font-size: 11px; color: #888; margin-top: 3px;">Select specific installed version/path to launch</div>
                        </div>
                    ` : '';
                    return `
                        <div class="system-item" style="border-left: 3px solid ${statusColor}; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px;">
                                <strong>${app.name}</strong>
                                <span style="color: ${statusColor}; font-weight: bold;">${status}</span>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 5px;">Vendor: ${app.vendor}</div>
                            <div style="font-size: 12px; color: #444; margin-top: 3px;">Capabilities: ${caps || 'N/A'}</div>
                            <div style="font-size: 12px; color: #444; margin-top: 3px;">Detected Versions: ${versions}</div>
                            ${versionLaunchUI}
                            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                                <button onclick="launchDesktopApp('${app.id}')" style="width:auto; padding: 8px 12px; background:#1976d2;">Launch</button>
                                <button onclick="askOmegaAboutApp('${app.name}', '${caps}')" style="width:auto; padding: 8px 12px; background:#6a1b9a;">Ask Omega</button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (error) {
                console.error('Error loading desktop apps:', error);
                const container = document.getElementById('desktopApps');
                if (container) {
                    container.innerHTML = '<p style="color:#f44336;">Failed to load desktop app integrations.</p>';
                }
            }
        }

        async function launchDesktopApp(appId) {
            try {
                const targetSelect = document.getElementById(`launchTarget_${appId}`);
                const launchTarget = targetSelect ? targetSelect.value : '';
                const response = await fetch('/api/desktop-apps/launch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({app_id: appId, launch_target: launchTarget})
                });
                const result = await response.json();
                if (result.success) {
                    showNotification(`Launched ${result.app}`, 'success');
                } else {
                    showNotification(result.error || 'Launch failed', 'error');
                }
            } catch (error) {
                console.error('Error launching app:', error);
                showNotification('Failed to launch desktop app', 'error');
            }
        }

        function askOmegaAboutApp(appName, capabilities) {
            const messageInput = document.getElementById('chatMessage');
            if (!messageInput) return;
            messageInput.value = `Help me use ${appName}. I need: ${capabilities}. Prioritize PDF fill/sign/edit steps and compatibility with older versions when relevant.`;
            sendChatMessage();
        }

        async function loadPdfActions() {
            try {
                const response = await fetch('/api/pdf-actions/list?limit=20');
                const result = await response.json();
                const pdfs = result.pdfs || [];
                const container = document.getElementById('pdfActionsList');
                if (!container) return;

                if (pdfs.length === 0) {
                    container.innerHTML = '<p>No recent PDFs found in Documents/Downloads/Desktop.</p>';
                    return;
                }

                container.innerHTML = pdfs.map(pdf => {
                    const fill = pdf.likely_fillable ? 'Likely fillable' : 'Unknown fillable';
                    const sign = pdf.likely_signable ? 'Likely signable' : 'Unknown signable';
                    return `
                        <div class="system-item" style="border-left: 3px solid #ff9800; margin-bottom: 10px;">
                            <div style="display:flex; justify-content:space-between; gap:10px; align-items:center;">
                                <strong>${pdf.name}</strong>
                                <span style="font-size:11px; color:#666;">${new Date(pdf.modified).toLocaleString()}</span>
                            </div>
                            <div style="font-size:12px; color:#666; margin-top:3px;">${pdf.folder}</div>
                            <div style="font-size:12px; color:#444; margin-top:3px;">${fill} | ${sign}</div>
                            <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
                                <button onclick="openPdfWithApp('${encodeURIComponent(pdf.path)}', 'adobe_acrobat')" style="width:auto; padding:8px 12px; background:#1565c0;">Open in Acrobat</button>
                                <button onclick="openPdfWithApp('${encodeURIComponent(pdf.path)}', 'adobe_reader')" style="width:auto; padding:8px 12px; background:#00838f;">Open in Reader</button>
                                <button onclick="openPdfWithApp('${encodeURIComponent(pdf.path)}', '')" style="width:auto; padding:8px 12px; background:#546e7a;">Open Default</button>
                                <button onclick="askOmegaForPdf('${pdf.name}')" style="width:auto; padding:8px 12px; background:#6a1b9a;">Ask Omega</button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (error) {
                console.error('Error loading PDF actions:', error);
                const container = document.getElementById('pdfActionsList');
                if (container) {
                    container.innerHTML = '<p style="color:#f44336;">Failed to load PDF actions.</p>';
                }
            }
        }

        async function openPdfWithApp(encodedPath, appId) {
            try {
                const response = await fetch('/api/pdf-actions/open', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        file_path: encodedPath,
                        app_id: appId || ''
                    })
                });
                const result = await response.json();
                if (result.success) {
                    showNotification(`Opened PDF: ${result.file}`, 'success');
                } else {
                    showNotification(result.error || 'Failed to open PDF', 'error');
                }
            } catch (error) {
                console.error('Error opening PDF:', error);
                showNotification('Failed to open PDF', 'error');
            }
        }

        function askOmegaForPdf(pdfName) {
            const messageInput = document.getElementById('chatMessage');
            if (!messageInput) return;
            messageInput.value = `Guide me step-by-step to fill, sign, or edit "${pdfName}" using Adobe tools. Include fallback steps for older Adobe versions.`;
            sendChatMessage();
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
                    <div class="stat-value">${data.cpu_temperature.toFixed(1)}<span class="stat-unit">Â°C</span></div>
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
                        Temp: ${s.temperature.toFixed(1)}Â°C | 
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
                    console.log(`âœ“ Fan speed set to ${value}%`);
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
                    console.log(`âœ“ RGB color set to ${color}`);
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
                    console.log(`âœ“ RGB lighting ${statusText}`);
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

        let selectedAudioPath = '';
        let selectedImagePath = '';
        async function loadAudioLab() {
            const listEl = document.getElementById('audioLabList');
            const statusEl = document.getElementById('audioLabStatus');
            if (!listEl) return;
            try {
                const response = await fetch('/api/audio/list?limit=60');
                const result = await response.json();
                const files = (result && result.files) || [];
                if (!files.length) {
                    listEl.innerHTML = '<p style="color:#666; font-style:italic;">No audio files found in Desktop/Documents/Downloads/project.</p>';
                    statusEl.textContent = 'No files found';
                    return;
                }
                listEl.innerHTML = files.map(file => `
                    <label style="display:block; padding:8px; border-bottom:1px solid #eee; cursor:pointer;">
                        <input type="radio" name="audioPick" value="${escapeHtml(file.path)}" onchange="selectedAudioPath=this.value">
                        <strong>${escapeHtml(file.name)}</strong>
                        <span style="color:#666; font-size:11px; margin-left:6px;">${escapeHtml(file.folder)}</span>
                    </label>
                `).join('');
                statusEl.textContent = `${files.length} audio files loaded`;
            } catch (error) {
                listEl.innerHTML = '<p style="color:#f44336;">Failed to load audio files.</p>';
                statusEl.textContent = 'Load error';
            }
        }

        async function askCreativeAgent() {
            const input = document.getElementById('mediaIdeaInput');
            const out = document.getElementById('mediaAgentOutput');
            const idea = (input && input.value || '').trim();
            if (!idea) {
                out.textContent = 'Enter a media idea first.';
                return;
            }
            try {
                const response = await fetch('/api/agents/group-message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        request: idea,
                        agents: ['creative_agent'],
                        payload: {type: 'media_assist'}
                    })
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    out.textContent = `Creative agent failed: ${result.error || response.statusText}`;
                    return;
                }
                const first = (result.results || [])[0];
                const text = first && first.response_text ? first.response_text : JSON.stringify(result, null, 2);
                out.textContent = text;
            } catch (error) {
                out.textContent = `Creative agent error: ${error.message}`;
            }
        }

        async function copySelectedAudio() {
            const statusEl = document.getElementById('audioLabStatus');
            if (!selectedAudioPath) {
                statusEl.textContent = 'Choose an audio file first.';
                return;
            }
            try {
                const response = await fetch('/api/audio/copy', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({source_path: selectedAudioPath, suffix: '_copy'})
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    statusEl.textContent = `Copy failed: ${result.error || response.statusText}`;
                    return;
                }
                statusEl.textContent = `Copied: ${result.target}`;
                loadAudioLab();
            } catch (error) {
                statusEl.textContent = `Copy error: ${error.message}`;
            }
        }

        async function reverseSelectedAudio() {
            const statusEl = document.getElementById('audioLabStatus');
            if (!selectedAudioPath) {
                statusEl.textContent = 'Choose an audio file first.';
                return;
            }
            try {
                const response = await fetch('/api/audio/effect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({source_path: selectedAudioPath, effect: 'reverse'})
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    statusEl.textContent = `Effect failed: ${result.error || response.statusText}`;
                    return;
                }
                statusEl.textContent = `Created FX: ${result.target}`;
                loadAudioLab();
            } catch (error) {
                statusEl.textContent = `Effect error: ${error.message}`;
            }
        }

        async function loadImageLab() {
            const listEl = document.getElementById('imageLabList');
            const statusEl = document.getElementById('imageLabStatus');
            if (!listEl) return;
            try {
                const response = await fetch('/api/images/list?limit=60');
                const result = await response.json();
                const files = (result && result.files) || [];
                if (!files.length) {
                    listEl.innerHTML = '<p style="color:#666; font-style:italic;">No image files found in Desktop/Documents/Downloads/project.</p>';
                    statusEl.textContent = 'No files found';
                    return;
                }
                listEl.innerHTML = files.map(file => `
                    <label style="display:block; padding:8px; border-bottom:1px solid #eee; cursor:pointer;">
                        <input type="radio" name="imagePick" value="${escapeHtml(file.path)}" onchange="selectedImagePath=this.value">
                        <strong>${escapeHtml(file.name)}</strong>
                        <span style="color:#666; font-size:11px; margin-left:6px;">${escapeHtml(file.folder)}</span>
                    </label>
                `).join('');
                statusEl.textContent = `${files.length} image files loaded`;
            } catch (error) {
                listEl.innerHTML = '<p style="color:#f44336;">Failed to load image files.</p>';
                statusEl.textContent = 'Load error';
            }
        }

        async function createImageFromPrompt() {
            const promptInput = document.getElementById('imagePromptInput');
            const statusEl = document.getElementById('imageLabStatus');
            const prompt = (promptInput && promptInput.value || '').trim();
            if (!prompt) {
                statusEl.textContent = 'Enter an image prompt first.';
                return;
            }
            try {
                const response = await fetch('/api/images/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt, width: 1024, height: 1024})
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    statusEl.textContent = `Create failed: ${result.error || response.statusText}`;
                    return;
                }
                statusEl.textContent = `Created image: ${result.path}`;
                loadImageLab();
            } catch (error) {
                statusEl.textContent = `Create error: ${error.message}`;
            }
        }

        async function editSelectedImage(operation) {
            const statusEl = document.getElementById('imageLabStatus');
            if (!selectedImagePath) {
                statusEl.textContent = 'Choose an image file first.';
                return;
            }
            try {
                const response = await fetch('/api/images/edit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({source_path: selectedImagePath, operation: operation})
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    statusEl.textContent = `Edit failed: ${result.error || response.statusText}`;
                    return;
                }
                statusEl.textContent = `Created edited image: ${result.target}`;
                loadImageLab();
            } catch (error) {
                statusEl.textContent = `Edit error: ${error.message}`;
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
            
            // Clear existing hint text if present
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
                    displayCouncilResponses(result.results, result.suggestions || []);
                } else {
                    addErrorMessage('Error: ' + (result.error || 'Failed to send message'));
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addErrorMessage('Error: ' + error.message);
            }
        }

        let recognition = null;
        let micActive = false;
        function toggleChatMic() {
            const btn = document.getElementById('chatMicBtn');
            const status = document.getElementById('chatMicStatus');
            const input = document.getElementById('chatMessage');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                status.textContent = 'Mic unavailable in this browser';
                return;
            }

            if (!recognition) {
                recognition = new SpeechRecognition();
                recognition.lang = 'en-US';
                recognition.interimResults = true;
                recognition.continuous = false;
                recognition.onresult = (event) => {
                    let transcript = '';
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        transcript += event.results[i][0].transcript;
                    }
                    input.value = transcript.trim();
                };
                recognition.onerror = (event) => {
                    status.textContent = `Mic error: ${event.error}`;
                    micActive = false;
                    btn.style.background = '#4caf50';
                };
                recognition.onend = () => {
                    micActive = false;
                    btn.style.background = '#4caf50';
                    status.textContent = 'Mic idle';
                };
            }

            if (micActive) {
                recognition.stop();
                micActive = false;
                btn.style.background = '#4caf50';
                status.textContent = 'Mic idle';
                return;
            }

            recognition.start();
            micActive = true;
            btn.style.background = '#f44336';
            status.textContent = 'Listening...';
        }

        async function routeToAgentFramework() {
            const input = document.getElementById('agentRouteInput');
            const requestText = (input.value || '').trim();
            if (!requestText) {
                addErrorMessage('Agent routing request cannot be empty');
                return;
            }
            addUserQuestion(`[ROUTED] ${requestText}`);
            input.value = '';
            const selectedAgents = getSelectedAgents();
            const externalTargets = parseExternalAiTargets();
            try {
                const response = await fetch('/api/agents/group-message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        request: requestText,
                        agents: selectedAgents,
                        external_targets: externalTargets,
                        payload: {type: 'compose_message'}
                    })
                });
                const result = await response.json();
                if (!response.ok || result.error) {
                    addErrorMessage('Agent routing failed: ' + (result.error || response.statusText));
                    return;
                }
                const agentResults = Array.isArray(result.results) ? result.results : [];
                if (agentResults.length === 0) {
                    addChatMessage('assistant', 'No agent responses returned.', 'agent-framework');
                }
                for (const entry of agentResults) {
                    if (entry.success) {
                        addChatMessage('assistant', entry.response_text || 'Completed.', entry.agent_name || entry.agent_id || 'agent');
                    } else {
                        addErrorMessage(`${entry.agent_id || 'agent'}: ${entry.error || 'Unknown error'}`);
                    }
                }
                const externalResults = Array.isArray(result.external_results) ? result.external_results : [];
                for (const ext of externalResults) {
                    if (ext.success) {
                        addChatMessage('assistant', ext.response || 'External AI completed.', ext.target || 'external-ai');
                    } else {
                        addErrorMessage(`${ext.target || ext.url || 'external-ai'}: ${ext.error || 'External request failed'}`);
                    }
                }
                if (Array.isArray(result.suggestions) && result.suggestions.length > 0) {
                    addSuggestionPanel(result.suggestions, 'Next options');
                }
            } catch (error) {
                addErrorMessage('Agent routing error: ' + error.message);
            }
        }

        async function loadAgentRoster() {
            const box = document.getElementById('agentSelectionBox');
            if (!box) return;
            try {
                const response = await fetch('/api/agents/status');
                const payload = await response.json();
                const agents = (((payload || {}).status || {}).agents || []).filter(a => a.active !== false);
                if (agents.length === 0) {
                    box.innerHTML = '<div style="color: #777; font-size: 12px;">No active agents found.</div>';
                    return;
                }
                box.innerHTML = agents.map(agent => `
                    <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: #333;">
                        <input type="checkbox" class="agent-check" value="${escapeHtml(agent.agent_id)}" checked>
                        <span><strong>${escapeHtml(agent.name || agent.agent_id)}</strong> (${escapeHtml(agent.agent_id)})</span>
                    </label>
                `).join('');
            } catch (error) {
                box.innerHTML = '<div style="color: #f44336; font-size: 12px;">Unable to load agents.</div>';
            }
        }

        function getSelectedAgents() {
            return Array.from(document.querySelectorAll('.agent-check:checked')).map(el => el.value);
        }

        function selectAllAgents(enabled) {
            document.querySelectorAll('.agent-check').forEach(el => {
                el.checked = !!enabled;
            });
        }

        function parseExternalAiTargets() {
            const input = document.getElementById('externalAiTargets');
            if (!input) return [];
            const raw = (input.value || '').trim();
            if (!raw) return [];
            try {
                const parsed = JSON.parse(raw);
                if (!Array.isArray(parsed)) throw new Error('Must be an array');
                return parsed
                    .filter(item => item && typeof item === 'object' && item.url)
                    .map(item => ({
                        name: String(item.name || '').trim(),
                        url: String(item.url || '').trim(),
                        api_key: String(item.api_key || '').trim()
                    }));
            } catch (error) {
                addErrorMessage('Invalid External AI JSON. Use [{"name":"X","url":"http://...","api_key":""}]');
                return [];
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
        
        function displayCouncilResponses(results, suggestions = []) {
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
            if (Array.isArray(suggestions) && suggestions.length > 0) {
                addSuggestionPanel(suggestions, 'Suggested next steps');
            }
            historyEl.scrollTop = historyEl.scrollHeight;
        }

        function addSuggestionPanel(items, title = 'Suggestions') {
            const historyEl = document.getElementById('chatHistory');
            const panel = document.createElement('div');
            panel.style.cssText = 'margin-bottom: 20px; padding: 12px; border-radius: 8px; background: #f8f9ff; border: 1px solid #d7dcff;';
            const safeItems = items.slice(0, 3).map(item => `<li style="margin: 6px 0;">${escapeHtml(item)}</li>`).join('');
            panel.innerHTML = `
                <div style="font-weight: bold; color: #3f51b5; margin-bottom: 8px;">${escapeHtml(title)}</div>
                <ul style="margin: 0; padding-left: 18px; color: #2d2d2d; font-size: 13px;">${safeItems}</ul>
            `;
            historyEl.appendChild(panel);
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
                const gpuStatus = data.gpu_available ? 'âœ“ Available' : 'âœ— Not Available';
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
                            <div style="font-weight: bold; color: #333; font-size: 13px; margin-bottom: 3px;">ðŸ’¡ Recommendation ${idx + 1}</div>
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
            loadDesktopApps();
            loadPdfActions();
            loadLoadBalancerData();
            
            // Load chatbot data
            loadChatbotStatus();
            loadChatHistory();
            loadAgentRoster();
            loadAudioLab();
            loadImageLab();
            
            // Set up auto-refresh every 2 seconds for faster updates
            setInterval(() => {
                loadStats();
                loadNotifications();
                loadIntegratedSystems();
                loadDesktopApps();
                loadLoadBalancerData();
            }, 2000);  // Faster refresh - 2 seconds instead of 5

            setInterval(() => {
                loadAgentRoster();
            }, 10000);

            // PDF scan is heavier; refresh less frequently
            setInterval(() => {
                loadPdfActions();
            }, 60000);
        });
        
        // Voice control function
        function activateOmegaVoice() {
            // Activate voice status
            updateVoiceStatus(true);
            
            fetch('/api/voice/speak', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: 'System status', type: 'status'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Omega voice activated', 'success');
                } else {
                    showNotification('Voice activation failed', 'error');
                    updateVoiceStatus(false);
                }
                // Return to idle after ~12 seconds
                setTimeout(() => {
                    updateVoiceStatus(false);
                }, 12000);
            })
            .catch(error => {
                console.error('Voice error:', error);
                showNotification('Voice system error', 'error');
            });
        }
    </script>
</body>
</html>'''
    
    def initialize_control_panel(self):
        """Initialize ControlPanel instance"""
        with self.control_panel_lock:
            if not self.control_panel:
                self.control_panel = ControlPanel(use_gradual_loading=False)
                self.control_panel.running = True
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
        self.initialize_control_panel()
        
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

