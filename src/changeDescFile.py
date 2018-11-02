# -*- coding: utf-8 -*-
import json
def changeDataPointId(datapoint,inputfilepath):
    with open(inputfilepath,'r', encoding='utf-8') as f:
        jobj = json.load(f)
        jobj["inputs"]["datapointId"][0] = "234"
        jobj["allDescribeData"][0]["subNode"][0]['subNode'][0]['subNode'][0]['subNode'][0]['nodeParameter']['datapointId'] = '234'
        print(jobj)

        outfilepath = inputfile[0:-4]+"-"+str(datapoint)+".txt"
        with open(outfilepath, "w") as f:
            json.dump(jobj, f)
        print("保存入文件完成...")
inputfile = r"C:\Users\wlk\Documents\WeChat Files\WLK_8178\Files\NBLabFlow_10551_admin.天津西站日照能量_62_desc.txt"
for i in range(9999921,9999931):
    changeDataPointId(i,inputfile)