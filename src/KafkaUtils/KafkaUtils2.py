# -*- coding: utf-8 -*-
import time
import pandas as pd
import traceback
from kafka import KafkaProducer
bootstrap_servers = '172.16.32.125:9092'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
print("build producer sucess")
topicpre = 'test-topic-'

datapoints_71_34 =[]
datapoints_69_153 =[]
datapoints_71_36 =[]

for i in range(99999500,99999650,3):
    datapoints_71_34.append(str(i))
    datapoints_71_36.append(str(i+1))
    datapoints_69_153.append(str(i+2))

def sendAMessage(datapoints,datas,valuestr,i):
    ts = datas["时间"][i]
    stamp = int(time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S")) * 1000)
    for datapointid in datapoints:
        value1 = datapointid+","+valuestr+"," + str(stamp) + "," + str(datas[valuestr][i])
        print("{} :{}".format(ts, value1))
        producer.send(topicpre+str(datapointid), key=str.encode(str(stamp)), value=str.encode(value1))
def sendManyMessage(data1,data2,data3,i):
    sendAMessage(datapoints_71_34,datas=data1,valuestr="device001_6001_0-1.0-71-34(mqtt)",i=i)
    sendAMessage(datapoints_71_36, datas=data2, valuestr="device001_6001_0-1.0-71-36(mqtt)", i=i)
    sendAMessage(datapoints_69_153, datas=data3, valuestr="device001_6001_0-1.0-69-153(mqtt)", i=i)


def loop(data1,data2,data3,n):
    for i in range(n):
        sendManyMessage(data1,data2,data3,n-i)
        time.sleep(15)


filepath71_34 = r"C:\Users\wlk\Documents\WeChat Files\WLK_8178\Files\data (1).csv"
filepath71_36 = r"C:\Users\wlk\Documents\WeChat Files\WLK_8178\Files\data (2).csv"
filepath69_153 = r"C:\Users\wlk\Documents\WeChat Files\WLK_8178\Files\data (3).csv"
data7134 = pd.read_csv(filepath71_34,sep=",")
data7136 = pd.read_csv(filepath71_36,sep=",")
data69153 = pd.read_csv(filepath69_153,sep=",")
length = len(data7134)
try:
    loop(data7134,data7136,data69153,length-1)
except Exception as e :
    producer.close()
    print("发生异常，关闭Kafka producer")
    print(traceback.print_exc())

producer.close()


