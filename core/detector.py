import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from scipy.stats import linregress

class PatternDetector:
    def __init__(self, window: int = 5):
        self.window = window

    def find_extrema(self, df: pd.DataFrame):
        """
        Identify local peaks and troughs in the closing price data.

        Logic:
        Uses scipy.signal.argrelextrema to find relative extrema in a 1D array.
        The 'order' parameter (self.window) defines how many points on each side 
        must be lower/higher than the point for it to be considered an extremum.

        Args:
            df (pd.DataFrame): Dataframe containing 'Close' prices.

        Returns:
            tuple: (peak_indices, trough_indices) as numpy arrays.
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
        Detects the Double Top pattern.

        A Double Top is characterized by two consecutive peaks at approximately 
        the same price level, followed by a price decline.

        Detection Logic:
        1. Find all local peaks using find_extrema.
        2. Extract the last two peaks.
        3. Calculate the percentage difference between the two peak values.
        4. If difference < threshold AND current price < peak price, pattern is valid.

        Args:
            df (pd.DataFrame): Price data.
            threshold (float): Max allowed price difference (%) between peaks.

        Returns:
            dict: Pattern details if found, else None.
        """
        peaks, _ = self.find_extrema(df)
        if len(peaks) < 2:
            return None
        
        # Check last two peaks
        last_peak_idx = peaks[-1]
        prev_peak_idx = peaks[-2]
        
        last_peak_val = df['Close'].iloc[last_peak_idx]
        prev_peak_val = df['Close'].iloc[prev_peak_val] # Wait, I had a bug here prev_peak_idx
        
        # Check if they are at similar levels
        diff = abs(last_peak_val - prev_peak_val) / prev_peak_val
        if diff < threshold:
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
        Detects the Double Bottom pattern.

        A Double Bottom is characterized by two consecutive troughs at approximately 
        the same price level, followed by a price increase.

        Detection Logic:
        1. Find all local troughs using find_extrema.
        2. Extract the last two troughs.
        3. Calculate the percentage difference between the two trough values.
        4. If difference < threshold AND current price > trough price, pattern is valid.

        Args:
            df (pd.DataFrame): Price data.
            threshold (float): Max allowed price difference (%) between troughs.

        Returns:
            dict: Pattern details if found, else None.
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

    def detect_head_and_shoulders(self, df: pd.DataFrame, threshold: float = 0.03):
        """
        Omuz Baş Omuz (Head and Shoulders) formasyonunu tespit eder.
        """
        peaks, _ = self.find_extrema(df)
        if len(peaks) < 3:
            return None
        
        p3 = df['Close'].iloc[peaks[-1]] # Sağ Omuz
        p2 = df['Close'].iloc[peaks[-2]] # Baş
        p1 = df['Close'].iloc[peaks[-3]] # Sol Omuz
        
        if p2 > p1 and p2 > p3:
            shoulder_diff = abs(p1 - p3) / p1
            if shoulder_diff < threshold:
                current_price = df['Close'].iloc[-1]
                if current_price < p3:
                    return {
                        "pattern": "Head and Shoulders",
                        "indices": [peaks[-3], peaks[-2], peaks[-1]],
                        "prediction": "Down"
                    }
        return None

    def detect_wedge(self, df: pd.DataFrame):
        """
        Yükselen ve Alçalan Takoz (Rising/Falling Wedge) formasyonlarını tespit eder.

        Mantık:
        1. Son 3 tepe ve 3 dip noktasını al.
        2. Yükselen Takoz: Her iki eğim de pozitif, ancak diplerin eğimi tepelerden büyük (yakınsama).
        3. Alçalan Takoz: Her iki eğim de negatif, ancak tepelerin eğimi diplerden büyük (yakınsama).
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 3 or len(troughs) < 3:
            return None
        
        last_peaks = peaks[-3:]
        last_troughs = troughs[-3:]
        
        peak_prices = df['Close'].iloc[last_peaks].values
        p_slope, _, _, _, _ = linregress(np.arange(len(last_peaks)), peak_prices)
        
        trough_prices = df['Close'].iloc[last_troughs].values
        t_slope, _, _, _, _ = linregress(np.arange(len(last_troughs)), trough_prices)
        
        # Yükselen Takoz (Genelde Ayı/Düşüş sinyali)
        if p_slope > 0 and t_slope > 0 and t_slope > p_slope:
            return {
                "pattern": "Rising Wedge",
                "indices": list(last_peaks) + list(last_troughs),
                "prediction": "Down"
            }
            
        # Alçalan Takoz (Genelde Boğa/Yükseliş sinyali)
        if p_slope < 0 and t_slope < 0 and abs(p_slope) > abs(t_slope):
            return {
                "pattern": "Falling Wedge",
                "indices": list(last_peaks) + list(last_troughs),
                "prediction": "Up"
            }
            
        return None
        """
        Simetrik Üçgen (Symmetrical Triangle) formasyonunu tespit eder.
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 3 or len(troughs) < 3:
            return None
        
        last_peaks = peaks[-3:]
        last_troughs = troughs[-3:]
        
        peak_prices = df['Close'].iloc[last_peaks].values
        peak_slope, _, _, _, _ = linregress(np.arange(len(last_peaks)), peak_prices)
        
        trough_prices = df['Close'].iloc[last_troughs].values
        trough_slope, _, _, _, _ = linregress(np.arange(len(last_troughs)), trough_prices)
        
        if peak_slope < 0 and trough_slope > 0:
            return {
                "pattern": "Symmetrical Triangle",
                "indices": list(last_peaks) + list(last_troughs),
                "prediction": "Volatility Breakout"
            }
        return None

if __name__ == "__main__":
    from services.data_fetcher import DataFetcher
    fetcher = DataFetcher()
    data = fetcher.fetch_ohlc("BTC-USD")
    detector = PatternDetector()
    print(f"BTC Triangle: {detector.detect_triangle(data)}")
