# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains #引入ActionChains鼠标操作类
from selenium.webdriver.common.keys import Keys #引入keys类操作

from bs4 import BeautifulSoup
import bs4
import requests
import re


def getAllStockList(url):
    resultList = []
    r = requests.get(url, timeout=30)  # 把爬取后的内容赋给r，超时时间30秒
    r.raise_for_status()  # 爬取网页时返回的状态码
    r.encoding = 'GB2312'
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')
    quotebody = soup.find("div",class_="quotebody")
    uls = quotebody.find("ul")
    lis = uls.find_all("li")
    for li in lis:
        for ch in li.children:
            resultList.append({
                "股票代号":re.match(".*?\((.*?)\)",ch.string).group(1),
                "股票名称":re.match("(.*?)\(",ch.string).group(1),
                "链接": ch["href"]
            })
    print("----"*20)
    for l in resultList:
        print(l)

    pass

def parseDetailStockHtml(text):
    bsoup = BeautifulSoup(text,"html.parser")
    sideContent1 = bsoup.find("div",class_="box-x1 line24")
    tbody = sideContent1.find("tbody")
    trs = tbody.find_all("tr")
    for tr in trs:
        print(tr)
        print("--")
        if isinstance(tr,bs4.element.Tag):
            tds = tr.find_all("td")
            for td in tds:
                print(td)
                span = td.find("span")
                print(span)
                # print(td)
        print("---"*5)

    ress= []
    # for conc in sideContent1:
    #     tbody = conc.find("tbody")
    #     trs = tbody.find_all("tr")
    #     res = []
    #     for tr in trs:
    #         ths = tr.find_all("th")
    #         tds = tr.find_all("td")
    #         rres = []
    #         for th in ths:
    #             rres.append(th.string)
    #         for td in tds:
    #             rres.append(td.string)
    #
    #         res.append(rres)
    #
    #     ress.append(res)
    return ress

def openDetailStockUrl(url):
    browser = webdriver.Firefox()
    browser.get(url)
    # browser.
    # we3 = browser.find_element_by_class_name("tt6_03")
    # ActionChains(browser).move_to_element(we3).perform()
    # time.sleep(1)
    # we2 = browser.find_element_by_id("tt6_02")
    # ActionChains(browser).move_to_element(we2).perform()
    # time.sleep(1)
    # we1 = browser.find_element_by_id("tt6_01")
    # ActionChains(browser).move_to_element(we1).perform()
    # time.sleep(1)
    # we = browser.find_element_by_id("tt6_03")
    # ActionChains(browser).move_to_element(we).perform()
    # time.sleep(1)
    html = browser.find_element_by_xpath("//*").get_attribute("outerHTML")
    browser.close()
    return html

def main():
    # url = "http://finance.sina.com.cn/realstock/company/sz000877/nc.shtml"
    url = "http://quote.eastmoney.com/sh600074.html"
    htmltext  = openDetailStockUrl(url)
    result  = parseDetailStockHtml(htmltext)
    for i in result:
        print(i)

main()
# getAllStockList("http://quote.eastmoney.com/stocklist.html")