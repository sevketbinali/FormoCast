import argparse
from services.data_fetcher import DataFetcher
from core.detector import PatternDetector
from services.visualizer import Visualizer
from services.interactive_visualizer import InteractiveVisualizer
from services.notifier import Notifier
from services.telegram_notifier import TelegramNotifier
from db.models import Database
import pandas as pd

def run_scanner(tickers):
    fetcher = DataFetcher()
    detector = PatternDetector()
    visualizer = Visualizer()
    interactive_viz = InteractiveVisualizer()
    notifier = Notifier()
    tg_notifier = TelegramNotifier()
    db = Database()

    for ticker in tickers:
        print(f"Scanning {ticker}...")
        df = fetcher.fetch_ohlc(ticker)
        if df.empty:
            continue

        # Check for patterns
        patterns = [
            detector.detect_double_top(df),
            detector.detect_double_bottom(df),
            detector.detect_head_and_shoulders(df),
            detector.detect_triangle(df),
            detector.detect_wedge(df),
            detector.detect_cup_and_handle(df)
        ]

        for p in patterns:
            if p:
                print(f"!!! Pattern Found: {p['pattern']} for {ticker}")
                # Save to DB with target and timeframe
                current_price = df['Close'].iloc[-1]
                target_price = p.get('target_price')
                timeframe = p.get('timeframe_days', 7)
                
                db.save_prediction(ticker, p['pattern'], p['prediction'], current_price, target_price, timeframe)
                
                # Generate Static Visual
                chart_path = visualizer.plot_pattern(df, ticker, p)
                
                # Generate Interactive Visual
                html_path = interactive_viz.generate_html(df, ticker, p)
                
                # Notify via Email
                notifier.send_pattern_alert(ticker, p, chart_path, html_path)

                # Notify via Telegram
                caption = f"🚀 *FormoCast Alert: {p['pattern']}*\nTicker: {ticker}\nPrediction: {p['prediction']}"
                tg_notifier.send_photo(chart_path, caption)

def run_analysis():
    db = Database()
    fetcher = DataFetcher()
    # Fetch pending OR checked but recently mature (for PnL update)
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticker, predicted_direction, entry_price, target_price, target_date FROM predictions WHERE accuracy_checked = 0")
    pending = cursor.fetchall()
    conn.close()
    
    if not pending:
        print("No pending predictions to analyze.")
        return

    for pred_id, ticker, direction, entry_price, target_price, target_date in pending:
        print(f"Analyzing prediction {pred_id} for {ticker}...")
        df = fetcher.fetch_ohlc(ticker, period="1mo")
        if df.empty:
            continue
        
        # Current price
        current_price = df['Close'].iloc[-1]
        
        # Target Hit?
        target_hit = False
        if target_price:
            if direction == "Up" and df['High'].max() >= target_price:
                target_hit = True
            elif direction == "Down" and df['Low'].min() <= target_price:
                target_hit = True

        # Date Expired?
        expired = datetime.now() >= datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")
        
        if target_hit or expired:
            outcome = "Correct" if target_hit else "Incorrect"
            # Final price for PnL calculation
            final_price = target_price if target_hit else current_price
            pnl = ((final_price - entry_price) / entry_price) * 100
            if direction == "Down": pnl = -pnl # Short position
            
            # Update DB
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE predictions SET actual_outcome = ?, pnl_percent = ?, accuracy_checked = 1 WHERE id = ?", (outcome, pnl, pred_id))
            conn.commit()
            conn.close()
            print(f"Outcome for {ticker}: {outcome} (PnL: {pnl:.2f}%)")

def run_report():
    analyzer = AccuracyAnalyzer()
    stats = analyzer.get_weekly_stats()
    notifier = Notifier()
    notifier.send_weekly_summary(stats)

if __name__ == "__main__":
    from core.analyzer import AccuracyAnalyzer
    parser = argparse.ArgumentParser(description="FormoCast: Finansal Formasyon Analiz Servisi")
    parser.add_argument("--scan", action="store_true", help="Tarayıcıyı çalıştır")
    parser.add_argument("--analyze", action="store_true", help="Doğruluk analizini çalıştır")
    parser.add_argument("--report", action="store_true", help="Haftalık özeti gönder")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "TSLA", "BTC-USD"], help="Taranacak semboller")
    
    args = parser.parse_args()

    if args.scan:
        run_scanner(args.tickers)
    elif args.analyze:
        run_analysis()
    elif args.report:
        run_report()
    else:
        parser.print_help()
