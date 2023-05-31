# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging
from strategy import turtle_trade


# “停机坪”策略
def check(code_name, data, end_date=None, threshold=15):
    """
        最近10天有一天涨停了，该日收盘价为10日内最高价
        这天之后三天：
        第一天的开盘价大于该日，收盘价大于该日，收盘比开盘在0.97到1.03之间波动
        第二天和第三天的收盘比开盘在0.97到1.03之间波动，上涨幅度在-5%到5%之间，开盘价和收盘价都要高于改日
    """
    origin_data = data

    begin_date = data.iloc[0]['日期']
    if end_date is not None:
        if end_date < begin_date:  # 该股票在end_date时还未上市
            logging.debug("{}在{}时还未上市".format(code_name, end_date))
            return False

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return

    data = data.tail(n=threshold)

    flag = False

    # 找出涨停日
    for index, row in data.iterrows():
        try:
            if float(row['涨跌幅']) > 9.5:
                if turtle_trade.check_enter(code_name, origin_data, row['日期'], threshold):
                    if check_internal(code_name, data, row):
                        flag = True
        except KeyError as error:
            logging.debug("{}处理异常：{}".format(code_name, error))

    return flag


def check_internal(code_name, data, limitup_row):

    limitup_price = limitup_row['close']

    limitup_end = data.loc[(data['date'] > limitup_row['date'])]

    limitup_end = limitup_end.head(n=3)

    if len(limitup_end.index) < 3:
        return False

    consolidation_day1 = limitup_end.iloc[0]
    consolidation_day23 = limitup_end = limitup_end.tail(n=2)

    if not(consolidation_day1['close'] > limitup_price and consolidation_day1['open'] > limitup_price and
        0.97 < consolidation_day1['close'] / consolidation_day1['open'] < 1.03):
        return False

    for index, row in consolidation_day23.iterrows():
        try:
            if not (0.97 < (row['close'] / row['open']) < 1.03 and -5 < row['p_change'] < 5
                    and row['close'] > limitup_price and row['open'] > limitup_price):
                return False
        except KeyError as error:
            logging.debug("{}处理异常：{}".format(code_name, error))

    logging.debug("股票{0} 涨停日期：{1}".format(code_name, limitup_row['date']))

    return True

