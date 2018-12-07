"""
Downloader Middleware manager

See documentation in docs/topics/downloader-middleware.rst
"""
import six

from twisted.internet import defer

from scrapy import Request, Response
from scrapy.middleware import MiddlewareManager
from scrapy.utils.defer import mustbe_deferred
from scrapy.utils.conf import build_component_list


class DownloaderMiddlewareManager(MiddlewareManager):

    component_name = 'downloader middleware'

    """
    从   settings.py或这custom_setting中拿到自定义的Middleware中间件
    """
    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(
            settings.getwithbase('DOWNLOADER_MIDDLEWARES'))

    """
    每个下载中间件都可以重写这几个方法,所以在这里将对应的中间件的相关方法抽取出来
    process_request:处理request
    process_response:处理response
    process_exception:处理异常
    """
    def _add_middleware(self, mw):
        if hasattr(mw, 'process_request'):
            self.methods['process_request'].append(mw.process_request)
        if hasattr(mw, 'process_response'):
            self.methods['process_response'].insert(0, mw.process_response)
        if hasattr(mw, 'process_exception'):
            self.methods['process_exception'].insert(0, mw.process_exception)

    """
    下载中间件的下载方法
    """
    def download(self, download_func, request, spider):
        """
        因为都是异步的进行处理,所以都使用@defer.inlineCallbacks来将其转换成异步方法调用
        """


        """
        针对之前根据用户配置的中间件的设置,以此调用各个中间件所设置的相关方法,
        在各个方法都调用完毕之后,才会将其真正的交给scrapy的下载器去进行下载
        """
        @defer.inlineCallbacks
        def process_request(request):
            for method in self.methods['process_request']:
                response = yield method(request=request, spider=spider)
                assert response is None or isinstance(response, (Response, Request)), \
                        'Middleware %s.process_request must return None, Response or Request, got %s' % \
                        (six.get_method_self(method).__class__.__name__, response.__class__.__name__)
                if response:#重要:::若某个中间件返回的结果是response,就直接返回,步子啊进行后续的处理啦
                    defer.returnValue(response)
            defer.returnValue((yield download_func(request=request,spider=spider)))


        """
        道理同process_request
        """
        @defer.inlineCallbacks
        def process_response(response):
            assert response is not None, 'Received None in process_response'
            if isinstance(response, Request):
                defer.returnValue(response)

            for method in self.methods['process_response']:
                response = yield method(request=request, response=response,
                                        spider=spider)
                assert isinstance(response, (Response, Request)), \
                    'Middleware %s.process_response must return Response or Request, got %s' % \
                    (six.get_method_self(method).__class__.__name__, type(response))
                if isinstance(response, Request):
                    defer.returnValue(response)
            defer.returnValue(response)

        """
        道理同process_request
        """
        @defer.inlineCallbacks
        def process_exception(_failure):
            exception = _failure.value
            for method in self.methods['process_exception']:
                response = yield method(request=request, exception=exception,
                                        spider=spider)
                assert response is None or isinstance(response, (Response, Request)), \
                    'Middleware %s.process_exception must return None, Response or Request, got %s' % \
                    (six.get_method_self(method).__class__.__name__, type(response))
                if response:
                    defer.returnValue(response)
            defer.returnValue(_failure)


        """
        将相关的中间处理设置好后,异步执行之
        """
        deferred = mustbe_deferred(process_request, request)
        deferred.addErrback(process_exception)
        deferred.addCallback(process_response)
        return deferred
