import unittest
import pandas as pd
import numpy as np
from core.detector import PatternDetector

class TestPatternDetector(unittest.TestCase):
    def setUp(self):
        self.detector = PatternDetector(window=2)

    def create_fake_data(self, prices):
        return pd.DataFrame({
            'Close': prices,
            'Open': prices,
            'High': prices,
            'Low': prices
        })

    def test_double_top_detection(self):
        # Create a double top: 10, 20 (peak), 15, 20 (peak), 18
        prices = [10, 12, 15, 20, 18, 15, 18, 20, 19, 17]
        df = self.create_fake_data(prices)
        result = self.detector.detect_double_top(df)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "Double Top")
        self.assertEqual(result['prediction'], "Down")

    def test_double_bottom_detection(self):
        # Create a double bottom: 20, 10 (trough), 15, 10 (trough), 12
        prices = [20, 18, 15, 10, 12, 15, 12, 10, 11, 13]
        df = self.create_fake_data(prices)
        result = self.detector.detect_double_bottom(df)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "Double Bottom")
        self.assertEqual(result['prediction'], "Up")

    def test_head_and_shoulders_detection(self):
        # Shoulder (15), Head (20), Shoulder (15)
        # We need peaks to be isolated by window=2
        # Indices of peaks: 3, 7, 11
        prices = [10, 12, 13, 15, 13, 12, 17, 20, 17, 12, 13, 15, 13, 12]
        df = self.create_fake_data(prices)
        result = self.detector.detect_head_and_shoulders(df)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "Head and Shoulders")
        self.assertEqual(result['prediction'], "Down")

    def test_triangle_detection(self):
        # Symmetrical Triangle: Lower highs, Higher lows
        prices = [15, 20, 15, 10, 15, 18, 15, 12, 15, 16, 15, 14, 15]
        df = self.create_fake_data(prices)
        result = self.detector.detect_triangle(df)
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "Symmetrical Triangle")

    def test_cup_and_handle_detection(self):
        # P1: 100, T1: 80, P2: 100, T2: 90
        prices = [90, 95, 100, 90, 85, 80, 85, 90, 100, 95, 90, 95, 100]
        df = self.create_fake_data(prices)
        result = self.detector.detect_cup_and_handle(df)
        self.assertIsNotNone(result)
        self.assertEqual(result['pattern'], "Cup and Handle")

if __name__ == '__main__':
    unittest.main()
