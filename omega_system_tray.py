"""
Omega System Tray Manager
=========================
Provides system tray icon for Omega with:
- Minimize to tray
- Restore on icon click
- Persistent across login/logout via Windows startup
- Context menu with quick actions
"""

import sys
import os
import threading
import subprocess
from pathlib import Path
from typing import Optional, Callable

# Try multiple tray libraries
PYSTRAY_AVAILABLE = False
WIN32_AVAILABLE = False

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    pass

try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    pass


class OmegaSystemTray:
    """System tray manager for Omega"""

    def __init__(self,
                 on_show: Optional[Callable] = None,
                 on_hide: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None):
        """
        Initialize system tray

        Args:
            on_show: Callback when user clicks to show window
            on_hide: Callback when user clicks to hide window
            on_quit: Callback when user clicks quit
        """
        self.on_show = on_show
        self.on_hide = on_hide
        self.on_quit = on_quit
        self.icon = None
        self.visible = True
        self.running = False
        self._tray_thread = None

        # State file for persistence
        self.state_file = Path(__file__).parent / ".omega_tray_state.json"

    def create_icon_image(self, size: int = 64) -> 'Image':
        """Create Omega icon image"""
        from PIL import Image, ImageDraw, ImageFont

        # Create image with transparency
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw black circle background
        margin = 2
        draw.ellipse([margin, margin, size-margin, size-margin],
                    fill=(0, 0, 0, 255), outline=(255, 0, 0, 255))

        # Draw Omega symbol (red)
        center = size // 2
        radius = size // 3

        # Draw arc for omega top
        draw.arc([center - radius, center - radius, center + radius, center + radius],
                start=30, end=150, fill=(255, 0, 0, 255), width=3)

        # Draw legs of omega
        leg_top = center + radius // 2
        leg_bottom = center + radius
        leg_spread = radius // 2

        draw.line([center - leg_spread, leg_top, center - leg_spread, leg_bottom],
                 fill=(255, 0, 0, 255), width=3)
        draw.line([center + leg_spread, leg_top, center + leg_spread, leg_bottom],
                 fill=(255, 0, 0, 255), width=3)

        # Add small feet
        draw.line([center - leg_spread - 4, leg_bottom, center - leg_spread + 4, leg_bottom],
                 fill=(255, 0, 0, 255), width=3)
        draw.line([center + leg_spread - 4, leg_bottom, center + leg_spread + 4, leg_bottom],
                 fill=(255, 0, 0, 255), width=3)

        return image

    def _create_menu(self):
        """Create system tray context menu"""
        return pystray.Menu(
            item('Show Omega', self._on_show_click, default=True),
            item('Hide Omega', self._on_hide_click),
            pystray.Menu.SEPARATOR,
            item('Control Panel', self._launch_control_panel),
            item('KITT Interface', self._launch_kitt_ui),
            pystray.Menu.SEPARATOR,
            item('Add to Startup', self._add_to_startup),
            item('Remove from Startup', self._remove_from_startup),
            pystray.Menu.SEPARATOR,
            item('Quit', self._on_quit_click)
        )

    def _on_show_click(self, icon=None, item=None):
        """Handle show click"""
        print("[Tray] Show clicked")
        self.visible = True
        if self.on_show:
            self.on_show()

    def _on_hide_click(self, icon=None, item=None):
        """Handle hide click"""
        print("[Tray] Hide clicked")
        self.visible = False
        if self.on_hide:
            self.on_hide()

    def _on_quit_click(self, icon=None, item=None):
        """Handle quit click"""
        print("[Tray] Quit clicked")
        self.running = False
        if self.on_quit:
            self.on_quit()
        if self.icon:
            self.icon.stop()

    def _launch_control_panel(self, icon=None, item=None):
        """Launch control panel"""
        print("[Tray] Launching Control Panel...")
        script = Path(__file__).parent / "omega_control_panel.py"
        if script.exists():
            subprocess.Popen([sys.executable, str(script)],
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

    def _launch_kitt_ui(self, icon=None, item=None):
        """Launch KITT UI"""
        print("[Tray] Launching KITT UI...")
        script = Path(__file__).parent / "omega_kitt_ui.py"
        if script.exists():
            subprocess.Popen([sys.executable, str(script)],
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

    def _add_to_startup(self, icon=None, item=None):
        """Add Omega to Windows startup"""
        try:
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            startup_script = startup_folder / "Omega_Tray.bat"

            current_script = Path(__file__).absolute()
            python_exe = sys.executable

            script_content = f'''@echo off
REM Omega System Tray - Auto-start on login
cd /d "{current_script.parent}"
start "" /B "{python_exe}" "{current_script}"
'''

            with open(startup_script, 'w') as f:
                f.write(script_content)

            print(f"[Tray] Added to startup: {startup_script}")

            # Show notification if possible
            if self.icon:
                self.icon.notify("Omega added to Windows startup", "Omega System Tray")

        except Exception as e:
            print(f"[Tray] Failed to add to startup: {e}")

    def _remove_from_startup(self, icon=None, item=None):
        """Remove Omega from Windows startup"""
        try:
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            startup_script = startup_folder / "Omega_Tray.bat"

            if startup_script.exists():
                startup_script.unlink()
                print(f"[Tray] Removed from startup: {startup_script}")

                if self.icon:
                    self.icon.notify("Omega removed from Windows startup", "Omega System Tray")
            else:
                print("[Tray] Startup script not found")

        except Exception as e:
            print(f"[Tray] Failed to remove from startup: {e}")

    def start(self, blocking: bool = False):
        """
        Start system tray icon

        Args:
            blocking: If True, run in current thread (blocks). If False, run in background thread.
        """
        if not PYSTRAY_AVAILABLE:
            print("[Tray] pystray not available. Install with: pip install pystray pillow")
            return False

        self.running = True

        # Create icon
        icon_image = self.create_icon_image()
        menu = self._create_menu()

        self.icon = pystray.Icon(
            "omega",
            icon_image,
            "Omega System Tray",
            menu
        )

        # Set up click handler (left-click shows window)
        self.icon.on_click = lambda icon, button: self._on_show_click()

        print("[Tray] System tray icon starting...")

        if blocking:
            self.icon.run()
        else:
            self._tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            self._tray_thread.start()
            print("[Tray] Running in background thread")

        return True

    def stop(self):
        """Stop system tray icon"""
        self.running = False
        if self.icon:
            self.icon.stop()
            self.icon = None
        print("[Tray] System tray stopped")

    def notify(self, message: str, title: str = "Omega"):
        """Show notification from tray"""
        if self.icon:
            self.icon.notify(message, title)

    def update_icon(self, image: 'Image' = None):
        """Update tray icon"""
        if self.icon:
            if image is None:
                image = self.create_icon_image()
            self.icon.icon = image


class OmegaTrayApp:
    """
    Complete tray application that manages Omega UI visibility
    """

    def __init__(self):
        self.tray = OmegaSystemTray(
            on_show=self.show_ui,
            on_hide=self.hide_ui,
            on_quit=self.quit_app
        )
        self.control_panel = None
        self.control_panel_process = None
        self.window_hwnd = None

    def show_ui(self):
        """Show Omega UI"""
        print("[App] Showing UI...")

        # If we have a window handle, use win32 to show it
        if WIN32_AVAILABLE and self.window_hwnd:
            try:
                win32gui.ShowWindow(self.window_hwnd, win32con.SW_SHOW)
                win32gui.SetForegroundWindow(self.window_hwnd)
                return
            except Exception as e:
                print(f"[App] Win32 show failed: {e}")

        # Otherwise, launch the control panel
        self._launch_control_panel()

    def hide_ui(self):
        """Hide Omega UI"""
        print("[App] Hiding UI...")

        if WIN32_AVAILABLE and self.window_hwnd:
            try:
                win32gui.ShowWindow(self.window_hwnd, win32con.SW_HIDE)
                return
            except Exception as e:
                print(f"[App] Win32 hide failed: {e}")

    def quit_app(self):
        """Quit the application"""
        print("[App] Quitting...")

        # Terminate control panel if running as subprocess
        if self.control_panel_process:
            self.control_panel_process.terminate()

        # Stop any running control panel
        if self.control_panel:
            try:
                self.control_panel.stop()
            except Exception:
                pass

    def _launch_control_panel(self):
        """Launch control panel as subprocess"""
        script = Path(__file__).parent / "omega_control_panel.py"
        if script.exists():
            print(f"[App] Launching: {script}")
            self.control_panel_process = subprocess.Popen(
                [sys.executable, str(script)],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
        else:
            print(f"[App] Control panel not found: {script}")

    def _find_omega_window(self) -> Optional[int]:
        """Find Omega window handle"""
        if not WIN32_AVAILABLE:
            return None

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if 'Omega' in title or 'OMEGA' in title or 'KITT' in title:
                    windows.append(hwnd)
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
            if windows:
                return windows[0]
        except Exception as e:
            print(f"[App] Window enumeration failed: {e}")

        return None

    def run(self):
        """Run the tray application"""
        print("=" * 60)
        print("OMEGA SYSTEM TRAY")
        print("=" * 60)
        print()
        print("Starting Omega system tray...")
        print("The icon will appear in your system tray (bottom-right)")
        print()
        print("Actions:")
        print("  - Left-click icon: Show Omega UI")
        print("  - Right-click icon: Show menu")
        print("  - Menu > Add to Startup: Auto-start on login")
        print()

        # Start tray (blocking)
        success = self.tray.start(blocking=True)

        if not success:
            print("[App] Failed to start system tray")
            print("Installing required packages...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "pillow"])
            print("Please restart the application")


def main():
    """Main entry point"""
    app = OmegaTrayApp()
    app.run()


if __name__ == "__main__":
    main()
