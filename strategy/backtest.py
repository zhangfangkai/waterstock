#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/20 20:39
# @Author  : zhangfangkai
# @File    : backtest.py
# @Use: PyCharm
import logging

import settings
from util import push, utils, db


def process_backtest(strategy, res, threshold=3):
    u"""
        回测测试

        思路是指定股票的指定日期之后3天上涨超过2%
        输出测试的结果
        同时返回策略的准确性

        res 的格式是：true, start_date,'code', 'name', 'nmc'(流通市值)
    """
    if not res:
        return
    success_count = 0
    fail_count = 0
    total = len(res)
    for stock in res:
        data = utils.read_data((stock[2],stock[3]))
        is_success = process_single(stock, data, threshold)
        if is_success == 0 and total > 1:
            total -= 1
        elif is_success == 1:
            success_count += 1
        elif is_success == -1:
            fail_count += 1
    logging.info(" {} 在 {} 天后, 总数:{}, 成功数:{}, 失败数:{}, 成功率: {:.2%}, 失败率 {:.2%}".format(strategy,threshold,total,success_count,fail_count, success_count/total,fail_count/total))

def process_single(stock, data, threshold = 5):
    start_date = stock[1]

    # 起始的收盘价
    start_close = data.loc[data['date']==start_date].iloc[-1]['close']

    # 获取起始后的几天
    mask = (data['date'] > start_date)
    data = data.loc[mask]
    data = data.head(n=threshold)
    if len(data)<threshold:
        return 0
    end_close = data.iloc[-1]['close']

    if end_close / start_close >= 1.02:
        push.sink_to_txt("{}, 预测日期:{}, 成功预测！{}天后，上涨幅度: {:.2%}\n".format(stock[3],start_date, threshold, end_close / start_close - 1))
        return 1
    elif end_close / start_close < 1:
        push.sink_to_txt("{}, 预测日期:{}, 预测失败...{}天后，上涨幅度: {:.2%}\n".format(stock[3], start_date, threshold, end_close / start_close - 1))
        return -1

if __name__ == '__main__':
    settings.init()
    t_shelve = db.ShelvePersistence()
    strategt_res = t_shelve.read_res()
    for key,val in strategt_res:
        print(key,val)
