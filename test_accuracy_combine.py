#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/22 22:14
# @Author  : zhangfangkai
# @File    : test_accuracy.py
# @Use: PyCharm
import os
import logging
logging.basicConfig(level=logging.DEBUG, format=' [%(asctime)s] - [%(filename)s] - [%(message)s]', filename='log/waterstock_combine.log')

import settings
from strategy.backtest_tmp import process_backtest_tmp


def main():
    dirtory = 'res_combine/'
    files = os.listdir(dirtory)
    files.sort()
    strategy_dict = dict()
    for filename in files:
        day = filename.split("_")[1].split(".")[0]
        filepath = dirtory + filename
        with open(filepath,'r') as f:
            strategy_name = ""
            for i in f:
                i = i.strip()
                if "::::::::::::::" in i:
                    strategy_name = i.replace("::::::::::::::","") + "__" + day
                elif i:
                    code = i.split("-")[0].strip()
                    name = i.strip("-")[1].strip("'")
                    tmp_val = (code, name)
                    if strategy_dict.get(strategy_name):
                        strategy_dict.get(strategy_name).append(tmp_val)
                    else:
                        strategy_dict[strategy_name] = [tmp_val]


    for key,val in strategy_dict.items():
        print(key,val)
        for i in range(1,10):
            process_backtest_tmp(key,val,i)


if __name__ == '__main__':
    settings.init()

    main()