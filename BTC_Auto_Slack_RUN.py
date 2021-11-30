
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
    post_message(myToken, "#cointrade", "BTC Autotrade is alive")

def print_waiting():
    print("Sell Waiting!")
    post_message(myToken, "#cointrade", "Sell Waiting")

# 로그인
upbit = pyupbit.Upbit(access, secret)
nowtime = datetime.datetime.now()
print(nowtime, " autotrade start")
post_message(myToken, "#cointrade", "BTC autotrade start" + str(nowtime))
schedule.every(60).minutes.do(print_alive)  # 60분마다 실행
buy_result = {'price':'0.0', 'volume' : '0.0'}  # 초기값 : 0
krw = get_balance("KRW")
buy_price = 100000000000 # 초기값 천억

# 비교대상 dataframe 조회 : dataframe조회 중 오류가 날 수 있으니 한번만 조회 후 입력값 사용

ma60 = get_ma60("KRW-BTC")
print("ma60=", ma60)
target_price = get_target_price("KRW-BTC", 0.3)  #dataframe조회시간 오래 걸릴 수 있음
print("target_price:",target_price)
drop_price = get_drop_price("KRW-BTC", 0.9 )
print("drop_price:",drop_price)
current_price = get_current_price("KRW-BTC")
print("current_price:",current_price)

#문자메세지
post_message(myToken, "#cointrade", "ma60 : " + str(ma60))
post_message(myToken, "#cointrade", "target_price : " + str(target_price))
post_message(myToken, "#cointrade", "current_price : " + str(current_price))


# 자동매매 시작
while True:
    schedule.run_pending()
    # time.sleep(1)
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") + datetime.timedelta(hours=1)  # 10:00
        end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(hours=2)  # 10:00 <현재< #7:59:59
        # While문이 끝나면 여기로 돌아옴

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            #target_price = get_target_price("KRW-BTC", 0.3)  #dataframe조회시간 오래 걸릴 수 있음
            #print("target_price:",target_price)
            #ma60 = get_ma60("KRW-BTC")  #dataframe조회시간 오래 걸릴 수 있음
            #print("ma60=", ma60)
            krw = get_balance("KRW")
            #print("krw:", krw)
            earn = get_balance("BTC")  # 현금 잔고와 Coin 잔고 확인
            #print("earn:", earn)
            current_price = get_current_price("KRW-BTC")
            #print("current_price:", current_price)


            if target_price < current_price :
            #if target_price < current_price and current_price < ma60:
                #print("매수준비")
                #print("buy_Price==", buy_price)
                current_price = get_current_price("KRW-BTC")
                #print("current_price:", current_price)

                if krw * 0.3 > 5000 and current_price < buy_price:
                #if krw * 0.3 > 5000 and current_price < buy_price and current_price < ma60:
                    #print("잔고 5000원 이상")
                    #print("buy_Price==", buy_price)
                    krw = get_balance("KRW")  # 잔고조회
                    buy_result = upbit.buy_market_order("KRW-BTC", krw * 0.3)
                    post_message(myToken, "#cointrade", "BTC buy : " + str(buy_result['price']) + str(now)) if buy_result is not None else None
                    #print("buy_result:",buy_result)
                    buy_price = get_current_price("KRW-BTC") if buy_result is not None else None  # 매수 금액을 buy_price에 입력
                    #print("buy_price_completed:", buy_price)
                    post_message(myToken, "#cointrade", "BTC buy price: " + str(buy_price) + str(now))
                    # 매수 끝나고 나서 매도 대기
                    while buy_price is not None :
                        current_price = get_current_price("KRW-BTC")
                        #print("현재가:",current_price)
                        #print("매수가격:", buy_price)
                        earn = get_balance("BTC")  # 현금 잔고와 Coin 잔고 확인
                        now = datetime.datetime.now()
                        #schedule.every(1).minutes.do(print_alive)  # 60분마다 실행
                        #print(now)
                        if buy_price * 1.05 < current_price and earn * 0.995 > 0.0001:
                            sell_result = upbit.sell_market_order("KRW-BTC", earn * 0.995)
                            sell_price = get_current_price("KRW-ETH") if sell_result is not None else None  # 매도 금액을 sell_price에 입력
                            print("매도가:", sell_price)
                            post_message(myToken, "#cointrade", "BTC 5Pro sell : " + str(float(sell_result['volume']))) if sell_result is not None else None
                            post_message(myToken, "#cointrade", "BTC 5Pro sell : " + str(sell_price))
                            break
                        elif buy_price * 1.03 < current_price and earn * 0.995 > 0.0001:
                            sell_result = upbit.sell_market_order("KRW-BTC", earn * 0.9950)
                            sell_price = get_current_price("KRW-BTC") if sell_result is not None else None  # 매도 금액을 sell_price에 입력
                            print("매도가:", sell_price)
                            post_message(myToken, "#cointrade", "BTC 3Pro sell : " + str(float(sell_result['volume']))) if sell_result is not None else None
                            post_message(myToken, "#cointrade", "BTC 3Pro sell : " + str(sell_price))
                            break
                        elif start_time + datetime.timedelta(hours=3) < now and buy_price * 1.02 < current_price and earn * 0.995 > 0.0001:
                            sell_result = upbit.sell_market_order("KRW-BTC", earn * 0.9950)
                            sell_price = get_current_price("KRW-BTC") if sell_result is not None else None  # 매도 금액을 sell_price에 입력
                            print("매도가:", sell_price)
                            post_message(myToken, "#cointrade", "BTC 2Pro sell : " + str(float(sell_result['volume']))) if sell_result is not None else None
                            post_message(myToken, "#cointrade", "BTC 2Pro sell : " + str(sell_price))
                            break
                        elif start_time + datetime.timedelta(hours=6) < now and buy_price * 1.015 < current_price and earn * 0.995 > 0.0001:
                            sell_result = upbit.sell_market_order("KRW-BTC", earn * 0.9950)
                            sell_price = get_current_price("KRW-BTC") if sell_result is not None else None  # 매도 금액을 sell_price에 입력
                            print("매도가:", sell_price)
                            post_message(myToken, "#cointrade", "BTC 1.5Pro sell : " + str(float(sell_result['volume']))) if sell_result is not None else None
                            post_message(myToken, "#cointrade", "BTC 1.5Pro sell : " + str(sell_price))
                            break
                        elif start_time + datetime.timedelta(hours=9) < now and buy_price * 1.01 < current_price and earn * 0.995 > 0.0001:
                            sell_result = upbit.sell_market_order("KRW-BTC", earn * 0.9950)
                            sell_price = get_current_price("KRW-BTC") if sell_result is not None else None  # 매도 금액을 sell_price에 입력
                            print("매도가:", sell_price)
                            post_message(myToken, "#cointrade", "BTC 1Pro sell : " + str(float(sell_result['volume']))) if sell_result is not None else None
                            post_message(myToken, "#cointrade", "BTC 1Pro sell : " + str(sell_price))
                            break
                        elif target_price > current_price :
                            #drop_price = get_drop_price("KRW-BTC", 0.9)
                            #print("drop_price:", drop_price)
                            if drop_price > current_price:
                                drop = get_balance("BTC")
                                if drop * 0.9 > 0.0001:
                                    sell_result = upbit.sell_market_order("KRW-BTC", drop * 0.90)
                                    sell_coin = float(sell_result['volume']) if sell_result is not None else None
                                    print("손절량:", sell_coin)
                                    post_message(myToken, "#cointrade", "BTC Drop sell : " + str(sell_coin))
                                    break
                        #print("매도대기중")
                        time.sleep(10)

            # 하락세 급락 방지 손절
            else:
                #drop_price = get_drop_price("KRW-BTC", 0.9 )
                #print("drop_price:",drop_price)
                if drop_price > current_price:
                    drop = get_balance("BTC")
                    #print("drop", drop)
                    if drop * 0.9 > 0.0001:
                        fail_result = upbit.sell_market_order("KRW-BTC", drop * 0.90)
                        post_message(myToken, "#cointrade", "BTC Drop sell : " + str(fail_result)) if fail_result is not None else None

        else:
            btc = get_balance("BTC")
            if btc * 0.9 > 0.0001:
                sell_result = upbit.sell_market_order("KRW-BTC", btc * 0.90) if sell_result is not None else None
                post_message(myToken, "#cointrade", "BTC sell : " + str(sell_result))
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, "#cointrade", e)
        break
        time.sleep(1)

#ADA >3 , ETH > 0.001 , BTC > 0.0001: