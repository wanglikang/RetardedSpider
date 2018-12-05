"""
This is the Scrapy engine which controls the Scheduler, Downloader and Spiders.

For more information see docs/topics/architecture.rst

"""
import logging
from time import time

from twisted.internet import defer, task
from twisted.python.failure import Failure

from scrapy import signals
from scrapy.core.scraper import Scraper
from scrapy.exceptions import DontCloseSpider
from scrapy import Response, Request
from scrapy.utils.misc import load_object
from scrapy.utils.reactor import CallLaterOnce
from scrapy.utils.log import logformatter_adapter, failure_to_exc_info

logger = logging.getLogger(__name__)

"""
执行引擎使用的slot，
作用是使用Twisted的主循环类不断的调度引擎的_next_request方法
（在引擎的open_spider方法中被设置）
此外，slot还有跟踪正在下载的request的功能
"""
class Slot(object):

    def __init__(self, start_requests, close_if_idle, nextcall, scheduler):
        self.closing = False
        self.inprogress = set() # requests in progress，用于跟踪正在进行的request请求
        self.start_requests = iter(start_requests)
        self.close_if_idle = close_if_idle
        self.nextcall = nextcall
        self.scheduler = scheduler
        self.heartbeat = task.LoopingCall(nextcall.schedule)

    def add_request(self, request):
        self.inprogress.add(request)

    def remove_request(self, request):
        self.inprogress.remove(request)
        self._maybe_fire_closing()

    def close(self):
        self.closing = defer.Deferred()
        self._maybe_fire_closing()
        return self.closing

    def _maybe_fire_closing(self):
        if self.closing and not self.inprogress:
            if self.nextcall:
                self.nextcall.cancel()
                if self.heartbeat.running:
                    self.heartbeat.stop()
            self.closing.callback(None)

"""
最重要的执行引擎类
"""
class ExecutionEngine(object):

    def __init__(self, crawler, spider_closed_callback):
        self.crawler = crawler
        self.settings = crawler.settings
        self.signals = crawler.signals#使用crawler的信号管理器
        self.logformatter = crawler.logformatter
        self.slot = None
        self.spider = None
        self.running = False
        self.paused = False
        self.scheduler_cls = load_object(self.settings['SCHEDULER'])#根据配置的调度器类来生成对应的对象
        downloader_cls = load_object(self.settings['DOWNLOADER'])#根据配置的下载器类来生成对应的类
        self.downloader = downloader_cls(crawler)
        self.scraper = Scraper(crawler)#生成一个刮取器
        self._spider_closed_callback = spider_closed_callback

    @defer.inlineCallbacks
    def start(self):
        """Start the execution engine"""
        assert not self.running, "Engine already running"
        self.start_time = time()
        yield self.signals.send_catch_log_deferred(signal=signals.engine_started)
        self.running = True
        self._closewait = defer.Deferred()
        yield self._closewait

    def stop(self):
        """Stop the execution engine gracefully"""
        assert self.running, "Engine not running"
        self.running = False
        dfd = self._close_all_spiders()
        return dfd.addBoth(lambda _: self._finish_stopping_engine())

    def close(self):
        """Close the execution engine gracefully.

        If it has already been started, stop it. In all cases, close all spiders
        and the downloader.
        """
        if self.running:
            # Will also close spiders and downloader
            return self.stop()
        elif self.open_spiders:
            # Will also close downloader
            return self._close_all_spiders()
        else:
            return defer.succeed(self.downloader.close())

    def pause(self):
        """Pause the execution engine"""
        self.paused = True

    def unpause(self):
        """Resume the execution engine"""
        self.paused = False

    """
    被CallLaterOnce包装后被slot设置，
    主要在reactor中的heartbeat中被定时调用（在slot中设置），不过也可以被代码主动调用
    """
    def _next_request(self, spider):
        slot = self.slot
        if not slot:
            return

        if self.paused:
            return
        #此处应该是通过调度器异步的获取待处理的request
        while not self._needs_backout(spider):
            if not self._next_request_from_scheduler(spider):
                break

        if slot.start_requests and not self._needs_backout(spider):
            try:
                request = next(slot.start_requests)
            except StopIteration:
                slot.start_requests = None
            except Exception:
                slot.start_requests = None
                logger.error('Error while obtaining start requests',
                             exc_info=True, extra={'spider': spider})
            else:
                self.crawl(request, spider)

        if self.spider_is_idle(spider) and slot.close_if_idle:
            self._spider_idle(spider)

    """
    判断当前引擎的状态是不是异常，需不需要回退（backout）
    """
    def _needs_backout(self, spider):
        slot = self.slot
        return not self.running \
            or slot.closing \
            or self.downloader.needs_backout() \
            or self.scraper.slot.needs_backout()

    """
    从调度器中请求下一个request，如果有request待处理，
    那么就对这个request进行下载处理，并对下载的操作添加一下回调函数
    """
    def _next_request_from_scheduler(self, spider):
        slot = self.slot
        request = slot.scheduler.next_request()
        if not request:
            return
        d = self._download(request, spider)
        d.addBoth(self._handle_downloader_output, request, spider)
        d.addErrback(lambda f: logger.info('Error while handling downloader output',
                                           exc_info=failure_to_exc_info(f),
                                           extra={'spider': spider}))
        d.addBoth(lambda _: slot.remove_request(request))
        d.addErrback(lambda f: logger.info('Error while removing request from slot',
                                           exc_info=failure_to_exc_info(f),
                                           extra={'spider': spider}))
        d.addBoth(lambda _: slot.nextcall.schedule())
        d.addErrback(lambda f: logger.info('Error while scheduling new request',
                                           exc_info=failure_to_exc_info(f),
                                           extra={'spider': spider}))
        return d

    """
    对下载器的结果输出进行的异步处理
    """
    def _handle_downloader_output(self, response, request, spider):
        assert isinstance(response, (Request, Response, Failure)), response
        # downloader middleware can return requests (for example, redirects)
        if isinstance(response, Request):
            self.crawl(response, spider)
            return
        # response is a Response or Failure
        d = self.scraper.enqueue_scrape(response, request, spider)
        d.addErrback(lambda f: logger.error('Error while enqueuing downloader output',
                                            exc_info=failure_to_exc_info(f),
                                            extra={'spider': spider}))
        return d

    def spider_is_idle(self, spider):
        if not self.scraper.slot.is_idle():
            # scraper is not idle
            return False

        if self.downloader.active:
            # downloader has pending requests
            return False

        if self.slot.start_requests is not None:
            # not all start requests are handled
            return False

        if self.slot.scheduler.has_pending_requests():
            # scheduler has pending requests
            return False

        return True

    @property
    def open_spiders(self):
        return [self.spider] if self.spider else []

    def has_capacity(self):
        """Does the engine have capacity to handle more spiders"""
        return not bool(self.slot)

    """
    调用schedule请求slot处理request，并且显式通知slot进行处理
    """
    def crawl(self, request, spider):
        assert spider in self.open_spiders, \
            "Spider %r not opened when crawling: %s" % (spider.name, request)
        self.schedule(request, spider)
        self.slot.nextcall.schedule()

    """
    通过slot将request入队，等待被reactor处理，
    """
    def schedule(self, request, spider):
        self.signals.send_catch_log(signal=signals.request_scheduled,
                request=request, spider=spider)
        if not self.slot.scheduler.enqueue_request(request):
            self.signals.send_catch_log(signal=signals.request_dropped,
                                        request=request, spider=spider)

    """
    根据请求进行下载，其实是调用_download进行下载
    并且在下载完成之后，通过reactor异步调度_downloaded函数。
    """
    def download(self, request, spider):
        d = self._download(request, spider)
        d.addBoth(self._downloaded, self.slot, request, spider)
        return d

    """
    在下载完成之后，从slot中将要对应的request移除，然后在判断response的类型：
        如果是Request，则继续进行下载；若是Response，则直接返回
    """
    def _downloaded(self, response, slot, request, spider):
        slot.remove_request(request)
        return self.download(response, spider) if isinstance(response, Request) else response

    """
    将下载的任务由下载器downloader进行下载的操作
    并添加了两个回调函数：
        在下载完毕complete的时候
        在下载成功success的时候
    """
    def _download(self, request, spider):
        slot = self.slot
        slot.add_request(request)
        def _on_success(response):
            assert isinstance(response, (Response, Request))
            if isinstance(response, Response):
                response.request = request # tie request to response received
                logkws = self.logformatter.crawled(request, response, spider)
                logger.log(*logformatter_adapter(logkws), extra={'spider': spider})
                self.signals.send_catch_log(signal=signals.response_received, response=response, request=request, spider=spider)
            return response

        """
        在下载完成的时候显式调用slot进行调度处理
        """
        def _on_complete(_):
            slot.nextcall.schedule()
            return _

        dwld = self.downloader.fetch(request, spider)
        dwld.addCallbacks(_on_success)
        dwld.addBoth(_on_complete)
        return dwld

    """
    ### 被scrapy.crawler.crawl调用
    开启爬虫系统
    创建调度器并开启，
    """
    @defer.inlineCallbacks
    def open_spider(self, spider, start_requests=(), close_if_idle=True):
        assert self.has_capacity(), "No free spider slot when opening %r" % \
            spider.name
        logger.info("Spider opened", extra={'spider': spider})
        nextcall = CallLaterOnce(self._next_request, spider)
        scheduler = self.scheduler_cls.from_crawler(self.crawler)
        start_requests = yield self.scraper.spidermw.process_start_requests(start_requests, spider)#先调用spider中间件进行处理
        slot = Slot(start_requests, close_if_idle, nextcall, scheduler)
        self.slot = slot
        self.spider = spider
        yield scheduler.open(spider)#开启调度器
        yield self.scraper.open_spider(spider)
        self.crawler.stats.open_spider(spider)
        yield self.signals.send_catch_log_deferred(signals.spider_opened, spider=spider)
        slot.nextcall.schedule()
        slot.heartbeat.start(5)

    """ 
    当调度器空闲的时候调用（在_next_request中判断）。
    可以被多次调用。
    如果某些extension引起了DontCloseSpider异常（在spider_idle 信号的处理器中），spider就不会关闭，直到下一个循环。
    并且这个方法会保证至少被执行一次
    """
    def _spider_idle(self, spider):
        """Called when a spider gets idle. This function is called when there
        are no remaining pages to download or schedule. It can be called
        multiple times. If some extension raises a DontCloseSpider exception
        (in the spider_idle signal handler) the spider is not closed until the
        next loop and this function is guaranteed to be called (at least) once
        again for this spider.
        """
        res = self.signals.send_catch_log(signal=signals.spider_idle, spider=spider, dont_log=DontCloseSpider)
        if any(isinstance(x, Failure) and isinstance(x.value, DontCloseSpider) for _, x in res):
            return

        if self.spider_is_idle(spider):
            self.close_spider(spider, reason='finished')

    """
    关闭爬虫（引擎）
    发送信息：关闭下载器、使用scrapyer关闭爬虫spider、关闭调度器
        发送关闭日志、关闭scawler关闭爬虫的信息、打印日志、
        重设当前的slot为空、重设当前的spider为空等
    """
    def close_spider(self, spider, reason='cancelled'):
        """Close (cancel) spider and clear all its outstanding requests"""

        slot = self.slot
        if slot.closing:
            return slot.closing
        logger.info("Closing spider (%(reason)s)",
                    {'reason': reason},
                    extra={'spider': spider})

        dfd = slot.close()

        def log_failure(msg):
            def errback(failure):
                logger.error(
                    msg,
                    exc_info=failure_to_exc_info(failure),
                    extra={'spider': spider}
                )
            return errback

        dfd.addBoth(lambda _: self.downloader.close())
        dfd.addErrback(log_failure('Downloader close failure'))

        dfd.addBoth(lambda _: self.scraper.close_spider(spider))
        dfd.addErrback(log_failure('Scraper close failure'))

        dfd.addBoth(lambda _: slot.scheduler.close(reason))
        dfd.addErrback(log_failure('Scheduler close failure'))

        dfd.addBoth(lambda _: self.signals.send_catch_log_deferred(
            signal=signals.spider_closed, spider=spider, reason=reason))
        dfd.addErrback(log_failure('Error while sending spider_close signal'))

        dfd.addBoth(lambda _: self.crawler.stats.close_spider(spider, reason=reason))
        dfd.addErrback(log_failure('Stats close failure'))

        dfd.addBoth(lambda _: logger.info("Spider closed (%(reason)s)",
                                          {'reason': reason},
                                          extra={'spider': spider}))

        dfd.addBoth(lambda _: setattr(self, 'slot', None))
        dfd.addErrback(log_failure('Error while unassigning slot'))

        dfd.addBoth(lambda _: setattr(self, 'spider', None))
        dfd.addErrback(log_failure('Error while unassigning spider'))

        dfd.addBoth(lambda _: self._spider_closed_callback(spider))

        return dfd

    def _close_all_spiders(self):
        dfds = [self.close_spider(s, reason='shutdown') for s in self.open_spiders]
        dlist = defer.DeferredList(dfds)
        return dlist

    @defer.inlineCallbacks
    def _finish_stopping_engine(self):
        yield self.signals.send_catch_log_deferred(signal=signals.engine_stopped)
        self._closewait.callback(None)
