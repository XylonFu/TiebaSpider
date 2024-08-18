import time

from scrapy import signals
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.response import response_status_message
from twisted.internet.error import TCPTimedOutError, ConnectionRefusedError, ConnectionDone, TimeoutError

from tieba.proxies import ProxyManager


class CustomProxyMiddleware:
    def __init__(self, settings):
        self.proxy_manager = ProxyManager(settings)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info(f'Spider opened: {spider.name}')

    def process_request(self, request, spider):
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            if 'original_url' not in request.meta:
                request.meta['original_url'] = request.url
            request.meta['proxy'] = f'http://{proxy}'
            original_url = request.meta.get('original_url', request.url)
            spider.logger.info(f'Using proxy: {proxy} for request: {original_url}')

    def process_response(self, request, response, spider):
        captcha_indicators = ['百度安全验证']
        if any(indicator in response.text.lower() for indicator in captcha_indicators):
            reason = 'captcha found in page content'
            spider.logger.debug(f'{reason}, changing proxy and retrying: {request.url}')
            return self.retry_request(request, reason, spider)

        if response.status != 200:
            reason = response_status_message(response.status)
            spider.logger.debug(f'Response status not 200, actually {response.status}: {request.url}')
            return self.retry_request(request, reason, spider)

        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception,
                      (ConnectionRefusedError, TCPTimedOutError, TunnelError, HttpError, ConnectionDone, TimeoutError)):
            reason = f'exception: {exception}'
            spider.logger.debug(
                f'Timeout or connection error, retrying {request.url} with a new proxy because of {reason}')
            return self.retry_request(request, reason, spider)

    def retry_request(self, request, reason, spider):
        current_time = time.time()
        original_url = request.meta.get('original_url', request.url)

        if current_time - self.proxy_manager.last_retry_time > self.proxy_manager.update_threshold:
            self.proxy_manager.get_new_proxy(force=True)
            current_proxy = self.proxy_manager.current_proxy
            spider.logger.warning(f'Using new proxy {current_proxy} to retry {original_url} because of {reason}')
        else:
            current_proxy = self.proxy_manager.current_proxy
            spider.logger.warning(f'Using current proxy {current_proxy} to retry {original_url} because of {reason}')

        new_request = request.replace(url=original_url, dont_filter=True)
        new_request.meta['proxy'] = f'http://{current_proxy}'
        return new_request
