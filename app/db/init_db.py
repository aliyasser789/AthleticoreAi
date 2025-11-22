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

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS tdee_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        activity_level TEXT NOT NULL,
        tdee_value REAL NOT NULL,
        goal_type TEXT NOT NULL,
        goal_offset INTEGER NOT NULL,
        goal_calories REAL NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS tdee_chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tdee_profile_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (tdee_profile_id) REFERENCES tdee_profile(id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS food_feed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        food_name TEXT,
        calories REAL,
        protein_g REAL,
        carbs_g REAL,
        fat_g REAL,
        entry_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS food_chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_feed_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (food_feed_id) REFERENCES food_feed(id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS calorie_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        entry_date TEXT NOT NULL,
        description TEXT,
        calories REAL,
        protein_g REAL,
        carbs_g REAL,
        fat_g REAL,
        created_at TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        workout_name TEXT NOT NULL,
        date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sender TEXT NOT NULL,        -- "user" or "ai"
    message TEXT NOT NULL,       -- the actual chat content
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
    )

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS workout_exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER NOT NULL,
        exercise_name TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        weight_kg REAL,
        previous_weight REAL,
        order_index INTEGER NOT NULL,
        notes TEXT,
        FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE
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
