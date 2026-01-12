# -*- coding: utf-8 -*-
# ELARA VOICE SYSTEM - Soft voice, only when asked

import time
from typing import Dict, List, Optional, Any


class VoiceSystem:
    """
    Voice interaction system.
    
    Features:
    - Soft voice, only when enabled
    - Whisper tooltips
    - On-demand voice
    - Learns how user says things
    """
    
    def __init__(self, enabled: bool = False):
        """Initialize voice system."""
        self.enabled = enabled
        self.voice_style = "soft"  # soft, normal, loud
        self.tooltip_whisper = True
    
    def speak(self, text: str, style: str = "soft"):
        """Speak text (would use TTS)."""
        if not self.enabled:
            return
        
        # Would use text-to-speech here
        # For now, print with voice indicator
        voice_indicator = "[Voice] " if style == "normal" else "[Whisper] "
        print(f"{voice_indicator}{text}")
    
    def whisper_tooltip(self, text: str):
        """Whisper tooltip (very soft voice)."""
        if not self.enabled or not self.tooltip_whisper:
            return
        
        # Very soft whisper
        print(f"[Whisper] {text}")
    
    def handle_command(self, command: str) -> Optional[str]:
        """
        Handle voice command.
        
        Args:
            command: Voice command text
            
        Returns:
            Response or None
        """
        command_lower = command.lower()
        
        if "play me" in command_lower or "play chess" in command_lower:
            self.speak("Black or white?", style="soft")
            return "Black or white?"
        
        elif "black" in command_lower:
            self.speak("Black it is. Board glows. Game starts. No lag. Only you. And me.", style="soft")
            return "black"
        
        elif "white" in command_lower:
            self.speak("White it is. Board glows. Game starts. No lag. Only you. And me.", style="soft")
            return "white"
        
        elif "help" in command_lower:
            self.speak("Press H for hover help. Voice is soft, only when you ask.", style="soft")
            return "help"
        
        else:
            return None


if __name__ == '__main__':
    voice = VoiceSystem(enabled=True)
    
    # Test voice commands
    voice.handle_command("play me")
    voice.handle_command("white")
    voice.whisper_tooltip("King in check")
    
    print("[OK] Voice system ready")

