import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load .env
load_dotenv()

def test_smtp():
    server_addr = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    receiver = os.getenv("RECEIVER_EMAIL")

    print(f"Testing SMTP connection to {server_addr}:{port}...")
    print(f"User: {user}")
    print(f"Receiver: {receiver}")

    msg = MIMEText("FormoCast E-posta bağlantı testi başarılı!")
    msg['Subject'] = "FormoCast Test Email"
    msg['From'] = user
    msg['To'] = receiver

    try:
        with smtplib.SMTP(server_addr, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            print("✅ E-posta başarıyla gönderildi!")
            return True
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        if "Authentication failed" in str(e):
            print("İPUCU: Gmail kullanıyorsanız 'Uygulama Şifresi' (App Password) kullanmanız gerekebilir.")
        return False

if __name__ == "__main__":
    test_smtp()
