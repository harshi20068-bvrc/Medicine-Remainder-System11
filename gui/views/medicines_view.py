"""
Medicine Management Tab View.
Provides Add, Edit, and Delete medicine management features.
"""

import customtkinter as ctk
from datetime import date
from typing import Dict, Any, Optional
from gui.theme import Theme
from models.medicine import MedicineModel


class MedicineFormModal(ctk.CTkToplevel):
    """Modal dialog window for Adding or Editing Medicine details."""

    def __init__(self, parent, user_id: int, med_data: Optional[Dict[str, Any]] = None, on_saved: Optional[callable] = None):
        super().__init__(parent)
        self.user_id = user_id
        self.med_data = med_data
        self.on_saved = on_saved

        self.title("Edit Medicine" if med_data else "Add New Medicine")
        self.geometry("500x620")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=Theme.BG_DARK)

        # Center on parent screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (620 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_form()

    def _build_form(self) -> None:
        """Builds form input fields."""
        # Top banner
        header = ctk.CTkFrame(self, fg_color=Theme.PRIMARY, height=50, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        lbl = ctk.CTkLabel(
            header,
            text="💊 " + ("Edit Medicine Details" if self.med_data else "Add New Medicine"),
            font=Theme.FONT_SUBTITLE,
            text_color="#FFFFFF"
        )
        lbl.pack(expand=True)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=15)

        # Medicine Name
        ctk.CTkLabel(scroll, text="Medicine Name *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        self.entry_name = ctk.CTkEntry(scroll, placeholder_text="e.g., Paracetamol, Amoxicillin", font=Theme.FONT_BODY)
        self.entry_name.pack(fill="x", pady=(0, 10))

        # Dosage
        ctk.CTkLabel(scroll, text="Dosage *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        self.entry_dosage = ctk.CTkEntry(scroll, placeholder_text="e.g., 500 mg, 1 Tablet, 5 ml", font=Theme.FONT_BODY)
        self.entry_dosage.pack(fill="x", pady=(0, 10))

        # Start Date & End Date
        date_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 10))

        start_sub = ctk.CTkFrame(date_frame, fg_color="transparent")
        start_sub.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkLabel(start_sub, text="Start Date (YYYY-MM-DD) *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w")
        self.entry_start = ctk.CTkEntry(start_sub, font=Theme.FONT_BODY)
        self.entry_start.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_start.pack(fill="x", pady=(2, 0))

        end_sub = ctk.CTkFrame(date_frame, fg_color="transparent")
        end_sub.pack(side="right", expand=True, fill="x", padx=(5, 0))
        ctk.CTkLabel(end_sub, text="End Date (Optional)", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w")
        self.entry_end = ctk.CTkEntry(end_sub, placeholder_text="YYYY-MM-DD", font=Theme.FONT_BODY)
        self.entry_end.pack(fill="x", pady=(2, 0))

        # Scheduled Time(s)
        ctk.CTkLabel(scroll, text="Scheduled Time(s) (Comma separated) *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        self.entry_times = ctk.CTkEntry(scroll, placeholder_text="e.g., 08:00 AM, 02:00 PM, 08:00 PM", font=Theme.FONT_BODY)
        self.entry_times.pack(fill="x", pady=(0, 10))

        # Frequency
        ctk.CTkLabel(scroll, text="Frequency *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        self.combo_freq = ctk.CTkComboBox(
            scroll,
            values=["Daily", "Weekly", "Every 2 Days", "Every 3 Days", "As Needed"],
            font=Theme.FONT_BODY
        )
        self.combo_freq.set("Daily")
        self.combo_freq.pack(fill="x", pady=(0, 10))

        # Notes / Instructions
        ctk.CTkLabel(scroll, text="Notes / Special Instructions", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(5, 2))
        self.entry_notes = ctk.CTkTextbox(scroll, height=70, font=Theme.FONT_BODY)
        self.entry_notes.pack(fill="x", pady=(0, 10))

        # Error label
        self.lbl_error = ctk.CTkLabel(scroll, text="", font=Theme.FONT_BODY, text_color=Theme.COLOR_MISSED)
        self.lbl_error.pack(pady=5)

        # Submit Button
        btn_save = ctk.CTkButton(
            scroll,
            text="💾 Save Medicine Details",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            height=40,
            command=self._save
        )
        btn_save.pack(fill="x", pady=(10, 5))

        # Fill values if editing
        if self.med_data:
            self.entry_name.insert(0, self.med_data.get('name', ''))
            self.entry_dosage.insert(0, self.med_data.get('dosage', ''))
            if self.med_data.get('start_date'):
                self.entry_start.delete(0, 'end')
                self.entry_start.insert(0, self.med_data.get('start_date'))
            if self.med_data.get('end_date'):
                self.entry_end.insert(0, self.med_data.get('end_date'))
            self.entry_times.insert(0, self.med_data.get('times', ''))
            if self.med_data.get('frequency'):
                self.combo_freq.set(self.med_data.get('frequency'))
            if self.med_data.get('notes'):
                self.entry_notes.insert("1.0", self.med_data.get('notes'))

    def _save(self) -> None:
        """Validates and saves the medicine."""
        name = self.entry_name.get().strip()
        dosage = self.entry_dosage.get().strip()
        start = self.entry_start.get().strip()
        end = self.entry_end.get().strip()
        times = self.entry_times.get().strip()
        freq = self.combo_freq.get().strip()
        notes = self.entry_notes.get("1.0", "end").strip()

        if not name or not dosage or not start or not times:
            self.lbl_error.configure(text="Please fill in all required fields (*).")
            return

        if self.med_data:
            success, msg = MedicineModel.update_medicine(
                medicine_id=self.med_data['id'],
                user_id=self.user_id,
                name=name,
                dosage=dosage,
                start_date=start,
                end_date=end,
                times=times,
                frequency=freq,
                notes=notes
            )
        else:
            success, msg, _ = MedicineModel.add_medicine(
                user_id=self.user_id,
                name=name,
                dosage=dosage,
                start_date=start,
                end_date=end,
                times=times,
                frequency=freq,
                notes=notes
            )

        if success:
            if self.on_saved:
                self.on_saved()
            self.destroy()
        else:
            self.lbl_error.configure(text=msg)


class MedicinesView(ctk.CTkFrame):
    """Medicines view displaying medicine cards and management actions."""

    def __init__(self, parent, user_id: int):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Constructs layout."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="Medicine Details Management", font=Theme.FONT_TITLE, text_color=Theme.TEXT_MAIN)
        title.pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text="➕ Add New Medicine",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self._open_add_modal
        )
        btn_add.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self) -> None:
        """Refreshes medicine list cards."""
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        meds = MedicineModel.get_user_medicines(self.user_id)
        if not meds:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="No medicine records found. Click 'Add New Medicine' to create one!",
                font=Theme.FONT_BODY,
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.pack(pady=50)
            return

        for med in meds:
            self._render_med_card(med)

    def _render_med_card(self, med: Dict[str, Any]) -> None:
        """Renders a single medicine card."""
        card = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.CARD_BG, corner_radius=12, border_width=1, border_color=Theme.CARD_HOVER)
        card.pack(fill="x", pady=8)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        top_bar = ctk.CTkFrame(content, fg_color="transparent")
        top_bar.pack(fill="x")

        name_lbl = ctk.CTkLabel(top_bar, text=f"💊 {med['name']}", font=("Segoe UI", 18, "bold"), text_color=Theme.ACCENT)
        name_lbl.pack(side="left")

        dosage_badge = ctk.CTkLabel(
            top_bar,
            text=f" Dosage: {med['dosage']} ",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            text_color=Theme.TEXT_MAIN,
            corner_radius=6
        )
        dosage_badge.pack(side="left", padx=15)

        # Action Buttons
        btn_delete = ctk.CTkButton(
            top_bar,
            text="🗑 Delete",
            width=70,
            height=30,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.COLOR_MISSED,
            hover_color="#DC2626",
            command=lambda m_id=med['id']: self._delete_medicine(m_id)
        )
        btn_delete.pack(side="right", padx=(5, 0))

        btn_edit = ctk.CTkButton(
            top_bar,
            text="✏ Edit",
            width=70,
            height=30,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            hover_color=Theme.INPUT_BG,
            command=lambda m=med: self._open_edit_modal(m)
        )
        btn_edit.pack(side="right", padx=5)

        # Schedule details
        details_str = f"📅 Dates: {med['start_date']} to {med['end_date'] or 'Ongoing'}   •   ⏰ Times: {med['times']}   •   🔄 Frequency: {med['frequency']}"
        details_lbl = ctk.CTkLabel(content, text=details_str, font=Theme.FONT_BODY, text_color=Theme.TEXT_MAIN)
        details_lbl.pack(anchor="w", pady=(8, 2))

        if med.get('notes'):
            notes_lbl = ctk.CTkLabel(content, text=f"📝 Notes: {med['notes']}", font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED)
            notes_lbl.pack(anchor="w", pady=(2, 0))

    def _open_add_modal(self) -> None:
        """Opens Add Medicine modal dialog."""
        MedicineFormModal(self, self.user_id, on_saved=self.refresh)

    def _open_edit_modal(self, med: Dict[str, Any]) -> None:
        """Opens Edit Medicine modal dialog."""
        MedicineFormModal(self, self.user_id, med_data=med, on_saved=self.refresh)

    def _delete_medicine(self, medicine_id: int) -> None:
        """Deletes a medicine entry."""
        MedicineModel.delete_medicine(medicine_id, self.user_id)
        self.refresh()
