import os
import smtplib
from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

content = """
股票掃描系統測試成功

明天開始改成正式版選股條件：

1. 成交量 > 8000張
2. 收盤價突破MA5
3. 每天下午14:30自動寄送
"""

msg = MIMEText(content)

msg["Subject"] = "台股選股系統已上線"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print("Email Sent")
