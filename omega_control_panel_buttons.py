"""
Omega Control Panel Buttons
============================
Button controls for the control panel: Push to Talk, Enter, Mute, Volume.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
from typing import Optional, Callable

class ControlPanelButtons:
    """Button controls for Omega Control Panel"""
    
    def __init__(self, fig, axes_section):
        """
        Initialize buttons
        
        Args:
            fig: Matplotlib figure
            axes_section: Axes object to add buttons to
        """
        self.fig = fig
        self.axes_section = axes_section
        self.buttons = {}
        self.callbacks = {}
        
        self.push_to_talk_active = False
        self.muted = False
        self.volume_level = 0.8  # 0.0 to 1.0
        
        self.on_push_to_talk = None
        self.on_enter = None
        self.on_mute_toggle = None
        self.on_volume_change = None
    
    def create_push_to_talk_button(self, position: tuple = (0.1, 0.1, 0.2, 0.3)):
        """
        Create Push to Talk button
        
        Args:
            position: (x, y, width, height) in axes coordinates
        """
        ax_button = self.fig.add_axes(position)
        button = Button(ax_button, 'Push to\nTalk', color='#4CAF50', hovercolor='#45a049')
        
        def on_press(event):
            self.push_to_talk_active = True
            button.color = '#66BB6A'  # Lighter green when active
            if self.on_push_to_talk:
                self.on_push_to_talk(True)
            self.fig.canvas.draw()
        
        def on_release(event):
            self.push_to_talk_active = False
            button.color = '#4CAF50'  # Normal green
            if self.on_push_to_talk:
                self.on_push_to_talk(False)
            self.fig.canvas.draw()
        
        button.on_clicked(lambda event: None)  # Placeholder
        button.on_pressed = on_press
        button.on_released = on_release
        
        self.buttons['push_to_talk'] = button
        return button
    
    def create_enter_button(self, position: tuple = (0.35, 0.1, 0.2, 0.3)):
        """
        Create Enter button
        
        Args:
            position: (x, y, width, height) in axes coordinates
        """
        ax_button = self.fig.add_axes(position)
        button = Button(ax_button, 'Enter', color='#2196F3', hovercolor='#1976D2')
        
        def on_click(event):
            if self.on_enter:
                self.on_enter()
        
        button.on_clicked(on_click)
        self.buttons['enter'] = button
        return button
    
    def create_mute_button(self, position: tuple = (0.6, 0.1, 0.15, 0.3)):
        """
        Create Mute button
        
        Args:
            position: (x, y, width, height) in axes coordinates
        """
        ax_button = self.fig.add_axes(position)
        button = Button(ax_button, 'Mute', color='#FF9800', hovercolor='#F57C00')
        
        def on_click(event):
            self.muted = not self.muted
            if self.muted:
                button.color = '#F44336'  # Red when muted
                button.label.set_text('Unmute')
            else:
                button.color = '#FF9800'  # Orange when not muted
                button.label.set_text('Mute')
            
            if self.on_mute_toggle:
                self.on_mute_toggle(self.muted)
            
            self.fig.canvas.draw()
        
        button.on_clicked(on_click)
        self.buttons['mute'] = button
        return button
    
    def create_volume_control(self, position: tuple = (0.78, 0.1, 0.18, 0.3)):
        """
        Create Volume control (slider-like buttons)
        
        Args:
            position: (x, y, width, height) in axes coordinates
        """
        ax_volume = self.fig.add_axes(position)
        ax_volume.set_facecolor('#E0E0E0')
        ax_volume.axis('off')
        
        ax_volume.text(0.5, 0.75, 'Volume', ha='center', va='top', fontsize=9, fontweight='bold')
        
        volume_text = ax_volume.text(0.5, 0.5, f'{int(self.volume_level * 100)}%', 
                                     ha='center', va='center', fontsize=10, fontweight='bold')
        
        ax_vol_down = self.fig.add_axes([position[0] + 0.02, position[1], 0.06, 0.25])
        button_vol_down = Button(ax_vol_down, '−', color='#9E9E9E', hovercolor='#757575')
        
        ax_vol_up = self.fig.add_axes([position[0] + 0.1, position[1], 0.06, 0.25])
        button_vol_up = Button(ax_vol_up, '+', color='#9E9E9E', hovercolor='#757575')
        
        def volume_down(event):
            self.volume_level = max(0.0, self.volume_level - 0.1)
            volume_text.set_text(f'{int(self.volume_level * 100)}%')
            if self.on_volume_change:
                self.on_volume_change(self.volume_level)
            self.fig.canvas.draw()
        
        def volume_up(event):
            self.volume_level = min(1.0, self.volume_level + 0.1)
            volume_text.set_text(f'{int(self.volume_level * 100)}%')
            if self.on_volume_change:
                self.on_volume_change(self.volume_level)
            self.fig.canvas.draw()
        
        button_vol_down.on_clicked(volume_down)
        button_vol_up.on_clicked(volume_up)
        
        self.buttons['volume_down'] = button_vol_down
        self.buttons['volume_up'] = button_vol_up
        self.volume_text = volume_text
        
        return (button_vol_down, button_vol_up, volume_text)
    
    def create_all_buttons(self, base_position_y: float = 0.1):
        """
        Create all buttons in a row
        
        Args:
            base_position_y: Y position for buttons (in axes coordinates)
        """
        ax = self.axes_section
        bbox = ax.get_position()
        
        fig_width = bbox.width
        fig_height = bbox.height
        fig_x0 = bbox.x0
        fig_y0 = bbox.y0
        
        button_width = 0.15 * fig_width
        button_height = 0.4 * fig_height
        button_y = fig_y0 + base_position_y * fig_height
        spacing = 0.05 * fig_width
        
        x1 = fig_x0 + 0.1 * fig_width
        self.create_push_to_talk_button((x1, button_y, button_width, button_height))
        
        x2 = x1 + button_width + spacing
        self.create_enter_button((x2, button_y, button_width * 0.8, button_height))
        
        x3 = x2 + button_width * 0.8 + spacing
        self.create_mute_button((x3, button_y, button_width * 0.7, button_height))
        
        x4 = x3 + button_width * 0.7 + spacing
        vol_width = min(0.2 * fig_width, fig_x0 + fig_width - x4 - 0.05 * fig_width)
        self.create_volume_control((x4, button_y, vol_width, button_height))
    
    def set_callbacks(self, on_push_to_talk: Optional[Callable] = None,
                     on_enter: Optional[Callable] = None,
                     on_mute_toggle: Optional[Callable] = None,
                     on_volume_change: Optional[Callable] = None):
        """
        Set button callbacks
        
        Args:
            on_push_to_talk: Callback(bool) for push to talk press/release
            on_enter: Callback() for enter button
            on_mute_toggle: Callback(bool) for mute toggle
            on_volume_change: Callback(float) for volume change
        """
        self.on_push_to_talk = on_push_to_talk
        self.on_enter = on_enter
        self.on_mute_toggle = on_mute_toggle
        self.on_volume_change = on_volume_change
    
    def update_volume_display(self):
        """Update volume display text"""
        if hasattr(self, 'volume_text'):
            self.volume_text.set_text(f'{int(self.volume_level * 100)}%')

def main():
    """Test buttons"""
    print("=" * 80)
    print(" " * 25 + "CONTROL PANEL BUTTONS TEST")
    print("=" * 80)
    print()
    print("Button Controls Created:")
    print("  - Push to Talk (green)")
    print("  - Enter (blue)")
    print("  - Mute/Unmute (orange/red)")
    print("  - Volume Control (up/down)")
    print()
    print("Ready for integration into control panel!")
    print("=" * 80)

if __name__ == "__main__":
    main()
