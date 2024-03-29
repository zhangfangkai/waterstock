# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from strategy import turtle_trade


# 持续上涨（MA10向上）
def check(code_name, data, end_date=None, threshold=10):
    """
        最近10天 ma10[t0]<ma10[t3]<ma10[t6]<ma10[t9] 并且t9 相对 t0 上涨 5%
    """
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, threshold), index=data.index.values)

    begin_date = data.iloc[0]['日期']
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug("{}在{}时还未上市".format(code_name, end_date))
            return False

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    data = data.tail(n=threshold)

    step1 = round(threshold/3)
    step2 = round(threshold*2/3)

    # 最近10天 ma10[t0]<ma10[t3]<ma10[t6]<ma10[t9] 并且t9 相对 t0 上涨 10%
    if data.iloc[0]['ma10'] < data.iloc[step1]['ma10'] < data.iloc[step2]['ma10'] < data.iloc[-1]['ma10'] and data.iloc[-1]['ma10'] > 1.05*data.iloc[0]['ma10']:
        return True
    else:
        return False

