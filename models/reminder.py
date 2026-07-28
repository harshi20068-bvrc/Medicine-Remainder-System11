"""
Reminder Model for generating dose schedules and tracking Taken / Missed statuses.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from database.db_manager import get_db
from models.medicine import MedicineModel


class ReminderModel:
    """Handles dose schedule generation, status updates, and history search/filter."""

    @classmethod
    def generate_daily_reminders(cls, user_id: int, target_date_str: Optional[str] = None) -> None:
        """Generates reminder log entries for active medicines for a given target date (default today)."""
        if not target_date_str:
            target_date_str = date.today().strftime("%Y-%m-%d")

        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        medicines = MedicineModel.get_user_medicines(user_id, active_only=True)
        db = get_db()

        for med in medicines:
            start_dt = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
            if med['end_date']:
                end_dt = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
            else:
                end_dt = date(2099, 12, 31)

            # Check if target date falls within medicine schedule range
            if not (start_dt <= target_dt <= end_dt):
                continue

            # Check frequency constraints
            freq = med['frequency'].strip()
            should_schedule = False

            if freq == "Daily" or freq == "As Needed":
                should_schedule = True
            elif freq == "Weekly":
                # Schedule on the same day of week as start_date
                if target_dt.weekday() == start_dt.weekday():
                    should_schedule = True
            elif freq.startswith("Every "):
                # Parse e.g. "Every 2 Days"
                try:
                    interval_days = int(freq.split()[1])
                    if (target_dt - start_dt).days % interval_days == 0:
                        should_schedule = True
                except (IndexError, ValueError):
                    should_schedule = True
            else:
                should_schedule = True

            if not should_schedule:
                continue

            # Parse times string (e.g. "08:00 AM, 02:00 PM" or "08:00, 14:00")
            time_list = [t.strip() for t in med['times'].split(",") if t.strip()]

            for t_str in time_list:
                # Normalize time format to HH:MM (24-hr) or standard format
                normalized_time = cls._normalize_time_str(t_str)

                try:
                    db.execute_commit("""
                        INSERT OR IGNORE INTO reminder_logs 
                        (user_id, medicine_id, scheduled_date, scheduled_time, status)
                        VALUES (?, ?, ?, ?, 'Pending')
                    """, (user_id, med['id'], target_date_str, normalized_time))
                except Exception:
                    pass

    @staticmethod
    def _normalize_time_str(t_str: str) -> str:
        """Converts time strings like '8:00 AM' or '14:00' to standard 24-hr format HH:MM."""
        t_str = t_str.strip()
        for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M", "%I %p", "%H:%M:%S"):
            try:
                dt = datetime.strptime(t_str, fmt)
                return dt.strftime("%H:%M")
            except ValueError:
                pass
        return t_str

    @classmethod
    def mark_status(cls, log_id: int, user_id: int, status: str, notes: str = "") -> Tuple[bool, str]:
        """Marks a reminder log as 'Taken' or 'Missed' with execution timestamp."""
        if status not in ('Taken', 'Missed', 'Pending'):
            return False, "Invalid status."

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        try:
            db.execute_commit("""
                UPDATE reminder_logs
                SET status = ?, marked_at = ?, notes = ?
                WHERE id = ? AND user_id = ?
            """, (status, now_str, notes.strip(), log_id, user_id))
            return True, f"Reminder marked as {status}."
        except Exception as e:
            return False, f"Failed to update status: {str(e)}"

    @classmethod
    def get_upcoming_reminders(cls, user_id: int, target_date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves reminders for dashboard display."""
        if not target_date_str:
            target_date_str = date.today().strftime("%Y-%m-%d")

        # First ensure logs exist for target date
        cls.generate_daily_reminders(user_id, target_date_str)
        cls.auto_update_missed_past_logs(user_id)

        db = get_db()
        rows = db.execute_query("""
            SELECT l.id as log_id, l.scheduled_date, l.scheduled_time, l.status, l.marked_at, l.notes as log_notes,
                   m.id as medicine_id, m.name as medicine_name, m.dosage, m.frequency, m.notes as med_notes
            FROM reminder_logs l
            JOIN medicines m ON l.medicine_id = m.id
            WHERE l.user_id = ? AND l.scheduled_date = ?
            ORDER BY l.scheduled_time ASC
        """, (user_id, target_date_str))

        return [dict(r) for r in rows]

    @classmethod
    def auto_update_missed_past_logs(cls, user_id: int) -> None:
        """Automatically updates pending logs from past dates or times to 'Missed'."""
        today_str = date.today().strftime("%Y-%m-%d")
        now_time_str = datetime.now().strftime("%H:%M")

        db = get_db()
        # Past dates
        db.execute_commit("""
            UPDATE reminder_logs
            SET status = 'Missed'
            WHERE user_id = ? AND status = 'Pending' AND scheduled_date < ?
        """, (user_id, today_str))

        # Today past times (grace period of 30 minutes)
        grace_dt = datetime.now() - timedelta(minutes=30)
        grace_time_str = grace_dt.strftime("%H:%M")
        db.execute_commit("""
            UPDATE reminder_logs
            SET status = 'Missed'
            WHERE user_id = ? AND status = 'Pending' AND scheduled_date = ? AND scheduled_time < ?
        """, (user_id, today_str, grace_time_str))

    @classmethod
    def search_and_filter_logs(cls, user_id: int, search_term: str = "",
                               status_filter: str = "All", start_date: str = "",
                               end_date: str = "") -> List[Dict[str, Any]]:
        """Performs multi-criteria search & filtering on reminder logs."""
        cls.auto_update_missed_past_logs(user_id)
        db = get_db()

        query = """
            SELECT l.id as log_id, l.scheduled_date, l.scheduled_time, l.status, l.marked_at, l.notes as log_notes,
                   m.id as medicine_id, m.name as medicine_name, m.dosage, m.frequency, m.notes as med_notes
            FROM reminder_logs l
            JOIN medicines m ON l.medicine_id = m.id
            WHERE l.user_id = ?
        """
        params: List[Any] = [user_id]

        if status_filter and status_filter != "All":
            query += " AND l.status = ?"
            params.append(status_filter)

        if start_date:
            query += " AND l.scheduled_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND l.scheduled_date <= ?"
            params.append(end_date)

        if search_term:
            term = f"%{search_term.strip()}%"
            query += " AND (m.name LIKE ? OR m.dosage LIKE ? OR m.notes LIKE ? OR l.notes LIKE ?)"
            params.extend([term, term, term, term])

        query += " ORDER BY l.scheduled_date DESC, l.scheduled_time DESC"

        rows = db.execute_query(query, tuple(params))
        return [dict(r) for r in rows]

    @classmethod
    def get_due_reminders_now(cls, user_id: int) -> List[Dict[str, Any]]:
        """Returns reminders that are due right now (for background notification worker)."""
        today_str = date.today().strftime("%Y-%m-%d")
        now_time_str = datetime.now().strftime("%H:%M")

        cls.generate_daily_reminders(user_id, today_str)

        db = get_db()
        rows = db.execute_query("""
            SELECT l.id as log_id, l.scheduled_date, l.scheduled_time, l.status,
                   m.name as medicine_name, m.dosage, m.notes as med_notes
            FROM reminder_logs l
            JOIN medicines m ON l.medicine_id = m.id
            WHERE l.user_id = ? AND l.scheduled_date = ? AND l.scheduled_time = ? AND l.status = 'Pending'
        """, (user_id, today_str, now_time_str))

        return [dict(r) for r in rows]
