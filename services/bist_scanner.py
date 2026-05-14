import time
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from config.tickers import BIST100_TICKERS
from core.detector import PatternDetector
from services.visualizer import Visualizer
from services.notifier import Notifier
from db.models import Database

class BistScanner:
    def __init__(self, interval_seconds=60):
        self.tickers = BIST100_TICKERS
        self.interval = interval_seconds
        self.detector = PatternDetector()
        self.visualizer = Visualizer()
        self.notifier = Notifier()
        self.db = Database()
        self.processed_signals = set() # Avoid spamming same signal in a short time

    def fetch_batch_data(self, tickers):
        """
        Fetches OHLC data for a batch of tickers efficiently.
        """
        try:
            data = yf.download(tickers, period="5d", interval="1h", group_by='ticker', progress=False)
            return data
        except Exception as e:
            print(f"Batch fetch error: {e}")
            return None

    def scan(self):
        print(f"[{datetime.now()}] BIST 100 Canlı Tarama Başladı... (Interval: {self.interval}s)")
        
        batch_size = 20
        for i in range(0, len(self.tickers), batch_size):
            batch = self.tickers[i:i+batch_size]
            print(f"Taranıyor: {batch[0]}...{batch[-1]}")
            
            batch_data = self.fetch_batch_data(batch)
            if batch_data is None: continue

            for ticker in batch:
                try:
                    # Handle single ticker vs multi-ticker dataframe structure
                    if len(batch) > 1:
                        df = batch_data[ticker].dropna()
                    else:
                        df = batch_data.dropna()

                    if df.empty or len(df) < 20: continue

                    self.check_patterns(ticker, df)
                except Exception as e:
                    print(f"Hata ({ticker}): {e}")

    def check_patterns(self, ticker, df):
        patterns = [
            self.detector.detect_double_top(df),
            self.detector.detect_double_bottom(df),
            self.detector.detect_head_and_shoulders(df),
            self.detector.detect_triangle(df),
            self.detector.detect_wedge(df),
            self.detector.detect_cup_and_handle(df)
        ]

        for p in patterns:
            if p:
                signal_key = f"{ticker}_{p['pattern']}_{df.index[-1]}"
                if signal_key not in self.processed_signals:
                    self.process_found_pattern(ticker, df, p)
                    self.processed_signals.add(signal_key)

    def process_found_pattern(self, ticker, df, p):
        print(f"🎯 FORMASYON YAKALANDI: {ticker} -> {p['pattern']}")
        
        current_price = df['Close'].iloc[-1]
        target_price = p.get('target_price')
        timeframe = p.get('timeframe_days', 7)

        # 1. DB Kayıt
        self.db.save_prediction(ticker, p['pattern'], p['prediction'], current_price, target_price, timeframe)

        # 2. Görselleştirme
        chart_path = self.visualizer.plot_pattern(df, ticker, p)

        # 3. Bildirim (Email)
        self.notifier.send_pattern_alert(ticker, p, chart_path)

    def start(self):
        while True:
            start_time = time.time()
            self.scan()
            
            # Clean up old signals every hour to keep memory low
            if len(self.processed_signals) > 1000:
                self.processed_signals.clear()

            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            print(f"Tarama tamamlandı. Bekleme süresi: {sleep_time:.2f}s")
            time.sleep(sleep_time)

if __name__ == "__main__":
    scanner = BistScanner(interval_seconds=300) # Default to 5 min for BIST to avoid yfinance limits
    scanner.start()
