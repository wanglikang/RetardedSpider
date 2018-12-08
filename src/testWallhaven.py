import urllib.request
from bs4 import BeautifulSoup
import re
import os
import _thread
import threading
from SpiderTool.SpiderTool import SpiderTool_Dowdload,SpiderTool
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

class myThread (threading.Thread):
    def __init__(self, threadID, downurl, filename):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.downurl = downurl
        self.filename = filename
    def run(self):
        if self.downurl.startswith("//"):
            self.downurl="https:"+self.downurl
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(self.downurl, self.filename)
        print("sucessful save "+self.downurl)

def findrealurl(url,v_patten):
    bigpic = re.compile(v_patten)
    req = urllib.request.Request(url=url, headers=headers)
    page = urllib.request.urlopen(req).read()
    page = page.decode('utf-8')
    return bigpic.findall(page)[0]


mainurl="https://alpha.wallhaven.cc"

searchkey = input("请输入要搜索图片的关键词：")
page1 = int(input("页码起始页："))
page2 = int(input("页码结束页："))

aaa = mainurl+"/search?q="+searchkey
print(aaa)

#saveDir = r'C:/Users/WLK/Pictures/'+searchkey+'/'
saveDir = r'./download_/'+searchkey+'/'

try:
    os.makedirs(saveDir)
except Exception as e :
    print(e)

findDetailUrlThread = SpiderTool(r'<a.*?class="preview".*?href="(.*?)".*?>')
findDetailUrlThread.start()
findDownloadThread = SpiderTool_Dowdload(r'<img.*?id="wallpaper".*?src="(.*?)".*?>', saveDir)
findDownloadThread.start()

for i in range(page1,page2,1):
    findDetailUrlThread.addqueue(aaa+"&page="+str(i))

while True:
    findDownloadThread.addqueue(findDetailUrlThread.getaresult())
