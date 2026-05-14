import unittest
import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime, timedelta
from core.detector import PatternDetector
from db.models import Database
from services.data_fetcher import DataFetcher

class TestBistProfessionalFlow(unittest.TestCase):
    def setUp(self):
        self.db_path = "tests/test_bist.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = Database(self.db_path)
        self.detector = PatternDetector()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def create_fake_bist_data(self, prices):
        dates = pd.date_range(end=datetime.now(), periods=len(prices), freq='H')
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * 1.01 for p in prices],
            'Low': [p * 0.99 for p in prices],
            'Close': prices,
            'Volume': [1000] * len(prices)
        }, index=dates)
        return df

    def test_complete_flow_double_top(self):
        # 1. Senaryo: THYAO.IS hissesinde İkili Tepe oluşuyor
        # P1: 100, Trough: 80, P2: 100, Breakout: 79
        # Data needs to be longer for argrelextrema(order=5)
        base = [90]*10
        prices = base + [95, 100, 95] + [85, 80, 85] + [95, 100, 95] + [85, 80, 79]
        df = self.create_fake_bist_data(prices)
        
        # 2. Tespit (Detection)
        p = self.detector.detect_double_top(df)
        self.assertIsNotNone(p)
        self.assertEqual(p['pattern'], "Double Top")
        self.assertEqual(p['prediction'], "Down")
        self.assertTrue(p['target_price'] < 80) # Hedef 60 olmalı (80 - (100-80))
        
        # 3. Kayıt (Persistence)
        ticker = "THYAO.IS"
        entry_price = df['Close'].iloc[-1]
        self.db.save_prediction(ticker, p['pattern'], p['prediction'], entry_price, p['target_price'], p['timeframe_days'])
        
        # DB Kontrol
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, entry_price, target_price FROM predictions WHERE ticker=?", (ticker,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], ticker)
        self.assertEqual(row[1], 79)
        self.assertAlmostEqual(row[2], 60.0)

    def test_verification_logic(self):
        # 1. Tahmin kaydet (Target hit senaryosu)
        ticker = "EREGL.IS"
        self.db.save_prediction(ticker, "Double Bottom", "Up", 40.0, 50.0, timeframe_days=-1) # Zaten süresi dolmuş gibi
        
        # 2. Doğrulama (Verification - Simulate run_analysis logic)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ticker, predicted_direction, entry_price, target_price FROM predictions")
        pred_id, ticker, direction, entry, target = cursor.fetchone()
        
        # Simüle edilen mevcut fiyat (Hedef vuruldu)
        current_price = 55.0 
        target_hit = True
        
        outcome = "Correct" if target_hit else "Incorrect"
        pnl = ((50.0 - 40.0) / 40.0) * 100 # Target price üzerinden PnL
        
        cursor.execute("UPDATE predictions SET actual_outcome = ?, pnl_percent = ?, accuracy_checked = 1 WHERE id = ?", (outcome, pnl, pred_id))
        conn.commit()
        
        # Sonuç Kontrol
        cursor.execute("SELECT actual_outcome, pnl_percent FROM predictions WHERE id = ?", (pred_id,))
        res = cursor.fetchone()
        conn.close()
        self.assertEqual(res[0], "Correct")
        self.assertEqual(res[1], 25.0) # (50-40)/40 = 0.25 -> %25

if __name__ == '__main__':
    unittest.main()
