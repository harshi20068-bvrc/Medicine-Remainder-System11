"""
Database Manager for Medicine Reminder System.
Handles SQLite connection, schema initialization, and transactional database queries.
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "medicine_reminder.db")


class DatabaseManager:
    """Manages SQLite database initialization, connections, and thread safety."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured sqlite3 connection with Row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Creates the necessary tables if they do not already exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Medicines Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    dosage TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    times TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    notes TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );
            """)

            # Reminder Logs Table (tracks scheduled doses and their Taken/Missed status)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminder_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    scheduled_date TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('Pending', 'Taken', 'Missed')),
                    marked_at TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (medicine_id) REFERENCES medicines (id) ON DELETE CASCADE,
                    UNIQUE(user_id, medicine_id, scheduled_date, scheduled_time)
                );
            """)

            # Create Indexes for fast querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_medicines_user ON medicines(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_date ON reminder_logs(user_id, scheduled_date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_status ON reminder_logs(status);")

            conn.commit()

    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Executes a SELECT query and returns rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Executes a SELECT query and returns one row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_commit(self, query: str, params: Tuple = ()) -> int:
        """Executes INSERT/UPDATE/DELETE query and returns the lastrowid or rowcount."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid


# Global Database Manager Singleton
_db_instance: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Returns the singleton instance of DatabaseManager."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
