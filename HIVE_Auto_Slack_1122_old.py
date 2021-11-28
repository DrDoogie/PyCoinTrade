import time
import pyupbit
import datetime
import requests
import schedule


#개인 인증 - 보안 주의
#access = "your-id"
#secret = "your-id"
#myToken = "your-id"

#슬랙 메시지 전송
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
    post_message(myToken, "#cointrade", "HIVE Autotrade is alive")

# 업비트 로그인
upbit = pyupbit.Upbit(access, secret)
nowtime= datetime.datetime.now()
print(nowtime," autotrade start")
post_message(myToken,"#cointrade", "PyCharm HIVE-autotrade start"+str(nowtime))
schedule.every(120).minutes.do(print_alive)  # 10분마다 실행
buy_price = 0   #초기값 : 0

# 자동매매 시작
while True:
    schedule.run_pending()
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-HIVE")+datetime.timedelta(hours=1)  #10:00 부터 시작
        end_time = start_time + datetime.timedelta(days=1)-datetime.timedelta(hours=2) #9:00 <현재< #7:59:59

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-HIVE", 0.4)
            current_price = get_current_price("KRW-HIVE")
            krw = get_balance("KRW")
            coin = get_balance("HIVE")                 #현금 잔고와 Coin 잔고 확인
            if target_price < current_price:
                if krw*0.3 > 400000:
                    buy_result = upbit.buy_market_order("KRW-HIVE", krw*0.3)
                    buy_price = float(buy_result['price'])
                    post_message(myToken, "#cointrade", "HIVE buy : " + str(buy_price)+str(now))
                    # 수익 전환 매도
                elif buy_price != 0 and buy_price * 1.05 < current_price and coin *0.9 >3.001:
                    success1_result = upbit.sell_market_order("KRW-HIVE", coin * 0.50)
                    success1_price = float(success1_result['price'])
                    post_message(myToken, "#cointrade", "HIVE 5Pro sell : " + str(success1_price))
                elif start_time + datetime.timedelta(hours=2) < now and buy_price != 0 and buy_price * 1.03 < current_price and coin *0.5 >3.001:
                    success2_result = upbit.sell_market_order("KRW-HIVE", coin * 0.50)
                    success2_price = float(success2_result['price'])
                    post_message(myToken, "#cointrade", "HIVE 3Pro sell : " + str(success2_price))
                elif start_time + datetime.timedelta(hours=4) < now and buy_price != 0 and buy_price * 1.02 < current_price and coin *0.5 > 3.001:
                    success3_result = upbit.sell_market_order("KRW-HIVE", coin * 0.50)
                    success3_price = float(success3_result['price'])
                    post_message(myToken, "#cointrade", "HIVE 2Pro sell : " + str(success3_price))
                elif start_time + datetime.timedelta(hours=6) < now and buy_price != 0 and buy_price * 1.015 < current_price and coin *0.5 > 3.001:
                    success4_result = upbit.sell_market_order("KRW-HIVE", coin * 0.50)
                    success4_price = float(success4_result['price'])
                    post_message(myToken, "#cointrade", "HIVE 1.5Pro sell : " + str(success4_price))
                elif start_time + datetime.timedelta(hours=10) < now and buy_price != 0 and buy_price * 1.01 < current_price and coin *0.5 > 3.001:
                    success5_result = upbit.sell_market_order("KRW-HIVE", coin * 0.50)
                    success5_price = float(success5_result['price'])
                    post_message(myToken, "#cointrade", "HIVE 1Pro sell : " + str(success5_price))
            # 하락세 급락 방지 손절
            else:
                drop_price = get_drop_price("KRW-HIVE", 0.9)
                if drop_price > current_price:
                    drop = get_balance("HIVE")
                    if drop * 0.9 > 3.001:
                        fail_result = upbit.sell_market_order("KRW-HIVE", drop * 0.90)
                        fail_price = float(fail_result['price'])
                        post_message(myToken, "#cointrade", "HIVE Drop sell : " + str(fail_price))

        else:
            btc = get_balance("HIVE")
            if btc * 0.9 > 3.001:
                sell_result = upbit.sell_market_order("KRW-HIVE", btc*0.90)
                post_message(myToken, "#cointrade", "HIVE sell : " + str(sell_result))
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, "#cointrade", e)
        break
        time.sleep(1)


#ADA >3 , ETH > 0.001 , BTC > 0.0001:, HIVE >3