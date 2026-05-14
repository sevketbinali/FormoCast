import sqlite3
import os

def migrate():
    db_path = os.getenv("DB_PATH", "data/formocast.db")
    print(f"Migrating database: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file not found. Nothing to migrate.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add missing columns if they don't exist
    columns_to_add = [
        ("target_price", "REAL"),
        ("target_date", "TEXT"),
        ("pnl_percent", "REAL")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE predictions ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
