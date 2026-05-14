import plotly.graph_objects as go
import pandas as pd
import os

class InteractiveVisualizer:
    def __init__(self, output_dir: str = "plots/interactive"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_html(self, df: pd.DataFrame, ticker: str, pattern_info: dict) -> str:
        """
        Generates an interactive HTML chart using Plotly.
        """
        fig = go.Figure()

        # Add Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Market Data'
        ))

        # Highlight Pattern Points
        indices = pattern_info['indices']
        pattern_df = df.iloc[indices]
        
        fig.add_trace(go.Scatter(
            x=pattern_df.index,
            y=pattern_df['Close'],
            mode='markers',
            marker=dict(size=12, color='#00d1b2', symbol='diamond'),
            name=f"Detected {pattern_info['pattern']}"
        ))

        # Layout styling for "Premium" look
        fig.update_layout(
            title=f"{ticker} - {pattern_info['pattern']} Analizi",
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            font=dict(color='#ffffff')
        )

        # Save to HTML
        filename = f"{ticker}_{pattern_info['pattern']}_interactive.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
