"""
Gatekeeper Utils Package
========================
Enhanced utilities for production-grade Gatekeeper system
"""

__version__ = "1.0.0"

# Compressed JSON
from .compressed_json import (
    CompressedJSON,
    save_json_auto,
    load_json_auto
)

# Integrity Checking
from .integrity_checker import (
    IntegrityChecker,
    IntegrityError,
    verify_integrity
)

# Notifications
from .win10_notifications import (
    Win10Toast,
    SystemNotifier,
    get_notifier,
    notify_cleanup_started,
    notify_cleanup_completed,
    notify_disk_space,
    notify_compression,
    notify_integrity_failure
)

__all__ = [
    # Compressed JSON
    'CompressedJSON',
    'save_json_auto',
    'load_json_auto',

    # Integrity
    'IntegrityChecker',
    'IntegrityError',
    'verify_integrity',

    # Notifications
    'Win10Toast',
    'SystemNotifier',
    'get_notifier',
    'notify_cleanup_started',
    'notify_cleanup_completed',
    'notify_disk_space',
    'notify_compression',
    'notify_integrity_failure',
]
