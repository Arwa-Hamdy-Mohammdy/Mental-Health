"""
Database module for MindCare AI.
Uses SQLite for persistent storage of users, password hashes, chat history, mood logs, and journal entries.
"""

import sqlite3
import hashlib
import secrets
import json
import os
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mindcare.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create Chat History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Create Mood Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            stress_level INTEGER NOT NULL,
            sleep_hours REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Create Journal Entries Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            mood_tag TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

# Password Hashing Utilities using PBKDF2 HMAC SHA256
def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    )
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, stored_hash)

# User Database Operations
def create_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    email_clean = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    pwd_hash, salt = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash, salt) VALUES (?, ?, ?)",
            (email_clean, pwd_hash, salt)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "email": email_clean}
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Email already exists

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    email_clean = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, password_hash, salt FROM users WHERE email = ?", (email_clean,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user["password_hash"], user["salt"]):
        return {"id": user["id"], "email": user["email"]}
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

# Chat History Operations
def save_chat_message(user_id: int, role: str, content: Any):
    conn = get_db_connection()
    cursor = conn.cursor()
    content_str = json.dumps(content) if not isinstance(content, str) else content
    cursor.execute(
        "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content_str)
    )
    conn.commit()
    conn.close()

def get_user_chat_history(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, created_at FROM chat_history WHERE user_id = ? ORDER BY id ASC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        content_val = row["content"]
        try:
            parsed_content = json.loads(content_val)
        except Exception:
            parsed_content = content_val
        history.append({
            "role": row["role"],
            "content": parsed_content,
            "created_at": row["created_at"]
        })
    return history

def clear_user_chat_history(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Mood & Journal Database Operations
def save_user_mood(user_id: int, mood: str, stress_level: int, sleep_hours: float, notes: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mood_logs (user_id, mood, stress_level, sleep_hours, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, mood, stress_level, sleep_hours, notes)
    )
    conn.commit()
    conn.close()

def get_user_moods(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT mood, stress_level, sleep_hours, notes, created_at FROM mood_logs WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_user_journal(user_id: int, text: str, mood_tag: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO journal_entries (user_id, text, mood_tag) VALUES (?, ?, ?)",
        (user_id, text, mood_tag)
    )
    conn.commit()
    conn.close()

def get_user_journals(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT text, mood_tag, created_at FROM journal_entries WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize Database on Import
init_db()
