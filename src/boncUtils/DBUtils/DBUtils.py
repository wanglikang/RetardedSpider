# -*- coding: utf-8 -*-
import MySQLdb
import time
batchRecord = 1 # 每批多少个数据
continuehour = 3 # 持续发送的多少个小时
parMin = 5 # 每几分钟添加一批
# 每5分钟往数据库里添加一批task，每批batchRecord个

batchInterrval = parMin * 60
host="172.16.12.252"
port = 3306
user = "root"
passwd = "root"
db="iot_26_10_26"
# db="test"
taskinfoTable = "taskinfo"
streamingconfigTable = "streamingconfig"
def insertTaskinfo(taskid, flowid, descpath, taskstatu, N):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
    cur = conn.cursor()
    sql = "INSERT INTO`"+db+"`.`"+taskinfoTable+"` (`taskID`, `flowID`, `taskDescPath`, `taskStatus`, `taskType`, `taskName`) VALUES (%s, %s, %s, %s, %s,%s)"
    records = []
    for i in range(0, N):
        records.append((taskid + i, taskid + i, descpath, taskstatu, '2', '重复任务'))

    print(sql)
    print(records)
    re = cur.executemany(sql, records)
    cur.close()
    conn.commit()
    conn.close()

def insertDataPoint(datapointid):

    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
    cur = conn.cursor()
    sql1 = "INSERT INTO`" + db + "`.`datapointinfo` (`dataPointID`, `dataPointName`, `srcID`, `storeID`, `srcType`, `storeType`, `otherInfo`, `status`)" \
                                " VALUES (%s, %s, %s, %s, %s,%s,%s,%s)"
    records = []
    records.append((str(datapointid), "测试数据点名称", str(datapointid), "3477", '9', '1', '{}', '1'))

    sql2 = "INSERT INTO`" + db + "`.`topicinfo` (`topicID`, `srcID`)" \
                                " VALUES (\"test-topic-"+str(datapointid)+"\", "+str(datapointid)+")"
    sql3 = "INSERT INTO`" + db + "`.`srcinfo` (`srcID`, `srcName`,`srcType`,`srcInfo`)" \
                                 " VALUES (\"" + str(datapointid) + "\", " + str(datapointid) + ",8,\"infoinfo\")"
    sql4 = "INSERT INTO`" + db + "`.`middlewareconfig` (`processID`, `topicID`,`brokerIDs`,`status`)" \
                                 " VALUES ('16',"+str(datapointid)+",'112',0)"
    sql5 = "INSERT INTO`" + db + "`.`clientconfig` (`processID`, `topicID`,`brokerIDs`,`status`,`brokerGroup`)" \
                                 " VALUES ('16'," + str(datapointid) + ",'112',0,3)"

    re = cur.executemany(sql1, records)
    re2 = cur.execute(sql2)
    re3 = cur.execute(sql3)
    re4 = cur.execute(sql4)
    re5 = cur.execute(sql5)
    cur.close()
    conn.commit()
    conn.close()


def insertStreamingConfig(processID, taskID,timeWindow,interval ,status, N):
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
    cur = conn.cursor()
    # INSERT INTO `iot_26_10_26`.`streamingconfig` (`processID`, `taskID`, `timeWindow`, `interval`, `status`) VALUES ('7', '1112848', '1', '1', '4');
    sql = "INSERT INTO `"+db+"`.`"+streamingconfigTable+"` (`processID`, `taskID`, `timeWindow`, `interval`, `status`) VALUES (%s, %s, %s, %s, %s)"
    records = []
    for i in range(0, N):
        records.append((processID, taskID+i, timeWindow, interval, status))

    print(sql)
    print(records)
    re = cur.executemany(sql, records)
    cur.close()
    conn.commit()
    conn.close()


def main():
    starttaskid = 99999300
    endtaskid = 99999400 #continuehour小时内，，每parMin分钟添加一批数据，每批数据batchRecord个task
    currtaskid = starttaskid

    while currtaskid < endtaskid:
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))
        insertDataPoint(currtaskid)
        insertDataPoint(currtaskid+1)
        insertTaskinfo(currtaskid, currtaskid,
                       "/home/spark/IOT/desc/NBLabFlow_10551_admin.天津西站日照能量_62_desc-"+str(currtaskid)+".txt", 0, batchRecord)

        #不用自己写入streamingconfig，，，数据库会自动创建相应的行
        #insertStreamingConfig(7,currtaskid,1,60,60,batchRecord)
        currtaskid += 2
        # time.sleep(batchInterrval)
        time.sleep(1)
def main2():
    starttaskid = 99999500
    endtaskid = 99999650 #continuehour小时内，，每parMin分钟添加一批数据，每批数据batchRecord个task
    currtaskid = starttaskid

    while currtaskid < endtaskid:
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))
        insertDataPoint(currtaskid)
        insertDataPoint(currtaskid+1)
        insertDataPoint(currtaskid + 2)
        insertTaskinfo(currtaskid, currtaskid,
                       "/home/spark/IOT/desc/NBLabFlow_11510_zhuduohui.dddddddd_16_desc-"+str(currtaskid)+".txt", 0, batchRecord)

        #不用自己写入streamingconfig，，，数据库会自动创建相应的行
        #insertStreamingConfig(7,currtaskid,1,60,60,batchRecord)
        currtaskid += 3
        # time.sleep(batchInterrval)
        # time.sleep(1)

main2()
#insertDataPoint(407193)

