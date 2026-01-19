#!/usr/bin/env python3
"""
Control Panel Buttons Integration Helper
=========================================
Helper functions to integrate buttons into control panel.
"""

def create_buttons_in_control_panel(control_panel):
    """
    Create control buttons in the control panel
    
    Args:
        control_panel: ControlPanel instance
    """
    from omega_control_panel_buttons import ControlPanelButtons
    from matplotlib.widgets import Button
    
    fig = control_panel.fig
    
    # Push to Talk button in yellow section (bottom left)
    ax_yellow = control_panel.ax_yellow
    bbox_yellow = ax_yellow.get_position()
    ax_ptt = fig.add_axes([bbox_yellow.x0 + 0.1 * bbox_yellow.width, 
                           bbox_yellow.y0 + 0.05 * bbox_yellow.height,
                           0.35 * bbox_yellow.width, 0.35 * bbox_yellow.height])
    button_ptt = Button(ax_ptt, 'Push to\nTalk', color='#4CAF50', hovercolor='#45a049')
    
    # Enter button in blue section (bottom middle)
    ax_blue = control_panel.ax_blue
    bbox_blue = ax_blue.get_position()
    ax_enter = fig.add_axes([bbox_blue.x0 + 0.25 * bbox_blue.width,
                             bbox_blue.y0 + 0.05 * bbox_blue.height,
                             0.5 * bbox_blue.width, 0.35 * bbox_blue.height])
    button_enter = Button(ax_enter, 'Enter', color='#2196F3', hovercolor='#1976D2')
    
    # Mute button in orange section (bottom right)
    ax_orange = control_panel.ax_orange
    bbox_orange = ax_orange.get_position()
    ax_mute = fig.add_axes([bbox_orange.x0 + 0.1 * bbox_orange.width,
                            bbox_orange.y0 + 0.05 * bbox_orange.height,
                            0.35 * bbox_orange.width, 0.35 * bbox_orange.height])
    button_mute = Button(ax_mute, 'Mute', color='#FF9800', hovercolor='#F57C00')
    
    # Volume control in orange section (next to mute)
    ax_vol_label = fig.add_axes([bbox_orange.x0 + 0.5 * bbox_orange.width,
                                 bbox_orange.y0 + 0.15 * bbox_orange.height,
                                 0.15 * bbox_orange.width, 0.15 * bbox_orange.height])
    ax_vol_label.axis('off')
    ax_vol_label.text(0.5, 0.5, 'Vol', ha='center', va='center', fontsize=8, fontweight='bold')
    
    ax_vol_down = fig.add_axes([bbox_orange.x0 + 0.67 * bbox_orange.width,
                                bbox_orange.y0 + 0.1 * bbox_orange.height,
                                0.12 * bbox_orange.width, 0.25 * bbox_orange.height])
    button_vol_down = Button(ax_vol_down, '−', color='#9E9E9E', hovercolor='#757575')
    
    ax_vol_up = fig.add_axes([bbox_orange.x0 + 0.8 * bbox_orange.width,
                              bbox_orange.y0 + 0.1 * bbox_orange.height,
                              0.12 * bbox_orange.width, 0.25 * bbox_orange.height])
    button_vol_up = Button(ax_vol_up, '+', color='#9E9E9E', hovercolor='#757575')
    
    # Store buttons
    control_panel.button_ptt = button_ptt
    control_panel.button_enter = button_enter
    control_panel.button_mute = button_mute
    control_panel.button_vol_down = button_vol_down
    control_panel.button_vol_up = button_vol_up
    
    # Button states
    control_panel.push_to_talk_active = False
    control_panel.muted = False
    control_panel.volume_level = 0.8
    
    # Set up callbacks
    def on_ptt_press(event):
        control_panel.push_to_talk_active = True
        button_ptt.color = '#66BB6A'
        fig.canvas.draw()
    
    def on_ptt_release(event):
        control_panel.push_to_talk_active = False
        button_ptt.color = '#4CAF50'
        fig.canvas.draw()
    
    def on_enter_click(event):
        # Enter button action
        pass
    
    def on_mute_click(event):
        control_panel.muted = not control_panel.muted
        if control_panel.muted:
            button_mute.color = '#F44336'
            button_mute.label.set_text('Unmute')
        else:
            button_mute.color = '#FF9800'
            button_mute.label.set_text('Mute')
        fig.canvas.draw()
    
    def on_vol_down(event):
        control_panel.volume_level = max(0.0, control_panel.volume_level - 0.1)
        fig.canvas.draw()
    
    def on_vol_up(event):
        control_panel.volume_level = min(1.0, control_panel.volume_level + 0.1)
        fig.canvas.draw()
    
    # Connect callbacks
    button_ptt.on_clicked(lambda event: None)
    button_ptt.on_pressed = on_ptt_press
    button_ptt.on_released = on_ptt_release
    button_enter.on_clicked(on_enter_click)
    button_mute.on_clicked(on_mute_click)
    button_vol_down.on_clicked(on_vol_down)
    button_vol_up.on_clicked(on_vol_up)
    
    return {
        'push_to_talk': button_ptt,
        'enter': button_enter,
        'mute': button_mute,
        'volume_down': button_vol_down,
        'volume_up': button_vol_up
    }
