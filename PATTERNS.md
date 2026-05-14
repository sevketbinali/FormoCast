# FormoCast: Formasyon Belirleme Standartları

Bu doküman, FormoCast servisinin finansal grafiklerde formasyonları hangi geometrik ve matematiksel kurallara göre tespit ettiğini açıklar.

## 1. Genel Metodoloji (Ekstremum Noktaları)
Tüm tespitler, fiyat grafiğindeki **Yerel Tepeler (Peaks)** ve **Yerel Dipler (Troughs)** üzerinden yapılır. 
- **Window (Pencere):** Bir noktanın tepe/dip sayılması için sağında ve solunda en az 5 mumdan daha yüksek/düşük olması gerekir.
- **Veri Kaynağı:** Kapanış fiyatları (Close) baz alınır.

## 2. Formasyon Kuralları

### 2.1 İkili Tepe (Double Top)
- **Geometri:** Birbirine çok yakın fiyat seviyelerinde iki tepe oluşmalıdır.
- **Eşik Değer:** İki tepe arasındaki fiyat farkı %2'den az olmalıdır.
- **Onay (Boyun Kırılımı):** İki tepe arasındaki en düşük seviyenin (boyun çizgisi) altına fiyat sarkmalıdır.
- **Sinyal:** Düşüş (Bearish).

### 2.2 İkili Dip (Double Bottom)
- **Geometri:** Birbirine çok yakın fiyat seviyelerinde iki dip oluşmalıdır.
- **Eşik Değer:** İki dip arasındaki fiyat farkı %2'den az olmalıdır.
- **Onay (Boyun Kırılımı):** İki dip arasındaki en yüksek seviyenin (boyun çizgisi) üzerine fiyat çıkmalıdır.
- **Sinyal:** Yükseliş (Bullish).

### 2.3 Omuz Baş Omuz (Head and Shoulders)
- **Geometri:** Üç tepe; orta tepe (baş) diğer iki tepeden (omuzlar) daha yüksektir.
- **Simetri:** Sol ve sağ omuz fiyatları birbirine %5 toleransla yakın olmalıdır.
- **Onay:** Mevcut fiyatın baş noktasından aşağı yönlü uzaklaşması.
- **Sinyal:** Düşüş (Bearish).

### 2.4 Simetrik Üçgen (Symmetrical Triangle)
- **Geometri:** Azalan tepeler ve artan dipler (Fiyat sıkışması).
- **Matematik:** Tepelerin eğimi negatif, diplerin eğimi pozitif olmalıdır.
- **Onay:** Eğimlerin birbirine yaklaşması (yakınsama).
- **Sinyal:** Volatilite Kırılımı (Yön bağımsız).

### 2.5 Takozlar (Wedges)
- **Yükselen Takoz:** Hem tepeler hem dipler yükseliyor, ancak dipler daha hızlı yükseliyor (Yakınsama). Sinyal: Düşüş.
- **Alçalan Takoz:** Hem tepeler hem dipler düşüyor, ancak tepeler daha hızlı düşüyor (Yakınsama). Sinyal: Yükseliş.

### 2.6 Fincan Kulp (Cup and Handle)
- **Geometri:** Büyük bir U şekli (Fincan) ve ardından küçük bir konsolidasyon (Kulp).
- **Derinlik:** Fincan derinliği başlangıç fiyatının en az %10'u kadar olmalıdır.
- **Sinyal:** Yükseliş (Bullish).

## 3. Gelecek Geliştirmeler (Doğruluk Artırımı)
- **Hacim Onayı:** Kırılım anında işlem hacminin ortalamanın üzerinde olması kuralı eklenecektir.
- **RSI Uyumsuzluğu:** Formasyonun RSI göstergesiyle desteklenmesi kontrol edilecektir.
