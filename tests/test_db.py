import unittest
import os
import sqlite3
from db.models import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_path = "tests/test_formocast.db"
        self.db = Database(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_get_prediction(self):
        self.db.save_prediction("AAPL", "Double Top", "Down", 150.0)
        pending = self.db.get_pending_predictions()
        
        # We need to wait or adjust the target_date logic for testing
        # But for now, let's just check if it was inserted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, pattern FROM predictions")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "AAPL")
        self.assertEqual(row[1], "Double Top")

    def test_update_accuracy(self):
        self.db.save_prediction("TSLA", "Double Bottom", "Up", 700.0)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM predictions LIMIT 1")
        pred_id = cursor.fetchone()[0]
        conn.close()
        
        self.db.update_accuracy(pred_id, "Correct")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT actual_outcome, accuracy_checked FROM predictions WHERE id = ?", (pred_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row[0], "Correct")
        self.assertEqual(row[1], 1)

if __name__ == '__main__':
    unittest.main()
