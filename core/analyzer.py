import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta

class AccuracyAnalyzer:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.getenv("DB_PATH", "data/formocast.db")

    def get_weekly_stats(self):
        """
        Haftalık özet verileri ve grafik verilerini hazırlar.
        """
        conn = sqlite3.connect(self.db_path)
        
        # 1. Temel İstatistikler
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        df = pd.read_sql_query('''
            SELECT actual_outcome, pnl_percent, pattern, prediction_date 
            FROM predictions 
            WHERE prediction_date >= ? AND accuracy_checked = 1
        ''', conn, params=(one_week_ago,))
        
        if df.empty:
            conn.close()
            return {
                "total_detections": 0, "correct": 0, "incorrect": 0,
                "accuracy_rate": 0, "avg_pnl": 0, "top_patterns": [],
                "pnl_history": [], "pattern_performance": []
            }

        total = len(df)
        correct = len(df[df['actual_outcome'] == "Correct"])
        incorrect = total - correct
        avg_pnl = df['pnl_percent'].mean()
        
        # 2. Formasyon Bazlı Başarı Oranı
        pattern_perf = df.groupby('pattern').apply(lambda x: {
            'count': len(x),
            'success_rate': (len(x[x['actual_outcome'] == "Correct"]) / len(x)) * 100
        }).to_dict()

        # 3. Zaman Serisi PnL (Kümülatif)
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        df = df.sort_values('prediction_date')
        df['cumulative_pnl'] = df['pnl_percent'].cumsum()
        
        pnl_history = df[['prediction_date', 'cumulative_pnl']].to_dict(orient='records')
        
        conn.close()
        
        return {
            "total_detections": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy_rate": (correct / total) * 100,
            "avg_pnl": avg_pnl,
            "top_patterns": sorted(df['pattern'].value_counts().items(), key=lambda x: x[1], reverse=True),
            "pnl_history": pnl_history,
            "pattern_performance": pattern_perf
        }
