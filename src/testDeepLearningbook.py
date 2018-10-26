import urllib.request
from bs4 import BeautifulSoup
import re
import os
import _thread
import threading

class myThread (threading.Thread):
    def __init__(self, threadID, downurl, filename):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.downurl = downurl
        self.filename = filename
    def run(self):
        urllib.request.urlretrieve(self.downurl, self.filename)



mainurl="http://www.deeplearningbook.org/"


page = urllib.request.urlopen(mainurl).read()
saveDir = 'C:/Users/WLK/Desktop/'
page = page.decode('ISO-8859-1')

bsbody = BeautifulSoup( page , "html.parser")
uls = bsbody.body.ul
#print(uls)
#print("------------------")

ccom = re.compile(r'<a.*?href=\"(.*?)\">(.*?)</a>')
i = 0
for li in uls:
    #print("start:"+str(li))
    linkandcontent = ccom.findall(str(li))
    linklen = len(linkandcontent)
    if linklen >0:
        print(linkandcontent)
        for links in linkandcontent:
            print(links[0])
            print(links[1])
            print(mainurl+links[0])
            print(saveDir + links[1] + ".html")

            try:
                thread1 = myThread(++i, mainurl + links[0],saveDir + links[1] + ".html")
                thread1.start()
                thread1.join()
                print("开启了一个线程用于下载：" + links[1])
            except:
                print("Error: 无法启动线程")
            print("done with"+links[1])

'''
try:
    os.makedirs(saveDir);
except Exception as e:
    print(e)


for imgurl in things:
    if imgurl[1]!='':
        print(imgurl[1])
        bigurl = requestDetailPic("http://desk.zol.com.cn/"+imgurl[0]);
        urllib.request.urlretrieve(bigurl, saveDir + '/' + imgurl[1]+".png")
'''