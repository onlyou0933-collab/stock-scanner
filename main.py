import os
import requests
import yfinance as yf
import smtplib

from email.mime.text import MIMEText


EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def get_stock_list():

    stocks = {}

    api_url = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"

    try:

        response = requests.get(api_url, timeout=30)
        data = response.json()

        for row in data:

            code = str(row.get("公司代號", "")).strip()
            name = str(row.get("公司簡稱", "")).strip()

            if code.isdigit():

                stocks[f"{code}.TW"] = name

    except Exception as e:

        print("取得股票清單失敗：", e)

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
            progress=False,
            threads=False
        )

        if len(df) < 6:
            continue

        close = df["Close"]
        volume = df["Volume"]

        today_close = float(close.iloc[-1])
        yesterday_close = float(close.iloc[-2])

        today_volume = int(volume.iloc[-1] / 1000)

        ma5_today = float(close.tail(5).mean())
        ma5_yesterday = float(close.iloc[-6:-1].mean())

        vol_ma5 = int(volume.tail(5).mean() / 1000)

        signal = (

            # 成交量 > 5000張
            today_volume > 5000

            and

            # 股價 > 50元
            today_close > 50

            and

            # 收盤價突破 MA5
            today_close > ma5_today
            and yesterday_close <= ma5_yesterday

            and

            # 成交量突破均量
            today_volume > vol_ma5

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


result.sort(
    key=lambda x: x["volume"],
    reverse=True
)


html = """
<html>
<body>

<h2>台股突破 MA5 通知</h2>

<p>
條件：
</p>

<ul>
<li>成交量 > 5000張</li>
<li>股價 > 50元</li>
<li>收盤價突破 MA5</li>
<li>成交量突破 5日均量</li>
</ul>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">

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

    yahoo_url = f"https://tw.stock.yahoo.com/quote/{s['code']}"

    html += f"""
    <tr>

        <td>{s['name']}</td>

        <td>
            {yahoo_url}
                {s['code']}
            </a>
        </td>

        <td>{s['close']}</td>

        <td
