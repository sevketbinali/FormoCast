import sqlite3
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path: str = "data/formocast.db"):
        self.db_path = db_path
        self._init_db()
        self.migrate()

    def migrate(self):
        """Adds missing columns for backward compatibility."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        columns = [("target_price", "REAL"), ("target_date", "TEXT"), ("pnl_percent", "REAL")]
        for col, col_type in columns:
            try:
                cursor.execute(f"ALTER TABLE predictions ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for predictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                pattern TEXT,
                prediction_date TEXT,
                predicted_direction TEXT,
                entry_price REAL,
                target_price REAL,
                target_date TEXT,
                actual_outcome TEXT,
                pnl_percent REAL,
                accuracy_checked INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_prediction(self, ticker, pattern, direction, entry_price, target_price=None, timeframe_days=7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now()
        target_date = (now + timedelta(days=timeframe_days)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO predictions (ticker, pattern, prediction_date, predicted_direction, entry_price, target_price, target_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, pattern, now.strftime("%Y-%m-%d %H:%M:%S"), direction, entry_price, target_price, target_date))
        conn.commit()
        conn.close()

    def get_latest_predictions(self, limit=10):
        """
        Retrieves the most recent predictions for the dashboard.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ticker, pattern, predicted_direction, entry_price, prediction_date, actual_outcome
            FROM predictions
            ORDER BY prediction_date DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    def get_pending_predictions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT id, ticker, prediction_date, predicted_direction, entry_price, target_date 
            FROM predictions 
            WHERE accuracy_checked = 0 AND target_date <= ?
        ''', (today,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_accuracy(self, prediction_id, outcome):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE predictions 
            SET actual_outcome = ?, accuracy_checked = 1 
            WHERE id = ?
        ''', (outcome, prediction_id))
        conn.commit()
        conn.close()

from datetime import timedelta
