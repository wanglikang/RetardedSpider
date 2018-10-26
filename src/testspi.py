#encoding=utf8
import urllib.request
import re
import os

mainurl="http://desk.zol.com.cn/nb/"
preurl = "http://desk.zol.com.cn"
Display_size="1366x768"

def findmatchDisplaysizeUrl(url):
    page = urllib.request.urlopen(url).read()
    page = page.decode('gbk')
    ccom = re.compile(r'<img src="(.*?)">');
    things = ccom.findall(page);
    print(things[0])
    return things[0];

def requestDetailPic(imgurl):
    print("imgurl :"+imgurl)
    page = urllib.request.urlopen(imgurl).read()
    page = page.decode('gbk')
    ccom = re.compile(r'<a.*?id="'+Display_size+r'".*?href="(.*?)".*?>.*?</a>')
    sizedparg = ccom.findall(page)
    print(sizedparg[0])
    return findmatchDisplaysizeUrl(preurl+sizedparg[0]);


headers = {
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    'Content-Length':'0'
}
page = urllib.request.urlopen(mainurl,headers).read()
saveDir='e://testpyspider'
page = page.decode('gbk')
#sprint(page)
ccom = re.compile(r'<a class="pic" href="(.*?)".*?'
                  r'<img.*?alt="(.*?)".*?src="(.*?)".*?>.*?'
                  r'</a>')
things = ccom.findall(page)
print(things)

try:
    os.makedirs(saveDir);
except Exception as e:
    print(e)

for imgurl in things:
    if imgurl[1]!='':
        print(imgurl[1])
        bigurl = requestDetailPic("http://desk.zol.com.cn/"+imgurl[0]);
        urllib.request.urlretrieve(bigurl, saveDir + '/' + imgurl[1]+".png")
