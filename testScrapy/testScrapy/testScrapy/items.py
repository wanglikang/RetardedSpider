# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TestscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    downloadurl = scrapy.Field()
    image_urls =  scrapy.Field()
    images =  scrapy.Field()
    name =  scrapy.Field()
    image_paths = scrapy.Field()
    keywd = scrapy.Field()

