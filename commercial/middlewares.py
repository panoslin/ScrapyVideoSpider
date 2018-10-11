# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from random import choice
import redis


class RandomHeadersMiddleware:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
            'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1'
        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = choice(self.user_agents)


class StoreBadResponseMiddleware:
    def __init__(self, settings):
        # Connection to redis
        self.r = redis.Redis(host=settings.get('REDIS_HOST'), port=settings.get('REDIS_PORT'),
                             db=settings.get('REDIS_DB'), decode_responses=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        # store the page that fail to reach
        if response.status != 200:
            self.r.sadd(spider.settings.get('BAD_REQUESTS'), response.url)
        return response
