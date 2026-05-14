# FormoCast: Profesyonel Gereksinim Spesifikasyonu

## 1. Yönetici Özeti
FormoCast, piyasa verilerini otonom olarak izlemek, yüksek olasılıklı teknik formasyonları tespit etmek ve kullanıcıya görsel istihbarat sunmak üzere tasarlanmış gelişmiş bir finansal gözetim sistemidir. Sistem; estetik mükemmellik, mimari sadelik ve veri odaklı doğruluk analizine öncelik verir.

## 2. Fonksiyonel Gereksinimler (FR)

### 2.1 Veri Toplama ve Gözetim
- **FR-1.1: Çoklu Varlık İzleme:** Sistem, `yfinance` üzerinden Hisse Senetleri, Kripto ve Forex paritelerini desteklemelidir.
- **FR-1.2: Dinamik Zaman Dilimleri:** Günlük, Haftalık ve 4 saatlik periyotları analiz edebilme yeteneği (yapılandırılabilir).
- **FR-1.3: Veri Bütünlüğü:** API limitleri ve eksik veri noktaları (NaN) için sağlam hata yönetimi uygulanmalıdır.

### 2.2 Formasyon Zekası
- **FR-2.1: Geometrik Formasyon Tespiti:** Aşağıdaki formasyonlar için yüksek doğruluklu algoritmaların uygulanması:
    - **İkili Tepe/Dip (Double Top/Bottom):** %2'lik bir sapma eşiği içinde 2 tepe/dip seviyesi dengesi.
    - **Omuz Baş Omuz (Head and Shoulders):** Omuz-baş-omuz simetrisinin tanınması.
    - **Üçgenler/Takozlar:** Ekstremum noktaları üzerinde lineer regresyon kullanarak yakınsayan trend çizgilerinin belirlenmesi.
- **FR-2.2: Sinyal Üretimi:** Tespit edilen her formasyon bir "Güven Puanı" ve "Öngörülen Yön" (Boğa/Ayı) üretmelidir.

### 2.3 Görsel Zeka ve Raporlama
- **FR-3.1: Premium Grafikleme:** Formasyon ekstremumlarını ve hedef bölgelerini vurgulayan, yayına hazır "Dark-Mode" grafiklerin oluşturulması.
- **FR-3.2: Otomatik Bildirimci:** Gömülü görseller ve yönetici özetleri ile gerçek zamanlı e-posta gönderimi.
- **FR-3.3: Haftalık Performans Denetimi:** Geçmiş tahmin sonuçlarına dayalı olarak otomatik "Başarı/Başarısızlık" raporu oluşturulması.

## 3. Fonksiyonel Olmayan Gereksinimler (NFR)

### 3.1 Tasarım Estetiği (ULTRATHINK Modu)
- **NFR-3.1.1: Kasıtlı Minimalizm:** Arayüz ve raporlar "generic" hazır şablonlardan kaçınmalıdır. Özel renk paletleri (#00d1b2, #2d2d2d) kullanılmalıdır.
- **NFR-3.1.2: Görsel Hiyerarşi:** E-posta raporları, tipografi ve boşluk kullanımı yoluyla en kritik bilgileri (Sembol + Yön) önceliklendirmelidir.

### 3.2 Mühendislik Standartları (Karpathy Prensipleri)
- **NFR-3.2.1: Cerrahi Uygulama:** Spekülatif soyutlamalardan kaçınılmalıdır. Her modül doğrudan bir fonksiyonel gereksinime hizmet etmelidir.
- **NFR-3.2.2: Ortam Eşitliği:** "Benim makinemde çalışıyor" sorununu önlemek için tam Dockerizasyon.
- **NFR-3.2.3: Veritabanı Performansı:** `ticker` ve `target_date` üzerinde indekslenmiş aramalar ile SQLite kullanımı.

## 4. Kısıt Analizi ve Varsayımlar
- **API Limitleri:** Kullanıcının `yfinance` ücretsiz katmanını kullandığı varsayılır. IP engellemelerini önlemek için gecikme (delay) mekanizmaları uygulanır.
- **Öngörü Ufku:** Tahminler şu anda 7 günlük bir ileriye dönük periyot ile sabitlenmiştir.
- **Güvenlik:** SMTP kimlik bilgileri asla kod içine gömülmemeli ve `.env` üzerinden enjekte edilmelidir.

## 5. Başarı Kriterleri
- **Tespit Güvenilirliği:** "Mükemmel" geçmiş formasyon örneklerinde sıfır hatalı pozitif.
- **Görsel Etki:** Raporlar "Kıdemli Mimar" görsel standartlarını karşılamalıdır (temiz, bilgilendirici, estetik).
- **Operasyonel Otonomi:** Sistem, manuel müdahale veya bellek sızıntısı olmadan 7 gün boyunca çalışabilmelidir.
