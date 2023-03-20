#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/20 20:39
# @Author  : zhangfangkai
# @File    : backtest.py
# @Use: PyCharm
import logging

from util import push


def process_backtest(code_name, data, start_date=None, threshold=3):
    u"""
        回测测试

        思路是指定股票的指定日期之后3天上涨超过2%
        输出测试的结果
        同时返回策略的准确性
    """
    if start_date is None:
        logging.ERROR("start is None")

    # 起始的收盘价
    start_close = data.iloc[data['date'] == start_date]['close']

    # 获取起始后的几天
    mask = (data['date'] > start_date)
    data = data.loc[mask]
    data = data.head(n=threshold)

    end_close = data.iloc[-1]['close']

    if end_close / start_close >= 1.02:
        push.strategy("{} 成功预测！{}天后，上涨幅度: {:.2%}".format(code_name, threshold, end_close / start_close - 1))
        return True
    else:
        push.strategy("{} 预测失败...{}天后，上涨幅度: {:.2%}".format(code_name, threshold, end_close / start_close - 1))
        return False