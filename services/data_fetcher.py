import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        pass

    def fetch_ohlc(self, ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches OHLC data for a given ticker.
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            if df.empty:
                print(f"No data found for {ticker}")
                return pd.DataFrame()
            return df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    fetcher = DataFetcher()
    data = fetcher.fetch_ohlc("AAPL")
    print(data.head())
