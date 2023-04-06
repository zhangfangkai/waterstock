import datetime

import settings


def push(filename, msg):
    with open(filename,"a",encoding="UTF-8")  as f:
        f.write(msg)

def sink_to_txt(msg=None):
    if settings.config['end_date'] == '1997-09-24':
        day = str(datetime.date.today())
    else:
        day = settings.config['end_date']
    filename = "./res/internal_" + day +".txt"
    push(filename,msg)


def sink_to_res(msg=None):
    if msg is None or not msg:
        msg = '今日没有符合条件的股票'
    if settings.config['end_date'] == '1997-09-24':
        day = str(datetime.date.today())
    else:
        day = settings.config['end_date']
    filename = "./res/res_" + day +".txt"
    push(filename, msg)
