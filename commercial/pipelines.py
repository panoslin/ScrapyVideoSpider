# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""

"""
import redis


class CommercialPipeline(object):
    def process_item(self, item, spider):
        r = redis.Redis(host=spider.settings.get('REDIS_HOST'), port=spider.settings.get('REDIS_PORT'),
                        db=spider.settings.get('REDIS_DB'), decode_responses=True)
        r.hset(spider.settings.get('SCRAPED_PIPE'),item['Mark']['SourceURL'] ,item)
        return item
