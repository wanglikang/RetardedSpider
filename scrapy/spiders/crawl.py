"""
This modules implements the CrawlSpider which is the recommended spider to use
for scraping typical web sites that requires crawling pages.

See documentation in docs/topics/spiders.rst
"""

import copy
import six

from scrapy import Request, HtmlResponse
from scrapy.utils.spider import iterate_spider_output
from scrapy.spiders import Spider


def identity(x):
    return x

"""
用于抽取网页中特定数据的规则
"""
class Rule(object):

    """
    link_extractor:抽取器的规则
    callback:回调函数
    cb_kwargs:回调函数的参数
    follow：是否跟随爬取
    process_links:爬取的链接？？？
    process_request:对request请求的处理，默认是不处理，原样返回
    """
    def __init__(self, link_extractor, callback=None, cb_kwargs=None, follow=None, process_links=None, process_request=identity):
        self.link_extractor = link_extractor
        self.callback = callback
        self.cb_kwargs = cb_kwargs or {}
        self.process_links = process_links
        self.process_request = process_request
        if follow is None:
            self.follow = False if callback else True
        else:
            self.follow = follow


class CrawlSpider(Spider):

    rules = ()

    def __init__(self, *a, **kw):
        super(CrawlSpider, self).__init__(*a, **kw)
        self._compile_rules()
    """
    子类实现的对结果处理的方法。为简单的调用_parse_response
    """
    def parse(self, response):
        return self._parse_response(response, self.parse_start_url, cb_kwargs={}, follow=True)

    """
      处理response，将会调用传入的回调函数以及回调函数的参数进行处理，
      返回request或者处理结果产生的item
      """

    def _parse_response(self, response, callback, cb_kwargs, follow=True):
        if callback:
            cb_res = callback(response, **cb_kwargs) or ()
            cb_res = self.process_results(response, cb_res)
            for requests_or_item in iterate_spider_output(cb_res):
                yield requests_or_item

        if follow and self._follow_links:#对request的子链接进行跟进处理，也就是根据设置的Rule进行处理
            for request_or_item in self._requests_to_follow(response):
                yield request_or_item

    """
       对request的结果response进行follow爬取,被本类中的_parse_response函数调用
       """

    def _requests_to_follow(self, response):
        if not isinstance(response, HtmlResponse):
            return
        seen = set()
        # 对每个规则rule进行判断：
        # 若匹配到了对应的规则，则使用规则中process_links函数进行处理，
        # 并将处理的结果交由rule中的proicess_request进行处理
        for n, rule in enumerate(self._rules):
            # 使用rule规则对response中的信息进行抽取，并且去重
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)


    """
    默认返回空列表，需要自定义实现，否则解析不出来啥东西
    """
    def parse_start_url(self, response):
        return []

    def process_results(self, response, results):
        return results

    """
    生成request交给带调度器进行调度，
    在Request中设置了回调函数_response_downloaded，也就是会先使用回调函数，在使用parse进行处理
    """
    def _build_request(self, rule, link):
        r = Request(url=link.url, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    """
    在response下载完毕后进行使用这个函数进行处理，内部也是调用_parse_response，
    其实就是不断的使用Rule对爬取到的页面进行迭代处理
    """
    def _response_downloaded(self, response):
        rule = self._rules[response.meta['rule']]
        return self._parse_response(response, rule.callback, rule.cb_kwargs, rule.follow)


    """
    对规则Rule进行“编译”处理，即提取其中的各个callback、process_links、process_request属性
    """
    def _compile_rules(self):
        def get_method(method):
            if callable(method):
                return method
            elif isinstance(method, six.string_types):
                return getattr(self, method, None)

        self._rules = [copy.copy(r) for r in self.rules]
        for rule in self._rules:
            rule.callback = get_method(rule.callback)
            rule.process_links = get_method(rule.process_links)
            rule.process_request = get_method(rule.process_request)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider._follow_links = crawler.settings.getbool(
            'CRAWLSPIDER_FOLLOW_LINKS', True)
        return spider

    def set_crawler(self, crawler):
        super(CrawlSpider, self).set_crawler(crawler)
        self._follow_links = crawler.settings.getbool('CRAWLSPIDER_FOLLOW_LINKS', True)
