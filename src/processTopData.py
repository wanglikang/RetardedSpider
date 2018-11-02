# -*- coding: utf-8 -*-
import re
import time
import numpy as np
import matplotlib.pyplot as plt
import copy
from datetime import datetime
import matplotlib.dates  as mdates
from matplotlib.dates import (MINUTELY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)


#
# 获取每一个top记录，，返回一个list，元素是一个dict{key是'ts'：值是包含相应的信息的dict}
#
def getDataFromFile(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        linesize = len(lines)
        currline = 2
        records = []
        while currline < linesize:

            qtime = lines[currline][0:-1]
            recordStamp = time.strptime(qtime, "%Y-%m-%d %H:%M:%S")
            stamp = int(time.mktime(recordStamp) * 1000)


            infos = []
            for i in range(1,16):
                linenumber = currline + i
                if(linenumber<linesize):
                    threadinfoStr = lines[linenumber]
                    threadInfos = re.match(
                        r"(?:\s+)?(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*)",
                        threadinfoStr)

                    if threadInfos:
                        infodict = {}
                        PID =   threadInfos.group(1)
                        USER =  threadInfos.group(2)
                        PR =    threadInfos.group(3)
                        NI =    threadInfos.group(4)
                        VIRT =  threadInfos.group(5)
                        RES =   threadInfos.group(6)
                        SHR =   threadInfos.group(7)
                        S =     threadInfos.group(8)
                        CPU =   threadInfos.group(9)
                        MEM =   threadInfos.group(10)
                        TIME =  threadInfos.group(11)
                        COMMAND = threadInfos.group(12)
                        infodict["PID"] = PID
                        infodict["USER"] = USER
                        infodict["PR"] = PR
                        infodict["NI"] = NI
                        infodict["VIRT"] = VIRT
                        infodict["RES"] = RES
                        infodict["SHR"] = SHR
                        infodict["S"] = S
                        infodict["CPU"] = float(CPU)
                        infodict["MEM"] = float(MEM)
                        infodict["TIME"] = TIME
                        infodict["COMMAND"] = COMMAND
                        threadinfo = {}
                        threadinfo["threadid"] = PID
                        threadinfo["info"] = infodict
                        infos.append(threadinfo)

            timeinfos = {}
            timeinfos["ts"] = recordStamp
            timeinfos["infos"] = infos
            records.append(timeinfos)
            currline += 17

        return records


def preProceddData():
    datamap = getDataFromFile()
    result = []
    for (k, v) in datamap.items():
        result.append((k, np.mean(v)))
    return result


def getKeyValueFromstruct_time(dic):
    stamp = dic['ts']

    return float(stamp)


def groupBySecound(seconds, lists):
    s = sorted(lists, key=getKeyValueFromstruct_time)
    length = len(s)

    # 间隔的秒数转化为毫秒数
    seconds = seconds * 1000
    currstamp = s[0]["ts"]

    index = 0
    groupedList = []
    groupcontent = []

    while index < length:
        # print(str(currstamp)+":"+str(s[index]["ts"]))
        if (s[index]["ts"] <= currstamp + seconds):
            groupcontent.append(s[index]["info"])
        else:
            groupedList.append({"ts": currstamp, "infos": groupcontent})
            currstamp += seconds
            groupcontent = []
        index += 1

    return groupedList


def reduceGroup(lists, key, func):
    cplist = copy.deepcopy(lists)
    # print(cplist)
    for batch in cplist:
        infos = batch["infos"]
        llist = []
        for info in infos:
            val = info[key]
            llist.append(val)
        # batch['infos']['freecpuinfo'] = func(llist)
        batch['infos'] = {key: func(llist)}
        # batch['infos'][key] = func(llist)
    return cplist


def getKeyValue(atuple):
    item = atuple[0]
    stamp = time.strptime(item, '%Y-%m-%d %H:%M')
    return stamp


def showdata(xdata, ydata):
    # print(xdata[0])
    # print(xdata[-1])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.xlabel('x')
    plt.ylabel('y')

    # ax.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d %H:%M'))  # 设置时间标签显示格式
    # plt.xticks(pd.date_range(,xdata[0], xdata[-1], freq='T') rotation=45)
    # ax.xaxis.set_major_locator(mdate.MinuteLocator())
    ax.plot(xdata, ydata, "b-")

    plt.show()
    print("plot done")


def stamp2str(str, format):
    return time.strftime(format, time.localtime(str))


def showType(structInfos, type):
    minterval = 5 * 60
    sortedinfos = groupBySecound(minterval, structInfos)
    meaninfo = reduceGroup(sortedinfos, type, lambda list: np.mean(list))
    rowxdata2 = [stamp2str(x["ts"] / 1000, "%Y-%m-%d %H:%M:%S") for x in meaninfo]
    xdata2 = [datetime.strptime(
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x['ts'] * 1.0 / 1000)),
        "%Y-%m-%d %H:%M:%S") for x in meaninfo]
    ydata2 = [x['infos'][type] / 1000 for x in meaninfo]

    formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
    fig, ax = plt.subplots()
    plt.plot_date(xdata2, ydata2)
    ax.xaxis.set_major_locator(
        mdates.MinuteLocator(interval=int(minterval / 60)))
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=90, labelsize=10)
    plt.title(type)
    plt.show()


def main():
    # showdata()
    # structInfos = getDataFromFile(r"C:\Users\wlk\Desktop\recordInfo.txt.10_30")
    structInfos = getDataFromFile(r"C:\Users\wlk\Desktop\serverlogs\2018-10-31\125\recordInfo.txt")
    print(structInfos[0])
    showType(structInfos, "freecpuinfo")

    showType(structInfos, "totalmem")
    showType(structInfos, "freemem")
    showType(structInfos, "buffcachemem")
    showType(structInfos, "usedmem")

    showType(structInfos, "totalswap")
    showType(structInfos, "freeswap")
    showType(structInfos, "usedswap")
    showType(structInfos, "availswap")


#main()
print(getDataFromFile(r"C:\Users\wlk\Desktop\serverlogs\2018-10-31\125\recordTopinfo.txt"))
