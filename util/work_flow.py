# -*- encoding: UTF-8 -*-

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
import logging
import time
import datetime
import urllib
import pandas as pd


def process():
    logging.info("************************ process start ***************************************")
    try:
        # ts.set_token(settings.config['token'])
        # pro = ts.pro_api()

        all_data = ts.get_today_all()
        # 去除创业板
        all_data = all_data[~all_data.code.str.contains('^30')]
        # 去除科创板
        all_data = all_data[~all_data.code.str.contains('^68')]

        subset = all_data[['code', 'name', 'nmc']]
        subset.to_csv(settings.config['stocks_file'], index=None, header=True)
        stocks = [tuple(x) for x in subset.values]
        statistics(all_data, stocks)
    except urllib.error.URLError as e:
        subset = pd.read_csv(settings.config['stocks_file'])
        subset['code'] = subset['code'].astype(str)
        stocks = [tuple(x) for x in subset.values]

    if utils.need_update_data():
        utils.prepare()
        data_fetcher.run(stocks)
        check_exit()

    strategies = {
        '海龟交易法则': turtle_trade.check_enter,
        '放量上涨': enter.check_volume,
        '突破平台': breakthrough_platform.check,
        '均线多头': keep_increasing.check,
        '无大幅回撤': low_backtrace_increase.check,
        '停机坪': parking_apron.check,
        '回踩年线': backtrace_ma250.check,
    }
    filename = "./res/res_" + str(datetime.date.today()) +".txt"

    with open(filename,"w",encoding="UTF-8")  as f:
        f.write("\n")

    if datetime.datetime.now().weekday() == 0:
        strategies['均线多头'] = keep_increasing.check

    for strategy, strategy_func in strategies.items():
        check(stocks, strategy, strategy_func)
        time.sleep(2)

    logging.info("************************ process   end ***************************************")


def check(stocks, strategy, strategy_func):
    end = None
    m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
    results = list(filter(m_filter, stocks))
    results = "\n".join(str(i) for i in results)
    results.strip("\n")
    push.strategy('******************************"{0}-开始"**********************'
                  '********\n{1}\n******************************"{0}-结束"******************************\n'.format(strategy, results))


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(code_name):
        data = utils.read_data(code_name)
        if data is None:
            return False
        else:
            return strategy_fun(code_name, data, end_date=end_date)
        # if result:
        #     message = turtle_trade.calculate(code_name, data)
        #     push.strategy("{0} {1}".format(code_name, message))

    return end_date_filter


# 统计数据
def statistics(all_data, stocks):
    limitup = len(all_data.loc[(all_data['changepercent'] >= 9.5)])
    limitdown = len(all_data.loc[(all_data['changepercent'] <= -9.5)])

    up5 = len(all_data.loc[(all_data['changepercent'] >= 5)])
    down5 = len(all_data.loc[(all_data['changepercent'] <= -5)])

    def ma250(stock):
        stock_data = utils.read_data(stock)
        return enter.check_ma(stock, stock_data)

    ma250_count = len(list(filter(ma250, stocks)))

    msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}\n年线以上个股数量：    {}"\
        .format(limitup, limitdown, up5, down5, ma250_count)
    push.statistics(msg)


def check_exit():
    t_shelve = db.ShelvePersistence()
    file = t_shelve.open()
    for key in file:
        code_name = file[key]['code_name']
        data = utils.read_data(code_name)
        if turtle_trade.check_exit(code_name, data):
            push.strategy("{0} 达到退出条件".format(code_name))
            del file[key]
        elif turtle_trade.check_stop(code_name, data, file[key]):
            push.strategy("{0} 达到止损条件".format(code_name))
            del file[key]

    file.close()

