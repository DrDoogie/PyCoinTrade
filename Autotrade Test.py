import time
import pyupbit
import datetime
import requests
import schedule

#access = "id"
#secret = "id"
#myToken ="id"


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

def get_ma60(ticker):
    """60일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=60)
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    return ma60


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_drop_price(ticker, d):
    """손절가 Target 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    drop_price = df.iloc[0]['close'] - (df.iloc[0]['high'] - df.iloc[0]['low']) * d
    return drop_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


def print_alive():
    print("Autotrade Server is alive!")
    post_message(myToken, "#coinautotrade", "ETH Autotrade is alive")

def print_waiting():
    print("Sell Waiting!")
    post_message(myToken, "#coinautotrade", "Sell Waiting")








upbit = pyupbit.Upbit(access, secret)
nowtime = datetime.datetime.now()


start_time = get_start_time("KRW-ETH") + datetime.timedelta(hours=1)  # 10:00
print("start_time",start_time)
end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(hours=2)  # 9:00 <현재< #7:59:59
print("end_time", end_time)

sell_result= "sell_time"
print(sell_result)



start_time = get_start_time("KRW-ETH") if buy_result is not defined else "2021-12-11 10:00:00"
print("get_start_time", get_start_time("KRW-ETH"))