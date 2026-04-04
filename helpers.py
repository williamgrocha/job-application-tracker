from functools import wraps
import sqlite3

from flask import redirect, session

# Init Database
def init_db():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            job_title TEXT NOT NULL,
            salary REAL,
            category TEXT NOT NULL CHECK(category IN ('Remote', 'Hybrid', 'On-site')),
            deadline TEXT,
            notes TEXT,
            date_added TEXT DEFAULT (date('now', 'localtime')),
            status TEXT NOT NULL DEFAULT 'Saved',
            link TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def brl(value):
    """Format value as BRL."""
    if value is None:
        value = 0
    return f"R${value:,.2f}"

def login_required(f):
    wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function