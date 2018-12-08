# -*- coding: utf-8 -*-
import time
import random
from kafka import KafkaProducer
import datetime
import random
bootstrap_servers = 'localhost:9092'
# bootstrap_servers = '172.16.32.125:9092'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
topicpre = 'test-topic-'


def sendAMessage2(topics):
    nowtime = time.time()
    nowstamp = int(nowtime * 1000)
    key = str(nowstamp)
    for atop in topics:
        value1 = atop + ",抽汽压力," + str(nowstamp) + "," + str(random.randint(1000, 10000))
        print("{} :{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(nowtime)), value1))
        producer.send(topicpre + str(atop), key=str.encode(key), value=str.encode(value1))


def sendAMessage(topics, datas, valuestr, i):
    ts = datas["时间"][i]
    stamp = int(time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S")) * 1000)
    for atop in topics:
        value1 = atop + "," + valuestr + "," + str(stamp) + "," + datas[valuestr][i]
        print("{} :{}".format(ts, value1))
        producer.send(topicpre + str(atop), key=str.encode(stamp), value=str.encode(value1))

def sendMessage2(producer,topic,key,value):
    producer.send(topic, key=str.encode(key), value=str.encode(value))

def sendManyMessage(n, topics, data1, data2, data3):
    i = 0
    while i < n:
        sendAMessage(topics)
        sendAMessage(topics)
        sendAMessage(topics)
        time.sleep(15)
        i += 1
    producer.close()


# 使用kafka每秒发送一批数据，发送一小时的
# totalcount = 3 * 60 * 60
#
# topics = []

# for i in range(99999200,99999270):
#     topics.append(str(i))
# 
# def inittopic():
#     for i in range(99999500, 99999512):
#     topics.append(str(i))

    # print(topics)
    # sendManyMessage(totalcount,topics)

# i = 0
# while i < n:
#     sendAMessage(topics)
#     time.sleep(15)
#     i += 1
# producer.close()

mtopic="kafka-topic-1"
for i in range(1000):
    atime = time.time()
    
    stampstr = str(int(atime * 1000))
    valuestr = ""
    for i in range(5):
        valuestr += str(random.randint(0,1000))+" "
    valuestr += str(random.randint(0, 1000))
    sendvalu = stampstr+" "+valuestr

    producer.send(topic=mtopic,key=str.encode(stampstr),value=str.encode(sendvalu))
    print("send key:{} value:{}".format(stampstr,sendvalu))
    time.sleep(5)
producer.close()


