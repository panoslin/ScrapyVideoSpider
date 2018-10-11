# -*- coding: utf-8 -*-
from ..items import *
import time
import json
import html


class XpcSpider(scrapy.Spider):
    name = 'xpc'
    allowed_domains = ['xinpianchang.com', 'openapi-vtom.vmovier.com', 'oss-xpc0.xpccdn.com']

    # # overwrite the __init__ method if necessary
    # def __init__(self, settings, *args, **kwargs):
    #     super(XpcSpider, self).__init__(*args, **kwargs)
    # # define connection r to redis
    # self.r = redis.Redis(host=settings.get('REDIS_HOST'), port=settings.get('REDIS_PORT'),
    #                      db=settings.get('REDIS_DB'), decode_responses=True)
    # self.conn, self.cur = self.GetConnected(settings)

    # `username`(field) for yii2_user table
    def uniqid(self, prefix=''):
        return prefix + hex(int(time.time()))[2:10] + hex(int(time.time() * 1000000) % 0x100000)[2:7]

    def unescape(self, string):
        if string:
            return html.unescape(string)
        else:
            return None

    # # overwrite this method so that we can
    # # access the project settings in __init__()
    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = cls(crawler.settings, *args, **kwargs)
    #     spider._set_crawler(crawler)
    #     return spider

    def start_requests(self):
        for num in range(10269950, 10312922):
        # for num in range(10269950, 10269970):
            url = 'http://www.xinpianchang.com/a{num}?from=ArticleList'.format(num=num)

            yield scrapy.Request(url=url, callback=self.VideoPageParser)

    def VideoPageParser(self, response):
        # skip the page that does not exist
        if '系统提示' in response.text:
            return None

        # extract info from the page if exist
        else:
            # instantiate the video item container
            video_base = yii2_video_base()
            user_files = yii2_user_files()
            crawvideo = CrawVideo()
            crawauthor = CrawAuthor()
            Mark = mark()

            # `vid` is the necessary param to reach the json api for video info
            # store and crawl it in the next step
            Mark['SourceURL'] = response.url
            Mark['vid'] = response.css('*').re_first('vid: "(.*?)"')

            # filling in the item container
            crawvideo['createtime'] = int(time.time())
            crawvideo['updatetime'] = int(time.time())

            crawvideo['broadcasttime'] = time.strftime('%Y%m%d', time.strptime(
                '2018-' + response.css('.update-time i::text').extract_first(), '%Y-%m-%d %M:%S')) if response.css(
                '.update-time i::text') else None  # format time
            crawvideo['tvcbookid'] = None
            crawvideo['infofrom'] = 'XinPianChang'
            crawvideo['crawname'] = 'XPC_a{num}?from=ArticleList'
            crawvideo['broadcastid'] = response.css('*').re_first('vid: "(.*?)"')
            crawvideo['broadcastname'] = self.unescape(response.css('.title-wrap .title::text').extract_first())
            crawvideo['broadcastdesc'] = self.unescape('\n'.join(
                map(lambda x: x.strip(), response.css('.filmplay-info-desc>p::text').extract())))
            crawvideo['videotype'] = ','.join(map(lambda x: x.strip(), response.css('.cate>a::text').extract()))
            crawvideo['views'] = response.css('.play-counts::text').extract_first()
            crawvideo['likes'] = response.css('.like-counts::text').extract_first()

            crawauthor['createtime'] = int(time.time())
            crawauthor['updatetime'] = int(time.time())
            crawauthor['infofrom'] = response.url
            crawauthor['crawname'] = crawvideo['crawname']

            video_base['title'] = crawvideo['broadcastname']
            video_base['introduction'] = crawvideo['broadcastdesc']
            video_base['privacy'] = 13
            video_base['created_at'] = int(time.time())
            video_base['updated_at'] = int(time.time())
            video_base['from_'] = 'Spider_at_XinPianChang'

            user_files['name'] = crawvideo['broadcastname']
            user_files['description'] = crawvideo['broadcastdesc']
            user_files['mime_type'] = 'video'
            user_files['status'] = 13
            user_files['created_at'] = int(time.time())
            user_files['updated_at'] = int(time.time())

            # extract each author into the item container
            for aur in response.css('.filmplay-creator div+.creator-list>li'):
                # instantiate the aythor item container
                user = yii2_user()
                user_profile = yii2_user_profile()
                user_creator = yii2_user_creator()

                Mark['author_page_id'] = aur.css('a::attr(href)').re_first('/u(\d*?)\?')

                crawvideo['broadcastauthorid'] = Mark['author_page_id']
                crawvideo['broadcastauthorname'] = self.unescape(aur.css('.name::text').extract_first())

                crawauthor['broadcastauthorid'] = Mark['author_page_id']
                crawauthor['broadcastauthorname'] = crawvideo['broadcastauthorname']

                user['username'] = self.uniqid('M')
                user['status'] = 13
                user['created_at'] = int(time.time())
                user['updated_at'] = int(time.time())
                user['src'] = 'XinPianChang'

                user_profile['nickname'] = crawvideo['broadcastauthorname']

                user_creator['name'] = crawvideo['broadcastauthorname']
                user_creator['status'] = 13
                user_creator['created_at'] = int(time.time())
                user_creator['updated_at'] = int(time.time())

                break  # break, cause we only need the major author, which can be the first author

            ItemPool = [video_base, user_files, user, user_profile, user_creator, crawvideo, crawauthor]

            next = response.urljoin('/user/intro/id-' + Mark['author_page_id'])
            yield scrapy.Request(url=next, meta={'ItemPool': ItemPool, 'Mark': Mark},
                                 callback=self.AuthorpageParser)

    def AuthorpageParser(self, response):
        Mark = response.meta['Mark']

        Mark['AvatarURL'] = response.css('.avator-wrap-s img::attr(src)').extract_first()

        video_base, user_files, user, user_profile, user_creator, crawvideo, crawauthor = response.meta['ItemPool']

        addr = response.css('.addr .con::text').extract_first()
        Mark['addr'] = addr

        crawvideo['region'] = addr.replace('\xa0', ',') if addr else None

        crawauthor['bio'] = self.unescape(response.css('.about .con::text').extract_first())
        crawauthor['dob'] = response.css('.date .con::text').extract_first().strip() if response.css(
            '.date .con::text') else None
        crawauthor['region'] = crawvideo['region']
        crawauthor['role'] = response.css('.icon-career+span::text').extract_first()
        crawauthor['fans'] = response.css('.fans-counts::text').extract_first()
        crawauthor['follow'] = response.css('.follow-wrap .fw_600 ::text').extract_first()

        if response.css('.sex .con::text').extract_first() == '女':
            user_profile['sex'] = 1
        elif response.css('.sex .con::text').extract_first() == '男':
            user_profile['sex'] = 2
        else:
            user_profile['sex'] = 0
        user_profile['introduction'] = crawauthor['bio']
        user_profile['birthdate'] = crawauthor['dob']

        user_creator['intro'] = crawauthor['bio']

        ItemPool = [video_base, user_files, user, user_profile, user_creator, crawvideo, crawauthor]
        next = 'https://openapi-vtom.vmovier.com/v3/video/{vid}?expand=resource,resource_origin?'.format(
            vid=Mark['vid'])
        yield scrapy.Request(url=next, meta={'ItemPool': ItemPool, 'Mark': Mark}, callback=self.VideoJsonParser)

    def VideoJsonParser(self, response):
        Mark = response.meta['Mark']
        video_base, user_files, user, user_profile, user_creator, crawvideo, crawauthor = response.meta['ItemPool']
        result = json.loads(response.text)

        Mark['VideoURL'] = result['data']['resource']['default']['url']

        crawvideo['duration'] = round(result['data']['resource']['default']['duration'] / 1000)
        crawvideo['vertical'] = int(
            int(result['data']['resource']['default']['width']) < int(result['data']['resource']['default']['height']))

        video_base['vertical'] = crawvideo['vertical']

        user_files['size'] = result['data']['resource']['default']['filesize']

        yield {'video_base': video_base, 'user_files': user_files, 'user': user, 'user_profile': user_profile,
               'user_creator': user_creator, 'crawvideo': crawvideo, 'crawauthor': crawauthor, 'Mark': Mark}
