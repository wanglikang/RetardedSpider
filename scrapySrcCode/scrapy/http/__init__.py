"""
Module containing all HTTP related classes

Use this module (instead of the more specific ones) when importing Headers,
Request and Response outside this module.
"""

from scrapySrcCode.scrapy.http import Headers

from scrapySrcCode.scrapy.http import Request
from scrapySrcCode.scrapy.http import FormRequest
from scrapySrcCode.scrapy.http import XmlRpcRequest

from scrapySrcCode.scrapy.http import Response
from scrapySrcCode.scrapy.http import HtmlResponse
from scrapySrcCode.scrapy.http import XmlResponse
from scrapySrcCode.scrapy.http import TextResponse
