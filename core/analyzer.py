import sqlite3
from datetime import datetime, timedelta

class AccuracyAnalyzer:
    def __init__(self, db_path: str = "data/formocast.db"):
        self.db_path = db_path

    def get_weekly_stats(self):
        """
        Calculates performance statistics for the last 7 days.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Total detections in the last week
        cursor.execute('''
            SELECT COUNT(*) FROM predictions WHERE prediction_date >= ?
        ''', (one_week_ago,))
        total_detections = cursor.fetchone()[0]
        
        # Accuracy of mature predictions
        cursor.execute('''
            SELECT actual_outcome, COUNT(*) 
            FROM predictions 
            WHERE accuracy_checked = 1 AND prediction_date >= ?
            GROUP BY actual_outcome
        ''', (one_week_ago,))
        outcomes = dict(cursor.fetchall())
        
        correct = outcomes.get("Correct", 0)
        incorrect = outcomes.get("Incorrect", 0)
        total_checked = correct + incorrect
        
        accuracy_rate = (correct / total_checked * 100) if total_checked > 0 else 0
        
        # Most frequent patterns
        cursor.execute('''
            SELECT pattern, COUNT(*) 
            FROM predictions 
            WHERE prediction_date >= ?
            GROUP BY pattern
            ORDER BY COUNT(*) DESC
        ''', (one_week_ago,))
        top_patterns = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_detections": total_detections,
            "accuracy_rate": accuracy_rate,
            "correct": correct,
            "incorrect": incorrect,
            "top_patterns": top_patterns
        }
