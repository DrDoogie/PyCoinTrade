# REST API

import requests

url = "https://api.upbit.com/v1/market/all"
resp= requests.get(url)
data = resp.json()

krw_tickers=[]
for coin in data:
    ticker=coin['market']

    if ticker.startswith("KRW"):
        krw_tickers.append(ticker)
print(krw_tickers)
print(len(krw_tickers))