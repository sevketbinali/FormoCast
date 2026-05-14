import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

class Notifier:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.receiver_email = os.getenv("RECEIVER_EMAIL")

    def send_pattern_alert(self, ticker: str, pattern_info: dict, chart_path: str, html_path: str = None):
        """
        Sends an email alert with the detected pattern, chart, and optional interactive HTML.
        """
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass, self.receiver_email]):
            print("SMTP settings missing. Skipping email notification.")
            return

        msg = MIMEMultipart('related')
        msg['Subject'] = f"🚀 FormoCast Alert: {pattern_info['pattern']} detected for {ticker}"
        msg['From'] = self.smtp_user
        msg['To'] = self.receiver_email

        # HTML Body
        html = f"""
        <html>
          <body style="background-color: #1a1a1a; color: #ffffff; font-family: sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #2d2d2d; border-radius: 10px; padding: 30px; border: 1px solid #4a4a4a;">
              <h1 style="color: #00d1b2; text-align: center;">FormoCast Alert</h1>
              <hr style="border: 0; border-top: 1px solid #4a4a4a; margin: 20px 0;">
              <p style="font-size: 18px;"><strong>{ticker}</strong> sembolünde <strong>{pattern_info['pattern']}</strong> formasyonu tespit edildi.</p>
              <p style="font-size: 16px;">
                Öngörülen Yön: <span style="color: {'#48c774' if pattern_info['prediction'] == 'Up' else '#ff3860'}; font-weight: bold;">{pattern_info['prediction']}</span><br>
                Hedef Fiyat: <span style="color: #00d1b2; font-weight: bold;">{f"{pattern_info['target_price']:.2f}" if isinstance(pattern_info.get('target_price'), (int, float)) else 'Belirlenmedi'}</span><br>
                Beklenen Vade: <span style="color: #b5b5b5;">{pattern_info.get('timeframe_days', '?')} Gün</span>
              </p>
              <div style="background-color: #333; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; border-left: 4px solid #00d1b2;">
                <strong>Profesyonel Analiz:</strong> {self._generate_commentary(pattern_info)}
              </div>
              <div style="text-align: center; margin-top: 30px;">
                <img src="cid:chart_image" alt="Technical Analysis Chart" style="max-width: 100%; border-radius: 5px; border: 1px solid #4a4a4a;">
              </div>
              <p style="text-align: center; margin-top: 20px;">
                <em>Detaylı analiz için ekteki interaktif HTML dosyasını açabilirsiniz.</em>
              </p>
              <p style="font-size: 14px; color: #b5b5b5; margin-top: 30px; text-align: center;">
                <em>FormoCast tarafından otomatik üretilmiştir.</em>
              </p>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))

        # Attach Static Image
        with open(chart_path, 'rb') as f:
            img_data = f.read()
            image = MIMEImage(img_data)
            image.add_header('Content-ID', '<chart_image>')
            msg.attach(image)

        # Attach Interactive HTML
        if html_path and os.path.exists(html_path):
            from email.mime.base import MIMEBase
            from email import encoders
            with open(html_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(html_path)}')
                msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                print(f"Alert email sent for {ticker}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_weekly_summary(self, stats: dict):
        """
        Sends a weekly summary report of detection performance.
        """
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass, self.receiver_email]):
            print("SMTP settings missing. Skipping weekly summary.")
            return

        msg = MIMEMultipart()
        msg['Subject'] = f"📊 FormoCast: Haftalık Performans Özeti"
        msg['From'] = self.smtp_user
        msg['To'] = self.receiver_email

        pattern_list_html = "".join([f"<li>{p[0]}: {p[1]} adet</li>" for p in stats['top_patterns']])

        html = f"""
        <html>
          <body style="background-color: #1a1a1a; color: #ffffff; font-family: sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #2d2d2d; border-radius: 10px; padding: 30px; border: 1px solid #4a4a4a;">
              <h1 style="color: #00d1b2; text-align: center;">Haftalık Performans Raporu</h1>
              <hr style="border: 0; border-top: 1px solid #4a4a4a; margin: 20px 0;">
              
              <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 30px;">
                <div>
                  <p style="color: #b5b5b5; margin: 0;">Toplam Tespit</p>
                  <h2 style="margin: 5px 0;">{stats['total_detections']}</h2>
                </div>
                <div>
                  <p style="color: #b5b5b5; margin: 0;">Doğruluk Oranı</p>
                  <h2 style="margin: 5px 0; color: #00d1b2;">%{stats['accuracy_rate']:.1f}</h2>
                </div>
              </div>

              <h3 style="color: #00d1b2;">En Sık Görülen Formasyonlar</h3>
              <ul>
                {pattern_list_html}
              </ul>

              <p style="font-size: 14px; color: #b5b5b5; margin-top: 30px; text-align: center;">
                <em>FormoCast tarafından otomatik olarak oluşturulmuştur.</em>
              </p>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                print("Weekly summary email sent.")
        except Exception as e:
            print(f"Failed to send weekly summary: {e}")

    def _generate_commentary(self, pattern_info: dict) -> str:
        pattern = pattern_info['pattern']
        
        comments = {
            "Double Top": "Fiyat iki kez direnç seviyesinden döndü. Boyun çizgisinin kırılması güçlü bir düşüş trendinin başlangıcı olabilir.",
            "Double Bottom": "Fiyat iki kez destek seviyesinden tepki aldı. Boyun çizgisinin aşılmasıyla yükseliş ivme kazanabilir.",
            "Head and Shoulders": "Trend dönüş formasyonu tamamlandı. Omuz seviyelerinin altındaki kapanışlar derinleşen bir satışı tetikleyebilir.",
            "Symmetrical Triangle": "Fiyat daralan bir üçgen içine sıkıştı. Yaklaşan hacimli bir kırılım yüksek volatiliteye neden olacaktır.",
            "Rising Wedge": "Yükselen takozda dipler tepelerden daha hızlı yükseliyor, bu durum alıcıların yorulduğunu ve bir düşüşün yakın olduğunu gösterir.",
            "Falling Wedge": "Alçalan takozda tepeler diplerden daha hızlı düşüyor, bu durum satıcıların baskısının azaldığını ve bir yükseliş tepkisinin yaklaştığını işaret eder.",
            "Cup and Handle": "Güçlü bir boğa formasyonu. Fincan derinliği kadar bir yükseliş potansiyeli masada, kulp üzerindeki kapanışlar takip edilmeli."
        }
        
        return comments.get(pattern, "Teknik göstergeler formasyonun olgunlaştığını gösteriyor. Kırılım yönünde pozisyon takibi önerilir.")
