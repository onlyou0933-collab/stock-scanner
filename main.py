import os
import smtplib
from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

# 測試資料
stocks = [
    {
        "name": "台積電",
        "code": "2330",
        "close": 1180,
        "ma5": 1172,
        "volume": 32500
    },
    {
        "name": "長榮",
        "code": "2603",
        "close": 218.5,
        "ma5": 214.2,
        "volume": 28100
    },
    {
        "name": "群創",
        "code": "3481",
        "close": 18.7,
        "ma5": 18.1,
        "volume": 15800
    }
]

html = """
<h2>台股突破 MA5 通知</h2>

<p>
條件：
<li>成交量 > 8000張</li>
<li>收盤價突破 MA5</li>
</p>

<table border="1" cellpadding="8" cellspacing="0">
<tr>
<th>股票名稱</th>
<th>股票代號</th>
<th>收盤價</th>
<th>MA5</th>
<th>成交量(張)</th>
</tr>
"""

for s in stocks:
    html += f"""
    <tr>
        <td>{s['name']}</td>
        <td>{s['code']}</td>
        <td>{s['close']}</td>
        <td>{s['ma5']}</td>
        <td>{s['volume']:,}</td>
    </tr>
    """

html += "</table>"

msg = MIMEText(html, "html", "utf-8")

msg["Subject"] = "台股突破 MA5 通知"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL, PASSWORD)
server.send_message(msg)
server.quit()

print("Email Sent")
