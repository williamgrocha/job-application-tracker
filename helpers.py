from datetime import datetime
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
            link TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()

def init_users_db():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
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
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function


def date_br(value):
    """Format date as DD/MM/YYYY."""
    if not value:
        return None
    try:
        value = datetime.strptime(value, "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        return value
    return value