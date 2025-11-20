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
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT
        );
        """
    )

    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tdee_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            activity_level TEXT,
            tdee_value REAL,
            goal_type TEXT,
            goal_offset INTEGER,
            goal_calories REAL,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

   
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calorie_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            description TEXT,
            calories REAL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            created_at TEXT,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

   
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal TEXT,
            plan_text TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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