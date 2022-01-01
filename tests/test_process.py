# -*- encoding: UTF-8 -*-

import tushare as ts
import logging
import urllib
import settings


def process():
    logging.info("************************ process start ***************************************")
    try:
        all_data = ts.get_today_all()
        all_data.to_csv("tttt.csv", index=None, header=True)

    except urllib.error.URLError as e:
        print(e)

if __name__ == "__main__":
    settings.init()
    process()
