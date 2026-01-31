"""
Omega Microsoft Integration
============================
Integrates Omega with Microsoft services and Windows ecosystem:
- Microsoft Graph API (Calendar, Mail, OneDrive, Teams)
- Windows Notification Center
- Windows Task Scheduler
- Windows Registry (startup)
- Cortana replacement capabilities
- Microsoft Account authentication
"""

import os
import sys
import json
import subprocess
import winreg
import ctypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Omega.Microsoft")

# Optional imports
MSAL_AVAILABLE = False
GRAPH_AVAILABLE = False
TOAST_AVAILABLE = False

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    logger.warning("msal not available - install with: pip install msal")

try:
    from msgraph import GraphServiceClient
    GRAPH_AVAILABLE = True
except ImportError:
    logger.warning("msgraph-sdk not available - install with: pip install msgraph-sdk")

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    try:
        from win11toast import toast as win11_toast
        TOAST_AVAILABLE = True
    except ImportError:
        logger.warning("Toast notifications not available - install with: pip install win10toast or win11toast")


class OmegaMicrosoftAuth:
    """Microsoft Authentication using MSAL"""

    # Microsoft Graph API scopes
    SCOPES = [
        "User.Read",
        "Mail.Read",
        "Mail.Send",
        "Calendars.ReadWrite",
        "Files.ReadWrite",
        "Tasks.ReadWrite",
        "Presence.Read",
    ]

    def __init__(self, client_id: str = None, tenant_id: str = "common"):
        """
        Initialize Microsoft authentication

        Args:
            client_id: Azure AD application client ID
            tenant_id: Azure AD tenant ID (default: 'common' for multi-tenant)
        """
        self.client_id = client_id or os.getenv("OMEGA_MS_CLIENT_ID")
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.token_cache_file = Path(__file__).parent / ".omega_ms_token_cache.json"
        self.app = None
        self.access_token = None

        if MSAL_AVAILABLE and self.client_id:
            self._init_msal_app()

    def _init_msal_app(self):
        """Initialize MSAL application"""
        cache = msal.SerializableTokenCache()

        # Load existing cache
        if self.token_cache_file.exists():
            cache.deserialize(self.token_cache_file.read_text())

        self.app = msal.PublicClientApplication(
            self.client_id,
            authority=self.authority,
            token_cache=cache
        )

    def _save_cache(self):
        """Save token cache to file"""
        if self.app and self.app.token_cache.has_state_changed:
            self.token_cache_file.write_text(self.app.token_cache.serialize())

    def authenticate_interactive(self) -> Optional[str]:
        """
        Authenticate interactively (opens browser)

        Returns:
            Access token or None
        """
        if not MSAL_AVAILABLE or not self.app:
            logger.error("MSAL not available or not configured")
            return None

        try:
            # Try to get token silently first
            accounts = self.app.get_accounts()
            if accounts:
                result = self.app.acquire_token_silent(self.SCOPES, account=accounts[0])
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    self._save_cache()
                    logger.info("Token acquired silently")
                    return self.access_token

            # Interactive authentication
            result = self.app.acquire_token_interactive(scopes=self.SCOPES)
            if "access_token" in result:
                self.access_token = result["access_token"]
                self._save_cache()
                logger.info("Token acquired interactively")
                return self.access_token
            else:
                logger.error(f"Authentication failed: {result.get('error_description')}")
                return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def authenticate_device_code(self) -> Optional[str]:
        """
        Authenticate using device code flow (for headless scenarios)

        Returns:
            Access token or None
        """
        if not MSAL_AVAILABLE or not self.app:
            logger.error("MSAL not available or not configured")
            return None

        try:
            flow = self.app.initiate_device_flow(scopes=self.SCOPES)
            if "user_code" not in flow:
                logger.error("Failed to initiate device flow")
                return None

            print(flow["message"])  # Shows "Go to https://microsoft.com/devicelogin and enter code: XXXXX"

            result = self.app.acquire_token_by_device_flow(flow)
            if "access_token" in result:
                self.access_token = result["access_token"]
                self._save_cache()
                logger.info("Token acquired via device code")
                return self.access_token
            else:
                logger.error(f"Authentication failed: {result.get('error_description')}")
                return None

        except Exception as e:
            logger.error(f"Device code authentication error: {e}")
            return None

    def get_token(self) -> Optional[str]:
        """Get current access token (authenticate if needed)"""
        if self.access_token:
            return self.access_token
        return self.authenticate_interactive()


class OmegaWindowsIntegration:
    """Windows system integration"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.icon_path = self.base_dir / "images" / "omega_logo_red_gold_wreath.ico"
        self.toaster = None

        if TOAST_AVAILABLE:
            try:
                self.toaster = ToastNotifier()
            except Exception:
                pass

    def send_notification(self, title: str, message: str, duration: int = 10) -> bool:
        """
        Send Windows toast notification

        Args:
            title: Notification title
            message: Notification body
            duration: Duration in seconds

        Returns:
            True if sent successfully
        """
        try:
            if self.toaster:
                icon = str(self.icon_path) if self.icon_path.exists() else None
                self.toaster.show_toast(
                    title,
                    message,
                    icon_path=icon,
                    duration=duration,
                    threaded=True
                )
                return True
            else:
                # Fallback to PowerShell notification
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastText02">
                            <text id="1">{title}</text>
                            <text id="2">{message}</text>
                        </binding>
                    </visual>
                </toast>
"@

                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Omega").Show($toast)
                '''

                subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True

        except Exception as e:
            logger.error(f"Notification error: {e}")
            return False

    def add_to_startup_registry(self, name: str = "OmegaSystem") -> bool:
        """
        Add Omega to Windows startup via registry

        Args:
            name: Registry key name

        Returns:
            True if successful
        """
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            script_path = self.base_dir / "OMEGA_SILENT_LAUNCHER.vbs"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'wscript.exe "{script_path}"')

            logger.info(f"Added to startup registry: {name}")
            return True

        except Exception as e:
            logger.error(f"Registry error: {e}")
            return False

    def remove_from_startup_registry(self, name: str = "OmegaSystem") -> bool:
        """
        Remove Omega from Windows startup registry

        Args:
            name: Registry key name

        Returns:
            True if successful
        """
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)

            logger.info(f"Removed from startup registry: {name}")
            return True

        except FileNotFoundError:
            logger.info(f"Registry key not found: {name}")
            return True
        except Exception as e:
            logger.error(f"Registry error: {e}")
            return False

    def create_scheduled_task(self, task_name: str = "OmegaAutoStart") -> bool:
        """
        Create Windows Task Scheduler task for Omega

        Args:
            task_name: Name of the scheduled task

        Returns:
            True if successful
        """
        try:
            vbs_path = self.base_dir / "OMEGA_SILENT_LAUNCHER.vbs"

            # XML task definition
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Omega System Auto-Start - Silent background launcher</Description>
    <Author>Omega</Author>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"{vbs_path}"</Arguments>
      <WorkingDirectory>{self.base_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

            # Save XML temporarily
            xml_path = self.base_dir / "logs" / "omega_task.xml"
            xml_path.parent.mkdir(exist_ok=True)
            xml_path.write_text(task_xml, encoding='utf-16')

            # Create task using schtasks
            result = subprocess.run(
                ["schtasks", "/Create", "/TN", task_name, "/XML", str(xml_path), "/F"],
                capture_output=True,
                text=True
            )

            # Clean up XML
            xml_path.unlink()

            if result.returncode == 0:
                logger.info(f"Scheduled task created: {task_name}")
                return True
            else:
                logger.error(f"Failed to create task: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Task scheduler error: {e}")
            return False

    def delete_scheduled_task(self, task_name: str = "OmegaAutoStart") -> bool:
        """
        Delete Windows Task Scheduler task

        Args:
            task_name: Name of the scheduled task

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["schtasks", "/Delete", "/TN", task_name, "/F"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"Scheduled task deleted: {task_name}")
                return True
            else:
                logger.error(f"Failed to delete task: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Task scheduler error: {e}")
            return False

    def set_as_default_assistant(self) -> bool:
        """
        Configure Omega as the default voice assistant (replaces Cortana activation)

        Note: This modifies Windows settings and may require admin privileges

        Returns:
            True if successful
        """
        try:
            # Disable Cortana
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"

            try:
                with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "AllowCortana", 0, winreg.REG_DWORD, 0)
                logger.info("Cortana disabled")
            except PermissionError:
                logger.warning("Admin privileges required to disable Cortana")

            # Set Omega as voice activation handler (user-level)
            # This creates a custom protocol handler
            protocol_path = r"SOFTWARE\Classes\omega"

            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, protocol_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "URL:Omega Protocol")
                winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

            command_path = f"{protocol_path}\\shell\\open\\command"
            script_path = self.base_dir / "omega_voice_handler.py"

            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, command_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'pythonw "{script_path}" "%1"')

            logger.info("Omega protocol handler registered")
            return True

        except Exception as e:
            logger.error(f"Assistant configuration error: {e}")
            return False


class OmegaGraphClient:
    """Microsoft Graph API client for Omega"""

    def __init__(self, auth: OmegaMicrosoftAuth):
        """
        Initialize Graph client

        Args:
            auth: OmegaMicrosoftAuth instance
        """
        self.auth = auth
        self.base_url = "https://graph.microsoft.com/v1.0"

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        token = self.auth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_user_profile(self) -> Optional[Dict]:
        """Get current user profile"""
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/me",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None

    def get_calendar_events(self, days: int = 7) -> List[Dict]:
        """
        Get calendar events for the next N days

        Args:
            days: Number of days to look ahead

        Returns:
            List of calendar events
        """
        try:
            import requests
            from datetime import timedelta

            start = datetime.utcnow().isoformat() + "Z"
            end = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

            response = requests.get(
                f"{self.base_url}/me/calendarview",
                headers=self._get_headers(),
                params={
                    "startDateTime": start,
                    "endDateTime": end,
                    "$orderby": "start/dateTime"
                }
            )
            response.raise_for_status()
            return response.json().get("value", [])
        except Exception as e:
            logger.error(f"Failed to get calendar events: {e}")
            return []

    def get_recent_emails(self, count: int = 10) -> List[Dict]:
        """
        Get recent emails

        Args:
            count: Number of emails to retrieve

        Returns:
            List of email messages
        """
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/me/messages",
                headers=self._get_headers(),
                params={
                    "$top": count,
                    "$orderby": "receivedDateTime desc"
                }
            )
            response.raise_for_status()
            return response.json().get("value", [])
        except Exception as e:
            logger.error(f"Failed to get emails: {e}")
            return []

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML supported)

        Returns:
            True if sent successfully
        """
        try:
            import requests
            message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": to}}
                    ]
                }
            }

            response = requests.post(
                f"{self.base_url}/me/sendMail",
                headers=self._get_headers(),
                json=message
            )
            response.raise_for_status()
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def get_onedrive_files(self, path: str = "/") -> List[Dict]:
        """
        List OneDrive files

        Args:
            path: Folder path

        Returns:
            List of files/folders
        """
        try:
            import requests
            if path == "/":
                url = f"{self.base_url}/me/drive/root/children"
            else:
                url = f"{self.base_url}/me/drive/root:{path}:/children"

            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get("value", [])
        except Exception as e:
            logger.error(f"Failed to get OneDrive files: {e}")
            return []


class OmegaMicrosoftIntegration:
    """
    Main integration class combining all Microsoft services
    """

    def __init__(self, client_id: str = None):
        """
        Initialize Microsoft integration

        Args:
            client_id: Azure AD application client ID
        """
        self.auth = OmegaMicrosoftAuth(client_id)
        self.windows = OmegaWindowsIntegration()
        self.graph = None

        if self.auth.client_id:
            self.graph = OmegaGraphClient(self.auth)

    def setup_autostart(self, method: str = "task") -> bool:
        """
        Configure Omega to start automatically with Windows

        Args:
            method: "task" for Task Scheduler, "registry" for registry, "startup" for startup folder

        Returns:
            True if successful
        """
        if method == "task":
            return self.windows.create_scheduled_task()
        elif method == "registry":
            return self.windows.add_to_startup_registry()
        elif method == "startup":
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            vbs_path = self.windows.base_dir / "OMEGA_SILENT_LAUNCHER.vbs"
            shortcut_path = startup_folder / "Omega.lnk"

            # Create shortcut using PowerShell
            ps_script = f'''
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "wscript.exe"
            $Shortcut.Arguments = '"{vbs_path}"'
            $Shortcut.WorkingDirectory = "{self.windows.base_dir}"
            $Shortcut.IconLocation = "{self.windows.icon_path}"
            $Shortcut.Save()
            '''

            try:
                subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True
                )
                logger.info(f"Startup shortcut created: {shortcut_path}")
                return True
            except Exception as e:
                logger.error(f"Shortcut creation error: {e}")
                return False
        else:
            logger.error(f"Unknown autostart method: {method}")
            return False

    def remove_autostart(self, method: str = "all") -> bool:
        """
        Remove Omega from automatic startup

        Args:
            method: "task", "registry", "startup", or "all"

        Returns:
            True if successful
        """
        success = True

        if method in ("task", "all"):
            success &= self.windows.delete_scheduled_task()

        if method in ("registry", "all"):
            success &= self.windows.remove_from_startup_registry()

        if method in ("startup", "all"):
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            for pattern in ["Omega*.lnk", "Omega*.bat", "omega*.lnk", "omega*.bat"]:
                for f in startup_folder.glob(pattern):
                    f.unlink()
                    logger.info(f"Removed: {f}")

        return success

    def notify(self, title: str, message: str) -> bool:
        """Send Windows notification"""
        return self.windows.send_notification(title, message)

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        status = {
            "msal_available": MSAL_AVAILABLE,
            "graph_available": GRAPH_AVAILABLE,
            "toast_available": TOAST_AVAILABLE,
            "client_id_configured": bool(self.auth.client_id),
            "authenticated": bool(self.auth.access_token),
            "icon_exists": self.windows.icon_path.exists(),
        }

        # Check startup methods
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                try:
                    winreg.QueryValueEx(key, "OmegaSystem")
                    status["registry_startup"] = True
                except FileNotFoundError:
                    status["registry_startup"] = False
        except Exception:
            status["registry_startup"] = False

        result = subprocess.run(
            ["schtasks", "/Query", "/TN", "OmegaAutoStart"],
            capture_output=True
        )
        status["task_scheduler_startup"] = result.returncode == 0

        return status


def main():
    """Test Microsoft integration"""
    print("=" * 60)
    print("OMEGA MICROSOFT INTEGRATION TEST")
    print("=" * 60)
    print()

    integration = OmegaMicrosoftIntegration()

    # Show status
    status = integration.get_status()
    print("Integration Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()

    # Test notification
    print("Testing notification...")
    integration.notify("Omega Test", "Microsoft integration is working!")

    # Setup autostart
    print("\nSetting up autostart via Task Scheduler...")
    if integration.setup_autostart("task"):
        print("  SUCCESS: Task created")
    else:
        print("  FAILED: Could not create task")

    print("\nDone!")


if __name__ == "__main__":
    main()
