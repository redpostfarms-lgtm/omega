# -*- coding: utf-8 -*-
# ELARA ADAPTIVE LEARNING ENGINE
# Learns user behavior: pause time, mouse grip, voice patterns

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class UserPattern:
    """Learned user pattern."""
    pause_time: float = 0.0
    mouse_velocity: float = 0.0
    grip_tightness: float = 0.0
    voice_pattern: str = ""
    move_style: str = "deliberate"
    preferred_speed: float = 1.0


class AdaptiveLearner:
    """
    Adaptive learning engine.
    
    Features:
    - Learns pause times between moves
    - Tracks mouse grip patterns
    - Adapts to voice patterns
    - Adjusts animation speed
    - Speaks back like user, but smoother
    """
    
    def __init__(self, data_file: str = "./.elara/user_patterns.json"):
        """Initialize adaptive learner."""
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.pattern = UserPattern()
        self.observations: List[Dict[str, Any]] = []
        
        # Load existing patterns
        self.load_patterns()
    
    def observe_move_timing(self, timestamp: float):
        """Observe timing between moves."""
        if self.observations:
            last_time = self.observations[-1].get('timestamp', timestamp)
            pause = timestamp - last_time
            self.pattern.pause_time = self.pattern.pause_time * 0.9 + pause * 0.1
        else:
            self.pattern.pause_time = 0.0
        
        self.observations.append({
            'timestamp': timestamp,
            'type': 'move',
            'pause_time': self.pattern.pause_time
        })
        
        # Keep only last 100 observations
        if len(self.observations) > 100:
            self.observations.pop(0)
    
    def observe_mouse_grip(self, positions: List[float], velocities: List[float]):
        """Observe mouse grip patterns."""
        if not velocities:
            return
        
        # Calculate average velocity
        avg_velocity = sum(velocities) / len(velocities)
        self.pattern.mouse_velocity = self.pattern.mouse_velocity * 0.9 + avg_velocity * 0.1
        
        # Calculate grip tightness from velocity variation
        if len(velocities) > 1:
            variance = sum((v - avg_velocity)**2 for v in velocities) / len(velocities)
            grip_tightness = 1.0 / (1.0 + variance)  # Higher variance = looser grip
            self.pattern.grip_tightness = self.pattern.grip_tightness * 0.9 + grip_tightness * 0.1
    
    def observe_voice(self, text: str, pattern: str):
        """Observe voice patterns."""
        # Learn how user says things
        self.pattern.voice_pattern = pattern
        
        # Example: learn how user says "bishop"
        if "bishop" in text.lower():
            # Would extract voice characteristics
            pass
    
    def adapt_to_user(self) -> Dict[str, Any]:
        """Adapt engine settings to user patterns."""
        adaptations = {}
        
        # Adapt animation speed based on pause time
        if self.pattern.pause_time > 3.0:
            # Slow player - slower animations
            adaptations['animation_speed'] = 0.8
            self.pattern.move_style = "deliberate"
        elif self.pattern.pause_time < 1.0:
            # Fast player - faster animations
            adaptations['animation_speed'] = 1.2
            self.pattern.move_style = "quick"
        else:
            adaptations['animation_speed'] = 1.0
            self.pattern.move_style = "normal"
        
        # Adapt magnetic snap based on grip
        if self.pattern.grip_tightness > 0.7:
            # Tight grip - stronger snap
            adaptations['magnetic_snap_strength'] = 0.4
        else:
            # Loose grip - gentler snap
            adaptations['magnetic_snap_strength'] = 0.2
        
        # Adapt preferred speed
        self.pattern.preferred_speed = adaptations.get('animation_speed', 1.0)
        
        return adaptations
    
    def generate_response(self, user_text: str) -> str:
        """Generate response that sounds like user but smoother."""
        # Adapt to user's voice pattern but make it smoother
        # Example: if user says "move the bishop", adapt to their style
        
        # For now, simplified
        base_response = f"Understood. {user_text}"
        
        # Make it smoother based on learned patterns
        if self.pattern.move_style == "quick":
            response = base_response.replace("Understood.", "Got it.")
        elif self.pattern.move_style == "deliberate":
            response = base_response.replace("Understood.", "Taking that into account.")
        else:
            response = base_response
        
        return response
    
    def save_patterns(self):
        """Save learned patterns to file."""
        data = {
            'pattern': asdict(self.pattern),
            'observations_count': len(self.observations),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_patterns(self):
        """Load learned patterns from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pattern_data = data.get('pattern', {})
                    self.pattern = UserPattern(**pattern_data)
            except Exception as e:
                print(f"[Learner] Error loading patterns: {e}")


if __name__ == '__main__':
    learner = AdaptiveLearner()
    
    # Simulate observations
    learner.observe_move_timing(time.time())
    time.sleep(2)
    learner.observe_move_timing(time.time())
    
    adaptations = learner.adapt_to_user()
    print(f"Adaptations: {adaptations}")
    
    learner.save_patterns()
    print("[OK] Adaptive learner ready")

