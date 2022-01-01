import datetime


# def push(msg):
#
#     if settings.config['push']['enable']:
#         payload = json.dumps({
#             "type": "headline",
#             "from": settings.config['push']['admin'],
#             "to": settings.config['push']['user'],
#             "subject": "investing",
#             "body": msg
#         })
#         response = requests.post(settings.config['push']['url'], auth=HTTPBasicAuth(settings.config['push']['admin'],
#                                                 settings.config['push']['admin_pass']), data=payload)
#         print(response.text)
#     logging.info(msg)

def push(msg):
    filename = "./res/res_" + str(datetime.date.today()) +".txt"

    with open(filename,"a",encoding="UTF-8")  as f:
        f.write(msg)

def statistics(msg=None):
    push(msg)


def strategy(msg=None):
    if msg is None or not msg:
        msg = '今日没有符合条件的股票'
    push(msg)
