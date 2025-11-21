import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "athleticore.db")


def create_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute(
       """ CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
     username TEXT NOT NULL UNIQUE,
     email TEXT NOT NULL UNIQUE,
     password_hash TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT,
     age INTEGER NOT NULL,
     gender TEXT NOT NULL,
     height INTEGER NOT NULL,
     weight INTEGER NOT NULL
      );
       """
    )

    

    conn.commit()


def init_db():
    """Create the database file and all tables."""
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = create_connection()
    create_tables(conn)
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
