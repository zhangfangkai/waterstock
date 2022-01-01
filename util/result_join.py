# -*- coding: utf-8 -*-
# @Time    : 2021/8/29 23:24
# @Author  : zfk
# @Email   : fangkai_zhang@163.com
# @File    : zfkjoin.py
import datetime

from util.sendmail import sendmail


def join_result():
    map = dict()
    filename = "./res/res_" + str(datetime.date.today()) + ".txt"
    # filename = "./res/res_2021-12-22.txt"
    final_res = ""
    with open(filename, "r", encoding="utf-8") as f:
        data = dict()
        data["haigui"] = set()
        data["fangliang"] = set()
        data["tupo"] = set()
        data["junxian"] = set()
        data["wudafu"] = set()
        data["tingjiping"] = set()
        data["huicai"] = set()
        data["final"] = set()

        lines = f.readlines()
        key = "final"

        for line in lines:

            if not line.strip():
                continue
            if "海龟交易法则" in line:
                key = "haigui"
            elif "放量上涨" in line:
                key = "fangliang"
            elif "突破平台" in line:
                key = "tupo"
            elif "均线多头" in line:
                key = "junxian"
            elif "无大幅回撤" in line:
                key = "wudafu"
            elif "停机坪" in line:
                key = "tingjiping"
            elif "回踩年线" in line:
                key = "huicai"
            datas = line.split(",")
            ascode = datas[0].strip("('")
            if len(datas) > 1:
                map[ascode] = datas[1].strip()
            data[key].add(ascode)
    final_res += "::::::::::::::海龟放量::::::::::::::\n"
    data["final_1"] = data["haigui"].intersection(data["fangliang"])
    for i in data["final_1"]:
        final_res += i + "-" + map[i] + "\n"
    final_res += "::::::::::::::海龟均线::::::::::::::\n"
    data["final_2"] = data["haigui"].intersection(data["junxian"])
    for i in data["final_2"]:
        final_res += i + "-" + map[i] + "\n"
    final_res += '::::::::::::::海龟突破::::::::::::::\n'
    data["final_3"] = data["haigui"].intersection(data["tupo"])
    for i in data["final_3"]:
        final_res += i + "-" + map[i] + "\n"
    final_res += '::::::::::::::均线突破::::::::::::::\n'
    data["final_4"] = data["fangliang"].intersection(data["tupo"])
    for i in data["final_4"]:
        final_res += i + "-" + map[i] + "\n"
    final_res += '::::::::::::::海龟均线突破::::::::::::::\n'
    data["final_5"] = data["fangliang"].intersection(data["tupo"]).intersection(data["haigui"])
    for i in data["final_5"]:
        final_res += i + "-" + map[i] + "\n"
    print(final_res)
    sendmail(final_res)


if __name__ == "__main__":
    join_result()
