import datetime

def push(msg):
    filename = "./res/res_" + str(datetime.date.today()) +".txt"

    with open(filename,"a",encoding="UTF-8")  as f:
        f.write(msg)


def sink_to_txt(msg=None):
    print(msg.strip())
    if msg is None or not msg:
        msg = '今日没有符合条件的股票'
    push(msg)
