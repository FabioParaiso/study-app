import sqlite3
import os

DB_PATH = "study_app.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("total_xp", "INTEGER DEFAULT 0"),
        ("high_score", "INTEGER DEFAULT 0"),
        ("total_questions_answered", "INTEGER DEFAULT 0"),
        ("correct_answers_count", "INTEGER DEFAULT 0"),
        ("last_accessed", "Timestamp"),
        ("is_active", "BOOLEAN DEFAULT 0")
    ]

    print("Migrating database...")
    for col_name, col_type in columns_to_add:
        try:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE study_materials ADD COLUMN {col_name} {col_type}")
            print(f"Successfully added {col_name}.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists. Skipping.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
