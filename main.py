import yfinance as yf
import os
import smtplib
from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

# 測試台積電資料
stock = yf.Ticker("2330.TW")
hist = stock.history(period="10d")

content = f"""
Yahoo Finance 測試成功

台積電最近資料：

{hist.tail().to_string()}
"""

msg = MIMEText(content)

msg["Subject"] = "Yahoo Finance 測試"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print("Email Sent")

