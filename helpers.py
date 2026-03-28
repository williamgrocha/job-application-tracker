import sqlite3

def init_db():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL, job_title TEXT NOT NULL, salary REAL, category TEXT NOT NULL CHECK(category IN ('remote', 'hybrid', 'onsite')), deadline TEXT)")
    conn.commit()
    conn.close()
    return None