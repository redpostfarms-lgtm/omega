"""
Omega Scanner Integration
=========================
Integrates KITT-style scanner effect into Omega Control Panel UI.
"""

import sys
from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np
import time

base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

try:
    from kitt_scanner_effect import KITTScannerEffect, ScannerAudioSync
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    print("[Warning] KITT scanner effect not available")

class OmegaScannerIntegration:
    """Integrates KITT scanner into Omega UI"""
    
    def __init__(self):
        self.scanner = None
        self.audio_sync = None
        
        if SCANNER_AVAILABLE:
            self.scanner = KITTScannerEffect(
                num_bars=16,
                color=(1.0, 0.215, 0.0)  # Orange-red (Omega gold-red blend)
            )
            self.audio_sync = ScannerAudioSync(self.scanner)
    
    def update_scanner(self, speech_active: bool = False, 
                      audio_amplitude: float = 0.0,
                      audio_file: Optional[str] = None,
                      audio_position: float = 0.0):
        """
        Update scanner animation
        
        Args:
            speech_active: Whether speech is active
            audio_amplitude: Audio amplitude (0.0 to 1.0)
            audio_file: Path to audio file (optional)
            audio_position: Position in audio file (0.0 to 1.0)
        """
        if not self.scanner:
            return
        
        if audio_file and self.audio_sync:
            try:
                self.audio_sync.update_from_file(audio_file, audio_position)
            except (IOError, OSError, AttributeError, RuntimeError) as e:
                self.scanner.update(speech_active, audio_amplitude)
        else:
            self.scanner.update(speech_active, audio_amplitude)
    
    def get_scanner_bars(self, num_bars: int = 16) -> List[Tuple[float, float, float, float]]:
        """
        Get scanner bar data for rendering
        
        Args:
            num_bars: Number of bars to return
            
        Returns:
            List of (x_position, height, width, intensity) tuples
        """
        if not self.scanner:
            return []
        
        colors = self.scanner.get_colors()
        intensities = self.scanner.get_bar_intensities()
        
        bars = []
        bar_width = 0.05  # Width of each bar (normalized)
        spacing = 0.02  # Spacing between bars
        
        for i, (color, intensity) in enumerate(zip(colors, intensities)):
            if i >= num_bars:
                break
            
            x_pos = 0.1 + (i / (num_bars - 1) if num_bars > 1 else 0.5) * 0.8
            height = 0.6 * intensity  # Height based on intensity
            width = bar_width
            
            bars.append((x_pos, height, width, intensity))
        
        return bars
    
    def render_to_axes(self, ax, num_bars: int = 16):
        """
        Render scanner to matplotlib axes
        
        Args:
            ax: Matplotlib axes object
            num_bars: Number of bars to render
        """
        if not self.scanner:
            return
        
        bars = self.get_scanner_bars(num_bars)
        colors = self.scanner.get_colors()
        
        ax.clear()
        ax.set_facecolor('#1a1a1a')  # Dark background (like KITT)
        ax.axis('off')
        
        for i, ((x_pos, height, width, intensity), color) in enumerate(zip(bars, colors)):
            ax.bar(x_pos, height, width=width, bottom=0.2, 
                  color=color, alpha=0.9, edgecolor='none')
        
        if self.scanner.speaking:
            ax.text(0.5, 0.95, 'Omega Speaking', ha='center', va='top',
                   fontsize=10, fontweight='bold', color='white',
                   transform=ax.transAxes)
        else:
            ax.text(0.5, 0.95, 'Omega Scanner', ha='center', va='top',
                   fontsize=10, fontweight='bold', color='#888888',
                   transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    def reset(self):
        """Reset scanner"""
        if self.scanner:
            self.scanner.reset()

def integrate_with_control_panel():
    """Integration instructions for control panel"""
    integration_guide = """
Integration with omega_control_panel.py:

1. Import scanner:
   from omega_scanner_integration import OmegaScannerIntegration

2. Initialize in __init__:
   self.scanner_integration = OmegaScannerIntegration()

3. Update in _update_gui (OIP section):
   if self.scanner_integration.scanner:
       audio_files = ['response.wav', 'omega_intro.wav']
       audio_found = None
       for af in audio_files:
           audio_path = base_dir / af
           if audio_path.exists():
               audio_found = str(audio_path)
               break
       
       if audio_found:
           self.scanner_integration.update_scanner(
               audio_file=audio_found,
               audio_position=0.5  # Current position in audio
           )
       else:
           self.scanner_integration.update_scanner(
               speech_active=self.speaking,
               audio_amplitude=0.5 if self.speaking else 0.0
           )
       
       self.scanner_integration.render_to_axes(self.ax_oip, num_bars=16)

4. Call update_scanner() regularly (in _update_gui or animation callback)
"""
    return integration_guide

def main():
    """Test integration"""
    print("=" * 80)
    print(" " * 20 + "OMEGA SCANNER INTEGRATION")
    print("=" * 80)
    print()
    
    if not SCANNER_AVAILABLE:
        print("[ERROR] KITT scanner effect not available")
        print("Make sure kitt_scanner_effect.py exists")
        return
    
    integration = OmegaScannerIntegration()
    
    print("Scanner Integration Created:")
    print(f"  - Scanner Available: {integration.scanner is not None}")
    print(f"  - Audio Sync Available: {integration.audio_sync is not None}")
    print()
    print("Integration Guide:")
    print(integrate_with_control_panel())
    print()
    print("=" * 80)
    print("Integration ready for control panel!")
    print("=" * 80)

if __name__ == "__main__":
    main()
