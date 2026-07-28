"""
Reminder Scheduler background daemon thread.
Periodically checks for due medicine reminders and triggers notifications.
"""

import time
import threading
from datetime import datetime
from typing import Callable, Optional, Set
from models.reminder import ReminderModel
from utils.notifier import NotificationManager


class ReminderScheduler:
    """Threaded background scheduler for medicine reminders."""

    def __init__(self, user_id: int, on_reminder_due_callback: Optional[Callable] = None, interval_sec: float = 10.0):
        self.user_id = user_id
        self.on_reminder_due_callback = on_reminder_due_callback
        self.interval_sec = interval_sec
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._notified_keys: Set[str] = set()

    def start(self) -> None:
        """Starts the scheduler thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stops the scheduler thread."""
        self.running = False

    def set_user_id(self, user_id: int) -> None:
        """Updates the active user ID for the scheduler."""
        self.user_id = user_id
        self._notified_keys.clear()

    def _run_loop(self) -> None:
        """Main background loop."""
        while self.running:
            try:
                if self.user_id:
                    self._check_reminders()
            except Exception as e:
                print(f"[Scheduler] Error checking reminders: {e}")
            
            time.sleep(self.interval_sec)

    def _check_reminders(self) -> None:
        """Checks for reminders due right now and triggers alerts."""
        due_list = ReminderModel.get_due_reminders_now(self.user_id)
        current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")

        for rem in due_list:
            key = f"{rem['log_id']}_{current_minute}"
            if key in self._notified_keys:
                continue

            self._notified_keys.add(key)

            # 1. Desktop toast notification
            NotificationManager.send_medicine_reminder(
                medicine_name=rem['medicine_name'],
                dosage=rem['dosage'],
                time_str=rem['scheduled_time'],
                notes=rem.get('med_notes', '')
            )

            # 2. GUI Popup window callback
            if self.on_reminder_due_callback:
                try:
                    self.on_reminder_due_callback(rem)
                except Exception as e:
                    print(f"[Scheduler] Error invoking UI callback: {e}")
