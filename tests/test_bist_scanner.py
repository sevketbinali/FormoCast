import unittest
from services.bist_scanner import BistScanner

class TestBistScanner(unittest.TestCase):
    def setUp(self):
        # Scan only 2 tickers for fast testing
        self.scanner = BistScanner(interval_seconds=60)
        self.scanner.tickers = ["THYAO.IS", "GARAN.IS"]

    def test_batch_fetch(self):
        data = self.scanner.fetch_batch_data(self.scanner.tickers)
        self.assertIsNotNone(data)
        self.assertIn("THYAO.IS", data.columns.levels[0])
        self.assertIn("GARAN.IS", data.columns.levels[0])

    def test_single_scan_cycle(self):
        # This just ensures no exceptions during a scan cycle
        try:
            self.scanner.scan()
        except Exception as e:
            self.fail(f"Scan cycle failed with error: {e}")

if __name__ == '__main__':
    unittest.main()
