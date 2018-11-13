# -*- coding: utf-8 -*-
import time
import random
from kafka import KafkaProducer
bootstrap_servers = '172.16.32.121:9092'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

topic = "0422cde4-887d-48ad-8282-203b9303d4c55"
# topic = "123topic1"


def sendAMessage(topics):
    nowtime = time.time()
    nowstamp = int(nowtime * 1000)
    key = str(nowstamp)
    for atop in topics:
        value1 = atop+",抽汽压力," + str(nowstamp) + "," + str(random.randint(1000, 10000))
        print("{} :{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(nowtime)), value1))
        producer.send(atop, key=str.encode(key), value=str.encode(value1))

def sendManyMessage(n,topics):
    i = 0
    while i < n:
        sendAMessage(topics)
        time.sleep(5)
        i += 1
    producer.close()

# 使用kafka每秒发送一批数据，发送一小时的
totalcount= 3*60*60

topics = ["test-topic-9999911",
          "test-topic-9999912",
          "test-topic-9999913",
          "test-topic-9999914",
          "test-topic-9999915",
          "test-topic-9999916",
          "test-topic-9999917",
          "test-topic-9999918",
          "test-topic-9999919",
          "test-topic-9999920",
          "test-topic-9999921",
          "test-topic-9999922",
          "test-topic-9999923",
          "test-topic-9999924",
          "test-topic-9999925",
          "test-topic-9999926",
          "test-topic-9999927",
          "test-topic-9999928",
          "test-topic-9999929",
          "test-topic-9999930"
          ]

sendManyMessage(totalcount,topics)



