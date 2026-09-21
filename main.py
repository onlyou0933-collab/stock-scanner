import os
import requests
import yfinance as yf
import smtplib

from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def get_stock_list():

    stocks = {}

    url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"

    try:

        data = requests.get(url, timeout=30).json()

        for row in data:

            code = row.get("公司代號", "")
            name = row.get("公司簡稱", "")

            if code.isdigit():
                stocks[f"{code}.TW"] = name

    except Exception as e:
        print("Get Stock List Error:", e)

    return stocks


stocks = get_stock_list()

print(f"股票數量: {len(stocks)}")

result = []

for symbol, name in stocks.items():

    try:

        df = yf.download(
            symbol,
            period="15d",
            auto_adjust=False,
            progress=False
        )

        if len(df) < 6:
            continue

        close = df["Close"].squeeze()
        volume = df["Volume"].squeeze()

        today_close = float(close.iloc[-1])
        yesterday_close = float(close.iloc[-2])

        today_volume = int(volume.iloc[-1] / 1000)

        ma5_today = float(close.tail(5).mean())
        ma5_yesterday = float(close.iloc[-6:-1].mean())

        vol_ma5 = int(volume.tail(5).mean() / 1000)

        signal = (
            today_volume > 5000
            and today_close > 50
            and today_close > ma5_today
            and yesterday_close <= ma5_yesterday
        )

        if signal:

            result.append({

                "name": name,

                "code": symbol.replace(".TW", ""),

                "close": round(today_close, 2),

                "ma5": round(ma5_today, 2),

                "volume": today_volume,

                "vol_ma5": vol_ma5

            })

    except Exception as e:

        print(symbol, e)

# 成交量排序
result.sort(
    key=lambda x: x["volume"],
    reverse=True
)

# 前500名
result = result[:500]

html = """
<h2>台股突破 MA5 通知</h2>

<p>
條件：
<ul>
<li>成交量 > 5000張</li>
<li>股價 > 50元</li>
<li>收盤價突破 MA5</li>
</ul>
</p>

<table border="1"
       cellpadding="8"
       cellspacing="0"
       style="border-collapse:collapse;">

<tr bgcolor="#D9EAD3">
<th>股票名稱</th>
<th>代號</th>
<th>收盤價</th>
<th>MA5</th>
<th>成交量(張)</th>
<th>均量5日</th>
</tr>
"""

for s in result:

    yahoo_url = (
        f"https://tw.stock.yahoo.com/quote/{s['code']}"
    )

    html += f"""
    <tr>

    <td>{s['name']}</td>

    <td>
      {yahoo_url}
      {s['code']}
      </a>
    </td>

    <td>{s['close']}</td>

    <td>{s['ma5']}</td>

    <td>{s['volume']:,}</td>

    <td>{s['vol_ma5']:,}</td>

    </tr>
    """

html += "</table>"

if not result:

    html += "<br><b>今日沒有符合條件股票</b>"

msg = MIMEText(
    html,
    "html",
    "utf-8"
)

msg["Subject"] = f"台股突破 MA5 通知 ({len(result)}檔)"
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
