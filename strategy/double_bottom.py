# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from util import push
from strategy import enter


# 平台突破策略
def check(stock_meta, data, end_date=None, threshold=30):
    # 一个月的数据
    # 最右侧是最高价
    # 找到最低价位置，如果最低价在靠右的，则向左寻找，如果最低价在靠左的，则向右寻找
    # 从左往右或者从右往左找的时候，如果能找到涨幅比他大5%的也可以

    origin_data = data
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...".format(stock_meta, threshold))
        return False, "", stock_meta[0], stock_meta[1], stock_meta[2]
    # 收盘价30日均价
    data['ma30'] = pd.Series(tl.MA(data['close'].values, threshold), index=data.index.values)

    begin_date = data.iloc[0].date
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug("{}\t在\t{}\t时还未上市".format(stock_meta, end_date))
            return False, "", stock_meta[0], stock_meta[1], stock_meta[2]

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]

    data = data.tail(n=threshold)

    breakthrough_row = None

    for index, row in data.iterrows():
        # 如果今天穿过了30日均线
        if row['open'] < row['ma30'] <= row['close']:
            # 成交量比大于2
            if enter.check_volume(stock_meta, origin_data, row['date'], threshold)[0]:
                breakthrough_row = row
                break

    if breakthrough_row is None:
        return False, "", stock_meta[0], stock_meta[1], stock_meta[2]

    data_front = data.loc[(data['date'] < breakthrough_row['date'])]
    data_end = data.loc[(data['date'] >= breakthrough_row['date'])]

    for index, row in data_front.iterrows():
        # 突破之前在ma30左右波动，在下5%到20%的范围里
        if not (-0.05 < (row['ma30'] - row['close']) / row['ma30'] < 0.2):
            return False, "", stock_meta[0], stock_meta[1], stock_meta[2]

    push.sink_to_txt("股票{0} 突破日期：{1}\n".format(stock_meta, breakthrough_row['date']))
    return True, breakthrough_row['date'], stock_meta[0], stock_meta[1], stock_meta[2]
