# -*- encoding: UTF-8 -*-
from strategy.backtest import process_backtest
from util import data_fetcher, db, push, utils
import settings
import strategy.enter as enter
from strategy import turtle_trade
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
import tushare as ts
import akshare as ak
import logging
import time
import datetime
import urllib
import pandas as pd


def process():
    logging.info("************************ process start ***************************************")
    try:
        if settings.config['is_backtest']:
            subset = pd.read_csv(settings.config['stocks_file'], dtype=object)
            subset['代码'] = subset['代码'].astype(str)
            stocks_metas = [tuple(x) for x in subset.values]
        else:
            all_data = ak.stock_zh_a_spot_em()
            subset = all_data[['代码', '名称']]
            # 去除科创板
            subset = subset[~subset['代码'].str.contains('^68')]
            # 去除北交所
            subset = subset[~subset['代码'].str.contains('^8')]

            subset['代码'] = subset['代码'].astype(str)
            subset.to_csv(settings.config['stocks_file'], quoting=1,index=None, header=True)
            stocks_metas = [tuple(x) for x in subset.values]
            statistics(all_data, stocks_metas)
    except urllib.error.URLError as e:
        logging.error(e)
        subset = pd.read_csv(settings.config['stocks_file'])

        subset['代码'] = subset['代码'].astype(str)
        stocks_metas = [tuple(x) for x in subset.values]

    # if not settings.config['is_backtest'] and utils.need_update_data():
    if utils.need_update_data():
        print("获取最新股票行情数据中，wait...")
        utils.prepare()
        data_fetcher.run(stocks_metas)
        print("股票行情数据获取完毕！")
    print("开始计算，wait...")

    # 数据列名
    # 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率,
    strategies = {
        '海龟交易法则': turtle_trade.check_enter,
        '放量上涨': enter.check_ma,
        '突破平台': breakthrough_platform.check,
        '均线多头': keep_increasing.check,
        # '无大幅回撤': low_backtrace_increase.check,
        # '停机坪': parking_apron.check,
        '回踩年线': backtrace_ma250.check,
    }
    filename = "./res/res_" + str(datetime.date.today()) + ".txt"

    with open(filename, "w", encoding="UTF-8") as f:
        f.write("----start----\n")

    end_date = settings.config['end_date']
    if end_date == '1997-09-24':
        end_date = None

    for strategy, strategy_func in strategies.items():
        check(stocks_metas, strategy, strategy_func, end_date)

    logging.info("************************ process   end ***************************************")


def check(stocks, strategy, strategy_func, end_date):
    m_filter = check_enter(end_date=end_date, strategy_fun=strategy_func)
    results = list(filter(m_filter, stocks))
    results = "\n".join(str(i) for i in results)
    results.strip("\n")
    push.sink_to_res(
        '******************************"{0}-开始"******************************\n{1}\n******************************"{0}-结束"******************************\n'.format(
            strategy, results))


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(code_name):
        data = utils.read_data(code_name)
        if data is None:
            return False
        else:
            return strategy_fun(code_name, data, end_date=end_date)

    return end_date_filter


def predict():
    t_shelve = db.ShelvePersistence()
    strategt_res = t_shelve.read_res()
    for key, val in strategt_res.items():
        for threshold in range(1, 30):
            process_backtest(key, val, threshold)


# 统计数据
def statistics(all_data, stocks):
    # changepercent--涨跌幅
    limitup = len(all_data.loc[(all_data['涨跌幅'] >= 9.5)])
    limitdown = len(all_data.loc[(all_data['涨跌幅'] <= -9.5)])

    up5 = len(all_data.loc[(all_data['涨跌幅'] >= 5)])
    down5 = len(all_data.loc[(all_data['涨跌幅'] <= -5)])

    push.sink_to_txt("涨停数：{} 跌停数：{}\n涨幅大于5%数：{} 跌幅大于5%数：{}\n".format(limitup, limitdown, up5, down5))
