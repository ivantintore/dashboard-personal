"""
Database module for Auth Service
SQLite database for user management, sessions, 2FA, and audit logs
"""
import sqlite3
import os
from datetime import datetime, timedelta
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
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                totp_secret TEXT,
                totp_enabled BOOLEAN DEFAULT FALSE,
                backup_codes TEXT
            )
        """)
        
        # Sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_2fa_verified BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Audit logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                email TEXT,
                ip_address TEXT,
                user_agent TEXT,
                details TEXT,
                severity TEXT DEFAULT 'info'
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_logs(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ip ON audit_logs(ip_address)")
        
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


# ==================== USER MANAGEMENT ====================

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


# ==================== 2FA MANAGEMENT ====================

def set_totp_secret(user_id: int, secret: str) -> bool:
    """Set TOTP secret for a user"""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET totp_secret = ? WHERE id = ?",
            (secret, user_id)
        )
        conn.commit()
        return True


def enable_totp(user_id: int, backup_codes: str) -> bool:
    """Enable TOTP for a user"""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET totp_enabled = TRUE, backup_codes = ? WHERE id = ?",
            (backup_codes, user_id)
        )
        conn.commit()
        return True


def disable_totp(user_id: int) -> bool:
    """Disable TOTP for a user"""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET totp_enabled = FALSE, totp_secret = NULL, backup_codes = NULL WHERE id = ?",
            (user_id,)
        )
        conn.commit()
        return True


def update_backup_codes(user_id: int, backup_codes: str) -> bool:
    """Update backup codes after one is used"""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET backup_codes = ? WHERE id = ?",
            (backup_codes, user_id)
        )
        conn.commit()
        return True


def get_totp_info(user_id: int) -> Optional[dict]:
    """Get TOTP info for a user"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT totp_secret, totp_enabled, backup_codes FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


# ==================== SESSION MANAGEMENT ====================

def create_session(
    user_id: int, 
    session_id: str, 
    expires_at: datetime,
    ip_address: str = None,
    user_agent: str = None,
    is_2fa_verified: bool = False
) -> None:
    """Create a new session"""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO sessions 
               (session_id, user_id, expires_at, ip_address, user_agent, is_2fa_verified) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, user_id, expires_at, ip_address, user_agent[:500] if user_agent else None, is_2fa_verified)
        )
        conn.commit()


def get_session(session_id: str) -> Optional[dict]:
    """Get session by session_id"""
    with get_db() as conn:
        row = conn.execute(
            """SELECT s.*, u.email, u.name, u.role, u.picture, u.totp_enabled
               FROM sessions s 
               JOIN users u ON s.user_id = u.id 
               WHERE s.session_id = ? AND s.expires_at > ?""",
            (session_id, datetime.now())
        ).fetchone()
        return dict(row) if row else None


def update_session_2fa_verified(session_id: str) -> bool:
    """Mark session as 2FA verified"""
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET is_2fa_verified = TRUE WHERE session_id = ?",
            (session_id,)
        )
        conn.commit()
        return True


def delete_session(session_id: str) -> None:
    """Delete a session"""
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()


def delete_user_sessions(user_id: int) -> None:
    """Delete all sessions for a user"""
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()


def cleanup_expired_sessions() -> int:
    """Remove expired sessions, returns count deleted"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(),))
        conn.commit()
        return cursor.rowcount


def invalidate_all_sessions() -> int:
    """Invalidate ALL sessions (for secret rotation)"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM sessions")
        conn.commit()
        return cursor.rowcount


def get_user_sessions(user_id: int) -> List[dict]:
    """Get all active sessions for a user"""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT id, created_at, expires_at, ip_address, user_agent 
               FROM sessions 
               WHERE user_id = ? AND expires_at > ?
               ORDER BY created_at DESC""",
            (user_id, datetime.now())
        ).fetchall()
        return [dict(row) for row in rows]


# ==================== AUDIT LOGGING ====================

def create_audit_log(
    event_type: str,
    user_id: int = None,
    email: str = None,
    ip_address: str = None,
    user_agent: str = None,
    details: str = None,
    severity: str = 'info'
) -> None:
    """Create an audit log entry"""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO audit_logs 
               (event_type, user_id, email, ip_address, user_agent, details, severity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (event_type, user_id, email, ip_address, user_agent, details, severity)
        )
        conn.commit()


def get_audit_logs(
    limit: int = 100,
    event_type: str = None,
    user_id: int = None,
    severity: str = None
) -> List[dict]:
    """Get audit logs with optional filters"""
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def count_events_by_ip(ip_address: str, event_type: str, minutes: int = 60) -> int:
    """Count events from an IP in the last N minutes"""
    since = datetime.now() - timedelta(minutes=minutes)
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as count FROM audit_logs 
               WHERE ip_address = ? AND event_type = ? AND timestamp > ?""",
            (ip_address, event_type, since)
        ).fetchone()
        return row['count'] if row else 0


def cleanup_old_audit_logs(days: int = 90) -> int:
    """Remove audit logs older than N days"""
    cutoff = datetime.now() - timedelta(days=days)
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM audit_logs WHERE timestamp < ?", (cutoff,))
        conn.commit()
        return cursor.rowcount
