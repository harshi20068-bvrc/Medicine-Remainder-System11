"""
Medicine Reminder System - Main Entry Point.
Initializes SQLite database and controls application lifecycle.
"""

import sys
import customtkinter as ctk
from database.db_manager import get_db
from gui.login_window import LoginWindow
from gui.dashboard_window import DashboardWindow


class MedicineReminderApp:
    """Main Application Controller managing login and dashboard transitions."""

    def __init__(self):
        # 1. Initialize SQLite Database
        print("[App] Initializing SQLite Database...")
        get_db()

        # 2. Configure CustomTkinter Appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.active_user = None
        self.login_window = None
        self.dashboard_window = None

    def run(self) -> None:
        """Starts the application by launching the login window."""
        self._show_login()

    def _show_login(self) -> None:
        """Launches the Login Window."""
        self.login_window = LoginWindow(on_login_success=self._on_login_success)
        self.login_window.mainloop()

    def _on_login_success(self, user_data: dict) -> None:
        """Callback on successful login."""
        self.active_user = user_data
        print(f"[App] User logged in: {user_data.get('username')}")

        # Transition to Dashboard Window
        self._show_dashboard()

    def _show_dashboard(self) -> None:
        """Launches the Dashboard Window."""
        self.dashboard_window = DashboardWindow(
            user_data=self.active_user,
            on_logout_callback=self._on_logout
        )
        self.dashboard_window.mainloop()

    def _on_logout(self) -> None:
        """Callback on user logout."""
        print("[App] User logged out.")
        self.active_user = None
        self._show_login()


if __name__ == "__main__":
    app = MedicineReminderApp()
    app.run()
