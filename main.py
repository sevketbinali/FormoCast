import argparse
from services.data_fetcher import DataFetcher
from core.detector import PatternDetector
from services.visualizer import Visualizer
from services.notifier import Notifier
from db.models import Database
import pandas as pd

def run_scanner(tickers):
    fetcher = DataFetcher()
    detector = PatternDetector()
    visualizer = Visualizer()
    notifier = Notifier()
    db = Database()

    for ticker in tickers:
        print(f"Scanning {ticker}...")
        df = fetcher.fetch_ohlc(ticker)
        if df.empty:
            continue

        # Check for patterns
        patterns = [
            detector.detect_double_top(df),
            detector.detect_double_bottom(df)
        ]

        for p in patterns:
            if p:
                print(f"!!! Pattern Found: {p['pattern']} for {ticker}")
                # Save to DB
                current_price = df['Close'].iloc[-1]
                db.save_prediction(ticker, p['pattern'], p['prediction'], current_price)
                
                # Generate Visual
                chart_path = visualizer.plot_pattern(df, ticker, p)
                
                # Notify
                notifier.send_pattern_alert(ticker, p, chart_path)

def run_analysis():
    db = Database()
    fetcher = DataFetcher()
    pending = db.get_pending_predictions()
    
    if not pending:
        print("No pending predictions to analyze.")
        return

    for pred_id, ticker, pred_date, direction, entry_price, target_date in pending:
        print(f"Analyzing prediction {pred_id} for {ticker}...")
        df = fetcher.fetch_ohlc(ticker, period="1mo")
        if df.empty:
            continue
        
        # Check price at target date (or most recent)
        # Find price on or after target_date
        target_price_series = df.loc[df.index >= pd.Timestamp(target_date)]
        if target_price_series.empty:
            continue
        
        target_price = target_price_series['Close'].iloc[0]
        
        outcome = "Correct" if (direction == "Up" and target_price > entry_price) or \
                              (direction == "Down" and target_price < entry_price) else "Incorrect"
        
        db.update_accuracy(pred_id, outcome)
        print(f"Outcome for {ticker}: {outcome}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FormoCast: Financial Pattern Analysis Service")
    parser.add_argument("--scan", action="store_true", help="Run pattern scanner")
    parser.add_argument("--analyze", action="store_true", help="Run accuracy analysis")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "TSLA", "BTC-USD"], help="List of tickers to scan")
    
    args = parser.parse_args()

    if args.scan:
        run_scanner(args.tickers)
    elif args.analyze:
        run_analysis()
    else:
        parser.print_help()
