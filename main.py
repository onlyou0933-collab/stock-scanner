import os
import smtplib
from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

# ===== 測試資料 =====
# 之後會改成 Yahoo Finance 真實資料

stocks = [
    {
        "name": "台積電",
        "code": "2330",
        "close": 1180,
        "y_close": 1110,
        "ma5": 1172,
        "volume": 32500,
        "vol_ma5": 18500
    },
    {
        "name": "長榮",
        "code": "2603",
        "close": 218.5,
        "y_close": 205,
        "ma5": 214.2,
        "volume": 28100,
        "vol_ma5": 15000
    },
    {
        "name": "群創",
        "code": "3481",
        "close": 18.7,
        "y_close": 18.5,
        "ma5": 18.1,
        "volume": 15800,
        "vol_ma5": 12000
    }
]

result = []

for s in stocks:

    change_pct = (
        (s["close"] - s["y_close"])
        / s["y_close"]
        * 100
    )

    signal = (
        s["volume"] > 8000 and
        s["close"] > s["ma5"] and
        s["volume"] > s["vol_ma5"] and
        change_pct >= 5 and
        s["close"] > 50
    )

    if signal:

        s["change_pct"] = round(change_pct, 2)

        result.append(s)

# 成交量由大到小排序
result.sort(
    key=lambda x: x["volume"],
    reverse=True
)

html = """
<h2>台股突破 MA5 選股通知</h2>

<p>
條件：
<ul>
<li>成交量 > 8000張</li>
<li>收盤價突破 MA5</li>
<li>成交量突破 5日均量</li>
<li>當日漲幅 ≥ 5%</li>
<li>股價 > 50元</li>
</ul>
</p>

<table border="1" cellpadding="8" cellspacing="0">
<tr bgcolor="#D9EAD3">
<th>股票名稱</th>
<th>代號</th>
<th>收盤價</th>
<th>漲幅%</th>
<th>MA5</th>
<th>成交量(張)</th>
</tr>
"""

for s in result:

    html += f"""
    <tr>
        <td>{s['name']}</td>
        <td>{s['code']}</td>
        <td>{s['close']}</td>
        <td>{s['change_pct']}%</td>
        <td>{s['ma5']}</td>
        <td>{s['volume']:,}</td>
    </tr>
    """

html += "</table>"

if len(result) == 0:

    html += "<br><b>今日無符合條件股票</b>"

msg = MIMEText(
    html,
    "html",
    "utf-8"
)

msg["Subject"] = "台股突破 MA5 選股通知"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP(
    "smtp.gmail.com",
    587
)

server.starttls()

server.login(
    EMAIL,
    PASSWORD
)

server.send_message(msg)

server.quit()

print("Email Sent")
