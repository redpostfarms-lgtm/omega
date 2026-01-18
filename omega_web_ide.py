#!/usr/bin/env python3
"""
Omega Web IDE
=============
Browser-based development environment
Voice chat + Code editor + File tree + LLM integration
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory
from pathlib import Path
import json
import subprocess
import sys
from typing import Dict, List, Any, Optional
import threading


app = Flask(__name__)
app.secret_key = "omega-web-ide-secret-key-change-in-production"

# Global state
current_directory = Path(".").resolve()
llm_available = False


# HTML Template for Web IDE
IDE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Omega Web IDE</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #2d2d30;
            padding: 10px 20px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            color: #4ec9b0;
            font-size: 20px;
        }

        .status {
            display: flex;
            gap: 15px;
            font-size: 12px;
        }

        .status-item {
            padding: 4px 12px;
            background: #3e3e42;
            border-radius: 4px;
        }

        .status-item.active {
            background: #0e639c;
        }

        .main-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        .sidebar {
            width: 250px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            padding: 10px;
            background: #2d2d30;
            font-size: 11px;
            text-transform: uppercase;
            color: #cccccc;
        }

        .file-tree {
            flex: 1;
            overflow-y: auto;
            padding: 5px;
        }

        .file-item {
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 3px;
            font-size: 13px;
        }

        .file-item:hover {
            background: #2a2d2e;
        }

        .file-item.folder {
            font-weight: bold;
        }

        .editor-container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .tabs {
            background: #2d2d30;
            display: flex;
            gap: 2px;
            padding: 5px;
            border-bottom: 1px solid #3e3e42;
        }

        .tab {
            padding: 5px 15px;
            background: #3e3e42;
            cursor: pointer;
            border-radius: 3px 3px 0 0;
            font-size: 13px;
        }

        .tab.active {
            background: #1e1e1e;
        }

        .editor {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }

        #code-editor {
            width: 100%;
            height: 100%;
            min-height: 400px;
            background: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
            padding: 15px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
        }

        .chat-panel {
            width: 350px;
            background: #252526;
            border-left: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 10px;
            background: #2d2d30;
            font-size: 14px;
            font-weight: bold;
        }

        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }

        .message.user {
            background: #0e639c;
            margin-left: 30px;
        }

        .message.assistant {
            background: #3e3e42;
            margin-right: 30px;
        }

        .message-sender {
            font-size: 11px;
            opacity: 0.7;
            margin-bottom: 5px;
        }

        .chat-input {
            padding: 15px;
            background: #2d2d30;
            border-top: 1px solid #3e3e42;
        }

        .chat-input input {
            width: 100%;
            padding: 10px;
            background: #3e3e42;
            border: 1px solid #555;
            color: #d4d4d4;
            border-radius: 4px;
            font-size: 13px;
        }

        .chat-input input:focus {
            outline: none;
            border-color: #4ec9b0;
        }

        .terminal {
            height: 200px;
            background: #1e1e1e;
            border-top: 1px solid #3e3e42;
            padding: 10px;
            overflow-y: auto;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
        }

        .terminal-line {
            margin: 2px 0;
        }

        .btn {
            padding: 8px 16px;
            background: #0e639c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }

        .btn:hover {
            background: #1177bb;
        }

        .btn-secondary {
            background: #3e3e42;
        }

        .btn-secondary:hover {
            background: #4e4e52;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Omega Web IDE</h1>
        <div class="status">
            <div class="status-item active">Flask Server</div>
            <div class="status-item" id="llm-status">LLM: Checking...</div>
            <div class="status-item" id="voice-status">Voice: Ready</div>
        </div>
    </div>

    <div class="main-container">
        <!-- File Tree Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">Explorer</div>
            <div class="file-tree" id="file-tree">
                <div class="file-item folder">📁 Loading...</div>
            </div>
        </div>

        <!-- Editor -->
        <div class="editor-container">
            <div class="tabs">
                <div class="tab active">Welcome.md</div>
            </div>
            <div class="editor">
                <textarea id="code-editor" placeholder="Select a file to edit..."># Welcome to Omega Web IDE

This is a browser-based development environment for the Gatekeeper system.

## Features:
- 📝 Code editor
- 📂 File browser
- 💬 AI chat (with local LLM)
- 🗣️ Voice interface
- 🖥️ Integrated terminal

## Quick Start:
1. Browse files in the sidebar
2. Edit code in the main editor
3. Chat with AI in the right panel
4. Save changes with Ctrl+S

Powered by Flask + Ollama/LM Studio
                </textarea>
            </div>
        </div>

        <!-- Chat Panel -->
        <div class="chat-panel">
            <div class="chat-header">💬 AI Assistant</div>
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">
                    <div class="message-sender">Omega</div>
                    <div>Hello! I'm your AI assistant. Ask me anything about your code!</div>
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="chat-input" placeholder="Ask me anything..." />
            </div>
        </div>
    </div>

    <!-- Terminal -->
    <div class="terminal" id="terminal">
        <div class="terminal-line">Omega Terminal v1.0</div>
        <div class="terminal-line">Type 'help' for commands</div>
        <div class="terminal-line">---</div>
    </div>

    <script>
        // Check LLM status
        fetch('/api/llm/status')
            .then(r => r.json())
            .then(data => {
                const statusEl = document.getElementById('llm-status');
                if (data.available) {
                    statusEl.textContent = `LLM: ${data.model}`;
                    statusEl.classList.add('active');
                } else {
                    statusEl.textContent = 'LLM: Offline';
                }
            });

        // Load file tree
        function loadFileTree() {
            fetch('/api/files/tree')
                .then(r => r.json())
                .then(data => {
                    const tree = document.getElementById('file-tree');
                    tree.innerHTML = '';

                    data.files.forEach(file => {
                        const item = document.createElement('div');
                        item.className = 'file-item';
                        item.textContent = `${file.is_dir ? '📁' : '📄'} ${file.name}`;
                        item.onclick = () => {
                            if (!file.is_dir) {
                                loadFile(file.path);
                            }
                        };
                        tree.appendChild(item);
                    });
                });
        }

        // Load file content
        function loadFile(path) {
            fetch(`/api/files/read?path=${encodeURIComponent(path)}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('code-editor').value = data.content;
                    addTerminalLine(`Loaded: ${path}`);
                });
        }

        // Chat with AI
        document.getElementById('chat-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const input = this.value;
                if (!input.trim()) return;

                // Add user message
                addChatMessage('You', input, 'user');
                this.value = '';

                // Send to AI
                fetch('/api/llm/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: input})
                })
                .then(r => r.json())
                .then(data => {
                    addChatMessage('Omega', data.response, 'assistant');
                });
            }
        });

        function addChatMessage(sender, text, type) {
            const messages = document.getElementById('chat-messages');
            const msg = document.createElement('div');
            msg.className = `message ${type}`;
            msg.innerHTML = `
                <div class="message-sender">${sender}</div>
                <div>${text}</div>
            `;
            messages.appendChild(msg);
            messages.scrollTop = messages.scrollHeight;
        }

        function addTerminalLine(text) {
            const terminal = document.getElementById('terminal');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.textContent = `> ${text}`;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }

        // Initialize
        loadFileTree();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main IDE page"""
    return render_template_string(IDE_TEMPLATE)


@app.route('/api/llm/status')
def llm_status():
    """Check LLM availability"""
    try:
        from omega_local_llm import get_brain_llm
        brain = get_brain_llm()
        return jsonify({
            'available': brain.llm.available,
            'model': brain.llm.config.model,
            'backend': brain.llm.config.backend
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        })


@app.route('/api/llm/chat', methods=['POST'])
def llm_chat():
    """Chat with LLM"""
    try:
        data = request.json
        message = data.get('message', '')

        from omega_local_llm import get_brain_llm
        brain = get_brain_llm()

        if brain.llm.available:
            response = brain.process_voice_input(message)
        else:
            response = "LLM not available. Please set up Ollama or LM Studio."

        return jsonify({
            'response': response,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'response': f"Error: {e}",
            'success': False
        })


@app.route('/api/files/tree')
def file_tree():
    """Get file tree"""
    try:
        files = []
        for item in current_directory.iterdir():
            # Skip hidden and system files
            if item.name.startswith('.') or item.name.startswith('__'):
                continue

            files.append({
                'name': item.name,
                'path': str(item),
                'is_dir': item.is_dir(),
                'size': item.stat().st_size if item.is_file() else 0
            })

        # Sort: directories first, then by name
        files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

        return jsonify({
            'files': files,
            'current_dir': str(current_directory)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'files': []
        })


@app.route('/api/files/read')
def read_file():
    """Read file content"""
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'error': 'No path provided'}), 400

        path = Path(file_path)

        # Security: ensure file is within current directory
        if not str(path.resolve()).startswith(str(current_directory)):
            return jsonify({'error': 'Access denied'}), 403

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'content': content,
            'path': str(path),
            'size': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/save', methods=['POST'])
def save_file():
    """Save file content"""
    try:
        data = request.json
        file_path = data.get('path')
        content = data.get('content', '')

        if not file_path:
            return jsonify({'error': 'No path provided'}), 400

        path = Path(file_path)

        # Security check
        if not str(path.resolve()).startswith(str(current_directory)):
            return jsonify({'error': 'Access denied'}), 403

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return jsonify({
            'success': True,
            'path': str(path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def start_ide_server(port: int = 5000, host: str = '127.0.0.1', debug: bool = False):
    """
    Start Omega Web IDE server

    Args:
        port: Port to run on
        host: Host to bind to
        debug: Enable debug mode
    """
    print("=" * 70)
    print("  OMEGA WEB IDE")
    print("=" * 70)
    print()
    print(f"  Starting server on http://{host}:{port}")
    print(f"  Working directory: {current_directory}")
    print()
    print("  Features:")
    print("    ✓ Code editor")
    print("    ✓ File browser")
    print("    ✓ AI chat (if Ollama/LM Studio is set up)")
    print("    ✓ Integrated terminal")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Use waitress for production on Windows
    if not debug:
        try:
            from waitress import serve
            serve(app, host=host, port=port)
        except ImportError:
            print("[IDE] waitress not installed, using Flask dev server")
            print("[IDE] Install: py -3.11 -m pip install waitress")
            app.run(host=host, port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Omega Web IDE')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--dir', default='.', help='Working directory')

    args = parser.parse_args()

    # Set working directory
    current_directory = Path(args.dir).resolve()

    # Start server
    start_ide_server(port=args.port, host=args.host, debug=args.debug)
