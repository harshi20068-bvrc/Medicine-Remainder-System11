"""
Dashboard Window - Main Application Container.
Houses sidebar navigation, content views, and background reminder scheduler.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Dict, Any, Optional
from gui.theme import Theme
from gui.views.overview_view import OverviewView
from gui.views.medicines_view import MedicinesView
from gui.views.schedule_view import ScheduleView
from gui.views.history_view import HistoryView
from gui.components.popup_dialog import ReminderPopupDialog
from utils.scheduler import ReminderScheduler


class DashboardWindow(ctk.CTk):
    """Main Application Dashboard Window."""

    def __init__(self, user_data: Dict[str, Any], on_logout_callback: callable):
        super().__init__()
        self.user_data = user_data
        self.on_logout_callback = on_logout_callback
        self.current_view_name = "overview"

        self.title("Medicine Reminder System - Dashboard")
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(fg_color=Theme.BG_DARK)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.winfo_screenheight() // 2) - (720 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

        # Initialize Background Scheduler
        self.scheduler = ReminderScheduler(
            user_id=self.user_data['id'],
            on_reminder_due_callback=self._on_reminder_due
        )
        self.scheduler.start()

        # Protocol for graceful window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        """Constructs layout with sidebar and content area."""
        # Main Grid Container
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Sidebar Header (App Logo + User Profile Info)
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=15, pady=(20, 15))

        logo_lbl = ctk.CTkLabel(brand_frame, text="💊 MediRemind", font=("Segoe UI", 20, "bold"), text_color=Theme.ACCENT)
        logo_lbl.pack(anchor="w")

        username = self.user_data.get('full_name') or self.user_data.get('username')
        user_lbl = ctk.CTkLabel(brand_frame, text=f"👤 {username}", font=Theme.FONT_BODY, text_color=Theme.TEXT_MUTED)
        user_lbl.pack(anchor="w", pady=(2, 0))

        # Nav Buttons Container
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill="x", padx=15, pady=10)

        self.btn_overview = self._create_nav_button(nav_container, "🏠 Overview", lambda: self.show_view("overview"))
        self.btn_medicines = self._create_nav_button(nav_container, "💊 Medicines", lambda: self.show_view("medicines"))
        self.btn_schedule = self._create_nav_button(nav_container, "📅 Schedule", lambda: self.show_view("schedule"))
        self.btn_history = self._create_nav_button(nav_container, "📊 History & Reports", lambda: self.show_view("history"))

        # Logout Button at bottom
        btn_logout = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            hover_color=Theme.COLOR_MISSED,
            corner_radius=8,
            height=36,
            command=self._logout
        )
        btn_logout.pack(side="bottom", padx=15, pady=20, fill="x")

        # Main Content Area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")

        # Instantiate View Frames
        self.views: Dict[str, ctk.CTkFrame] = {
            "overview": OverviewView(self.content_area, self.user_data['id'], nav_callback=self.show_view),
            "medicines": MedicinesView(self.content_area, self.user_data['id']),
            "schedule": ScheduleView(self.content_area, self.user_data['id']),
            "history": HistoryView(self.content_area, self.user_data['id'])
        }

        # Display default view
        self.show_view("overview")

    def _create_nav_button(self, parent, text: str, command: callable) -> ctk.CTkButton:
        """Helper to construct uniform sidebar nav button."""
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=Theme.FONT_BODY_BOLD,
            anchor="w",
            fg_color="transparent",
            hover_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_MAIN,
            corner_radius=8,
            height=40,
            command=command
        )
        btn.pack(fill="x", pady=4)
        return btn

    def show_view(self, view_name: str) -> None:
        """Switches current active view."""
        self.current_view_name = view_name

        # Hide all views
        for v in self.views.values():
            v.pack_forget()

        # Reset nav button highlights
        self.btn_overview.configure(fg_color="transparent")
        self.btn_medicines.configure(fg_color="transparent")
        self.btn_schedule.configure(fg_color="transparent")
        self.btn_history.configure(fg_color="transparent")

        # Highlight selected nav button & show target view
        if view_name == "overview":
            self.btn_overview.configure(fg_color=Theme.PRIMARY)
        elif view_name == "medicines":
            self.btn_medicines.configure(fg_color=Theme.PRIMARY)
        elif view_name == "schedule":
            self.btn_schedule.configure(fg_color=Theme.PRIMARY)
        elif view_name == "history":
            self.btn_history.configure(fg_color=Theme.PRIMARY)

        target_view = self.views.get(view_name)
        if target_view:
            target_view.pack(fill="both", expand=True)
            if hasattr(target_view, "refresh"):
                target_view.refresh()

    def _on_reminder_due(self, reminder_data: Dict[str, Any]) -> None:
        """Callback invoked when a background scheduled reminder is due."""
        # Open interactive TopLevel popup dialog on GUI thread
        self.after(0, lambda: ReminderPopupDialog(
            parent=self,
            reminder_data=reminder_data,
            user_id=self.user_data['id'],
            on_status_updated=self._on_status_updated_from_popup
        ))

    def _on_status_updated_from_popup(self) -> None:
        """Refreshes the current active view after popup action."""
        active_view = self.views.get(self.current_view_name)
        if active_view and hasattr(active_view, "refresh"):
            active_view.refresh()

    def _logout(self) -> None:
        """Stops scheduler and logs out user."""
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
        self.destroy()
        self.on_logout_callback()

    def _on_close(self) -> None:
        """Window close handler."""
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
        self.destroy()
