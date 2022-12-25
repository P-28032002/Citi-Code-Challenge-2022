import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint

import datetime
import matplotlib.pyplot as plt
import seaborn as sns;
import pickle

sns.set(style="whitegrid")

pd.core.common.is_list_like = pd.api.types.is_list_like

start = datetime.datetime(2016, 1, 1)
end = datetime.datetime(2020, 1, 1)

stockz = sorted(["EEM", "SPY", "GDX", "XLF", "XOP", "AMLP", "FXI", "QQQ", "EWZ", "EFA", "USO", "HYG", "IAU",
                 "IWM", "XLE", "XLU", "IEMG", "GDXJ", "SLV", "VWO", "XLP", "XLI", "OIH", "LQD", "XLK", "VEA",
                 "TLT", "IEFA", "XLV", "EWJ", "GLD", "IYR", "BKLN", "EWH", "ASHR", "XLB", "RSX", "JNK", "KRE",
                 "XBI", "AGG", "VNQ", "GOVT", "UNG", "IVV", "XLY", "EWT", "PFF", "XLRE", "MCHI", "INDA", "BND",
                 "USMV", "EZU", "SMH", "XRT", "EWY", "IEF", "SPLV", "XLC", "IJR", "VIXY", "EWG", "EWW", "VTI",
                 "VGK", "IBB", "PGX", "VOO", "EMB", "SCHF", "VEU", "SJNK", "EMLC", "XME", "DIA", "EWA", "VCSH",
                 "JPST", "MLPA", "VCIT", "ITB", "ACWI", "KWEB", "EWC", "EWU", "BNDX", "SHY", "VT", "IWD", "VXUS",
                 "MBB", "ACWX", "XHB", "BSV", "SHV", "FEZ", "IWF", "IGSB", "SPYV", "ITOT", "FPE", "FVD", "SHYG",
                 "VYM", "BBJP", "DGRO", "KBE", "VTV", "SPAB", "SPIB", "IWR", "DBC", "BIL", "SPSB", "FLOT", "GLDM",
                 "VIG", "XES", "SCHE", "TIP", "PDBC", "SPYG", "MINT", "SCZ", "SPDW", "PCY", "USHY", "IXUS", "NEAR",
                 "EPI", "SPLG", "HYLB", "AAXJ", "SPEM", "VMBS", "BIV", "QUAL", "ILF", "EWP"])

df = pd.read_csv('yfinance-data.csv', index_col='Date')
# df.to_csv('yfinance-data.csv', index=False)
for col in df.columns:
    if df[col].isnull().any():
        df.drop(col, axis=1, inplace=True)


def find_cointegrated_pairs(data, threshold=0.05):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < threshold:
                pairs.append((keys[i], keys[j], pvalue))
    return score_matrix, pvalue_matrix, pairs


scores, pvalues, pairs = find_cointegrated_pairs(df)


def total_pairs_under_threshold(threshold):
    totalsum = 0
    for i in range(len(pvalues)):
        cursum = sum(pvalues[i] <= threshold)
        totalsum += cursum
        print(stockz[i], cursum)
    return totalsum


def pairs_under_threshold(pairs, threshold):
    new_pairs = []
    for pair in pairs:
        if pair[2] <= threshold:
            new_pairs.append(pair)
    return new_pairs


def get_weights(pairs, max_allocation=.01):
    weights = []
    for p in pairs:
        # print(p)
        weights.append(1 / p[2])

    weights = np.array(weights)
    total = np.sum(weights)

    normalized = weights / total

    while any((normalized) > max_allocation):
        # print(normalized.max())
        normalized[normalized.argmax()] = max_allocation
        normalized = normalized / sum(normalized)

    scale_factor = 1 / normalized.min()
    scaled = scale_factor * normalized
    return scaled


def spread_difference(s1, s2):
    S1 = df[s1]
    S2 = df[s2]

    S1 = sm.add_constant(S1)
    results = sm.OLS(S2, S1).fit()
    S1 = S1[s1]
    b = results.params[s1]

    spread = S2 - b * S1
    spread.plot(figsize=(12, 6))
    plt.axhline(spread.mean(), color='black')
    plt.xlim('2016-01-01', '2020-01-01')
    plt.legend(['Spread']);


spread_difference('XLRE', 'XLU')


def spread_ratio(s1, s2):
    S1 = df[s1]
    S2 = df[s2]
    ratio = S1 / S2
    ratio.plot(figsize=(12, 6))
    plt.axhline(ratio.mean(), color='black')
    plt.xlim('2016-01-01', '2020-01-01')
    plt.legend(['Price Ratio']);
    return ratio


ratio = spread_ratio('XLRE', 'XLU')


def zscore(series):
    return (series - series.mean()) / np.std(series)


ratios = df['XLRE'] / df['XLU']
train_test_index = int(len(ratios) * .70)
train = ratios[:train_test_index]
test = ratios[train_test_index:]

ratios_mavg5 = train.rolling(window=5, center=False).mean()
ratios_mavg60 = train.rolling(window=60, center=False).mean()
std_60 = train.rolling(window=60, center=False).std()
zscore_60_5 = (ratios_mavg5 - ratios_mavg60) / std_60
buy = train.copy()
sell = train.copy()
buy[zscore_60_5 > -1] = 0
sell[zscore_60_5 < 1] = 0
S1 = df['XLRE'].iloc[:train_test_index]
S2 = df['XLU'].iloc[:train_test_index]

S1[60:].plot(color='b')
S2[60:].plot(color='c')
buyR = 0 * S1.copy()
sellR = 0 * S1.copy()

buyR[buy != 0] = S1[buy != 0]
sellR[buy != 0] = S2[buy != 0]
buyR[sell != 0] = S2[sell != 0]
sellR[sell != 0] = S1[sell != 0]


def single_trade(s1, s2, window1, window2, w=1, use_ratio=False):
    if (window1 == 0) or (window2 == 0):
        return 0

    S1 = df[s1].iloc[train_test_index:]
    S2 = df[s2].iloc[train_test_index:]

    ratios = S1 / S2
    ma1 = ratios.rolling(window=window1,
                         center=False).mean()
    ma2 = ratios.rolling(window=window2,
                         center=False).mean()
    std = ratios.rolling(window=window2,
                         center=False).std()
    zscore = (ma1 - ma2) / std

    money = 0
    countS1 = 0
    countS2 = 0
    for i in range(len(ratios)):
        if zscore[i] < -1:
            if use_ratio:
                countS1 -= 1 * ratios[i] * w
                money += (S1[i] - S2[i]) * w * ratios[i]
            else:
                money += (S1[i] - S2[i] * ratios[i]) * w
                countS1 -= 1 * w

            countS2 += 1 * ratios[i] * w
        elif zscore[i] > 1:
            if use_ratio:
                money -= (S1[i] - S2[i]) * w * ratios[i]
                countS1 += 1 * ratios[i] * w
            else:
                money -= (S1[i] - S2[i] * ratios[i]) * w
                countS1 += 1 * w

            countS2 -= 1 * ratios[i] * w

        elif abs(zscore[i]) < 0.75:
            money += S1[i] * countS1 + S2[i] * countS2
            countS1 = 0
            countS2 = 0
    return money


map = {}
for p in pairs:
    lis = []
    lis.append(p[0])
    lis.append(p[1])
    map[tuple(lis)] = single_trade(p[0], p[1], 60, 5, 1)
map = dict(sorted(map.items(), key=lambda item: item[1], reverse=True))

dbfile = open('map.pkl', 'ab')
pickle.dump(map, dbfile)
dbfile.close()
