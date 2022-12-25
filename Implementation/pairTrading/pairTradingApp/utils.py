import pickle

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns;

sns.set(style="whitegrid")
plt.style.use('dark_background')
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data as pdr


pd.core.common.is_list_like = pd.api.types.is_list_like
start = datetime.datetime(2016, 1, 1)
end = datetime.datetime(2020, 1, 1)

df = pd.read_csv('../new_data_with_sectors.csv')
df = df.query("Date >= '2016-01-01'and Date <= '2020-01-01'")
df = df.pivot(index='Date', columns='Symbol', values='Close')
df.columns = ["".join(tup) for tup in df.columns.to_flat_index()]
df.reset_index()
df.index = pd.to_datetime(df.index, format="%Y/%m/%d")
start_date = '2016-01-01'
end_date = '2020-01-01'


def zscore(series):
    return (series - series.mean()) / np.std(series)


def visualize(stock1, stock2):
    ratios = df[stock1] / df[stock2]
    train_test_index = int(len(ratios) * .70)
    train = ratios[:train_test_index]
    test = ratios[train_test_index:]

    zscore(ratios).plot(figsize=(12, 6))
    plt.axhline(zscore(ratios).mean())
    plt.axhline(1.0, color='red')
    plt.axhline(-1.0, color='green')
    plt.xlim('2016-01-01', '2020-01-01')
    plt.legend('Z-Score')

    plt.savefig('./static/img1.jpg')
    plt.close()


    ratios_mavg5 = train.rolling(window=5, center=False).mean()
    ratios_mavg60 = train.rolling(window=60, center=False).mean()
    std_60 = train.rolling(window=60, center=False).std()
    zscore_60_5 = (ratios_mavg5 - ratios_mavg60) / std_60
    plt.figure(figsize=(12, 6))
    plt.plot(train.index, train.values)
    plt.plot(ratios_mavg5.index, ratios_mavg5.values)
    plt.plot(ratios_mavg60.index, ratios_mavg60.values)
    plt.legend(['Ratio', '5d Ratio MA', '60d Ratio MA'])
    plt.ylabel('Ratio')
    plt.savefig('./static/img2.jpg')
    plt.close()

    plt.figure(figsize=(12, 6))
    zscore_60_5.plot()
    plt.xlim('2016-03-25', '2018-07-01')
    plt.axhline(0, color='black')
    plt.axhline(1.0, color='red', linestyle='--')
    plt.axhline(-1.0, color='green', linestyle='--')
    plt.legend(['Rolling Ratio z-Score', 'Mean', '+1', '-1'])
    plt.savefig('./static/img3.jpg')
    plt.close()

    plt.figure(figsize=(12, 6))

    train[160:].plot()
    buy = train.copy()
    sell = train.copy()
    buy[zscore_60_5 > -1] = 0
    sell[zscore_60_5 < 1] = 0
    buy[160:].plot(color='g', linestyle='None', marker='^')
    sell[160:].plot(color='r', linestyle='None', marker='^')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, ratios.min(), ratios.max()))
    plt.xlim(start_date, end_date)
    plt.legend(['Ratio', 'Buy Signal', 'Sell Signal'])
    plt.savefig('./static/img4.jpg')
    plt.close()

    plt.figure(figsize=(12, 7))
    S1 = df[stock1].iloc[:train_test_index]
    S2 = df[stock2].iloc[:train_test_index]
    S1[60:].plot(color='b')
    S2[60:].plot(color='c')
    buyR = 0 * S1.copy()
    sellR = 0 * S1.copy()

    # When you buy the ratio, you buy stock S1 and sell S2
    buyR[buy != 0] = S1[buy != 0]
    sellR[buy != 0] = S2[buy != 0]

    # When you sell the ratio, you sell stock S1 and buy S2
    buyR[sell != 0] = S2[sell != 0]
    sellR[sell != 0] = S1[sell != 0]

    buyR[60:].plot(color='g', linestyle='None', marker='^')
    sellR[60:].plot(color='r', linestyle='None', marker='^')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, min(S1.min(), S2.min()), max(S1.max(), S2.max())))
    plt.ylim(min(S1.min(), S2.min()) - 100, max(S1.max(), S2.max()) + 100)
    plt.xlim(start_date, end_date)

    plt.legend([stock1, stock2, 'Buy Signal', 'Sell Signal'])
    plt.savefig('./static/img5.jpg')
    plt.close()


# visualize('ITC', 'KOTAKBANK')

def read_pickle():
    dbfile = open(r'../map.pkl', 'rb')
    data = pickle.load(dbfile)
    dbfile.close()
    return data


# data = read_pickle()