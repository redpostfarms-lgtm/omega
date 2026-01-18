"""
Windows 10 Toast Notifications
==============================
Quiet notifications for cleanup, disk space, and system events
"""

import os
import sys
from typing import Optional, Literal


class Win10Toast:
    """Windows 10 toast notification handler"""

    def __init__(self, app_name: str = "Gatekeeper System"):
        """
        Initialize toast notifier

        Args:
            app_name: Application name shown in notifications
        """
        self.app_name = app_name
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if toast notifications are available"""
        if sys.platform != 'win32':
            return False

        try:
            import win10toast
            return True
        except ImportError:
            try:
                # Try alternate library
                import win11toast
                return True
            except ImportError:
                return False

    def notify(self,
               title: str,
               message: str,
               icon_path: Optional[str] = None,
               duration: int = 5,
               threaded: bool = True) -> bool:
        """
        Show toast notification

        Args:
            title: Notification title
            message: Notification message
            icon_path: Path to icon (optional)
            duration: Duration in seconds
            threaded: Run in background thread

        Returns:
            True if notification shown, False otherwise
        """
        if not self.available:
            # Fallback: print to console
            print(f"\n[{self.app_name}] {title}: {message}")
            return False

        try:
            # Try win10toast first
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    title=f"{self.app_name} - {title}",
                    msg=message,
                    icon_path=icon_path,
                    duration=duration,
                    threaded=threaded
                )
                return True
            except ImportError:
                pass

            # Try win11toast as fallback
            try:
                from win11toast import toast
                toast(
                    title=f"{self.app_name} - {title}",
                    body=message,
                    icon=icon_path,
                    duration='short' if duration <= 5 else 'long'
                )
                return True
            except ImportError:
                pass

        except Exception as e:
            print(f"[Toast] Error showing notification: {e}")
            # Fallback to console
            print(f"\n[{self.app_name}] {title}: {message}")
            return False

        return False


class SystemNotifier:
    """System-level notifications for Gatekeeper"""

    def __init__(self):
        """Initialize system notifier"""
        self.toaster = Win10Toast("Gatekeeper")
        self.notifications_enabled = True

    def enable(self) -> None:
        """Enable notifications"""
        self.notifications_enabled = True

    def disable(self) -> None:
        """Disable notifications"""
        self.notifications_enabled = False

    def cleanup_started(self, location: str) -> bool:
        """Notify when cleanup starts"""
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title="Cleanup Started",
            message=f"Cleaning up: {location}",
            duration=3,
            threaded=True
        )

    def cleanup_completed(self, files_removed: int, space_freed: float) -> bool:
        """
        Notify when cleanup completes

        Args:
            files_removed: Number of files removed
            space_freed: Space freed in MB

        Returns:
            True if notification shown
        """
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title="Cleanup Complete",
            message=f"Removed {files_removed} files, freed {space_freed:.1f}MB",
            duration=5,
            threaded=True
        )

    def disk_space_warning(self, path: str, usage_percent: float) -> bool:
        """
        Notify when disk space is low

        Args:
            path: Disk path
            usage_percent: Usage percentage

        Returns:
            True if notification shown
        """
        if not self.notifications_enabled:
            return False

        if usage_percent >= 90:
            title = "Critical Disk Space"
            message = f"{path} is {usage_percent:.0f}% full - CRITICAL"
        elif usage_percent >= 80:
            title = "Low Disk Space"
            message = f"{path} is {usage_percent:.0f}% full"
        else:
            return False  # Don't notify if below 80%

        return self.toaster.notify(
            title=title,
            message=message,
            duration=10,
            threaded=True
        )

    def compression_completed(self, files_compressed: int, space_saved: float) -> bool:
        """
        Notify when compression completes

        Args:
            files_compressed: Number of files compressed
            space_saved: Space saved in MB

        Returns:
            True if notification shown
        """
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title="Compression Complete",
            message=f"Compressed {files_compressed} files, saved {space_saved:.1f}MB",
            duration=5,
            threaded=True
        )

    def integrity_check_failed(self, file_path: str) -> bool:
        """
        Notify when integrity check fails

        Args:
            file_path: Path to corrupted file

        Returns:
            True if notification shown
        """
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title="Integrity Check Failed",
            message=f"File corrupted: {os.path.basename(file_path)}",
            duration=10,
            threaded=True
        )

    def system_ready(self) -> bool:
        """Notify when system is ready"""
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title="System Ready",
            message="Gatekeeper system initialized and ready",
            duration=3,
            threaded=True
        )

    def backup_completed(self, file_count: int) -> bool:
        """
        Notify when backup completes

        Args:
            file_count: Number of files backed up

        Returns:
            True if notification shown
        """
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title="Backup Complete",
            message=f"Backed up {file_count} files",
            duration=5,
            threaded=True
        )

    def custom(self, title: str, message: str, duration: int = 5) -> bool:
        """
        Custom notification

        Args:
            title: Notification title
            message: Notification message
            duration: Duration in seconds

        Returns:
            True if notification shown
        """
        if not self.notifications_enabled:
            return False

        return self.toaster.notify(
            title=title,
            message=message,
            duration=duration,
            threaded=True
        )


# Global notifier instance
_notifier = None


def get_notifier() -> SystemNotifier:
    """Get global notifier instance"""
    global _notifier
    if _notifier is None:
        _notifier = SystemNotifier()
    return _notifier


# Convenience functions
def notify_cleanup_started(location: str) -> bool:
    """Notify cleanup started"""
    return get_notifier().cleanup_started(location)


def notify_cleanup_completed(files_removed: int, space_freed: float) -> bool:
    """Notify cleanup completed"""
    return get_notifier().cleanup_completed(files_removed, space_freed)


def notify_disk_space(path: str, usage_percent: float) -> bool:
    """Notify disk space warning"""
    return get_notifier().disk_space_warning(path, usage_percent)


def notify_compression(files_compressed: int, space_saved: float) -> bool:
    """Notify compression completed"""
    return get_notifier().compression_completed(files_compressed, space_saved)


def notify_integrity_failure(file_path: str) -> bool:
    """Notify integrity check failure"""
    return get_notifier().integrity_check_failed(file_path)


def install_toast_notifications() -> bool:
    """
    Install toast notification libraries

    Returns:
        True if installation successful
    """
    if sys.platform != 'win32':
        print("[Toast] Not on Windows - notifications not available")
        return False

    try:
        import subprocess
        import sys

        print("[Toast] Installing win10toast...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "win10toast", "--quiet"
        ])
        print("[Toast] ✓ Installation complete")
        return True
    except Exception as e:
        print(f"[Toast] ✗ Installation failed: {e}")
        print("[Toast] Run: py -3.11 -m pip install win10toast")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("  WINDOWS 10 TOAST NOTIFICATIONS")
    print("=" * 70)
    print()

    notifier = get_notifier()

    if not notifier.toaster.available:
        print("Toast notifications not available!")
        print()
        print("Install with:")
        print("  py -3.11 -m pip install win10toast")
        print()
    else:
        print("Testing notifications...")
        print()

        # Test basic notification
        notifier.custom("Test Notification", "System is working correctly")
        print("✓ Basic notification sent")

        # Test disk space warning
        notifier.disk_space_warning("C:", 85.0)
        print("✓ Disk space warning sent")

        # Test cleanup notification
        notifier.cleanup_completed(42, 128.5)
        print("✓ Cleanup notification sent")

    print()
    print("Example usage:")
    print()
    print("  from utils.win10_notifications import get_notifier")
    print()
    print("  notifier = get_notifier()")
    print("  notifier.cleanup_started('conversations')")
    print("  # ... do cleanup ...")
    print("  notifier.cleanup_completed(files=10, space_freed=50.5)")
    print()
    print("  # Check disk space")
    print("  notifier.disk_space_warning('C:', 85.0)")
    print()
    print("=" * 70)
