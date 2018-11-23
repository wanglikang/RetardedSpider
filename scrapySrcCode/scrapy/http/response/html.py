"""
This module implements the HtmlResponse class which adds encoding
discovering through HTML encoding declarations to the TextResponse class.

See documentation in docs/topics/request-response.rst
"""

from scrapySrcCode.scrapy.http import TextResponse

class HtmlResponse(TextResponse):
    pass
