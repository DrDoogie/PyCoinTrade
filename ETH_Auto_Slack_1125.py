
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
    post_message(myToken, "#cointrade", "ETH Autotrade is alive")

# 로그인
upbit = pyupbit.Upbit(access, secret)
nowtime = datetime.datetime.now()
print(nowtime, " autotrade start")
post_message(myToken, "#cointrade", "ETH-autotrade start" + str(nowtime))
schedule.every(60).minutes.do(print_alive)  # 10분마다 실행

buy_result = {'price':'0.0', 'volume' : '0.0'}  # 초기 dict 값 : 0
sell_result = {'price':'0.0', 'volume' : '0.0'}  # 초기 dict 값 : 0
#buy_price = float(buy_result['price'])
current_price = get_current_price("KRW-ETH")
#buy_price = 0.0 #초기 매수가 0원
buy_volume = float(buy_result['volume'])

# 자동매매 시작
while True:
    schedule.run_pending()
    try:
        # 시간 체크 하기
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH") + datetime.timedelta(hours=1)  # 10:00
        end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(hours=1)  # 10:00 <현재< 다음날 #8:59:59

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-ETH", 0.5)
            current_price = get_current_price("KRW-ETH")
            krw = get_balance("KRW")
            #print("현재잔고")
            #print(krw)
            earn = get_balance("ETH")  # 현금 잔고와 Coin 잔고 확인
            if krw *0.8  > 5000:
                if target_price < current_price:
                    buy_result = upbit.buy_market_order("KRW-ETH", krw*0.8)
                    buy_price = get_current_price("KRW-ETH") * 1.001 # 매수 금액을 buy_price에 입력
                    print("매수금액")
                    print(buy_price)
                    post_message(myToken, "#cointrade", "ETH buy : " + str(buy_price) )
                    # 현재가가 Target_price보다 크고 buy_price가 현재가 보다 작으면 매수
                    # 5% 수익나면 매도
                    while True :
                        #print("매도대기중")
                        current_price = get_current_price("KRW-ETH")
                        earn = get_balance("ETH")
                        if buy_price * 1.05 < current_price and earn * 0.995 > 0.001:
                            sell_result = upbit.sell_market_order("KRW-ETH", earn * 0.995)
                            sell_coin = float(sell_result['volume'])
                            post_message(myToken, "#cointrade", "ETH 5Pro sell : " + str(sell_coin))
                            break

                        elif buy_price * 1.03 < current_price and earn * 0.995 > 0.001:
                            sell_result = upbit.sell_market_order("KRW-ETH", earn * 0.9950)
                            sell_coin = float(sell_result['volume'])
                            post_message(myToken, "#cointrade", "ETH 3Pro sell : " + str(sell_coin))
                            break
                            # 4시간 경과 후부터 2% 수익 나면 매도

                        elif start_time + datetime.timedelta(hours=4) < now and buy_price * 1.02 < current_price and earn * 0.995 > 0.001:
                            sell_result = upbit.sell_market_order("KRW-ETH", earn * 0.9950)
                            sell_coin = float(sell_result['volume'])
                            post_message(myToken, "#cointrade", "ETH 2Pro sell : " + str(sell_coin))
                            break
                            # 6시간 경과 후부터 1.5% 수익 나면 매도

                        elif start_time + datetime.timedelta(hours=6) < now and buy_price * 1.015 < current_price and earn * 0.995 > 0.001:
                            sell_result = upbit.sell_market_order("KRW-ETH", earn * 0.9950)
                            sell_coin = float(sell_result['volume'])
                            post_message(myToken, "#cointrade", "ETH 1.5Pro sell : " + str(sell_coin))
                            break

                        elif start_time + datetime.timedelta(hours=8) < now and buy_price * 1.010 < current_price and earn * 0.995 > 0.001:
                            sell_result = upbit.sell_market_order("KRW-ETH", earn * 0.9950)
                            sell_coin = float(sell_result['volume'])
                            post_message(myToken, "#cointrade", "ETH 1.5Pro sell : " + str(sell_coin))
                            break
                        elif target_price > current_price :
                            drop_price = get_drop_price("KRW-ETH", 0.9)
                            if drop_price > current_price:
                                drop = get_balance("ETH")
                                if drop * 0.9 > 0.001:
                                    sell_result = upbit.sell_market_order("KRW-ETH", drop * 0.90)
                                    sell_coin = float(sell_result['volume'])
                                    post_message(myToken, "#cointrade", "ETH Drop sell : " + str(sell_coin))

                        #elif 1>0 :
                         #   print("매도 대기중")
                        time.sleep(1)

                # target_price > current_price 인 경우
                else:
                    drop_price = get_drop_price("KRW-ETH", 0.9)
                    if drop_price > current_price:
                        drop = get_balance("ETH")
                        if drop * 0.9 > 0.001:
                            sell_result = upbit.sell_market_order("KRW-ETH", drop * 0.90)
                            sell_coin = float(sell_result['volume'])
                            post_message(myToken, "#cointrade", "ETH Drop sell : " + str(sell_coin))

            else:
                if target_price * 1.1 < current_price:
                    btc = get_balance("ETH")
                    if btc * 0.9 > 0.001:
                        sell_result = upbit.sell_market_order("KRW-ETH", btc * 0.90)
                        sell_coin = float(sell_result['volume'])
                        post_message(myToken, "#cointrade", "ETH sell : " + str(sell_coin))




        else:
            btc = get_balance("ETH")
            if btc * 0.9 > 0.001:
                sell_result = upbit.sell_market_order("KRW-ETH", btc * 0.90)
                sell_coin = float(sell_result['volume'])
                post_message(myToken, "#cointrade", "ETH sell : " + str(sell_coin))
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, "#cointrade", e)
        break
        time.sleep(1)

#ADA >3 , ETH > 0.001 , BTC > 0.0001: