"""
Notification Manager for sending desktop toast alerts and sound chimes.
"""

import sys
import os

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


class NotificationManager:
    """Sends native desktop notifications and sound alerts."""

    @staticmethod
    def send_notification(title: str, message: str, app_name: str = "Medicine Reminder") -> None:
        """Triggers a desktop toast notification and audio chime."""
        # 1. Play sound chime if on Windows
        if WINSOUND_AVAILABLE:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

        # 2. Trigger Plymouth / Plyer desktop notification
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name=app_name,
                    timeout=10
                )
                return
            except Exception as e:
                print(f"[Notifier] Notification error: {e}")

        # Fallback console print if notification backend failed
        print(f"[NOTIFICATION] {title}: {message}")

    @classmethod
    def send_medicine_reminder(cls, medicine_name: str, dosage: str, time_str: str, notes: str = "") -> None:
        """Formats and sends a medicine reminder notification."""
        title = f"💊 Medicine Reminder: {medicine_name}"
        msg = f"Time: {time_str}\nDosage: {dosage}"
        if notes:
            msg += f"\nNotes: {notes}"
        cls.send_notification(title, msg)
