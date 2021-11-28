
import time
import pyupbit
import datetime
import requests
import schedule

#access = "your-id"
#secret = "your-id"
#myToken = "your-id"


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )


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
    post_message(myToken, "#cointrade", "ETH Autotrade is alive")


# 로그인
upbit = pyupbit.Upbit(access, secret)
nowtime = datetime.datetime.now()
print(nowtime, " autotrade start")
post_message(myToken, "#cointrade", "PyCharm ETH-autotrade start" + str(nowtime))
schedule.every(60).minutes.do(print_alive)  # 10분마다 실행
buy_result = {'price':'0.0', 'volume' : '0.0'}  # 초기값 : 0

# 자동매매 시작
while True:
    schedule.run_pending()
    # time.sleep(1)
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH") + datetime.timedelta(hours=1)  # 10:00
        end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(hours=1)  # 9:00 <현재< #8:59:59

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-ETH", 0.5)
            print(target_price)
            current_price = get_current_price("KRW-ETH")
            print(current_price)

            krw = get_balance("KRW")
            earn = get_balance("ETH")  # 현금 잔고와 Coin 잔고 확인
            if target_price < current_price:
                if krw * 0.3 > 5000:
                    buy_result = upbit.buy_market_order("KRW-ETH", krw * 0.3)
                    post_message(myToken, "#cointrade", "ETH buy : " + str(buy_result) + str(now))
                # 수익 전환
                elif buy_result != 0 and buy_result * 1.05 < current_price and earn * 0.9 > 0.001:
                    success1_result = upbit.sell_market_order("KRW-ETH", earn * 0.50)
                    post_message(myToken, "#cointrade", "ETH 5Pro sell : " + str(float(success1_result['price'])))
                elif buy_result != 0 and buy_result * 1.03 < current_price and earn * 0.5 > 0.001:
                    success2_result = upbit.sell_market_order("KRW-ETH", earn * 0.50)
                    post_message(myToken, "#cointrade", "ETH 3Pro sell : " + str(float(success2_result['price'])))
                elif start_time + datetime.timedelta(hours=6) < now and buy_result != 0 and buy_result * 1.02 < current_price and earn * 0.5 > 0.001:
                    success3_result = upbit.sell_market_order("KRW-ETH", earn * 0.50)
                    post_message(myToken, "#cointrade", "ETH 2Pro sell : " + str(float(success3_result['price'])))
                elif start_time + datetime.timedelta(hours=10) < now and buy_result != 0 and buy_result * 1.015 < current_price and earn * 0.5 > 0.001:
                    success4_result = upbit.sell_market_order("KRW-ETH", earn * 0.50)
                    post_message(myToken, "#cointrade", "ETH 1.5Pro sell : " + str(float(success4_result['price'])))
                elif start_time + datetime.timedelta(hours=13) < now and buy_result != 0 and buy_result * 1.01 < current_price and earn * 0.5 > 0.001:
                    success5_result = upbit.sell_market_order("KRW-ETH", earn * 0.50)
                    post_message(myToken, "#cointrade", "ETH 1Pro sell : " + str(float(success5_result['price'])))

            # 하락세 급락 방지 손절
            else:
                drop_price = get_drop_price("KRW-ETH", 0.9)
                if drop_price > current_price:
                    drop = get_balance("ETH")
                    if drop * 0.9 > 0.001:
                        fail_result = upbit.sell_market_order("KRW-ETH", drop * 0.90)
                        post_message(myToken, "#cointrade", "ETH Drop sell : " + str(fail_result))

        else:
            btc = get_balance("ETH")
            if btc * 0.9 > 0.001:
                sell_result = upbit.sell_market_order("KRW-ETH", btc * 0.90)
                post_message(myToken, "#cointrade", "ETH sell : " + str(sell_result))
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, "#cointrade", e)
        break
        time.sleep(1)

