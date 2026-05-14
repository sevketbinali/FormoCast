import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime
from core.detector import PatternDetector
from services.visualizer import Visualizer
from services.notifier import Notifier

class BinanceStreamer:
    def __init__(self, ticker: str = "btcusdt", interval: str = "1h"):
        self.ticker = ticker
        self.interval = interval
        self.url = f"wss://stream.binance.com:9443/ws/{ticker}@kline_{interval}"
        self.data_buffer = []
        self.detector = PatternDetector()
        self.visualizer = Visualizer()
        self.notifier = Notifier()

    async def start(self):
        print(f"[{datetime.now()}] {self.ticker} için WebSocket akışı başlatılıyor...")
        async with websockets.connect(self.url) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # k = kline data
                kline = data['k']
                is_closed = kline['x']
                
                if is_closed:
                    print(f"[{datetime.now()}] Yeni mum kapandı: {kline['c']}")
                    # Bu noktada veriyi buffer'a ekleyip tarama yapabiliriz
                    # Ancak WebSocket sadece yeni veriyi verir. 
                    # İlk başta geçmiş veriyi yfinance'den alıp sonra üzerine eklemek daha mantıklı.
                    await self.run_instant_scan(kline)

    async def run_instant_scan(self, last_kline):
        # Gerçek bir uygulamada burada geçmiş veriyi hafızada tutarız.
        # Basitlik için her yeni mumda yfinance'den son veriyi çekip tarama yapıyoruz.
        print(f"Anlık tarama tetiklendi: {self.ticker}")
        # Not: Burada main.py'deki mantığı çağırabiliriz.
        pass

if __name__ == "__main__":
    streamer = BinanceStreamer()
    asyncio.run(streamer.start())
