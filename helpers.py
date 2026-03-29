import sqlite3

# Init Database
def init_db():
    conn = sqlite3.connect("applications.db") # Create connection and store in the conn variable
    cursor = conn.cursor() # Create DB cursor

    # Create Table once
    cursor.execute("CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL, job_title TEXT NOT NULL, salary REAL, category TEXT NOT NULL CHECK(category IN ('remote', 'hybrid', 'onsite')), deadline TEXT)")
    conn.commit() # Commit all changes
    conn.close() # Close connection
    return None

def usd(value):
    """Format value as BRL."""
    return f"R${value:,.2f}"