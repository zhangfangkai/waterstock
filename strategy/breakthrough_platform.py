# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from util import push
from strategy import enter


# 平台突破策略
def check(stock_meta, data, end_date=None, threshold=30):
    """
        穿过了30日均线，并且成交比ma30量比值大于2，突破之前在 ma30左右波动，在-5%到20%的范围里
    """
    origin_data = data
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...".format(stock_meta, threshold))
        return False

    # 收盘价30日均价
    data['ma30'] = pd.Series(tl.MA(data['close'].values, threshold), index=data.index.values)

    begin_date = data.iloc[0].date
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug("{}\t在\t{}\t时还未上市".format(stock_meta, end_date))
            return False

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]

    # 取今天的数据
    data = data.tail(n=1)

    breakthrough_row = None

    for index, row in data.iterrows():
        # 如果今天穿过了30日均线
        if row['open'] < row['ma30'] <= row['close']:
            # 成交量比大于2
            if enter.check_volume(stock_meta, origin_data, row['date'], threshold)[0]:
                breakthrough_row = row
                break

    if breakthrough_row is None:
        return False

    data_front = data.loc[(data['date'] < breakthrough_row['date'])]
    data_end = data.loc[(data['date'] >= breakthrough_row['date'])]

    for index, row in data_front.iterrows():
        # 突破之前在ma30左右波动，在下5%到20%的范围里
        if not (-0.05 < (row['ma30'] - row['close']) / row['ma30'] < 0.2):
            return False

    push.sink_to_txt("股票{0} 突破日期：{1}\n".format(stock_meta, breakthrough_row['date']))
    return True