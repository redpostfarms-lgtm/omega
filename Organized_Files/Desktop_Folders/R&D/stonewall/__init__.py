# -*- coding: utf-8 -*-
# STONEWALL VPN - The Ultimate VPN System

from .stonewall_core import StonewallVPN, StonewallConfig, KillSwitch, Obfuscator
from .agent_protection import AgentProtection, ProtectedScraper, protect_agent_requests

try:
    from .babel_onnx import BabelONNX, get_babel_onnx
    HAS_BABEL_ONNX = True
except ImportError:
    HAS_BABEL_ONNX = False
    BabelONNX = None

try:
    from .bait_farm import BaitFarm
    HAS_BAIT_FARM = True
except ImportError:
    HAS_BAIT_FARM = False
    BaitFarm = None

__version__ = "2.0.0"
__all__ = [
    'StonewallVPN',
    'StonewallConfig',
    'KillSwitch',
    'Obfuscator',
    'AgentProtection',
    'ProtectedScraper',
    'protect_agent_requests',
    'BabelONNX',
    'get_babel_onnx',
    'BaitFarm'
]

