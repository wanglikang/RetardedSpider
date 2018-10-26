# -*- coding: utf-8 -*-
import urllib.request
import requests
from bs4 import BeautifulSoup
import bs4
import re


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
url = "http://www.zuihaodaxue.cn/zuihaodaxuepaiming2017.html"
def fetchUrl(url):
    response = requests.get(url=url)
    response.encoding = 'utf-8'
    # print(response.text)
    return response.text.encode("utf-8")
def parseHtml(text):
    bsoup = BeautifulSoup(text,"html.parser")
    trs = bsoup.find("tbody").children
    resultset = []
    for tr in trs:
        if isinstance(tr,bs4.element.Tag):
            td = tr("td")
            grps = re.compile("<td>(\\d+)<td>").findall(str(td[0]))
            resultset.append((
                    int(grps[0]),
                    str(td[1].string),
                    str(td[2].string),
                    float(td[3].string)))
    return resultset
def output(set):
    print("{:2s}\t|{:11s}\t|{:<5s}|{:5s}".format("排名","学校名字","地区","总分"))
    for res in set:
        print("{:3d}\t|{:11s}\t|{:<5s}|{:.5f}".format(res[0], res[1], res[2], res[3]))

    pass

def main():
    text = fetchUrl(url)
    result = parseHtml(text)
    output(result)

    pass
# if __name__ == "__main__":

main()
