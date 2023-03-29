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
import logging
import time
import datetime
import urllib
import pandas as pd




def process():
    logging.info("************************ process start ***************************************")

    t_shelve = db.ShelvePersistence()

    try:
        if settings.config['is_backtest']:
            subset = pd.read_csv(settings.config['stocks_file'])
            subset['code'] = subset['code'].astype(str)
            stocks_metas = [tuple(x) for x in subset.values]
        else:
            all_data = ts.get_today_all()
            # 去除创业板
            # all_data = all_data[~all_data.code.str.contains('^30')]
            # 去除科创板
            all_data = all_data[~all_data.code.str.contains('^68')]

            # nmc--流通市值
            subset = all_data[['code', 'name', 'nmc']]
            subset.to_csv(settings.config['stocks_file'], index=None, header=True)
            stocks_metas = [tuple(x) for x in subset.values]
            statistics(all_data, stocks_metas)
    except urllib.error.URLError as e:
        logging.error(e)
        subset = pd.read_csv(settings.config['stocks_file'])
        subset['code'] = subset['code'].astype(str)
        stocks_metas = [tuple(x) for x in subset.values]

    if not settings.config['is_backtest'] and utils.need_update_data():
    # if utils.need_update_data():

        utils.prepare()
        data_fetcher.run(stocks_metas)
        # 校验某些股票是否触发海龟止损了
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
    filename = "./res/res_" + str(datetime.date.today()) + ".txt"

    with open(filename, "w", encoding="UTF-8") as f:
        f.write("----start----\n")

    end_date = settings.config['end_date']
    if end_date == '1997-09-24':
        end_date = None

    for strategy, strategy_func in strategies.items():
        res = []
        for stocks_meta in stocks_metas:
            data = utils.read_data(stocks_meta)
            if data is not None:
                single_res = strategy_func(stocks_meta, data, end_date=end_date)
                if single_res[0] is True:
                    res.append(single_res)

        t_shelve.save_res(strategy,res)


    logging.info("************************ process   end ***************************************")

def predict():
    t_shelve = db.ShelvePersistence()
    strategt_res = t_shelve.read_res()
    for key, val in strategt_res.items():
        for threshold in range(1, 30):
            process_backtest(key, val, threshold)

# 统计数据
def statistics(all_data, stocks):
    # changepercent--涨跌幅
    limitup = len(all_data.loc[(all_data['changepercent'] >= 9.5)])
    limitdown = len(all_data.loc[(all_data['changepercent'] <= -9.5)])

    up5 = len(all_data.loc[(all_data['changepercent'] >= 5)])
    down5 = len(all_data.loc[(all_data['changepercent'] <= -5)])

    ma250_count = 1000

    msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}\n年线以上个股数量：    {}" \
        .format(limitup, limitdown, up5, down5, ma250_count)
    push.sink_to_txt(msg)


def check_exit():
    t_shelve = db.ShelvePersistence()
    file = t_shelve.open()
    for key in file:
        code_name = file[key]['code_name']
        data = utils.read_data(code_name)
        if turtle_trade.check_exit(code_name, data):
            push.sink_to_txt("{0} 达到退出条件".format(code_name))
            del file[key]
        elif turtle_trade.check_stop(code_name, data, file[key]):
            push.sink_to_txt("{0} 达到止损条件".format(code_name))
            del file[key]

    file.close()
