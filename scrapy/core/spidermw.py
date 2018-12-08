"""
Spider Middleware manager

See documentation in docs/topics/spider-middleware.rst
"""
import six
from twisted.python.failure import Failure
from scrapy.middleware import MiddlewareManager
from scrapy.utils.defer import mustbe_deferred
from scrapy.utils.conf import build_component_list

def _isiterable(possible_iterator):
    return hasattr(possible_iterator, '__iter__')
"""
控制全部的spider中间件,
"""
class SpiderMiddlewareManager(MiddlewareManager):

    component_name = 'spider middleware'

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(settings.getwithbase('SPIDER_MIDDLEWARES'))

    """
    先通过在总的中间件管理器添加中间件:调用父类的_add_middleware
    每个spider中间件可以重写4个方法,本spiderMiddlewareManager可以对它们进行管理
    process_spider_input:对spiderd的输入进行处理
    process_spider_output::对spider的输出进行处理
    process_spider_exception:对spider的异常进行处理
    process_start_requests:对最开始的request请求进行处理
    """
    def _add_middleware(self, mw):
        super(SpiderMiddlewareManager, self)._add_middleware(mw)
        if hasattr(mw, 'process_spider_input'):
            self.methods['process_spider_input'].append(mw.process_spider_input)
        if hasattr(mw, 'process_spider_output'):
            self.methods['process_spider_output'].insert(0, mw.process_spider_output)
        if hasattr(mw, 'process_spider_exception'):
            self.methods['process_spider_exception'].insert(0, mw.process_spider_exception)
        if hasattr(mw, 'process_start_requests'):
            self.methods['process_start_requests'].insert(0, mw.process_start_requests)

    """
    scrape_response首先依次调用中间件的process_spider_input，然后调用传递进来的scrap_func，也就是call_spider方法，
    如果某个中间件的'process_spider_input'方法抛出了异常，则以Failure调用call_spider方法。
    如果所有中间件都处理成功，且call_spider也返回成功，则调用'process_spider_output'方法，
    这个方法依次调用中间件的'process_spider_output'方法。
    """
    def scrape_response(self, scrape_func, response, request, spider):
        fname = lambda f:'%s.%s' % (
                six.get_method_self(f).__class__.__name__,
                six.get_method_function(f).__name__)

        def process_spider_input(response):
            for method in self.methods['process_spider_input']:
                try:
                    result = method(response=response, spider=spider)
                    assert result is None, \
                            'Middleware %s must returns None or ' \
                            'raise an exception, got %s ' \
                            % (fname(method), type(result))
                except:
                    return scrape_func(Failure(), request, spider)
            return scrape_func(response, request, spider)

        def process_spider_exception(_failure):
            exception = _failure.value
            for method in self.methods['process_spider_exception']:
                result = method(response=response, exception=exception, spider=spider)
                assert result is None or _isiterable(result), \
                    'Middleware %s must returns None, or an iterable object, got %s ' % \
                    (fname(method), type(result))
                if result is not None:
                    return result
            return _failure

        def process_spider_output(result):
            for method in self.methods['process_spider_output']:
                result = method(response=response, result=result, spider=spider)
                assert _isiterable(result), \
                    'Middleware %s must returns an iterable object, got %s ' % \
                    (fname(method), type(result))
            return result

        dfd = mustbe_deferred(process_spider_input, response)
        dfd.addErrback(process_spider_exception)
        dfd.addCallback(process_spider_output)
        return dfd

    def process_start_requests(self, start_requests, spider):
        return self._process_chain('process_start_requests', start_requests, spider)
