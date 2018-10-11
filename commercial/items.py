# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
"""
the order to insert the mysql table is :
yii2_user -->user_id
avatar-->  yii2_user_profile
yii2_user_creator

user_id-->  yii2_video_base -->mime_id
object-->  yii2_user_files
"""
import scrapy


class CrawVideo(scrapy.Item):
    createtime = scrapy.Field()
    updatetime = scrapy.Field()
    broadcasttime = scrapy.Field()
    tvcbookid = scrapy.Field()
    infofrom = scrapy.Field()
    crawname = scrapy.Field()
    broadcastid = scrapy.Field()
    broadcastname = scrapy.Field()
    broadcastname2 = scrapy.Field()
    broadcastdesc = scrapy.Field()
    license = scrapy.Field()
    broadcastauthorid = scrapy.Field()
    broadcastauthorname = scrapy.Field()
    industry = scrapy.Field()
    videotype = scrapy.Field()
    language = scrapy.Field()
    region = scrapy.Field()
    brand = scrapy.Field()
    agency = scrapy.Field()
    tags = scrapy.Field()
    views = scrapy.Field()
    likes = scrapy.Field()
    comments = scrapy.Field()
    favourated = scrapy.Field()
    shared = scrapy.Field()
    rated = scrapy.Field()
    award = scrapy.Field()
    duration = scrapy.Field()
    vertical = scrapy.Field()
    credits = scrapy.Field()


class CrawAuthor(scrapy.Item):
    createtime = scrapy.Field()
    updatetime = scrapy.Field()
    tvcbookauthorid = scrapy.Field()
    broadcastregtime = scrapy.Field()
    infofrom = scrapy.Field()
    crawname = scrapy.Field()
    broadcastauthorid = scrapy.Field()
    broadcastauthorname = scrapy.Field()
    marktype = scrapy.Field()
    bio = scrapy.Field()
    dob = scrapy.Field()
    mobile = scrapy.Field()
    email = scrapy.Field()
    wechat = scrapy.Field()
    others = scrapy.Field()
    region = scrapy.Field()
    role = scrapy.Field()
    views = scrapy.Field()
    fans = scrapy.Field()
    likeother = scrapy.Field()
    liked = scrapy.Field()
    follow = scrapy.Field()
    videocount = scrapy.Field()


class yii2_video_base(scrapy.Item):
    title = scrapy.Field()
    introduction = scrapy.Field()
    privacy = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    from_ = scrapy.Field()
    user_id = scrapy.Field()
    vertical = scrapy.Field()


class yii2_user_files(scrapy.Item):
    user_id = scrapy.Field()
    object = scrapy.Field()
    name = scrapy.Field()
    size = scrapy.Field()
    description = scrapy.Field()
    mime_type = scrapy.Field()
    mime_id = scrapy.Field()
    status = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()


class yii2_user(scrapy.Item):
    username = scrapy.Field()
    status = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    src = scrapy.Field()


class yii2_user_profile(scrapy.Item):
    user_id = scrapy.Field()
    realname = scrapy.Field()
    nickname = scrapy.Field()
    sex = scrapy.Field()
    avatar = scrapy.Field()
    hometown_id = scrapy.Field()
    location_id = scrapy.Field()
    introduction = scrapy.Field()
    address = scrapy.Field()
    birthdate = scrapy.Field()
    country = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    area = scrapy.Field()


class yii2_user_creator(scrapy.Item):
    user_id = scrapy.Field()
    name = scrapy.Field()
    intro = scrapy.Field()
    tags = scrapy.Field()
    location_id = scrapy.Field()
    status = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    avatar = scrapy.Field()
    country_id = scrapy.Field()
    state_id = scrapy.Field()
    city_id = scrapy.Field()


class mark(scrapy.Item):
    SourceURL = scrapy.Field()
    vid = scrapy.Field()
    author_page_id = scrapy.Field()
    AvatarURL = scrapy.Field()
    VideoURL = scrapy.Field()
    addr = scrapy.Field()
