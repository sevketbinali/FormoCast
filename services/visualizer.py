import matplotlib.pyplot as plt
import pandas as pd
import os

class Visualizer:
    def __init__(self, output_dir: str = "plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Apply a dark theme for a premium look
        plt.style.use('dark_background')

    def plot_pattern(self, df: pd.DataFrame, ticker: str, pattern_info: dict) -> str:
        """
        Generates a chart highlighting the detected pattern.
        """
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], color='#00d1b2', label='Close Price', linewidth=1.5)
        
        pattern_name = pattern_info['pattern']
        indices = pattern_info['indices']
        
        # Highlight pattern points
        pattern_dates = df.index[indices]
        pattern_values = df['Close'].iloc[indices]
        plt.scatter(pattern_dates, pattern_values, color='#ff3860', s=100, zorder=5, label=f'{pattern_name} Points')
        
        # Add labels and title
        plt.title(f"{ticker} - {pattern_name} Detected", fontsize=16, color='white', pad=20)
        plt.xlabel("Date", color='#b5b5b5')
        plt.ylabel("Price", color='#b5b5b5')
        plt.legend()
        plt.grid(color='#4a4a4a', linestyle='--', linewidth=0.5)
        
        # Save the plot
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{pattern_name}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        
        return filepath

if __name__ == "__main__":
    from services.data_fetcher import DataFetcher
    fetcher = DataFetcher()
    data = fetcher.fetch_ohlc("TSLA")
    viz = Visualizer()
    path = viz.plot_pattern(data, "TSLA", {"pattern": "Double Top", "indices": [len(data)-20, len(data)-10]})
    print(f"Saved plot to {path}")
