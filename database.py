import sqlite3
import hashlib
import os

DB_PATH = "studymate_users.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()

def create_user(username, password):
    salt = os.urandom(16).hex()
    password_hash = hash_password(password, salt)
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users(username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt)
            )
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username already exists."

def verify_user(username, password):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
        ).fetchone()
    if not row:
        return False
    return hash_password(password, row[1]) == row[0]
