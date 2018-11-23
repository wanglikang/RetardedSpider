# -*- coding: utf-8 -*-
import scrapy
import os
import re
from ..items import TestscrapyItem


class Spider1Spider(scrapy.Spider):
    name = "spider1"
    allowed_domains = ["wallhaven.cc"]
    start_urls = ['https://alpha.wallhaven.cc']

    keyword = ""
    def start_requests(self):
        searchkey = input("请输入要搜索图片的关键词：")
        self.keyword = searchkey
        page1 = int(input("页码起始页："))
        page2 = int(input("页码结束页："))
        aaa = self.start_urls[0] + "/search?q=" + searchkey

        for pagenumber in range(page1,page2):
            yield scrapy.Request(url=aaa+"&page="+str(pagenumber), callback=self.parse)

    def parse(self, response):
        comm = re.compile(r'<a.*?class="preview".*?href="(.*?)".*?>')
        things = comm.findall(str(response.text))
        for pre in things:
            yield scrapy.Request(url=pre, callback=self.parseDetail)

    def parseDetail(self, response):
        comm = re.compile(r'<img.*?id="wallpaper".*?src="(.*?)".*?>')
        things = comm.findall(str(response.text))
        for thing in things:
            aitem = TestscrapyItem()
            aitem['image_urls'] = ["https:"+thing,]
            aitem['keywd'] = self.keyword
            yield aitem