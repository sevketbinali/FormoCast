import unittest
import os
import sqlite3
from datetime import datetime, timedelta
from core.analyzer import AccuracyAnalyzer
from db.models import Database

class TestAccuracyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.db_path = "tests/test_analyzer.db"
        self.db = Database(db_path=self.db_path)
        self.analyzer = AccuracyAnalyzer(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_weekly_stats(self):
        # Insert some test data
        # One correct, one incorrect, one old
        now = datetime.now()
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Manually insert to have control
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Correct prediction
        cursor.execute('''
            INSERT INTO predictions (ticker, pattern, prediction_date, predicted_direction, actual_outcome, accuracy_checked)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("AAPL", "Double Top", yesterday, "Down", "Correct", 1))
        
        # 2. Incorrect prediction
        cursor.execute('''
            INSERT INTO predictions (ticker, pattern, prediction_date, predicted_direction, actual_outcome, accuracy_checked)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("TSLA", "Double Bottom", yesterday, "Up", "Incorrect", 1))
        
        # 3. Pending prediction
        cursor.execute('''
            INSERT INTO predictions (ticker, pattern, prediction_date, predicted_direction, accuracy_checked)
            VALUES (?, ?, ?, ?, ?)
        ''', ("BTC-USD", "Triangle", yesterday, "Up", 0))
        
        conn.commit()
        conn.close()
        
        stats = self.analyzer.get_weekly_stats()
        
        self.assertEqual(stats['total_detections'], 3)
        self.assertEqual(stats['correct'], 1)
        self.assertEqual(stats['incorrect'], 1)
        self.assertEqual(stats['accuracy_rate'], 50.0)
        self.assertTrue(len(stats['top_patterns']) > 0)

if __name__ == '__main__':
    unittest.main()
