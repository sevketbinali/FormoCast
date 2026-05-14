import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import pandas as pd
from datetime import datetime

class Visualizer:
    def __init__(self, plots_dir=None):
        self.plots_dir = plots_dir or os.getenv("PLOTS_DIR", "plots")
        os.makedirs(self.plots_dir, exist_ok=True)

    def plot_pattern(self, df: pd.DataFrame, ticker: str, pattern_info: dict) -> str:
        """
        Creates a high-fidelity candlestick chart with pattern highlights.
        """
        # Slice data to show only the last 50-60 candles for clarity
        plot_df = df.tail(60).copy()
        
        # Prepare pattern-specific markings
        pattern_name = pattern_info['pattern']
        indices = pattern_info.get('indices', [])
        
        # Highlight points
        h_points = []
        for idx in indices:
            if idx in plot_df.index: # If index is in our slice
                h_points.append(plot_df.loc[idx, 'Close'])
            else:
                h_points.append(None)

        # File naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{pattern_name.replace(' ', '_')}_{timestamp}.png"
        filepath = os.path.join(self.plots_dir, filename)

        # Style configuration
        mc = mpf.make_marketcolors(up='#00d1b2', down='#ff3860',
                                  edge='inherit',
                                  wick='inherit',
                                  volume='inherit')
        s  = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, 
                                gridcolor='#333333', facecolor='#0f0f0f')

        # Add trendlines if needed (e.g. Neckline)
        alines = []
        if 'neckline' in pattern_info:
            neck_val = pattern_info['neckline']
            alines.append([(plot_df.index[0], neck_val), (plot_df.index[-1], neck_val)])

        # Plotting
        mpf.plot(plot_df, 
                 type='candle', 
                 style=s,
                 title=f"\n{ticker} - {pattern_name}",
                 ylabel='Fiyat',
                 volume=True,
                 alines=dict(alines=alines, colors='#00d1b2', linewidths=2, alpha=0.5),
                 savefig=dict(fname=filepath, dpi=100, bbox_inches='tight'),
                 tight_layout=True)

        return filepath
