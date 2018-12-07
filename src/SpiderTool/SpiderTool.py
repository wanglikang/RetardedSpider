import urllib.request
from bs4 import BeautifulSoup
import re
import os
import _thread
import threading

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}


class SpiderTool(threading.Thread):
    def __init__(self, patt):
        threading.Thread.__init__(self)
        self.urllist = []
        self.resultlist = []
        self.stop = False;
        self.resultSem = threading.Semaphore(0)
        self.newurlSem = threading.Semaphore(0)
        self.runSem = threading.Semaphore(0)
        self.regPatten = patt

    def run(self):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        while not self.stop:
            print("SpiderTool is running------")
            self.runSem.acquire()
            self.newurlSem.acquire()
            print("SpiderTool is running++++++")
            uurl = str(self.urllist.pop())
            print("uurl is :"+uurl)
            page = urllib.request.urlopen(uurl).read()
            page = page.decode('utf-8')

            comm = re.compile(self.regPatten)
            things = comm.findall(str(page))
            for a in things:
                self.resultlist.append(a)
                #print(a)
                self.resultSem.release()

    def addqueue(self,obj):
        self.urllist.append(obj)
        self.runSem.release()
        self.newurlSem.release()

    def killthis(self):
        self.stop = True

    def getaresult(self):
        self.resultSem.acquire()
        if len(self.resultlist) > 0:
            return self.resultlist.pop()
        else:
            return None



class SpiderTool_Dowdload(threading.Thread):
    def __init__(self, regPatten ,downloaddirpath):
        threading.Thread.__init__(self)
        self.downloadlist = []
        self.stop = False;
        self.listlock = threading.Semaphore(0)
        self.runlock = threading.Semaphore(0)
        if str(downloaddirpath).endswith("/"):
            self.downloaddirpath = downloaddirpath
        else:
            self.downloaddirpath = downloaddirpath+"/"


        self.regPatten = regPatten
    def run(self):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        while not self.stop:
            self.runlock.acquire()
            self.listlock.acquire()
            print("SpiderTool_download is running!")
            detailurl  = str(self.downloadlist.pop())
            page = urllib.request.urlopen(detailurl).read()
            page = page.decode('utf-8')

            comm = re.compile(self.regPatten)
            thisdownloadurl = comm.findall(str(page))[0]
            if thisdownloadurl.startswith("//"):
                thisdownloadurl = "https:" + thisdownloadurl

            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent',
                                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
            urllib.request.install_opener(opener)

            _thread.start_new_thread(urllib.request.urlretrieve,(thisdownloadurl, self.downloaddirpath+thisdownloadurl[thisdownloadurl.rindex("/")+1:]))
            print("sucessful save " +thisdownloadurl + " which is "+ self.downloaddirpath+thisdownloadurl[thisdownloadurl.rindex("/")+1:])

    def addqueue(self, obj):
        print("SpiderTool_Dowdload addqueue:"+obj)
        self.downloadlist.append(obj)
        self.listlock.release()
        self.runlock.release()

    def killthis(self):
        self.stop = True ;

