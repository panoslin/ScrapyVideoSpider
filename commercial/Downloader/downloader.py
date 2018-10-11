#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2018/10/9
# IDE: PyCharm
"""
configuration:
[date]: db_in_date
[video]: Thread
[pump]:
SCRAPED_PIPE
DOWNLOADED_PIPE
"""
import requests
from random import choice
import redis
import os
import configparser
import uuid
import threading
from queue import Queue


class DownloadThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.lock = threading.Lock()

    def run(self):
        while True:
            data = self.queue.get()
            self.DownloadVideo(data)
            self.queue.task_done()

    def RandomHeaders(self):
        headers = choice(
            [
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }, {
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
            }]
        )
        return headers

    def DownloadVideo(self, data):
        VideoURL = data['Mark']['VideoURL']
        url = VideoURL
        print("Downloading video {url}".format(url=url.strip('\n')))
        FileName = str(uuid.uuid1()) + '.' + url.split('.')[-1]
        PathFile = os.path.join('Download', 'video', FileName)
        try:
            response = requests.get(url, headers=self.RandomHeaders())
            with open(PathFile, 'wb') as video:
                video.write(response.content)
        except Exception as e:
            print("Connection error {e} occors...".format(e=e))
            return

        Y, m, d = config.get("date", "db_in_date").split('/')
        data['user_files']['object'] = os.path.join('daq', Y, m, d, FileName).replace('\\', '/')
        self.DownloadAvatar(data)

    def DownloadAvatar(self, data):
        AvatarURL = data['Mark']['AvatarURL']
        url = AvatarURL
        print("Downloading avatar {url}".format(url=url.strip('\n')))
        FileName = str(uuid.uuid1()) + '.' + url.split('@')[0].split('.')[-1]
        PathFile = os.path.join('Download', 'avatar', FileName)

        try:
            response = requests.get(url, headers=self.RandomHeaders())
            with open(PathFile, 'wb') as avatar:
                avatar.write(response.content)
        except Exception as e:
            print("Connection error {e} occors...".format(e=e))
            return

        prefix = 'https://image.tvcbook.com/default/avatar/'
        Y, m, d = config.get("date", "db_in_date").split('/')
        avatar_ = os.path.join(prefix, Y, m + d, FileName).replace('\\', '/')
        data['user_profile']['avatar'] = avatar_
        data['user_creator']['avatar'] = avatar_

        r.sadd(PumpOut, data)


class Downloader:
    def __init__(self):

        self.THREAD = config.getint("download", "THREAD")
        self.queueLock = threading.Lock()
        self.workQueue = Queue(30)  # set up a queue with an upper bound of items up to 30

        PathDownload = "Download"
        if not os.path.exists(os.path.join(PathDownload, 'video')):
            os.makedirs(os.path.join(PathDownload, 'video'))
        if not os.path.exists(os.path.join(PathDownload, 'avatar')):
            os.makedirs(os.path.join(PathDownload, 'avatar'))

    def GenerateThread(self):
        for tName in range(self.THREAD):
            thread = DownloadThread(self.workQueue)
            thread.daemon = True
            thread.start()

    def run(self):
        self.GenerateThread()
        for i in r.hgetall(PumpIn).values():
            data = eval(i)
            self.workQueue.put(data)

        self.workQueue.join()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    cur_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    config.read(os.path.join(cur_path, "Config.ini"))
    host = config.get("redis", "host")
    port = config.getint("redis", "port")
    db = config.getint("redis", "db")
    r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    PumpIn = config.get("pump", "SCRAPED_PIPE")
    PumpOut = config.get("pump", "DOWNLOADED_PIPE")
    downloader = Downloader()
    try:
        downloader.run()
    except Exception as e:
        print('Exception raised {e}'.format(e=e))
