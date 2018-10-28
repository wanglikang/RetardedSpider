# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains #引入ActionChains鼠标操作类
from selenium.webdriver.common.keys import Keys #引入keys类操作

from bs4 import BeautifulSoup
import bs4
import re

def parseHtml(text):
    bsoup = BeautifulSoup(text,"html.parser")
    sideContent = bsoup.find_all("div",class_="cont trade_info_cont")
    print(type(sideContent))
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


def openurl(url):
    browser = webdriver.Chrome()
    browser.get(url)
    # browser.
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

    # print(html)
    return html

url = "http://finance.sina.com.cn/realstock/company/sz000877/nc.shtml"
htmltext  = openurl(url)
result  = parseHtml(htmltext)
for i in result:
    print(i)