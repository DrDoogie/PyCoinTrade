import pyupbit
import numpy as np


df = pyupbit.get_ohlcv("KRW-ETH", count=10)
#print(df)
#변동폭 * k 계산, (고가-저가) * k값
df['range'] = (df['high'] - df['low']) * 0.7
df['target'] = df['open'] + df['range'].shift(1)

print(df)
fee = 0.005
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'] - fee,
                     1)

df['hpr'] = df['ror'].cumprod()
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")