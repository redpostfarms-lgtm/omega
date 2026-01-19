#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Voice - Universal Voice Module
Import this module from any Omega system to access voice capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add paths
_module_path = Path(__file__).parent
sys.path.insert(0, str(_module_path / "omega_integration"))
sys.path.insert(0, str(_module_path / "omega_voice_profiles"))
sys.path.insert(0, str(_module_path / "omega_visual_feedback"))

# Import components
try:
    from omega_voice_hub import omega_voice_hub
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    omega_voice_hub = None


async def speak(text: str, color: str = "red", visualize: bool = True) -> bool:
    """
    Universal speak function - use from any Omega system

    Args:
        text: Text to speak
        color: LED color (red/green/blue/etc.)
        visualize: Enable LED visualization

    Returns:
        True if successful

    Example:
        >>> import omega_voice
        >>> await omega_voice.speak("Hello from Omega!", color="red")
    """
    if not VOICE_AVAILABLE or not omega_voice_hub:
        print(f"[Omega Voice] ⚠ Voice system not available: {text}")
        return False

    return await omega_voice_hub.quick_speak(text, color=color)


async def announce(message: str, priority: str = "normal") -> bool:
    """
    System announcement with priority-based colors

    Args:
        message: Announcement text
        priority: Priority level (low/normal/high/critical)

    Example:
        >>> import omega_voice
        >>> await omega_voice.announce("System ready", priority="normal")
    """
    if not VOICE_AVAILABLE or not omega_voice_hub:
        print(f"[Omega Voice] ⚠ Voice system not available: {message}")
        return False

    await omega_voice_hub.system_announce(message, priority)
    return True


def set_led_state(state: str):
    """
    Set LED state (idle/listening/processing/speaking/error/success)

    Args:
        state: State name

    Example:
        >>> import omega_voice
        >>> omega_voice.set_led_state("processing")
    """
    if VOICE_AVAILABLE and omega_voice_hub:
        omega_voice_hub.set_led_state(state)


def get_voice_status() -> dict:
    """
    Get voice system status

    Returns:
        Status dictionary

    Example:
        >>> import omega_voice
        >>> status = omega_voice.get_voice_status()
        >>> print(status["led_connected"])
    """
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.get_status()

    return {
        "available": False,
        "error": "Voice system not initialized"
    }


# Synchronous wrapper for simple use cases
def speak_sync(text: str, color: str = "red"):
    """
    Synchronous speak function

    Args:
        text: Text to speak
        color: LED color

    Example:
        >>> import omega_voice
        >>> omega_voice.speak_sync("Hello!")
    """
    asyncio.run(speak(text, color))


# Quick access to components
def get_azz_voice():
    """Get AZZ Voice System instance"""
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.azz_voice
    return None


def get_led_matrix():
    """Get LED Matrix controller instance"""
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.led_matrix
    return None


def get_voice_led():
    """Get Voice-LED integration instance"""
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.voice_led
    return None
