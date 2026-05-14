import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

class PatternDetector:
    def __init__(self, window: int = 5):
        self.window = window

    def find_extrema(self, df: pd.DataFrame):
        """
        Finds local peaks and troughs in the price data.
        """
        # Using 'Close' price for simplicity as per Karpathy Guidelines
        data = df['Close'].values
        
        # Local Maxima
        peaks = argrelextrema(data, np.greater, order=self.window)[0]
        # Local Minima
        troughs = argrelextrema(data, np.less, order=self.window)[0]
        
        return peaks, troughs

    def detect_double_top(self, df: pd.DataFrame, threshold: float = 0.02):
        """
        Detects Double Top pattern.
        """
        peaks, _ = self.find_extrema(df)
        if len(peaks) < 2:
            return None
        
        # Check last two peaks
        last_peak_idx = peaks[-1]
        prev_peak_idx = peaks[-2]
        
        last_peak_val = df['Close'].iloc[last_peak_idx]
        prev_peak_val = df['Close'].iloc[prev_peak_idx]
        
        # Check if they are at similar levels
        diff = abs(last_peak_val - prev_peak_val) / prev_peak_val
        if diff < threshold:
            # Simple check: the price should be below the peaks now
            current_price = df['Close'].iloc[-1]
            if current_price < last_peak_val:
                return {
                    "pattern": "Double Top",
                    "indices": [prev_peak_idx, last_peak_idx],
                    "prediction": "Down"
                }
        return None

    def detect_double_bottom(self, df: pd.DataFrame, threshold: float = 0.02):
        """
        Detects Double Bottom pattern.
        """
        _, troughs = self.find_extrema(df)
        if len(troughs) < 2:
            return None
        
        last_trough_idx = troughs[-1]
        prev_trough_idx = troughs[-2]
        
        last_trough_val = df['Close'].iloc[last_trough_idx]
        prev_trough_val = df['Close'].iloc[prev_trough_idx]
        
        diff = abs(last_trough_val - prev_trough_val) / prev_trough_val
        if diff < threshold:
            current_price = df['Close'].iloc[-1]
            if current_price > last_trough_val:
                return {
                    "pattern": "Double Bottom",
                    "indices": [prev_trough_idx, last_trough_idx],
                    "prediction": "Up"
                }
        return None

if __name__ == "__main__":
    from services.data_fetcher import DataFetcher
    fetcher = DataFetcher()
    data = fetcher.fetch_ohlc("MSFT")
    detector = PatternDetector()
    dt = detector.detect_double_top(data)
    db = detector.detect_double_bottom(data)
    print(f"Double Top: {dt}")
    print(f"Double Bottom: {db}")
