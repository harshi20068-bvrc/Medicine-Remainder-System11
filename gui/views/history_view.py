"""
History and Reports Tab View.
Provides multi-criteria search/filter, adherence statistics, and CSV/HTML report exporters.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Dict, Any, List
from gui.theme import Theme
from models.reminder import ReminderModel
from utils.reporter import ReportGenerator


class HistoryView(ctk.CTkFrame):
    """View displaying historical medicine logs with search, filter, and report generation."""

    def __init__(self, parent, user_id: int):
        super().__init__(parent, fg_color="transparent")
        self.user_id = user_id
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Constructs layout."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="Medicine History & Reports", font=Theme.FONT_TITLE, text_color=Theme.TEXT_MAIN)
        title.pack(side="left")

        # Report Export Buttons
        btn_csv = ctk.CTkButton(
            header,
            text="📥 Export CSV",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=34,
            command=self._export_csv
        )
        btn_csv.pack(side="right", padx=(5, 0))

        btn_html = ctk.CTkButton(
            header,
            text="📊 Export HTML Report",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY_LIGHT,
            hover_color=Theme.ACCENT,
            corner_radius=8,
            height=34,
            command=self._export_html
        )
        btn_html.pack(side="right", padx=5)

        # Adherence Summary Cards Bar
        self.summary_frame = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, corner_radius=12)
        self.summary_frame.pack(fill="x", padx=20, pady=10)
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_stat_rate = self._build_stat_item(self.summary_frame, 0, "ADHERENCE RATE", "0%", Theme.ACCENT)
        self.lbl_stat_taken = self._build_stat_item(self.summary_frame, 1, "TOTAL TAKEN", "0", Theme.COLOR_TAKEN)
        self.lbl_stat_missed = self._build_stat_item(self.summary_frame, 2, "TOTAL MISSED", "0", Theme.COLOR_MISSED)
        self.lbl_stat_pending = self._build_stat_item(self.summary_frame, 3, "PENDING DOSES", "0", Theme.COLOR_PENDING)

        # Search and Filter Control Bar
        filter_bar = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, corner_radius=10)
        filter_bar.pack(fill="x", padx=20, pady=10)

        # Search entry
        ctk.CTkLabel(filter_bar, text="🔍 Search:", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(side="left", padx=(15, 5), pady=10)
        self.entry_search = ctk.CTkEntry(filter_bar, placeholder_text="Medicine name, notes...", width=180, font=Theme.FONT_BODY)
        self.entry_search.pack(side="left", padx=5, pady=10)
        self.entry_search.bind("<Return>", lambda e: self.refresh())

        # Status Dropdown
        ctk.CTkLabel(filter_bar, text="Status:", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(side="left", padx=(15, 5), pady=10)
        self.combo_status = ctk.CTkComboBox(
            filter_bar,
            values=["All", "Taken", "Missed", "Pending"],
            width=110,
            font=Theme.FONT_BODY,
            command=lambda v: self.refresh()
        )
        self.combo_status.set("All")
        self.combo_status.pack(side="left", padx=5, pady=10)

        # Date Range inputs
        ctk.CTkLabel(filter_bar, text="From:", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(side="left", padx=(15, 5), pady=10)
        self.entry_from = ctk.CTkEntry(filter_bar, placeholder_text="YYYY-MM-DD", width=105, font=Theme.FONT_BODY)
        self.entry_from.pack(side="left", padx=5, pady=10)

        ctk.CTkLabel(filter_bar, text="To:", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(side="left", padx=(10, 5), pady=10)
        self.entry_to = ctk.CTkEntry(filter_bar, placeholder_text="YYYY-MM-DD", width=105, font=Theme.FONT_BODY)
        self.entry_to.pack(side="left", padx=5, pady=10)

        btn_apply = ctk.CTkButton(
            filter_bar,
            text="Filter",
            width=70,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.refresh
        )
        btn_apply.pack(side="left", padx=10, pady=10)

        btn_reset = ctk.CTkButton(
            filter_bar,
            text="Reset",
            width=65,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.CARD_HOVER,
            hover_color=Theme.INPUT_BG,
            command=self._reset_filters
        )
        btn_reset.pack(side="left", padx=2, pady=10)

        # Results scroll list
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _build_stat_item(self, parent, col: int, label: str, val: str, color: str) -> ctk.CTkLabel:
        """Helper to create summary stat items."""
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=col, padx=10, pady=12, sticky="ew")

        lbl = ctk.CTkLabel(box, text=label, font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED)
        lbl.pack()

        val_lbl = ctk.CTkLabel(box, text=val, font=("Segoe UI", 18, "bold"), text_color=color)
        val_lbl.pack(pady=(2, 0))

        return val_lbl

    def _reset_filters(self) -> None:
        """Resets search and filter controls."""
        self.entry_search.delete(0, 'end')
        self.combo_status.set("All")
        self.entry_from.delete(0, 'end')
        self.entry_to.delete(0, 'end')
        self.refresh()

    def refresh(self) -> None:
        """Applies filters and refreshes UI."""
        search = self.entry_search.get().strip()
        status = self.combo_status.get().strip()
        f_date = self.entry_from.get().strip()
        t_date = self.entry_to.get().strip()

        # Update summary statistics
        metrics = ReportGenerator.calculate_adherence_metrics(self.user_id, start_date=f_date, end_date=t_date)
        self.lbl_stat_rate.configure(text=f"{metrics['adherence_rate']}%")
        self.lbl_stat_taken.configure(text=str(metrics['taken_doses']))
        self.lbl_stat_missed.configure(text=str(metrics['missed_doses']))
        self.lbl_stat_pending.configure(text=str(metrics['pending_doses']))

        # Clear scroll list
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        logs = ReminderModel.search_and_filter_logs(
            user_id=self.user_id,
            search_term=search,
            status_filter=status,
            start_date=f_date,
            end_date=t_date
        )

        if not logs:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="No reminder history logs match your search and filter criteria.",
                font=Theme.FONT_BODY,
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return

        for log in logs:
            self._render_log_item(log)

    def _render_log_item(self, log: Dict[str, Any]) -> None:
        """Renders a single log entry row card."""
        card = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.CARD_BG, corner_radius=10, border_width=1, border_color=Theme.CARD_HOVER)
        card.pack(fill="x", pady=4)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=15, pady=10, fill="both", expand=True)

        date_lbl = ctk.CTkLabel(
            left,
            text=f"📅 {log['scheduled_date']} @ {log['scheduled_time']}",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_MUTED
        )
        date_lbl.pack(anchor="w")

        name_lbl = ctk.CTkLabel(
            left,
            text=f"💊 {log['medicine_name']}  ({log['dosage']})",
            font=Theme.FONT_HEADER,
            text_color=Theme.TEXT_MAIN
        )
        name_lbl.pack(anchor="w", pady=(2, 0))

        if log.get('marked_at'):
            action_lbl = ctk.CTkLabel(
                left,
                text=f"Marked on: {log['marked_at']}",
                font=Theme.FONT_SMALL,
                text_color=Theme.TEXT_MUTED
            )
            action_lbl.pack(anchor="w", pady=(1, 0))

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=15, pady=10)

        st = log['status']
        st_color = Theme.get_status_color(st)

        st_lbl = ctk.CTkLabel(
            right,
            text=f" {st.upper()} ",
            font=Theme.FONT_BODY_BOLD,
            fg_color=st_color,
            text_color="#FFFFFF",
            corner_radius=6
        )
        st_lbl.pack(side="right")

    def _export_csv(self) -> None:
        """Handles CSV report export."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")],
            title="Save Medicine History Report CSV"
        )
        if path:
            success = ReportGenerator.export_to_csv(
                user_id=self.user_id,
                filepath=path,
                search_term=self.entry_search.get().strip(),
                status_filter=self.combo_status.get().strip(),
                start_date=self.entry_from.get().strip(),
                end_date=self.entry_to.get().strip()
            )
            if success:
                messagebox.showinfo("Export Successful", f"History report exported successfully to:\n{path}")

    def _export_html(self) -> None:
        """Handles HTML report export."""
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Document", "*.html")],
            title="Save Medicine Adherence Report HTML"
        )
        if path:
            success = ReportGenerator.generate_html_report(
                user_id=self.user_id,
                filepath=path,
                search_term=self.entry_search.get().strip(),
                status_filter=self.combo_status.get().strip(),
                start_date=self.entry_from.get().strip(),
                end_date=self.entry_to.get().strip()
            )
            if success:
                messagebox.showinfo("Export Successful", f"HTML Report generated successfully to:\n{path}")
