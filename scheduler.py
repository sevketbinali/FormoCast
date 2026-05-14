import time
import schedule
import os
import subprocess
from datetime import datetime

def job():
    print(f"[{datetime.now()}] Otomatik tarama başlatılıyor...")
    # main.py'yi --scan bayrağıyla çalıştır
    tickers = os.getenv("MONITOR_TICKERS", "AAPL MSFT TSLA BTC-USD").split()
    cmd = ["python", "main.py", "--scan", "--tickers"] + tickers
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Hata: {result.stderr}")
    except Exception as e:
        print(f"İşlem sırasında hata oluştu: {e}")

def analysis_job():
    print(f"[{datetime.now()}] Doğruluk analizi başlatılıyor...")
    cmd = ["python", "main.py", "--analyze"]
    subprocess.run(cmd)

def report_job():
    print(f"[{datetime.now()}] Haftalık rapor gönderiliyor...")
    cmd = ["python", "main.py", "--report"]
    subprocess.run(cmd)

# Zamanlama kuralları
# Her gün saat 23:00'da tara (Borsa kapanış sonrası)
schedule.every().day.at("23:00").do(job)

# Her gün saat 00:00'da geçmiş tahminleri analiz et
schedule.every().day.at("00:00").do(analysis_job)

# Her Pazar saat 21:00'da haftalık rapor gönder
schedule.every().sunday.at("21:00").do(report_job)

print("FormoCast Zamanlayıcı başlatıldı. Servis otonom olarak çalışıyor...")

if __name__ == "__main__":
    # İlk çalışma için hemen bir tarama yap (isteğe bağlı)
    # job() 
    
    while True:
        schedule.run_pending()
        time.sleep(60)
