#!/usr/bin/env python3
"""
KITT Scanner Effect
===================
Knight Rider KITT-style scanner animation for Omega UI.
Synchronized with speech for visual feedback.
"""

import numpy as np
import time
from typing import Optional, Tuple, List
from datetime import datetime

class KITTScannerEffect:
    """KITT-style scanner animation effect"""
    
    def __init__(self, num_bars: int = 16, color: Tuple[float, float, float] = (1.0, 0.0, 0.0)):
        """
        Initialize KITT scanner effect
        
        Args:
            num_bars: Number of bars in scanner (8-16 recommended)
            color: RGB color tuple (default: red)
        """
        self.num_bars = num_bars
        self.color = color
        self.scan_position = 0.0  # Current scan position (0.0 to 1.0)
        self.scan_speed = 0.05  # Base scan speed (0.0 to 1.0 per frame)
        self.intensity = 0.7  # Base intensity (0.0 to 1.0)
        self.speaking = False
        self.speech_intensity = 0.0  # Current speech intensity (0.0 to 1.0)
        self.last_update = time.time()
        
    def update(self, speech_active: bool = False, speech_amplitude: float = 0.0):
        """
        Update scanner animation
        
        Args:
            speech_active: Whether speech is currently active
            speech_amplitude: Audio amplitude (0.0 to 1.0) for intensity control
        """
        self.speaking = speech_active
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        
        # Adjust speed based on speech
        if speech_active:
            # Increase speed during speech (1.5x to 3x base speed)
            speed_multiplier = 1.5 + (speech_amplitude * 1.5)
            current_speed = self.scan_speed * speed_multiplier
            # Increase intensity during speech
            self.speech_intensity = min(1.0, speech_amplitude * 1.2)
        else:
            current_speed = self.scan_speed
            self.speech_intensity = max(0.0, self.speech_intensity - 0.05)  # Fade out
        
        # Update scan position (wrap around)
        self.scan_position += current_speed * (delta_time * 60)  # Assume 60 FPS
        if self.scan_position > 1.0:
            self.scan_position -= 1.0
        
        # Calculate intensity
        if speech_active:
            self.intensity = 0.7 + (self.speech_intensity * 0.3)  # 0.7 to 1.0
        else:
            self.intensity = max(0.5, self.intensity - 0.02)  # Fade to 0.5
    
    def get_bar_intensities(self) -> List[float]:
        """
        Get intensity values for each bar (0.0 to 1.0)
        
        Returns:
            List of intensity values for each bar
        """
        intensities = []
        
        # Create wave pattern
        for i in range(self.num_bars):
            # Position of this bar (0.0 to 1.0)
            bar_position = i / (self.num_bars - 1) if self.num_bars > 1 else 0.5
            
            # Calculate distance from scan position (wrapped)
            distance = abs(bar_position - self.scan_position)
            if distance > 0.5:
                distance = 1.0 - distance
            
            # Wave pattern (bell curve / Gaussian-like)
            # Wider wave for smoother effect
            wave_width = 0.15 + (self.speech_intensity * 0.1)  # Wider during speech
            intensity = np.exp(-(distance ** 2) / (2 * (wave_width ** 2)))
            
            # Apply base intensity
            bar_intensity = intensity * self.intensity
            
            # Add pulsing effect during speech
            if self.speaking:
                pulse = 0.1 * np.sin(time.time() * 10)  # Fast pulse
                bar_intensity = min(1.0, bar_intensity + pulse)
            
            intensities.append(max(0.0, min(1.0, bar_intensity)))
        
        return intensities
    
    def get_colors(self) -> List[Tuple[float, float, float]]:
        """
        Get color values for each bar (with intensity applied)
        
        Returns:
            List of RGB color tuples
        """
        intensities = self.get_bar_intensities()
        colors = []
        
        for intensity in intensities:
            # Apply color with intensity
            r, g, b = self.color
            color = (r * intensity, g * intensity, b * intensity)
            colors.append(color)
        
        return colors
    
    def reset(self):
        """Reset scanner to initial state"""
        self.scan_position = 0.0
        self.intensity = 0.7
        self.speech_intensity = 0.0
        self.speaking = False
        self.last_update = time.time()

class ScannerAudioSync:
    """Synchronize scanner with audio"""
    
    def __init__(self, scanner: KITTScannerEffect):
        """
        Initialize audio synchronization
        
        Args:
            scanner: KITTScannerEffect instance to control
        """
        self.scanner = scanner
        self.audio_file = None
        self.sample_rate = 22050
        
    def update_from_audio(self, audio_data: Optional[np.ndarray] = None, 
                         audio_amplitude: float = 0.0):
        """
        Update scanner based on audio
        
        Args:
            audio_data: Audio data array (optional)
            audio_amplitude: Audio amplitude (0.0 to 1.0)
        """
        speech_active = audio_amplitude > 0.1  # Threshold for speech detection
        self.scanner.update(speech_active, audio_amplitude)
    
    def update_from_file(self, audio_file_path: str, position: float = 0.0):
        """
        Update scanner based on audio file
        
        Args:
            audio_file_path: Path to audio file
            position: Position in audio file (0.0 to 1.0)
        """
        try:
            import librosa
            
            # Load audio if not already loaded
            if self.audio_file != audio_file_path:
                audio_data, self.sample_rate = librosa.load(audio_file_path, sr=None)
                self.audio_data = audio_data
                self.audio_file = audio_file_path
            
            # Get audio amplitude at current position
            sample_index = int(position * len(self.audio_data))
            if sample_index < len(self.audio_data):
                # Get amplitude in a small window around position
                window_start = max(0, sample_index - 100)
                window_end = min(len(self.audio_data), sample_index + 100)
                window = self.audio_data[window_start:window_end]
                amplitude = float(np.abs(window).mean())
                
                # Normalize to 0.0-1.0
                audio_amplitude = min(1.0, amplitude * 2.0)
                
                speech_active = audio_amplitude > 0.1
                self.scanner.update(speech_active, audio_amplitude)
            else:
                self.scanner.update(False, 0.0)
                
        except Exception as e:
            # Fallback: no audio
            self.scanner.update(False, 0.0)

def main():
    """Test scanner effect"""
    print("=" * 80)
    print(" " * 25 + "KITT SCANNER EFFECT TEST")
    print("=" * 80)
    print()
    
    scanner = KITTScannerEffect(num_bars=16, color=(1.0, 0.0, 0.0))
    
    print("Scanner Effect Created:")
    print(f"  - Bars: {scanner.num_bars}")
    print(f"  - Color: RGB{scanner.color}")
    print(f"  - Base Speed: {scanner.scan_speed}")
    print()
    print("Testing animation...")
    
    # Simulate animation
    for i in range(20):
        # Simulate speech
        speech_active = (i % 10) < 5  # Alternate speech on/off
        amplitude = 0.5 if speech_active else 0.0
        
        scanner.update(speech_active, amplitude)
        intensities = scanner.get_bar_intensities()
        
        # Visual representation (text)
        bar_visual = "".join(["█" if int > 0.5 else "░" for int in intensities])
        print(f"Frame {i:2d}: {bar_visual} (speech: {speech_active}, amp: {amplitude:.2f})")
        time.sleep(0.1)
    
    print()
    print("=" * 80)
    print("Test complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
