import pyupbit

access = "your-id"
secret = "your-id"
upbit = pyupbit.Upbit(access,secret)

print ( upbit . get_balance ( "KRW-BTC" ))      # KRW-XRP
print ( upbit . get_balance ( "KRW" ))          # 실행할 수 있습니다
locals()