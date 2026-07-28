"""
Medicine Model for managing medicine details and CRUD operations.
"""

from typing import List, Dict, Any, Optional, Tuple
from database.db_manager import get_db


class MedicineModel:
    """Handles CRUD operations for user medicine details."""

    @classmethod
    def add_medicine(cls, user_id: int, name: str, dosage: str, start_date: str,
                     end_date: str, times: str, frequency: str, notes: str = "") -> Tuple[bool, str, Optional[int]]:
        """Adds a new medicine entry for a user."""
        name = name.strip()
        dosage = dosage.strip()
        start_date = start_date.strip()
        end_date = end_date.strip() if end_date else ""
        times = times.strip()
        frequency = frequency.strip()
        notes = notes.strip()

        if not name or not dosage or not start_date or not times:
            return False, "Medicine Name, Dosage, Start Date, and Time(s) are required.", None

        db = get_db()
        try:
            med_id = db.execute_commit("""
                INSERT INTO medicines (user_id, name, dosage, start_date, end_date, times, frequency, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, dosage, start_date, end_date, times, frequency, notes))

            return True, "Medicine added successfully!", med_id
        except Exception as e:
            return False, f"Error adding medicine: {str(e)}", None

    @classmethod
    def update_medicine(cls, medicine_id: int, user_id: int, name: str, dosage: str,
                        start_date: str, end_date: str, times: str, frequency: str,
                        notes: str = "", is_active: int = 1) -> Tuple[bool, str]:
        """Updates an existing medicine entry."""
        name = name.strip()
        dosage = dosage.strip()
        start_date = start_date.strip()
        times = times.strip()

        if not name or not dosage or not start_date or not times:
            return False, "Medicine Name, Dosage, Start Date, and Time(s) are required."

        db = get_db()
        try:
            db.execute_commit("""
                UPDATE medicines 
                SET name = ?, dosage = ?, start_date = ?, end_date = ?, times = ?, 
                    frequency = ?, notes = ?, is_active = ?
                WHERE id = ? AND user_id = ?
            """, (name, dosage, start_date, end_date, times, frequency, notes, is_active, medicine_id, user_id))

            return True, "Medicine updated successfully!"
        except Exception as e:
            return False, f"Error updating medicine: {str(e)}"

    @classmethod
    def delete_medicine(cls, medicine_id: int, user_id: int) -> Tuple[bool, str]:
        """Deletes a medicine entry and associated reminder logs."""
        db = get_db()
        try:
            db.execute_commit("DELETE FROM medicines WHERE id = ? AND user_id = ?", (medicine_id, user_id))
            return True, "Medicine deleted successfully!"
        except Exception as e:
            return False, f"Error deleting medicine: {str(e)}"

    @classmethod
    def get_user_medicines(cls, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieves all medicines belonging to a specific user."""
        db = get_db()
        query = "SELECT * FROM medicines WHERE user_id = ?"
        params = [user_id]
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY name ASC"

        rows = db.execute_query(query, tuple(params))
        return [dict(r) for r in rows]

    @classmethod
    def get_by_id(cls, medicine_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetches a single medicine by ID."""
        db = get_db()
        row = db.execute_one("SELECT * FROM medicines WHERE id = ? AND user_id = ?", (medicine_id, user_id))
        return dict(row) if row else None
