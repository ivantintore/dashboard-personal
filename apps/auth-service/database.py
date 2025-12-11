"""
Database module for Auth Service
SQLite database for user management
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/auth.db")


def get_db_path():
    """Get database path, creating directory if needed"""
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return DATABASE_PATH


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database with required tables"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    
    # Create admin user if ADMIN_EMAIL is set and no admins exist
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        with get_db() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE role = 'admin'"
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT OR IGNORE INTO users (email, role) VALUES (?, 'admin')",
                    (admin_email,)
                )
                conn.commit()
                print(f"✅ Admin user created: {admin_email}")


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def create_or_update_user(email: str, name: str = None, picture: str = None) -> dict:
    """Create user if not exists, or update last_login"""
    with get_db() as conn:
        existing = get_user_by_email(email)
        if existing:
            conn.execute(
                "UPDATE users SET name = ?, picture = ?, last_login = ? WHERE email = ?",
                (name or existing.get('name'), picture, datetime.now(), email)
            )
            conn.commit()
            return get_user_by_email(email)
        else:
            conn.execute(
                "INSERT INTO users (email, name, picture, last_login) VALUES (?, ?, ?, ?)",
                (email, name, picture, datetime.now())
            )
            conn.commit()
            return get_user_by_email(email)


def get_all_users() -> List[dict]:
    """Get all users"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def add_user(email: str, role: str = 'user') -> bool:
    """Add a new authorized user"""
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (email, role) VALUES (?, ?)",
                (email, role)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def delete_user(user_id: int) -> bool:
    """Delete a user"""
    with get_db() as conn:
        # Don't allow deleting the last admin
        admins = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
        ).fetchone()
        user = get_user_by_id(user_id)
        if user and user['role'] == 'admin' and admins['count'] <= 1:
            return False
        
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True


def update_user_role(user_id: int, role: str) -> bool:
    """Update user role"""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (role, user_id)
        )
        conn.commit()
        return True


# Session management
def create_session(user_id: int, session_id: str, expires_at: datetime) -> None:
    """Create a new session"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
            (session_id, user_id, expires_at)
        )
        conn.commit()


def get_session(session_id: str) -> Optional[dict]:
    """Get session by session_id"""
    with get_db() as conn:
        row = conn.execute(
            """SELECT s.*, u.email, u.name, u.role, u.picture 
               FROM sessions s 
               JOIN users u ON s.user_id = u.id 
               WHERE s.session_id = ? AND s.expires_at > ?""",
            (session_id, datetime.now())
        ).fetchone()
        return dict(row) if row else None


def delete_session(session_id: str) -> None:
    """Delete a session"""
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()


def cleanup_expired_sessions() -> None:
    """Remove expired sessions"""
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(),))
        conn.commit()

