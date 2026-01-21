import sqlite3
import os

DB_PATH = "study_app.db"

def migrate_passwords():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Adicionando coluna hashed_password na tabela students...")
        cursor.execute("ALTER TABLE students ADD COLUMN hashed_password VARCHAR")
        print("Coluna adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Coluna hashed_password já existe.")
        else:
            print(f"Erro ao adicionar coluna: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_passwords()
