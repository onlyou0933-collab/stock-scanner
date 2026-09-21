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

        print("股票清單取得失敗:", e)

    return stocks


stocks = get_stock_list()

print(f"取得股票數量: {len(stocks)}")

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

        signal = (

            # 成交量 > 5000張
            today_volume > 5000

            # 股價 > 50元
            and today_close > 50

            # 價格突破MA5
            and today_close > ma5_today
            and yesterday_close <= ma5_yesterday

            # 量突破5日均量
            and today_volume > vol_ma5

        )

        if signal:

            result.append({

                "name": name,

        
