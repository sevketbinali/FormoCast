import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "data/formocast.db"):
        self.db_path = db_path
        self._init_db()

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
                target_date TEXT,
                actual_outcome TEXT,
                accuracy_checked INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_prediction(self, ticker, pattern, predicted_direction, entry_price):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        prediction_date = datetime.now().strftime("%Y-%m-%d")
        # Set target date to 1 week from now for simplicity
        target_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT INTO predictions (ticker, pattern, prediction_date, predicted_direction, entry_price, target_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, pattern, prediction_date, predicted_direction, entry_price, target_date))
        
        conn.commit()
        conn.close()

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
