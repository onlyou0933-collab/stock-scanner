import os
import smtplib
from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

msg = MIMEText("GitHub自動寄信測試成功")

msg["Subject"] = "Stock Scanner Test"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login(EMAIL, PASSWORD)
server.send_message(msg)

server.quit()

print("Email Sent")
