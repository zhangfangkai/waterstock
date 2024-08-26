# -*- encoding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG, format=' [%(asctime)s]-[%(filename)s]-[%(lineno)d]-[%(message)s]', filename='log/waterstock.log')


logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

logging.info("init-zfk")
from util import utils, work_flow
from util.result_join import join_result
import schedule
import time
import settings
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
logging.info("init-zfk2")


def job():
    if utils.is_weekday():
        work_flow.process()
        join_result()


def main():
    # 初始化setting，读取config.yaml
    settings.init()
    logging.info("-------start--------")
    if settings.config['cron']:
        EXEC_TIME = "18:00"
        schedule.every().day.at(EXEC_TIME).do(job)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        work_flow.process()
        # work_flow.predict()
        join_result()


if __name__ == '__main__':
    main()


