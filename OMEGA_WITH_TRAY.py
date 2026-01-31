"""
Omega with System Tray Integration
===================================
Launches Omega Control Panel with system tray support:
- Minimizes to tray instead of closing
- Click tray icon to restore
- Persists across login/logout
- Auto-starts on Windows login (optional)

ARCHITECTURE:
- System tray runs in MAIN thread (pystray requirement)
- Control panel launched as SEPARATE PROCESS (matplotlib requirement)
- Win32 API used to show/hide control panel window
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

# Try to import required modules
PYSTRAY_AVAILABLE = False
WIN32_AVAILABLE = False

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    print("[WARNING] pystray not available. Install with: pip install pystray pillow")

try:
    import win32gui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    print("[WARNING] pywin32 not available. Install with: pip install pywin32")


class OmegaWithTray:
    """Omega application with system tray integration"""

    def __init__(self):
        self.tray_icon = None
        self.control_panel_process = None
        self.window_visible = True
        self.running = True
        self.base_dir = base_dir

        # Icon path
        self.icon_path = self.base_dir / "images" / "omega_logo_red_gold_wreath.ico"

    def create_tray_icon_image(self, size: int = 64) -> 'Image':
        """Create Omega icon for system tray"""
        # Try to load actual icon first
        if self.icon_path.exists():
            try:
                img = Image.open(str(self.icon_path))
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                return img
            except Exception as e:
                print(f"[Omega] Could not load icon: {e}")

        # Fallback: Create programmatic icon
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Black circle background with red border
        margin = 2
        draw.ellipse([margin, margin, size-margin, size-margin],
                    fill=(0, 0, 0, 255), outline=(255, 0, 0, 255))

        # Red omega symbol
        cx, cy = size // 2, size // 2
        r = size // 3

        # Omega arc
        draw.arc([cx - r, cy - r, cx + r, cy + r],
                start=30, end=150, fill=(255, 0, 0, 255), width=3)

        # Omega legs
        leg_y1 = cy + r // 2
        leg_y2 = cy + r
        spread = r // 2

        draw.line([cx - spread, leg_y1, cx - spread, leg_y2], fill=(255, 0, 0, 255), width=3)
        draw.line([cx + spread, leg_y1, cx + spread, leg_y2], fill=(255, 0, 0, 255), width=3)

        # Feet
        draw.line([cx - spread - 4, leg_y2, cx - spread + 4, leg_y2], fill=(255, 0, 0, 255), width=3)
        draw.line([cx + spread - 4, leg_y2, cx + spread + 4, leg_y2], fill=(255, 0, 0, 255), width=3)

        return image

    def create_tray_menu(self):
        """Create system tray context menu"""
        return pystray.Menu(
            item('Show Omega', self.show_window, default=True),
            item('Hide to Tray', self.hide_to_tray),
            pystray.Menu.SEPARATOR,
            item('Launch Control Panel', self.launch_control_panel),
            item('Launch KITT UI', self.launch_kitt_ui),
            pystray.Menu.SEPARATOR,
            item('Add to Windows Startup', self.add_to_startup),
            item('Remove from Startup', self.remove_from_startup),
            pystray.Menu.SEPARATOR,
            item('Quit Omega', self.quit_app)
        )

    def _find_omega_windows(self):
        """Find all Omega-related windows"""
        windows = []
        if not WIN32_AVAILABLE:
            return windows

        def enum_callback(hwnd, results):
            if win32gui.IsWindow(hwnd):
                title = win32gui.GetWindowText(hwnd)
                title_upper = title.upper()
                if any(x in title_upper for x in ['OMEGA', 'CONTROL PANEL', 'KITT', 'FIGURE']):
                    results.append((hwnd, title))
            return True

        try:
            win32gui.EnumWindows(enum_callback, windows)
        except Exception as e:
            print(f"[Omega] Window enumeration error: {e}")

        return windows

    def show_window(self, icon=None, item=None):
        """Show the Omega window"""
        print("[Omega] Showing window...")
        self.window_visible = True

        windows = self._find_omega_windows()

        if windows:
            for hwnd, title in windows:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    print(f"[Omega] Restored: {title}")
                except Exception as e:
                    print(f"[Omega] Could not restore {title}: {e}")
        else:
            # No window found, launch control panel
            print("[Omega] No window found, launching control panel...")
            self.launch_control_panel()

    def hide_to_tray(self, icon=None, item=None):
        """Hide window to system tray"""
        print("[Omega] Hiding to tray...")
        self.window_visible = False

        windows = self._find_omega_windows()

        for hwnd, title in windows:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                print(f"[Omega] Hidden: {title}")
            except Exception as e:
                print(f"[Omega] Could not hide {title}: {e}")

    def launch_control_panel(self, icon=None, item=None):
        """Launch control panel as separate process"""
        script = self.base_dir / "omega_control_panel.py"
        if script.exists():
            print(f"[Omega] Launching control panel: {script}")
            try:
                self.control_panel_process = subprocess.Popen(
                    [sys.executable, str(script)],
                    cwd=str(self.base_dir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                print(f"[Omega] Control panel started (PID: {self.control_panel_process.pid})")
            except Exception as e:
                print(f"[Omega] Failed to launch control panel: {e}")
        else:
            print(f"[Omega] Control panel not found: {script}")

    def launch_kitt_ui(self, icon=None, item=None):
        """Launch KITT UI as separate process"""
        script = self.base_dir / "omega_kitt_ui.py"
        if script.exists():
            print(f"[Omega] Launching KITT UI: {script}")
            try:
                subprocess.Popen(
                    [sys.executable, str(script)],
                    cwd=str(self.base_dir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
            except Exception as e:
                print(f"[Omega] Failed to launch KITT UI: {e}")
        else:
            print(f"[Omega] KITT UI not found: {script}")

    def add_to_startup(self, icon=None, item=None):
        """Add Omega to Windows startup"""
        try:
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            startup_script = startup_folder / "Omega_Tray.bat"

            current_script = Path(__file__).absolute()

            script_content = f'''@echo off
REM Omega System Tray - Auto-start on login
cd /d "{current_script.parent}"
start "" /B pythonw "{current_script}"
'''
            with open(startup_script, 'w') as f:
                f.write(script_content)

            print(f"[Omega] Added to startup: {startup_script}")

            if self.tray_icon:
                self.tray_icon.notify("Omega will now start automatically on login", "Added to Startup")

        except Exception as e:
            print(f"[Omega] Failed to add to startup: {e}")

    def remove_from_startup(self, icon=None, item=None):
        """Remove Omega from Windows startup"""
        try:
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

            removed = False
            for pattern in ["Omega*.bat", "omega*.bat", "Omega*.lnk", "omega*.lnk"]:
                for script in startup_folder.glob(pattern):
                    script.unlink()
                    print(f"[Omega] Removed: {script}")
                    removed = True

            if self.tray_icon:
                if removed:
                    self.tray_icon.notify("Omega removed from Windows startup", "Removed from Startup")
                else:
                    self.tray_icon.notify("Omega was not in Windows startup", "Not Found")

        except Exception as e:
            print(f"[Omega] Failed to remove from startup: {e}")

    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        print("[Omega] Quitting...")
        self.running = False

        # Terminate control panel process
        if self.control_panel_process:
            try:
                self.control_panel_process.terminate()
                print("[Omega] Control panel terminated")
            except Exception:
                pass

        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()

        sys.exit(0)

    def run(self):
        """Run Omega with system tray"""
        print("=" * 70)
        print(" " * 20 + "OMEGA SYSTEM TRAY")
        print("=" * 70)
        print()
        print("Starting Omega System Tray...")
        print()
        print("Features:")
        print("  - System tray icon (bottom-right of taskbar)")
        print("  - Left-click tray icon: Show/restore window")
        print("  - Right-click tray icon: Menu options")
        print("  - 'Add to Windows Startup' for auto-start on login")
        print()
        print("Look for the Omega icon in your system tray!")
        print()
        print("-" * 70)

        if not PYSTRAY_AVAILABLE:
            print("[ERROR] pystray not available. Install with: pip install pystray pillow")
            print("[Omega] Launching control panel directly instead...")
            self.launch_control_panel()

            # Wait for control panel to exit
            if self.control_panel_process:
                self.control_panel_process.wait()
            return

        # Create and run tray icon
        print("[Omega] Creating system tray icon...")
        icon_image = self.create_tray_icon_image()
        menu = self.create_tray_menu()

        self.tray_icon = pystray.Icon(
            "omega_tray",
            icon_image,
            "Omega System\nClick to show",
            menu
        )

        # Double-click / left-click shows window
        self.tray_icon.on_activate = self.show_window

        print("[Omega] System tray icon running...")
        print("[Omega] Right-click the tray icon for options")

        # This blocks - tray icon event loop
        self.tray_icon.run()


def main():
    """Main entry point"""
    # Check for required packages
    missing = []

    try:
        import pystray
    except ImportError:
        missing.append("pystray")

    try:
        from PIL import Image
    except ImportError:
        missing.append("pillow")

    try:
        import win32gui
    except ImportError:
        missing.append("pywin32")

    if missing:
        print(f"[Omega] Missing packages: {', '.join(missing)}")
        print("[Omega] Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
        print("[Omega] Packages installed. Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    app = OmegaWithTray()
    app.run()


if __name__ == "__main__":
    main()
