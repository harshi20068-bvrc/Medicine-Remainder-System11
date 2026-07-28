"""
Popup alert dialog window triggered when a scheduled medicine reminder is due.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
from gui.theme import Theme
from models.reminder import ReminderModel


class ReminderPopupDialog(ctk.CTkToplevel):
    """Visual pop-up window alert for scheduled medicine doses."""

    def __init__(self, parent, reminder_data: Dict[str, Any], user_id: int, on_status_updated: Optional[Callable] = None):
        super().__init__(parent)

        self.reminder_data = reminder_data
        self.user_id = user_id
        self.on_status_updated = on_status_updated

        self.title("💊 Medicine Due Reminder!")
        self.geometry("460x320")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=Theme.BG_DARK)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (460 // 2)
        y = (self.winfo_screenheight() // 2) - (320 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the popup alert layout."""
        # Top banner frame
        header_frame = ctk.CTkFrame(self, fg_color=Theme.PRIMARY, corner_radius=0, height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="💊 TIME TO TAKE YOUR MEDICINE",
            font=Theme.FONT_SUBTITLE,
            text_color="#FFFFFF"
        )
        title_lbl.pack(expand=True)

        # Main content card
        card_frame = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, corner_radius=12)
        card_frame.pack(fill="both", expand=True, padx=20, pady=15)

        med_name = self.reminder_data.get('medicine_name', 'Medicine')
        dosage = self.reminder_data.get('dosage', '1 dose')
        time_str = self.reminder_data.get('scheduled_time', '')
        notes = self.reminder_data.get('med_notes', '')

        # Medicine Name
        name_lbl = ctk.CTkLabel(
            card_frame,
            text=med_name,
            font=("Segoe UI", 20, "bold"),
            text_color=Theme.ACCENT
        )
        name_lbl.pack(anchor="w", padx=20, pady=(15, 5))

        # Dosage & Time Info
        info_str = f"Dosage: {dosage}   •   Scheduled Time: {time_str}"
        info_lbl = ctk.CTkLabel(
            card_frame,
            text=info_str,
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_MAIN
        )
        info_lbl.pack(anchor="w", padx=20, pady=2)

        # Notes if available
        if notes:
            notes_lbl = ctk.CTkLabel(
                card_frame,
                text=f"Instructions: {notes}",
                font=Theme.FONT_BODY,
                text_color=Theme.TEXT_MUTED
            )
            notes_lbl.pack(anchor="w", padx=20, pady=5)

        # Buttons frame
        btn_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(15, 10), side="bottom")

        btn_taken = ctk.CTkButton(
            btn_frame,
            text="✔ Mark as Taken",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.COLOR_TAKEN,
            hover_color="#059669",
            text_color="#FFFFFF",
            corner_radius=8,
            height=36,
            command=self._mark_taken
        )
        btn_taken.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_missed = ctk.CTkButton(
            btn_frame,
            text="✖ Mark as Missed",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.COLOR_MISSED,
            hover_color="#DC2626",
            text_color="#FFFFFF",
            corner_radius=8,
            height=36,
            command=self._mark_missed
        )
        btn_missed.pack(side="right", expand=True, fill="x", padx=(5, 0))

    def _mark_taken(self) -> None:
        """Action for Mark Taken button."""
        log_id = self.reminder_data.get('log_id')
        if log_id:
            ReminderModel.mark_status(log_id, self.user_id, 'Taken')
        if self.on_status_updated:
            self.on_status_updated()
        self.destroy()

    def _mark_missed(self) -> None:
        """Action for Mark Missed button."""
        log_id = self.reminder_data.get('log_id')
        if log_id:
            ReminderModel.mark_status(log_id, self.user_id, 'Missed')
        if self.on_status_updated:
            self.on_status_updated()
        self.destroy()
