"""
User Model for authentication and user profile management.
Uses salted SHA-256 password hashing.
"""

import hashlib
import secrets
from typing import Optional, Dict, Any, Tuple
from database.db_manager import get_db


class UserModel:
    """Handles User registration, authentication, and profile lookup."""

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Helper to compute SHA-256 hash with salt."""
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

    @classmethod
    def register(cls, username: str, password: str, full_name: str = "") -> Tuple[bool, str]:
        """Registers a new user account."""
        username = username.strip().lower()
        if not username or not password:
            return False, "Username and password cannot be empty."

        if len(password) < 6:
            return False, "Password must be at least 6 characters long."

        db = get_db()
        existing = db.execute_one("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            return False, "Username already exists. Please choose another."

        salt = secrets.token_hex(16)
        password_hash = cls._hash_password(password, salt)

        try:
            user_id = db.execute_commit(
                "INSERT INTO users (username, password_hash, salt, full_name) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt, full_name.strip())
            )
            return True, f"Registration successful! Welcome, {username}."
        except Exception as e:
            return False, f"Failed to create user: {str(e)}"

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates user login credentials."""
        username = username.strip().lower()
        if not username or not password:
            return None

        db = get_db()
        user_row = db.execute_one("SELECT * FROM users WHERE username = ?", (username,))
        if not user_row:
            return None

        salt = user_row['salt']
        input_hash = cls._hash_password(password, salt)

        if input_hash == user_row['password_hash']:
            return dict(user_row)
        return None

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetches user details by user ID."""
        db = get_db()
        user_row = db.execute_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return dict(user_row) if user_row else None
