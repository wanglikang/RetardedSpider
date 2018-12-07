# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains #引入ActionChains鼠标操作类
from selenium.webdriver.common.keys import Keys #引入keys类操作

from bs4 import BeautifulSoup
import bs4
import requests
import re
import threading

def getAllStockList(url):
    resultList = []
    r = requests.get(url, timeout=30)  # 把爬取后的内容赋给r，等待时间对多30秒
    r.raise_for_status()  # 爬取网页时返回的状态码
    r.encoding = 'GB2312'
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')
    quotebody = soup.find("div",class_="quotebody")
    # print(quotebody)
    uls = quotebody.find("ul")
    lis = uls.find_all("li")
    for li in lis:
        for ch in li.children:
            resultList.append({
                "股票代码":re.match(".*?\((.*?)\)",ch.string).group(1),
                "股票名称":re.match("(.*?)\(",ch.string).group(1),
                "链接": ch["href"]
            })

    print("----"*20)
    print(resultList)
    print("共{}个".format(len(resultList)))
    return resultList
    # resultList.append(re.findall(r"[s][hz]\d{6}", href)[0])

def parseDetailStockHtml(text):
    bsoup = BeautifulSoup(text,"html.parser")
    sideContent = bsoup.find_all("div",class_="cont trade_info_cont")
    #print(type(sideContent))
    ress= []
    for conc in sideContent:
        tbody = conc.find("tbody")
        trs = tbody.find_all("tr")
        res = []
        for tr in trs:
            ths = tr.find_all("th")
            tds = tr.find_all("td")
            rres = []
            for th in ths:
                rres.append(th.string)
            for td in tds:
                rres.append(td.string)

            res.append(rres)

        ress.append(res)
    return ress

def openDetailStockUrl(url):
    """"firefox的headless模式设置，但是不行
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.set_headless()
    brower = webdriver.Firefox(firefox_options=fireFoxOptions)
    """
    browser = webdriver.Firefox()
    browser.maximize_window()
    browser.get(url)
    try:
        we3 = browser.find_element_by_id("tt6_03")
        ActionChains(browser).move_to_element(we3).perform()
        time.sleep(1)
        we2 = browser.find_element_by_id("tt6_02")
        ActionChains(browser).move_to_element(we2).perform()
        time.sleep(1)
        we1 = browser.find_element_by_id("tt6_01")
        ActionChains(browser).move_to_element(we1).perform()
        time.sleep(1)
        we = browser.find_element_by_id("tt6_03")
        ActionChains(browser).move_to_element(we).perform()
        time.sleep(1)
        html = browser.find_element_by_xpath("//*").get_attribute("outerHTML")
        print("成功解析到{}".format(url))
        return html
        #####################
        # print(html)
    except Exception as e:
        print("解析股票代码出错，url:{}".format(url))
        return None
    finally:
        browser.close()


def main():
    #{'股票代码': '900957', '股票名称': '凌云B股', '链接': 'http://quote.eastmoney.com/sh900957.html'}
    stocklistdict = getAllStockList("http://quote.eastmoney.com/stocklist.html")
    count = 0.0

    #从500开始的原因是sina上面的对应eastmoney有些股票没有，或者是代码不对。
    for index in range(500,len(stocklistdict)):
        count=count+1
        if count>50:
            return
        url = "http://finance.sina.com.cn/realstock/company/sh{}/nc.shtml".format(stocklistdict[index]["股票代码"])
        # MyThread(openDetailStockUrl, url)
        htmltext = openDetailStockUrl(url)
        if htmltext is not None:
            result = parseDetailStockHtml(htmltext)
            for i in result:
                print(i)
            #time.sleep(1)


class MyThread(threading.Thread):
    def __init__(self,func,arg):
        super(MyThread, self).__init__()#注意：一定要显式的调用父类的初始化函数。
        self.func = func
        self.arg=arg
    def run(self):#定义每个线程要运行的函数
        self.func(self.arg)



#getAllStockList("http://quote.eastmoney.com/stocklist.html")
main()