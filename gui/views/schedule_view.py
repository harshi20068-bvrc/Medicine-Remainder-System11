"""
Schedule View for upcoming and past medicine reminders.
Allows interactive status tracking (Taken / Missed).
"""

import customtkinter as ctk
from datetime import date, timedelta
from typing import Dict, Any
from gui.theme import Theme
from models.reminder import ReminderModel


class ScheduleView(ctk.CTkFrame):
    """View displaying scheduled medicine reminders with status controls."""

    def __init__(self, parent, user_id: int):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self.selected_date = date.today().strftime("%Y-%m-%d")

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Constructs layout."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="Upcoming Reminders Schedule", font=Theme.FONT_TITLE, text_color=Theme.TEXT_MAIN)
        title.pack(side="left")

        # Date Navigator bar
        date_bar = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, corner_radius=10)
        date_bar.pack(fill="x", padx=20, pady=10)

        btn_today = ctk.CTkButton(
            date_bar,
            text="Today",
            width=80,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._select_today
        )
        btn_today.pack(side="left", padx=10, pady=10)

        btn_tomorrow = ctk.CTkButton(
            date_bar,
            text="Tomorrow",
            width=90,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            hover_color=Theme.INPUT_BG,
            command=self._select_tomorrow
        )
        btn_tomorrow.pack(side="left", padx=5, pady=10)

        ctk.CTkLabel(date_bar, text="Date (YYYY-MM-DD):", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(side="left", padx=(20, 5))

        self.entry_date = ctk.CTkEntry(date_bar, width=120, font=Theme.FONT_BODY)
        self.entry_date.insert(0, self.selected_date)
        self.entry_date.pack(side="left", padx=5)

        btn_filter = ctk.CTkButton(
            date_bar,
            text="🔍 Go",
            width=60,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY_LIGHT,
            command=self._on_custom_date_go
        )
        btn_filter.pack(side="left", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _select_today(self) -> None:
        """Selects today's date."""
        self.selected_date = date.today().strftime("%Y-%m-%d")
        self.entry_date.delete(0, 'end')
        self.entry_date.insert(0, self.selected_date)
        self.refresh()

    def _select_tomorrow(self) -> None:
        """Selects tomorrow's date."""
        self.selected_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.entry_date.delete(0, 'end')
        self.entry_date.insert(0, self.selected_date)
        self.refresh()

    def _on_custom_date_go(self) -> None:
        """Applies custom date filter."""
        d_str = self.entry_date.get().strip()
        if d_str:
            self.selected_date = d_str
            self.refresh()

    def refresh(self) -> None:
        """Refreshes reminder dose items for selected date."""
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        reminders = ReminderModel.get_upcoming_reminders(self.user_id, self.selected_date)
        if not reminders:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text=f"No scheduled medicine reminders for {self.selected_date}.",
                font=Theme.FONT_BODY,
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.pack(pady=50)
            return

        for rem in reminders:
            self._render_reminder_card(rem)

    def _render_reminder_card(self, rem: Dict[str, Any]) -> None:
        """Renders a single dose item."""
        card = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.CARD_BG, corner_radius=10, border_width=1, border_color=Theme.CARD_HOVER)
        card.pack(fill="x", pady=6)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=15, pady=12, fill="both", expand=True)

        time_lbl = ctk.CTkLabel(left, text=f"⏰ Scheduled Time: {rem['scheduled_time']}", font=Theme.FONT_BODY_BOLD, text_color=Theme.ACCENT)
        time_lbl.pack(anchor="w")

        name_lbl = ctk.CTkLabel(left, text=f"💊 {rem['medicine_name']} ({rem['dosage']})", font=Theme.FONT_HEADER, text_color=Theme.TEXT_MAIN)
        name_lbl.pack(anchor="w", pady=(2, 0))

        if rem.get('med_notes'):
            notes_lbl = ctk.CTkLabel(left, text=f"Instructions: {rem['med_notes']}", font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED)
            notes_lbl.pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=15, pady=12)

        st = rem['status']
        st_color = Theme.get_status_color(st)

        st_lbl = ctk.CTkLabel(
            right,
            text=f" {st.upper()} ",
            font=Theme.FONT_BODY_BOLD,
            fg_color=st_color,
            text_color="#FFFFFF",
            corner_radius=6
        )
        st_lbl.pack(side="left", padx=(0, 10))

        btn_take = ctk.CTkButton(
            right,
            text="✔ Taken",
            width=75,
            height=32,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.COLOR_TAKEN,
            hover_color="#059669",
            command=lambda l_id=rem['log_id']: self._mark_status(l_id, 'Taken')
        )
        btn_take.pack(side="left", padx=3)

        btn_miss = ctk.CTkButton(
            right,
            text="✖ Missed",
            width=75,
            height=32,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.COLOR_MISSED,
            hover_color="#DC2626",
            command=lambda l_id=rem['log_id']: self._mark_status(l_id, 'Missed')
        )
        btn_miss.pack(side="left", padx=3)

    def _mark_status(self, log_id: int, status: str) -> None:
        """Marks status and reloads list."""
        ReminderModel.mark_status(log_id, self.user_id, status)
        self.refresh()
