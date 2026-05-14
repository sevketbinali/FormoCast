import asyncio
import json
import websockets
import pandas as pd
import os
from datetime import datetime
from services.data_fetcher import DataFetcher
from core.detector import PatternDetector
from services.visualizer import Visualizer
from services.notifier import Notifier
from services.telegram_notifier import TelegramNotifier
from db.models import Database

class RealTimeStreamer:
    def __init__(self, tickers=None, interval="1h"):
        self.tickers = tickers or os.getenv("MONITOR_TICKERS", "BTCUSDT ETHUSDT").lower().split()
        self.interval = interval
        self.base_url = "wss://stream.binance.com:9443/stream?streams="
        self.streams = "/".join([f"{t}@kline_{interval}" for t in self.tickers])
        self.url = self.base_url + self.streams
        
        # In-memory storage for rolling windows
        self.price_data = {}
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.visualizer = Visualizer()
        self.notifier = Notifier()
        self.tg_notifier = TelegramNotifier()
        self.db = Database()

    async def initialize_history(self):
        """
        Pre-populates the in-memory buffer with historical data from yfinance.
        """
        print(f"[{datetime.now()}] Geçmiş veriler yükleniyor...")
        for ticker in self.tickers:
            # yfinance expects symbols like BTC-USD, Binance uses BTCUSDT
            # For simplicity, we assume the user provides Binance-compatible symbols
            yf_ticker = ticker.upper().replace("USDT", "-USD")
            df = self.fetcher.fetch_ohlc(yf_ticker, period="5d", interval="1h")
            if not df.empty:
                self.price_data[ticker] = df
                print(f"{ticker} için {len(df)} mum yüklendi.")

    async def start(self):
        await self.initialize_history()
        
        print(f"[{datetime.now()}] WebSocket bağlantısı kuruluyor: {self.url}")
        async with websockets.connect(self.url) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    stream_name = data['stream']
                    ticker = stream_name.split('@')[0]
                    kline = data['data']['k']
                    
                    # Check if candle is closed
                    if kline['x']:
                        await self.process_closed_candle(ticker, kline)
                except Exception as e:
                    print(f"Stream hatası: {e}")
                    await asyncio.sleep(5) # Reconnect logic would be better

    async def process_closed_candle(self, ticker, kline):
        print(f"[{datetime.now()}] {ticker.upper()} - Mum Kapandı: {kline['c']}")
        
        # New candle data
        new_row = {
            'Open': float(kline['o']),
            'High': float(kline['h']),
            'Low': float(kline['l']),
            'Close': float(kline['c']),
            'Volume': float(kline['v'])
        }
        new_df = pd.DataFrame([new_row], index=[pd.to_datetime(kline['t'], unit='ms')])
        
        # Update buffer
        if ticker in self.price_data:
            self.price_data[ticker] = pd.concat([self.price_data[ticker], new_df]).iloc[-100:]
            
            # Run detection
            df = self.price_data[ticker]
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
                    await self.trigger_alert(ticker, df, p)

    async def trigger_alert(self, ticker, df, pattern_info):
        print(f"🎯 Pattern Found! {ticker}: {pattern_info['pattern']}")
        # Save to DB
        self.db.save_prediction(ticker.upper(), pattern_info['pattern'], pattern_info['prediction'], df['Close'].iloc[-1])
        
        # Visuals
        chart_path = self.visualizer.plot_pattern(df, ticker.upper(), pattern_info)
        
        # Notifications
        self.notifier.send_pattern_alert(ticker.upper(), pattern_info, chart_path)
        caption = f"🚀 *Real-Time Alert: {pattern_info['pattern']}*\nTicker: {ticker.upper()}\nPrice: {df['Close'].iloc[-1]}"
        self.tg_notifier.send_photo(chart_path, caption)

if __name__ == "__main__":
    streamer = RealTimeStreamer()
    asyncio.run(streamer.start())
