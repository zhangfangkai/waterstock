# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging


# TODO 真实波动幅度（ATR）放大
# 最后一个交易日收市价从下向上突破指定区间内最高价
from util import push


def check_breakthrough(code_name, data, end_date=None, threshold=30):
    max_price = 0
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold+1)
    if len(data) < threshold + 1:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 最后一天收市价
    last_close = float(data.iloc[-1]['close'])
    last_open = float(data.iloc[-1]['open'])

    data = data.head(n=threshold)
    second_last_close = data.iloc[-1]['close']

    for index, row in data.iterrows():
        if row['close'] > max_price:
            max_price = float(row['close'])

    if last_close > max_price > second_last_close and max_price > last_open and last_close / last_open > 1.02:
        return True
    else:
        return False


def check_ma(code_name, data, end_date=None, ma_days=10):
    """
        收盘价高于N日均线
    """
    if code_name[1] == '三一重工':
        print(111)
    if data is None or len(data) < ma_days:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, ma_days))
        return False

    ma_tag = 'ma' + str(ma_days)
    data[ma_tag] = pd.Series(tl.MA(data['收盘'].values, ma_days), index=data.index.values)

    begin_date = data.iloc[0]['日期']
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug("{}在{}时还未上市".format(code_name, end_date))
            return False
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    last_open = data.iloc[-1]['开盘']
    last_close = data.iloc[-1]['收盘']
    last_ma = data.iloc[-1][ma_tag]
    if last_close > last_ma and last_ma > last_open:
        return True
    else:
        return False


# 上市日小于60天
def check_new(code_name, data, end_date=None, threshold=60):
    size = len(data.index)
    if size < threshold:
        return True
    else:
        return False



def check_volume(code_name, data, end_date=None, threshold=60):
    """
        规则：最后一天收盘价要高于开盘价，上涨率要大于2，成交额不低于2亿，最后一天的成交量大于之前5天成交均量的2倍
    """

    # 流通市值介于50亿到300亿之间
    # if code_name[2] > 3000000 or code_name[2] < 1000000:
    #     return False

    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...".format(code_name, threshold))
        return False
    # 得到成交量的5日移动均线
    data['vol_ma5'] = pd.Series(tl.MA(data['成交量'].values, 5), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    if data.empty:
        return False
    p_change = data.iloc[-1]['涨跌幅']
    # 最后一天的上涨率小于2，或者最后一天收盘价低于开盘价
    if p_change < 2 or data.iloc[-1]['收盘'] < data.iloc[-1]['开盘']:
        return False
    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        logging.debug("{0}:样本小于{1}天...".format(code_name, threshold))
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['收盘']
    # 最后一天成交量
    last_vol = data.iloc[-1]['成交量']

    amount = last_close * last_vol * 100

    # 成交额不低于2亿
    if amount < 500000000:
       return False

    data = data.head(n=threshold)
    mean_vol = data.iloc[-1]['vol_ma5']

    # 最后一天成交量大于前面5天的成交量的2倍
    vol_ratio = last_vol / mean_vol
    if vol_ratio >= 2:
        push.sink_to_txt("{0}\t量比：{1:.2f}\t涨幅：{2}%\n".format(code_name, vol_ratio, p_change))
        return True
    else:
        return False
