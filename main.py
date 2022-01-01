# -*- encoding: UTF-8 -*-

from util import utils, work_flow
import settings
import logging
import schedule
import time

from util.result_join import join_result


def job():
    if utils.is_weekday():
        work_flow.process()
        join_result()


logging.basicConfig(format='%(asctime)s %(message)s', filename='sequoia.log')
logging.getLogger().setLevel(logging.INFO)
settings.init()

if settings.config['cron']:
    EXEC_TIME = "16:30"
    schedule.every().day.at(EXEC_TIME).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    work_flow.process()
    join_result()
