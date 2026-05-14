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

    def send_pattern_alert(self, ticker: str, pattern_info: dict, chart_path: str):
        """
        Sends an email alert with the detected pattern and chart.
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
          <body style="background-color: #1a1a1a; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #2d2d2d; border-radius: 10px; padding: 30px; border: 1px solid #4a4a4a;">
              <h1 style="color: #00d1b2; text-align: center;">FormoCast Alert</h1>
              <hr style="border: 0; border-top: 1px solid #4a4a4a; margin: 20px 0;">
              <p style="font-size: 18px;">We detected a <strong>{pattern_info['pattern']}</strong> for <strong>{ticker}</strong>.</p>
              <p style="font-size: 16px;">Predicted Direction: <span style="color: {'#48c774' if pattern_info['prediction'] == 'Up' else '#ff3860'}; font-weight: bold;">{pattern_info['prediction']}</span></p>
              <div style="text-align: center; margin-top: 30px;">
                <img src="cid:chart_image" alt="Technical Analysis Chart" style="max-width: 100%; border-radius: 5px; border: 1px solid #4a4a4a;">
              </div>
              <p style="font-size: 14px; color: #b5b5b5; margin-top: 30px; text-align: center;">
                <em>This is an automated analysis by FormoCast.</em>
              </p>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))

        # Attach Image
        with open(chart_path, 'rb') as f:
            img_data = f.read()
            image = MIMEImage(img_data)
            image.add_header('Content-ID', '<chart_image>')
            msg.attach(image)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                print(f"Alert email sent for {ticker}")
        except Exception as e:
            print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Test block
    pass
