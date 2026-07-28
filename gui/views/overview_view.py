"""
Overview / Main Dashboard Tab View.
Displays metric summary cards and quick access upcoming dose list.
"""

import customtkinter as ctk
from datetime import date
from typing import Dict, Any, Callable
from gui.theme import Theme
from models.medicine import MedicineModel
from models.reminder import ReminderModel
from utils.reporter import ReportGenerator


class OverviewView(ctk.CTkFrame):
    """Overview dashboard view with metric stat cards and quick dose actions."""

    def __init__(self, parent, user_id: int, nav_callback: Callable[[str], None]):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self.nav_callback = nav_callback

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Constructs the layout for the overview tab."""
        # Top Title Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Dashboard Overview",
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_MAIN
        )
        title_lbl.pack(side="left")

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text=f"Today is {date.today().strftime('%B %d, %Y')}",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED
        )
        subtitle_lbl.pack(side="right")

        # Stats Cards Grid Container
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_col")

        # Stat Card Widgets
        self.card_active = self._create_stat_card(self.stats_frame, 0, "Active Medicines", "0", Theme.ACCENT)
        self.card_today = self._create_stat_card(self.stats_frame, 1, "Today's Doses", "0", Theme.PRIMARY_LIGHT)
        self.card_adherence = self._create_stat_card(self.stats_frame, 2, "Adherence Rate", "0%", Theme.COLOR_TAKEN)
        self.card_missed = self._create_stat_card(self.stats_frame, 3, "Missed Doses", "0", Theme.COLOR_MISSED)

        # Quick Actions Bar
        actions_frame = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, corner_radius=12)
        actions_frame.pack(fill="x", padx=20, pady=15)

        act_title = ctk.CTkLabel(actions_frame, text="Quick Actions:", font=Theme.FONT_HEADER, text_color=Theme.TEXT_MAIN)
        act_title.pack(side="left", padx=15, pady=10)

        btn_add = ctk.CTkButton(
            actions_frame,
            text="➕ Add New Medicine",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            command=lambda: self.nav_callback("medicines")
        )
        btn_add.pack(side="left", padx=10, pady=10)

        btn_schedule = ctk.CTkButton(
            actions_frame,
            text="📅 View Full Schedule",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            hover_color=Theme.INPUT_BG,
            corner_radius=8,
            command=lambda: self.nav_callback("schedule")
        )
        btn_schedule.pack(side="left", padx=10, pady=10)

        btn_history = ctk.CTkButton(
            actions_frame,
            text="📊 History & Reports",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            hover_color=Theme.INPUT_BG,
            corner_radius=8,
            command=lambda: self.nav_callback("history")
        )
        btn_history.pack(side="left", padx=10, pady=10)

        # Today's Scheduled Reminders Section
        section_title = ctk.CTkLabel(
            self,
            text="Today's Scheduled Reminders",
            font=Theme.FONT_SUBTITLE,
            text_color=Theme.TEXT_MAIN
        )
        section_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=5)

    def _create_stat_card(self, parent, col: int, label: str, default_val: str, color: str) -> Dict[str, Any]:
        """Helper to render a uniform stat metric card."""
        card = ctk.CTkFrame(parent, fg_color=Theme.CARD_BG, corner_radius=12, border_width=1, border_color=Theme.CARD_HOVER)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")

        lbl_title = ctk.CTkLabel(card, text=label, font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED)
        lbl_title.pack(anchor="w", padx=15, pady=(12, 2))

        val_lbl = ctk.CTkLabel(card, text=default_val, font=("Segoe UI", 22, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=15, pady=(0, 12))

        return {"val_lbl": val_lbl}

    def refresh(self) -> None:
        """Refreshes metrics and today's dose cards."""
        # 1. Update stats
        meds = MedicineModel.get_user_medicines(self.user_id, active_only=True)
        self.card_active['val_lbl'].configure(text=str(len(meds)))

        metrics = ReportGenerator.calculate_adherence_metrics(self.user_id)
        today_reminders = ReminderModel.get_upcoming_reminders(self.user_id)

        self.card_today['val_lbl'].configure(text=str(len(today_reminders)))
        self.card_adherence['val_lbl'].configure(text=f"{metrics['adherence_rate']}%")
        self.card_missed['val_lbl'].configure(text=str(metrics['missed_doses']))

        # 2. Re-render scroll list
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        if not today_reminders:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="🎉 No reminders scheduled for today! Enjoy your day.",
                font=Theme.FONT_BODY,
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return

        for rem in today_reminders:
            self._render_dose_card(rem)

    def _render_dose_card(self, rem: Dict[str, Any]) -> None:
        """Renders a single dose item card."""
        card = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.CARD_BG, corner_radius=10, border_width=1, border_color=Theme.CARD_HOVER)
        card.pack(fill="x", pady=6)

        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.pack(side="left", padx=15, pady=12, fill="both", expand=True)

        time_lbl = ctk.CTkLabel(
            left_frame,
            text=f"⏰ {rem['scheduled_time']}",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.ACCENT
        )
        time_lbl.pack(anchor="w")

        name_lbl = ctk.CTkLabel(
            left_frame,
            text=f"{rem['medicine_name']}  ({rem['dosage']})",
            font=Theme.FONT_HEADER,
            text_color=Theme.TEXT_MAIN
        )
        name_lbl.pack(anchor="w", pady=(2, 0))

        if rem.get('med_notes'):
            notes_lbl = ctk.CTkLabel(
                left_frame,
                text=f"Notes: {rem['med_notes']}",
                font=Theme.FONT_SMALL,
                text_color=Theme.TEXT_MUTED
            )
            notes_lbl.pack(anchor="w", pady=(2, 0))

        # Status badge & action buttons
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=12)

        st = rem['status']
        st_color = Theme.get_status_color(st)

        st_badge = ctk.CTkLabel(
            right_frame,
            text=f" {st.upper()} ",
            font=Theme.FONT_BODY_BOLD,
            fg_color=st_color,
            text_color="#FFFFFF",
            corner_radius=6
        )
        st_badge.pack(side="left", padx=(0, 10))

        if st == 'Pending':
            btn_take = ctk.CTkButton(
                right_frame,
                text="Take",
                width=65,
                height=30,
                font=Theme.FONT_BODY_BOLD,
                fg_color=Theme.COLOR_TAKEN,
                hover_color="#059669",
                command=lambda l_id=rem['log_id']: self._mark_status(l_id, 'Taken')
            )
            btn_take.pack(side="left", padx=3)

            btn_miss = ctk.CTkButton(
                right_frame,
                text="Miss",
                width=65,
                height=30,
                font=Theme.FONT_BODY_BOLD,
                fg_color=Theme.COLOR_MISSED,
                hover_color="#DC2626",
                command=lambda l_id=rem['log_id']: self._mark_status(l_id, 'Missed')
            )
            btn_miss.pack(side="left", padx=3)

    def _mark_status(self, log_id: int, status: str) -> None:
        """Marks reminder status and refreshes view."""
        ReminderModel.mark_status(log_id, self.user_id, status)
        self.refresh()
