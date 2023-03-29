#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/22 22:14
# @Author  : zhangfangkai
# @File    : test_accuracy.py
# @Use: PyCharm
import os
import logging
logging.basicConfig(level=logging.DEBUG, format=' [%(asctime)s] - [%(filename)s] - [%(message)s]', filename='log/waterstock.log')

import settings
from strategy.backtest_tmp import process_backtest_tmp


def main():
    dirtory = 'res_bak/'
    files = os.listdir(dirtory)
    strategy_dict = dict()
    for filename in files:
        day = filename.split("_")[1].split(".")[0]
        filepath = dirtory + filename
        with open(filepath,'r') as f:
            strategy_name = ""
            for i in f:
                i = i.strip()
                if "-开始" in i:
                    strategy_name = i.split('"')[1].replace("-开始","") + "__" + day
                if "停机坪-结束" in i:
                    break
                if i.startswith("(") and '突破日期：' not in i:
                    code = i.strip("()").split(", ")[0].strip("'")
                    name = i.strip("()").split(", ")[1].strip("'")
                    tmp_val = (code, name)
                    if strategy_dict.get(strategy_name):
                        strategy_dict.get(strategy_name).append(tmp_val)
                    else:
                        strategy_dict[strategy_name] = [tmp_val]


    for key,val in strategy_dict.items():
        print(key,val)
        process_backtest_tmp(key,val)


if __name__ == '__main__':
    settings.init()

    main()