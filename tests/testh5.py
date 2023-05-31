#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/9 15:19
# @Author  : zhangfangkai
# @File    : testh5.py
# @Use: PyCharm
import os
import pandas as pd

stock = "000002"
file_name = '../data/'+stock + '.h5'
if os.path.exists(file_name):
    data = pd.read_hdf(file_name)
    pd.set_option('display.max_columns', None)
    print(data.head())
else:
    print('not exists')