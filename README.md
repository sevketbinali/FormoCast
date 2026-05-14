# FormoCast 🚀

FormoCast; hisse senedi ve kripto grafiklerinde teknik analiz formasyonlarını tespit eden, fiyat hareketlerini öngören ve sizi profesyonel düzeyde görsel raporlarla e-posta yoluyla bilgilendiren otonom bir finansal analiz servisidir.

## ✨ Temel Özellikler
- **Otomatik Tespit:** İkili Tepe/Dip, Omuz Baş Omuz, Üçgen ve Takoz formasyonları.
- **İnteraktif Raporlar:** Plotly tabanlı, tarayıcıda incelenebilir interaktif grafikler.
- **Premium Statik Görseller:** E-postalarda hızlı önizleme için karanlık mod grafikler.
- **Performans Analitiği:** Zaman içindeki tahmin doğruluğunu izler.
- **Otonom Çalışma:** Zamanlanmış görevlerle 7/24 kesintisiz izleme.
- **Çok Kanallı Bildirim:** E-posta ve Telegram üzerinden anlık uyarılar.

## 🛠 Teknoloji Yığını
- **Python 3.10+** (Pandas, Scipy, Matplotlib)
- **yfinance** (Piyasa Verisi)
- **SQLite** (Kalıcılık)
- **Docker & Docker Compose**

## 🚀 Başlarken

### 1. Ön Gereksinimler
- Docker ve Docker Compose yüklü olmalıdır.
- Bir SMTP sunucusu (örneğin, Gmail Uygulama Şifresi).

### 2. Yapılandırma
`.env.example` dosyasını `.env` olarak kopyalayın ve bilgilerinizi doldurun:
```bash
cp .env.example .env
```

### 3. Kullanım
Formasyon tarayıcıyı çalıştırın:
```bash
docker-compose run app python main.py --scan --tickers AAPL TSLA BTC-USD
```

Doğruluk analizini çalıştırın:
```bash
docker-compose run app python main.py --analyze
```

## 📂 Proje Yapısı
- `core/`: Tespit ve tahmin mantığı.
- `services/`: Harici entegrasyonlar (Veri, Görsel, E-posta).
- `db/`: Veritabanı modelleri ve kalıcılık.
- `docs/`: (Detaylar için `requirements.md`, `design.md`, `tasks.md` dosyalarına bakın).

## 📄 Dökümantasyon
Mimari ve gereksinimler hakkında daha derinlemesine bilgi için lütfen şu dosyalara bakın:
- [Gereksinimler](requirements.md)
- [Tasarım Dokümanı](design.md)
- [Görev Yol Haritası](tasks.md)
