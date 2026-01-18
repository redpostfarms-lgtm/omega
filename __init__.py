"""
The Gatekeeper - Advanced AI Assistant System
==============================================

A production-ready AI assistant with:
- Voice interaction (TTS + Speech Recognition)
- Advanced emotion detection
- Multi-agent orchestration
- Predictive health monitoring
- Multi-channel notifications
- Local LLM integration
- Web-based IDE

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "The Gatekeeper Project"

# Core exports
from pathlib import Path

# Version info
VERSION = __version__
ROOT_DIR = Path(__file__).parent

# Package metadata
__all__ = [
    "__version__",
    "VERSION",
    "ROOT_DIR",
]
