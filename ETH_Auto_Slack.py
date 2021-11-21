import time
import pyupbit
import datetime
import requests
import schedule

access = "kxkbjuQrLzUF8MHE0sGdFThxkIifbrmNvoofbbc8"
secret = "DjEs4Z05nvx1WJxNa8rGOxKNRaVOogvDxpKAijt8"
myToken = "xoxb-2750670045522-2752959579764-zuV1ouahzr5rYW9f6fbXdtdf"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_drop_price(ticker, d):
    """손절가 조회"""
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
    post_message(myToken, "#pycoin", "ETH Autotrade is alive")

# 로그인
upbit = pyupbit.Upbit(access, secret)
nowtime= datetime.datetime.now()
print(nowtime," autotrade start")
post_message(myToken,"#pycoin", "ETH-autotrade start"+str(nowtime))
schedule.every(60).minutes.do(print_alive)  # 10분마다 실행
# 자동매매 시작
while True:
    schedule.run_pending()
    #time.sleep(1)
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")+datetime.timedelta(hours=1)  #10:00
        end_time = start_time + datetime.timedelta(days=1)-datetime.timedelta(hours=1) #9:00 <현재< #8:59:59

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-ETH", 0.5)
            current_price = get_current_price("KRW-ETH")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw*0.3 > 5000:
                    buy_result = upbit.buy_market_order("KRW-ETH", krw*0.3)
                    post_message(myToken, "#pycoin", "ETH buy : " + str(buy_result)+str(now))
                    # 수익 전환
                    if buy_result * 1.03 < current_price:
                        earn = get_balance("ETH")
                        if earn * 0.5 > 0.001:
                            success_result = upbit.sell_market_order("KRW-ETH", earn * 0.50)
                            post_message(myToken, "#pycoin", "ETH 3Pro sell : " + str(success_result))
                            if buy_result * 1.05 < current_price:
                                earn_2nd = get_balance("ETH")
                                if earn_2nd *0.9  > 0.001:
                                    double_success_result = upbit.sell_market_order("KRW-ETH", earn_2nd * 0.90)
                                    post_message(myToken, "#pycoin", "ETH 5Pro sell : " + str(double_success_result))

            # 급락 방지 손절
            else:
                drop_price = get_drop_price("KRW-ETH", 0.9)
                if drop_price > current_price:
                    drop = get_balance("ETH")
                    if drop * 0.9 > 0.001:
                        fail_result = upbit.sell_market_order("KRW-ETH", drop * 0.90)
                        post_message(myToken, "#pycoin", "ETH Drop sell : " + str(fail_result))

        else:
            btc = get_balance("ETH")
            if btc * 0.9 > 0.001:
                sell_result = upbit.sell_market_order("KRW-ETH", btc*0.90)
                post_message(myToken, "#pycoin", "ETH sell : " + str(sell_result))
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, "#pycoin", e)
        time.sleep(1)


#ADA >3 , ETH > 0.001 , BTC > 0.0001: