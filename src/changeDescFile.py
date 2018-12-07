# -*- coding: utf-8 -*-
import json
def changeDataPointId(datapoint,inputfilepath):
    with open(inputfilepath,'r', encoding='utf-8') as f:
        jobj = json.load(f)
        jobj["inputs"]["datapointId"][0] = datapoint
        jobj["inputs"]["datapointId"][1] = datapoint+1
        jobj["inputs"]["datapointId"][2] = datapoint + 2
        jobj["timeWindow"]="60"
        jobj["timeInterval"] = "60"
        # jobj["allDescribeData"][0]["subNode"][0]['subNode'][0]['subNode'][0]['subNode'][0]['nodeParameter']['datapointId'] = datapoint
        #jobj["allDescribeData"][0]["subNode"][0]['nodeParameter']['datapointId'] = datapoint
        #jobj["allDescribeData"][0]["subNode"][1]['nodeParameter']['datapointId'] = datapoint+1
        jobj["allDescribeData"][0]["subNode"][0]["subNode"][0]['nodeParameter']['datapointId'] = datapoint
        jobj["allDescribeData"][0]["subNode"][0]["subNode"][1]['nodeParameter']['datapointId'] = datapoint+1
        jobj["allDescribeData"][0]["subNode"][0]["subNode"][2]['nodeParameter']['datapointId'] = datapoint+2

        print(jobj)
        outfilepath = inputfile[0:-4]+"-"+str(datapoint)+".txt"
        with open(outfilepath, "w", encoding='utf-8') as f:
            json.dump(jobj, f,ensure_ascii=False,indent=4)
        print("保存入文件完成..."+outfilepath)
# inputfile = r"C:\Users\wlk\Documents\WeChat Files\WLK_8178\Files\NBLabFlow_10551_admin.天津西站日照能量_62_desc.txt"
#inputfile = r"C:\Users\wlk\Desktop\integralSum\NBLabFlow_11324_zhuduohui.w_testPlus_4_desc.txt"
inputfile = r"C:\Users\wlk\Desktop\descs\NBLabFlow_11510_zhuduohui.dddddddd_16_desc.txt"
for i in range(99999500,99999800,3):
    print(i)
    changeDataPointId(i,inputfile)