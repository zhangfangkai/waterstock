#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/22 22:14
# @Author  : zhangfangkai
# @File    : test_accuracy.py
# @Use: PyCharm
import csv

import settings
from strategy.backtest_tmp import process_backtest_tmp


def out(day, strategy_name,interval, total, success, fail):
    with open('accuracy_combine.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow([day, strategy_name, interval,total, success, fail])


def init():
    with open('accuracy_combine.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["day", "strategy_name", "interval","total", "success", "fail"])


def main():
    init()
    filepath = 'log/waterstock_combine.log'
    with open(filepath,'r') as f:
        for i in f:
            i = i.strip()
            strategy_name = i.split("在")[0].split("day:")[1].split(",")[1].strip()
            interval = i.split("在")[1].split("天后")[0].strip()
            total = i.split("总数:")[1].split(",")[0].strip()
            success = i.split("成功数:")[1].split(",")[0].strip()
            fail = i.split("失败数:")[1].split(",")[0].strip()
            day = i.split("day:")[1].split(",")[0].strip()
            out(day,strategy_name,interval,total,success,fail)

if __name__ == '__main__':
    main()