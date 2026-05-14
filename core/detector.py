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
        """
        data = df['Close'].values
        peaks = argrelextrema(data, np.greater, order=self.window)[0]
        troughs = argrelextrema(data, np.less, order=self.window)[0]
        return peaks, troughs

    def _is_recent(self, df, indices, max_lookback=15):
        """Checks if the pattern's last point is within the last 'max_lookback' candles."""
        last_pos = max(indices)
        return (len(df) - 1 - last_pos) <= max_lookback

    def detect_double_top(self, df: pd.DataFrame, threshold: float = 0.02):
        """
        İkili Tepe tespiti ve Boyun Çizgisi Kırılımı.
        
        Kural: 
        1. İki benzer tepe (P1, P2).
        2. Aradaki en düşük seviye (Boyun Çizgisi).
        3. Mevcut fiyatın Boyun Çizgisinin altına inmesi (Kırılım).
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 2 or len(troughs) < 1:
            return None
        
        p2_idx, p1_idx = peaks[-1], peaks[-2]
        
        # Recency Check: Tepe çok eski olmamalı
        if not self._is_recent(df, [p2_idx], max_lookback=15):
            return None

        p2_val, p1_val = df['Close'].iloc[p2_idx], df['Close'].iloc[p1_idx]
        
        # Tepeler arası mesafe kontrolü (Benzer seviye)
        if abs(p2_val - p1_val) / p1_val < threshold:
            # İki tepe arasındaki en düşük noktayı (neckline) bul
            neckline_val = df['Close'].iloc[p1_idx:p2_idx].min()
            current_price = df['Close'].iloc[-1]
            
            # Kırılım Kontrolü: Fiyat boyun çizgisinin altına inmeli
            if current_price < neckline_val:
                # Hedef Fiyat: Boyun çizgisi - (Tepe yüksekliği)
                target = neckline_val - (p2_val - neckline_val)
                return {
                    "pattern": "Double Top",
                    "indices": [p1_idx, p2_idx],
                    "neckline": neckline_val,
                    "target_price": target,
                    "prediction": "Down",
                    "timeframe_days": 14 # İkili tepe genelde 2 haftada hedefe ulaşır
                }
        return None

    def detect_double_bottom(self, df: pd.DataFrame, threshold: float = 0.02):
        """
        İkili Dip tespiti ve Boyun Çizgisi Kırılımı.
        """
        peaks, troughs = self.find_extrema(df)
        if len(troughs) < 2 or len(peaks) < 1:
            return None

        t2_idx, t1_idx = troughs[-1], troughs[-2]
        
        # Recency Check
        if not self._is_recent(df, [t2_idx], max_lookback=15):
            return None

        t2_val, t1_val = df['Close'].iloc[t2_idx], df['Close'].iloc[t1_idx]
        
        if abs(t2_val - t1_val) / t1_val < threshold:
            # İki dip arasındaki en yüksek nokta (neckline)
            neckline_val = df['Close'].iloc[t1_idx:t2_idx].max()
            current_price = df['Close'].iloc[-1]
            
            # Kırılım: Fiyat boyun çizgisinin üstüne çıkmalı
            if current_price > neckline_val:
                # Hedef Fiyat: Boyun çizgisi + (Dip derinliği)
                target = neckline_val + (neckline_val - t2_val)
                return {
                    "pattern": "Double Bottom",
                    "indices": [t1_idx, t2_idx],
                    "neckline": neckline_val,
                    "target_price": target,
                    "prediction": "Up",
                    "timeframe_days": 14
                }
        return None

    def detect_head_and_shoulders(self, df: pd.DataFrame, threshold: float = 0.05):
        """
        Omuz Baş Omuz tespiti.
        """
        peaks, _ = self.find_extrema(df)
        if len(peaks) < 3:
            return None
        
        p3, p2, p1 = df['Close'].iloc[peaks[-1]], df['Close'].iloc[peaks[-2]], df['Close'].iloc[peaks[-3]]
        
        if not self._is_recent(df, [peaks[-1]], max_lookback=20):
            return None

        if p2 > p1 and p2 > p3:
            shoulder_diff = abs(p1 - p3) / p1
            if shoulder_diff < threshold:
                current_price = df['Close'].iloc[-1]
                if current_price < p3:
                    # Hedef: Baş-Boyun mesafesi kadar aşağı
                    target = p3 - (p2 - p3)
                    return {
                        "pattern": "Head and Shoulders",
                        "indices": [peaks[-3], peaks[-2], peaks[-1]],
                        "target_price": target,
                        "prediction": "Down",
                        "timeframe_days": 21
                    }
        return None

    def detect_wedge(self, df: pd.DataFrame):
        """
        Yükselen/Alçalan Takoz tespiti.
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 3 or len(troughs) < 3:
            return None
        
        if not self._is_recent(df, [peaks[-1], troughs[-1]], max_lookback=15):
            return None

        last_peaks, last_troughs = peaks[-3:], troughs[-3:]
        p_slope, _, _, _, _ = linregress(np.arange(3), df['Close'].iloc[last_peaks].values)
        t_slope, _, _, _, _ = linregress(np.arange(3), df['Close'].iloc[last_troughs].values)
        
        current_price = df['Close'].iloc[-1]
        if p_slope > 0 and t_slope > 0 and t_slope > p_slope:
            return {
                "pattern": "Rising Wedge", 
                "indices": list(last_peaks) + list(last_troughs), 
                "target_price": current_price * 0.90, # %10 düşüş hedefi
                "prediction": "Down",
                "timeframe_days": 10
            }
        if p_slope < 0 and t_slope < 0 and abs(p_slope) > abs(t_slope):
            return {
                "pattern": "Falling Wedge", 
                "indices": list(last_peaks) + list(last_troughs), 
                "target_price": current_price * 1.10, # %10 yükseliş hedefi
                "prediction": "Up",
                "timeframe_days": 10
            }
        return None

    def detect_triangle(self, df: pd.DataFrame):
        """
        Simetrik Üçgen tespiti.
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 3 or len(troughs) < 3:
            return None
        
        if not self._is_recent(df, [peaks[-1], troughs[-1]], max_lookback=15):
            return None

        last_peaks, last_troughs = peaks[-3:], troughs[-3:]
        p_slope, _, _, _, _ = linregress(np.arange(3), df['Close'].iloc[last_peaks].values)
        t_slope, _, _, _, _ = linregress(np.arange(3), df['Close'].iloc[last_troughs].values)
        
        # Simetrik: Biri negatif biri pozitif eğimli olmalı ve birbirlerine yaklaşmalı
        if p_slope < 0 and t_slope > 0:
            current_price = df['Close'].iloc[-1]
            # Kırılım yönüne göre (basitçe son muma bakıyoruz şimdilik)
            prediction = "Up" if current_price > df['Close'].iloc[last_peaks[-1]] else "Down"
            target = current_price * 1.15 if prediction == "Up" else current_price * 0.85
            return {
                "pattern": "Symmetrical Triangle",
                "indices": list(last_peaks) + list(last_troughs),
                "target_price": target,
                "prediction": prediction,
                "timeframe_days": 10
            }
        return None

    def detect_cup_and_handle(self, df: pd.DataFrame, threshold: float = 0.05):
        """
        Fincan Kulp tespiti.
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 2 or len(troughs) < 2:
            return None
        
        # Son iki tepe ve son iki dip
        p2_idx, p1_idx = peaks[-1], peaks[-2]
        t2_idx, t1_idx = troughs[-1], troughs[-2]
        
        if not self._is_recent(df, [p2_idx, t2_idx], max_lookback=25):
            return None

        # Sıralama kontrolü: P1 < T1 < P2 < T2 (veya benzeri)
        if not (p1_idx < t1_idx < p2_idx < t2_idx):
            return None
            
        p1, t1, p2, t2 = df['Close'].iloc[p1_idx], df['Close'].iloc[t1_idx], df['Close'].iloc[p2_idx], df['Close'].iloc[t2_idx]
        
        # P1 ve P2 benzer seviyede mi?
        rim_diff = abs(p1 - p2) / p1
        if rim_diff < threshold:
            # Fincan derinliği (T1, P1'in en az %10 altında mı?)
            cup_depth = (p1 - t1) / p1
            if cup_depth > 0.10:
                # Kulp sığlığı (T2, T1'den yukarıda mı?)
                if t2 > t1:
                    current_price = df['Close'].iloc[-1]
                    if current_price > p2:
                        # Hedef: Fincan derinliği kadar yukarı
                        target = p2 + (p1 - t1)
                        return {
                            "pattern": "Cup and Handle",
                            "indices": [p1_idx, t1_idx, p2_idx, t2_idx],
                            "target_price": target,
                            "prediction": "Up",
                            "timeframe_days": 30 # Fincan kulp uzun vadeli bir formasyondur
                        }
        return None

    def detect_triangle(self, df: pd.DataFrame):
        """
        Simetrik Üçgen tespiti.
        """
        peaks, troughs = self.find_extrema(df)
        if len(peaks) < 3 or len(troughs) < 3:
            return None
        
        last_peaks, last_troughs = peaks[-3:], troughs[-3:]
        p_slope, _, _, _, _ = linregress(np.arange(3), df['Close'].iloc[last_peaks].values)
        t_slope, _, _, _, _ = linregress(np.arange(3), df['Close'].iloc[last_troughs].values)
        
        if p_slope < 0 and t_slope > 0:
            return {"pattern": "Symmetrical Triangle", "indices": list(last_peaks) + list(last_troughs), "prediction": "Volatility Breakout"}
        return None

if __name__ == "__main__":
    pass
