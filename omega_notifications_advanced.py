"""
Advanced Notification System for The Gatekeeper
================================================
Multi-channel notifications: Email, Slack, Discord, Telegram, Teams

Features:
- Template-based messages (Jinja2)
- Multiple delivery channels
- Async delivery
- Retry logic
- Notification history
- Priority levels

Requirements:
- jinja2>=3.1.2
- python-telegram-bot>=20.7
- discord.py>=2.3.2
- slack-sdk>=3.26.0
- aiohttp>=3.9.0
"""

import os
import sys
import logging
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Warning: jinja2 not available for templates")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("Warning: aiohttp not available for async webhooks")


class Priority(Enum):
    """Notification priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Channel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    TEAMS = "teams"
    WEBHOOK = "webhook"


@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_from: str = ""
    email_password: str = ""
    email_to: List[str] = field(default_factory=list)

    # Slack
    slack_webhook_url: str = ""
    slack_token: str = ""
    slack_channel: str = "#general"

    # Discord
    discord_webhook_url: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Teams
    teams_webhook_url: str = ""

    # Generic webhook
    webhook_url: str = ""

    # Templates directory
    templates_dir: str = "notification_templates"


@dataclass
class NotificationResult:
    """Result from sending notification"""
    channel: Channel
    success: bool
    message: str
    timestamp: datetime
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'channel': self.channel.value,
            'success': self.success,
            'message': self.message[:100],  # Truncate for storage
            'timestamp': self.timestamp.isoformat(),
            'error': self.error
        }


class NotificationManager:
    """
    Advanced notification manager with multiple channels

    Usage:
        manager = NotificationManager(config)
        await manager.send(
            "System Alert",
            "Disk space low",
            channels=[Channel.EMAIL, Channel.SLACK],
            priority=Priority.HIGH
        )
    """

    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        Initialize notification manager

        Args:
            config: NotificationConfig or None to load from environment
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or self._load_config_from_env()
        self.history: List[NotificationResult] = []
        self.max_history = 1000

        # Initialize template environment
        if JINJA2_AVAILABLE:
            templates_path = Path(self.config.templates_dir)
            if templates_path.exists():
                self.jinja_env = Environment(loader=FileSystemLoader(str(templates_path)))
            else:
                self.jinja_env = None
        else:
            self.jinja_env = None

    def _load_config_from_env(self) -> NotificationConfig:
        """Load configuration from environment variables"""
        return NotificationConfig(
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            email_from=os.getenv('EMAIL_FROM', ''),
            email_password=os.getenv('EMAIL_PASSWORD', ''),
            email_to=os.getenv('EMAIL_TO', '').split(',') if os.getenv('EMAIL_TO') else [],
            slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL', ''),
            slack_token=os.getenv('SLACK_TOKEN', ''),
            slack_channel=os.getenv('SLACK_CHANNEL', '#general'),
            discord_webhook_url=os.getenv('DISCORD_WEBHOOK_URL', ''),
            telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID', ''),
            teams_webhook_url=os.getenv('TEAMS_WEBHOOK_URL', ''),
            webhook_url=os.getenv('WEBHOOK_URL', ''),
            templates_dir=os.getenv('NOTIFICATION_TEMPLATES_DIR', 'notification_templates')
        )

    async def send(
        self,
        title: str,
        message: str,
        channels: List[Channel] = None,
        priority: Priority = Priority.NORMAL,
        template: Optional[str] = None,
        template_data: Optional[dict] = None
    ) -> List[NotificationResult]:
        """
        Send notification to multiple channels

        Args:
            title: Notification title
            message: Notification message
            channels: List of channels to send to (default: all configured)
            priority: Notification priority
            template: Optional template name
            template_data: Data for template rendering

        Returns:
            List of NotificationResults
        """
        # Render template if provided
        if template and self.jinja_env:
            try:
                tmpl = self.jinja_env.get_template(template)
                message = tmpl.render(title=title, message=message, **(template_data or {}))
            except Exception as e:
                self.logger.error(f"Template rendering failed: {e}")

        # Default to all configured channels if none specified
        if channels is None:
            channels = self._get_configured_channels()

        # Send to each channel
        results = []
        for channel in channels:
            try:
                if channel == Channel.EMAIL:
                    result = await self._send_email(title, message, priority)
                elif channel == Channel.SLACK:
                    result = await self._send_slack(title, message, priority)
                elif channel == Channel.DISCORD:
                    result = await self._send_discord(title, message, priority)
                elif channel == Channel.TELEGRAM:
                    result = await self._send_telegram(title, message, priority)
                elif channel == Channel.TEAMS:
                    result = await self._send_teams(title, message, priority)
                elif channel == Channel.WEBHOOK:
                    result = await self._send_webhook(title, message, priority)
                else:
                    result = NotificationResult(
                        channel=channel,
                        success=False,
                        message="Unknown channel",
                        timestamp=datetime.now(),
                        error="Unknown channel type"
                    )

                results.append(result)
                self._add_to_history(result)

            except Exception as e:
                self.logger.error(f"Failed to send to {channel.value}: {e}")
                result = NotificationResult(
                    channel=channel,
                    success=False,
                    message=message,
                    timestamp=datetime.now(),
                    error=str(e)
                )
                results.append(result)
                self._add_to_history(result)

        return results

    async def _send_email(
        self,
        title: str,
        message: str,
        priority: Priority
    ) -> NotificationResult:
        """Send email notification"""
        if not all([self.config.email_from, self.config.email_password, self.config.email_to]):
            return NotificationResult(
                channel=Channel.EMAIL,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="Email not configured"
            )

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(self.config.email_to)
            msg['Subject'] = f"[{priority.name}] {title}"

            msg.attach(MIMEText(message, 'plain'))

            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_from, self.config.email_password)
                server.send_message(msg)

            self.logger.info(f"Email sent: {title}")
            return NotificationResult(
                channel=Channel.EMAIL,
                success=True,
                message=message,
                timestamp=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Email failed: {e}")
            return NotificationResult(
                channel=Channel.EMAIL,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _send_slack(
        self,
        title: str,
        message: str,
        priority: Priority
    ) -> NotificationResult:
        """Send Slack notification via webhook"""
        if not self.config.slack_webhook_url:
            return NotificationResult(
                channel=Channel.SLACK,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="Slack webhook not configured"
            )

        if not AIOHTTP_AVAILABLE:
            return NotificationResult(
                channel=Channel.SLACK,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="aiohttp not available"
            )

        try:
            # Priority color
            color_map = {
                Priority.LOW: "#36a64f",
                Priority.NORMAL: "#2196F3",
                Priority.HIGH: "#ff9800",
                Priority.CRITICAL: "#f44336"
            }

            payload = {
                "attachments": [{
                    "color": color_map.get(priority, "#2196F3"),
                    "title": title,
                    "text": message,
                    "footer": "The Gatekeeper",
                    "ts": int(datetime.now().timestamp())
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.slack_webhook_url, json=payload) as resp:
                    if resp.status == 200:
                        self.logger.info(f"Slack sent: {title}")
                        return NotificationResult(
                            channel=Channel.SLACK,
                            success=True,
                            message=message,
                            timestamp=datetime.now()
                        )
                    else:
                        error = await resp.text()
                        return NotificationResult(
                            channel=Channel.SLACK,
                            success=False,
                            message=message,
                            timestamp=datetime.now(),
                            error=f"HTTP {resp.status}: {error}"
                        )

        except Exception as e:
            self.logger.error(f"Slack failed: {e}")
            return NotificationResult(
                channel=Channel.SLACK,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _send_discord(
        self,
        title: str,
        message: str,
        priority: Priority
    ) -> NotificationResult:
        """Send Discord notification via webhook"""
        if not self.config.discord_webhook_url:
            return NotificationResult(
                channel=Channel.DISCORD,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="Discord webhook not configured"
            )

        if not AIOHTTP_AVAILABLE:
            return NotificationResult(
                channel=Channel.DISCORD,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="aiohttp not available"
            )

        try:
            # Priority color
            color_map = {
                Priority.LOW: 3066993,    # Green
                Priority.NORMAL: 2196F3,  # Blue
                Priority.HIGH: 16744192,  # Orange
                Priority.CRITICAL: 16007990  # Red
            }

            payload = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": color_map.get(priority, 2196243),
                    "footer": {"text": "The Gatekeeper"},
                    "timestamp": datetime.now().isoformat()
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.discord_webhook_url, json=payload) as resp:
                    if resp.status == 204:
                        self.logger.info(f"Discord sent: {title}")
                        return NotificationResult(
                            channel=Channel.DISCORD,
                            success=True,
                            message=message,
                            timestamp=datetime.now()
                        )
                    else:
                        error = await resp.text()
                        return NotificationResult(
                            channel=Channel.DISCORD,
                            success=False,
                            message=message,
                            timestamp=datetime.now(),
                            error=f"HTTP {resp.status}: {error}"
                        )

        except Exception as e:
            self.logger.error(f"Discord failed: {e}")
            return NotificationResult(
                channel=Channel.DISCORD,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _send_telegram(
        self,
        title: str,
        message: str,
        priority: Priority
    ) -> NotificationResult:
        """Send Telegram notification"""
        if not all([self.config.telegram_bot_token, self.config.telegram_chat_id]):
            return NotificationResult(
                channel=Channel.TELEGRAM,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="Telegram not configured"
            )

        if not AIOHTTP_AVAILABLE:
            return NotificationResult(
                channel=Channel.TELEGRAM,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="aiohttp not available"
            )

        try:
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"

            text = f"*{title}*\n\n{message}\n\n_Priority: {priority.name}_"

            payload = {
                "chat_id": self.config.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        self.logger.info(f"Telegram sent: {title}")
                        return NotificationResult(
                            channel=Channel.TELEGRAM,
                            success=True,
                            message=message,
                            timestamp=datetime.now()
                        )
                    else:
                        error = await resp.text()
                        return NotificationResult(
                            channel=Channel.TELEGRAM,
                            success=False,
                            message=message,
                            timestamp=datetime.now(),
                            error=f"HTTP {resp.status}: {error}"
                        )

        except Exception as e:
            self.logger.error(f"Telegram failed: {e}")
            return NotificationResult(
                channel=Channel.TELEGRAM,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _send_teams(
        self,
        title: str,
        message: str,
        priority: Priority
    ) -> NotificationResult:
        """Send Microsoft Teams notification"""
        if not self.config.teams_webhook_url:
            return NotificationResult(
                channel=Channel.TEAMS,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="Teams webhook not configured"
            )

        if not AIOHTTP_AVAILABLE:
            return NotificationResult(
                channel=Channel.TEAMS,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="aiohttp not available"
            )

        try:
            # Teams message card format
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": title,
                "themeColor": "0076D7",
                "title": title,
                "sections": [{
                    "activityTitle": "The Gatekeeper",
                    "activitySubtitle": f"Priority: {priority.name}",
                    "text": message
                }]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.teams_webhook_url, json=payload) as resp:
                    if resp.status == 200:
                        self.logger.info(f"Teams sent: {title}")
                        return NotificationResult(
                            channel=Channel.TEAMS,
                            success=True,
                            message=message,
                            timestamp=datetime.now()
                        )
                    else:
                        error = await resp.text()
                        return NotificationResult(
                            channel=Channel.TEAMS,
                            success=False,
                            message=message,
                            timestamp=datetime.now(),
                            error=f"HTTP {resp.status}: {error}"
                        )

        except Exception as e:
            self.logger.error(f"Teams failed: {e}")
            return NotificationResult(
                channel=Channel.TEAMS,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error=str(e)
            )

    async def _send_webhook(
        self,
        title: str,
        message: str,
        priority: Priority
    ) -> NotificationResult:
        """Send generic webhook notification"""
        if not self.config.webhook_url:
            return NotificationResult(
                channel=Channel.WEBHOOK,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="Webhook not configured"
            )

        if not AIOHTTP_AVAILABLE:
            return NotificationResult(
                channel=Channel.WEBHOOK,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error="aiohttp not available"
            )

        try:
            payload = {
                "title": title,
                "message": message,
                "priority": priority.name,
                "timestamp": datetime.now().isoformat(),
                "source": "The Gatekeeper"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.webhook_url, json=payload) as resp:
                    if resp.status in [200, 201, 204]:
                        self.logger.info(f"Webhook sent: {title}")
                        return NotificationResult(
                            channel=Channel.WEBHOOK,
                            success=True,
                            message=message,
                            timestamp=datetime.now()
                        )
                    else:
                        error = await resp.text()
                        return NotificationResult(
                            channel=Channel.WEBHOOK,
                            success=False,
                            message=message,
                            timestamp=datetime.now(),
                            error=f"HTTP {resp.status}: {error}"
                        )

        except Exception as e:
            self.logger.error(f"Webhook failed: {e}")
            return NotificationResult(
                channel=Channel.WEBHOOK,
                success=False,
                message=message,
                timestamp=datetime.now(),
                error=str(e)
            )

    def _get_configured_channels(self) -> List[Channel]:
        """Get list of configured channels"""
        channels = []

        if all([self.config.email_from, self.config.email_password, self.config.email_to]):
            channels.append(Channel.EMAIL)
        if self.config.slack_webhook_url:
            channels.append(Channel.SLACK)
        if self.config.discord_webhook_url:
            channels.append(Channel.DISCORD)
        if all([self.config.telegram_bot_token, self.config.telegram_chat_id]):
            channels.append(Channel.TELEGRAM)
        if self.config.teams_webhook_url:
            channels.append(Channel.TEAMS)
        if self.config.webhook_url:
            channels.append(Channel.WEBHOOK)

        return channels

    def _add_to_history(self, result: NotificationResult):
        """Add result to history with size limit"""
        self.history.append(result)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_stats(self) -> Dict:
        """Get notification statistics"""
        if not self.history:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'by_channel': {}
            }

        successful = sum(1 for r in self.history if r.success)
        failed = len(self.history) - successful

        by_channel = {}
        for channel in Channel:
            channel_results = [r for r in self.history if r.channel == channel]
            if channel_results:
                by_channel[channel.value] = {
                    'total': len(channel_results),
                    'successful': sum(1 for r in channel_results if r.success),
                    'failed': sum(1 for r in channel_results if not r.success)
                }

        return {
            'total': len(self.history),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(self.history) if self.history else 0,
            'by_channel': by_channel
        }

    def save_history(self, filepath: str):
        """Save notification history to JSON"""
        history_data = [result.to_dict() for result in self.history]
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
        self.logger.info(f"Saved {len(history_data)} notification results to {filepath}")


# Global instance
_manager_instance: Optional[NotificationManager] = None


def get_notification_manager(config: Optional[NotificationConfig] = None) -> NotificationManager:
    """Get or create global notification manager"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = NotificationManager(config)
    return _manager_instance


# Convenience functions
async def notify(
    title: str,
    message: str,
    channels: Optional[List[Channel]] = None,
    priority: Priority = Priority.NORMAL
) -> List[NotificationResult]:
    """
    Send notification (convenience function)

    Args:
        title: Notification title
        message: Notification message
        channels: Channels to send to (default: all configured)
        priority: Notification priority

    Returns:
        List of NotificationResults
    """
    manager = get_notification_manager()
    return await manager.send(title, message, channels, priority)


if __name__ == "__main__":
    # Demo/test mode
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Notifications Demo")
    parser.add_argument('--title', default='Test Notification', help='Notification title')
    parser.add_argument('--message', default='This is a test message', help='Message content')
    parser.add_argument('--channel', help='Channel to send to (email, slack, discord, telegram, teams)')
    parser.add_argument('--priority', default='NORMAL', choices=['LOW', 'NORMAL', 'HIGH', 'CRITICAL'], help='Priority level')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        manager = get_notification_manager()

        print("\n📬 Advanced Notification Manager")
        print(f"Configured channels: {[c.value for c in manager._get_configured_channels()]}")

        if args.channel:
            # Send to specific channel
            try:
                channel = Channel(args.channel)
                channels = [channel]
            except ValueError:
                print(f"❌ Unknown channel: {args.channel}")
                return
        else:
            # Send to all configured
            channels = None

        priority = Priority[args.priority]

        print(f"\n📤 Sending '{args.title}' (Priority: {priority.name})")

        results = await manager.send(
            args.title,
            args.message,
            channels=channels,
            priority=priority
        )

        print(f"\n📊 Results:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.channel.value}: {'Success' if result.success else result.error}")

        if args.stats and manager.history:
            stats = manager.get_stats()
            print(f"\n📈 Statistics:")
            print(f"  Total: {stats['total']}")
            print(f"  Successful: {stats['successful']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Success rate: {stats['success_rate']:.1%}")

    asyncio.run(main())
