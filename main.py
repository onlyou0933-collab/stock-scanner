import os
import smtplib
import pandas as pd
import yfinance as yf

from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

# 先測試這些股票
stocks = {
    "2330.TW": "台積電",
    "2317.TW": "鴻海",
    "2454.TW": "聯發科",
    "2603.TW": "長榮",
    "2609.TW": "陽明",
    "2303.TW": "聯電",
    "2881.TW": "富邦金",
    "2882.TW": "國泰金",
    "3231.TWO": "緯創",
    "2382.TW": "廣達"
}

result = []

for symbol, name in stocks.items():

    try:

        df = yf.download(
            symbol,
            period="15d",
            progress=False,
            auto_adjust=False
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

        change_pct = (
            (today_close - yesterday_close)
            / yesterday_close
            * 100
        )

        signal = (
            today_volume > 8000
            and today_close > ma5_today
            and yesterday_close <= ma5_yesterday
            and today_volume > vol_ma5
            and change_pct >= 5
            and today_close > 50
        )

        if signal:

            result.append({
                "name": name,
                "code": symbol.replace(".TW", "").replace(".TWO", ""),
                "close": round(today_close, 2),
                "change_pct": round(change_pct, 2),
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

<table border="1" cellpadding="8" cellspacing="0"
style="border-collapse:collapse;">

<tr bgcolor="#D9EAD3">
<th>股票名稱</th>
<th>代號</th>
<th>收盤價</th>
<th>漲幅%</th>
<th>MA5</th>
<th>成交量(張)</th>
<th>均量5日</th>
</tr>
"""

for s in result:

    url = f"https://tw.stock.yahoo.com/quote/{s['code']}"

    html += f"""
    <tr>
      <td>{s['name']}</td>

      <td>
        {url}
          {s['code']}
        </a>
      </td>

      <td>{s['close']}</td>
      <td>{s['change_pct']}%</td>
      <td>{s['ma5']}</td>
      <td>{s['volume']:,}</td>
      <td>{s['vol_ma5']:,}</td>
    </tr>
    """

html += "</table>"

if len(result) == 0:
    html += "<br><b>今日沒有符合條件股票</b>"

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
