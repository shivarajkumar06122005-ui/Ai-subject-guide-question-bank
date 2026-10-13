import sqlite3

DB_NAME = "mcode.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            academic_level TEXT,
            department TEXT,
            tokens INTEGER DEFAULT 100,
            streak INTEGER DEFAULT 1
        )
    """)
    
    # Study progress table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            unit_id TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(email) REFERENCES users(email)
        )
    """)
    conn.commit()
    conn.close()

def save_user_profile(email: str, full_name: str, academic_level: str, department: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (email, full_name, academic_level, department, tokens, streak)
        VALUES (?, ?, ?, ?, 100, 1)
        ON CONFLICT(email) DO UPDATE SET
        full_name=excluded.full_name,
        academic_level=excluded.academic_level,
        department=excluded.department
    """, (email, full_name, academic_level, department))
    conn.commit()
    conn.close()

def get_user_profile(email: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email, full_name, academic_level, department, tokens, streak FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "email": row[0],
            "full_name": row[1],
            "academic_level": row[2],
            "department": row[3],
            "tokens": row[4],
            "streak": row[5]
        }
    return None

def update_user_progress(email: str, tokens_to_add: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET tokens = tokens + ?, streak = streak + 1 
        WHERE email = ?
    """, (tokens_to_add, email))
    conn.commit()
    conn.close()
