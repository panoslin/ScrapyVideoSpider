#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2018/10/10
# IDE: PyCharm
import redis
import mysql.connector
import configparser
import os
from pprint import pprint


class Database:
    def __init__(self, config):
        self.config = config
        self.conn, self.conn_local, self.cur, self.cur_local = self.GetConnected()

    def GetConnected(self):
        # Construct MySQL connect
        # online DB config
        database = self.config.get("mysql", "database")
        user_name = self.config.get("mysql", "user_name")
        password = self.config.get("mysql", "password")
        host = self.config.get("mysql", "host")
        port = self.config.get("mysql", "port")

        # local DB config
        database_local = self.config.get("mysql", "database_local")
        user_name_local = self.config.get("mysql", "user_name_local")
        password_local = self.config.get("mysql", "password_local")
        host_local = self.config.get("mysql", "host_local")
        port_local = self.config.get("mysql", "port_local")

        conn = mysql.connector.connect(user=user_name, password=password, host=host, port=port, database=database)
        cur = conn.cursor()

        conn_local = mysql.connector.connect(user=user_name_local, password=password_local, host=host_local,
                                             port=port_local, database=database_local)
        cur_local = conn_local.cursor()

        return conn, conn_local, cur, cur_local

    # Get regional infos from mysql database yii2_location
    def GetLocation(self, addr):
        country = 1
        province = 0
        city = 0
        area = ''
        if addr is None:
            return country, province, city, area
        elif addr == '海外':
            country = 0
            area = '海外'
        elif addr == '台湾':
            country = 1
            province = 272
        elif addr == '香港':
            country = 1
            province = 273
        elif addr == '澳门':
            country = 1
            province = 274
        else:
            addrs = addr.split('\xa0')
            for s in addrs:
                if s[-1:] == '市':
                    s = s[0:-1]
                    sqlSELECT = "SELECT id FROM yii2_location WHERE name_chs LIKE %(s)s"
                    D = {
                        's': '%{s}%'.format(s=s)
                    }
                    self.cur.execute(sqlSELECT, D)
                    results = self.cur.fetchall()
                    if len(results) != 0:
                        city = results[0][0]
                elif s[-1:] == '区':
                    area = s
                else:
                    sqlSELECT = "SELECT id FROM yii2_location WHERE name_chs LIKE %(s)s"
                    D = {
                        's': '%{s}%'.format(s=s)
                    }
                    self.cur.execute(sqlSELECT, D)
                    results = self.cur.fetchall()
                    if len(results) != 0:
                        province = results[0][0]
        return country, province, city, area

    def CreateUserDB(self, data):
        """
        insert into 3 table, which are yii2_user, yii2_user_profile and yii2_user_creator
        :return: user_id
        """
        tables = ['yii2_user', 'yii2_user_profile', 'yii2_user_creator']

        # get regional infos and match with corresponding id in the mysql database
        addr = data['Mark']['addr']
        country, province, city, area = self.GetLocation(addr)

        # D: data, ES: execution statement
        # insertion into yii2_user
        D1 = {
            'username': data['user']['username'],
            'status': data['user']['status'],
            'created_at': data['user']['created_at'],
            'updated_at': data['user']['updated_at'],
            'src': data['user']['src'],
        }
        ES1 = (
            "INSERT INTO {table} ( `username`, `status`, `created_at`, `updated_at`, `src`) "
            "VALUES ( %(username)s, %(status)s, %(created_at)s, %(updated_at)s, %(src)s );".format(table=tables[0]))
        self.cur.execute(ES1, D1)
        user_id = self.cur.lastrowid  # get the id of the insertion column

        # insertion into yii2_user_profile
        D2 = {
            'user_id': user_id,
            'nickname': data['user_profile']['nickname'],
            'sex': data['user_profile']['sex'],
            'avatar': data['user_profile']['avatar'],
            'location_id': city,
            'introduction': data['user_profile']['introduction'],
            'birthdate': data['user_profile']['birthdate'],
            'country': country,
            'province': province,
            'city': city,
            'area': area,
        }
        ES2 = (
            "INSERT INTO {table} ( `user_id`, `nickname`, `sex`, `avatar`, "
            "`location_id`, `introduction`, `birthdate`, `country`, "
            "`province`, `city`, `area`) "
            "VALUES ( %(user_id)s, %(nickname)s, %(sex)s, %(avatar)s, "
            "%(location_id)s, %(introduction)s, %(birthdate)s, %(country)s, "
            "%(province)s, %(city)s, %(area)s);".format(table=tables[1]))
        self.cur.execute(ES2, D2)

        # insertion into yii2_user_creator
        D3 = {
            'user_id': user_id,
            'name': data['user_creator']['name'],
            'intro': data['user_creator']['intro'],
            'location_id': city,
            'status': data['user_creator']['status'],
            'created_at': data['user_creator']['created_at'],
            'updated_at': data['user_creator']['updated_at'],
            'avatar': data['user_profile']['avatar'],
            'country_id': country,
            'state_id': province,
            'city_id': city,
        }
        ES3 = (
            "INSERT INTO {table} ( `user_id`, `name`, `intro`, `location_id`, "
            "`status`, `created_at`, `updated_at`, `avatar`, `country_id`, "
            "`state_id`, `city_id`) "
            "VALUES ( %(user_id)s, %(name)s, %(intro)s, %(location_id)s, "
            "%(status)s, %(created_at)s, %(updated_at)s, %(avatar)s, %(country_id)s, "
            "%(state_id)s, %(city_id)s);".format(table=tables[2]))
        self.cur.execute(ES3, D3)

        return user_id

    def InsertOnline(self, data, user_id):
        """
        insert into 2 tables yii2_video_base, yii2_user_files
        :return:video_id
        """
        tables = ['yii2_video_base', 'yii2_user_files']

        # insertion into yii2_video_base
        D1 = {
            'title': data['video_base']['title'],
            'introduction': data['video_base']['introduction'],
            'privacy': data['video_base']['privacy'],
            'created_at': data['video_base']['created_at'],
            'updated_at': data['video_base']['updated_at'],
            'from': data['video_base']['from_'],
            'user_id': user_id,
            'vertical': data['video_base']['vertical'],
        }
        ES1 = (
            "INSERT INTO {table} ( `title`, `introduction`, `privacy`, `created_at`, `updated_at`, "
            "`from`, `user_id`, `vertical`) "
            "VALUES "
            "( %(title)s, %(introduction)s, %(privacy)s, %(created_at)s, %(updated_at)s, "
            "%(from)s, %(user_id)s, %(vertical)s);".format(table=tables[0]))

        self.cur.execute(ES1, D1)
        video_id = self.cur.lastrowid

        # insertion into yii2_user_files

        D2 = {
            'user_id': user_id,
            'object': data['user_files']['object'],
            'name': data['user_files']['name'],
            'size': data['user_files']['size'],
            'description': data['user_files']['description'],
            'mime_type': data['user_files']['mime_type'],
            'mime_id': video_id,
            'status': data['user_files']['status'],
            'created_at': data['user_files']['created_at'],
            'updated_at': data['user_files']['updated_at'],
        }
        ES2 = (
            "INSERT INTO {table} ( `user_id`, `object`, `name`, `size`, "
            "`description`, `mime_type`, `mime_id`, `status`, "
            "`created_at`, `updated_at`) "
            "VALUES "
            "( %(user_id)s, %(object)s, %(name)s, %(size)s, "
            "%(description)s, %(mime_type)s, %(mime_id)s, %(status)s, "
            "%(created_at)s, %(updated_at)s);".format(table=tables[1]))
        self.cur.execute(ES2, D2)

        return video_id

    def InsertLocal(self, data, user_id, video_id):
        """
        insert into 2 tables crawvideo, crawauthor
        """
        tables = ['crawvideo', 'crawauthor']

        # insertion into crawvideo
        D1 = {
            'createtime': data['crawvideo']['createtime'],
            'updatetime': data['crawvideo']['updatetime'],
            # 'broadcasttime': data['crawvideo']['broadcasttime'],
            'broadcasttime': None,
            'tvcbookid': video_id,
            'infofrom': data['crawvideo']['infofrom'],
            'crawname': data['crawvideo']['crawname'],
            'broadcastid': data['crawvideo']['broadcastid'],
            'broadcastname': data['crawvideo']['broadcastname'],
            'broadcastdesc': data['crawvideo']['broadcastdesc'],
            'broadcastauthorid': data['crawvideo']['broadcastauthorid'],
            'broadcastauthorname': data['crawvideo']['broadcastauthorname'],
            'region': data['crawvideo']['region'],
            'views': data['crawvideo']['views'],
            'likes': data['crawvideo']['likes'],
            'duration': data['crawvideo']['duration'],
            'vertical': data['crawvideo']['vertical'],
        }
        ES1 = (
            "INSERT INTO {table} ( `createtime`, `updatetime`, `broadcasttime`, `tvcbookid`, "
            "`infofrom`, `crawname`, `broadcastid`, `broadcastname`, `broadcastdesc`, "
            "`broadcastauthorid`, `broadcastauthorname`, `region`, `views`, `likes`, "
            "`duration`, `vertical`) "
            "VALUES "
            "( %(createtime)s, %(updatetime)s, %(broadcasttime)s, %(tvcbookid)s, "
            "%(infofrom)s, %(crawname)s, %(broadcastid)s, %(broadcastname)s, %(broadcastdesc)s, "
            "%(broadcastauthorid)s, %(broadcastauthorname)s, %(region)s, %(views)s, %(likes)s, "
            "%(duration)s, %(vertical)s);".format(table=tables[0])
        )
        self.cur_local.execute(ES1, D1)

        # insertion into crawauthor
        D2 = {
            'createtime': data['crawauthor']['createtime'],
            'updatetime': data['crawauthor']['updatetime'],
            'tvcbookauthorid': user_id,
            'infofrom': data['crawauthor']['infofrom'],
            'crawname': data['crawauthor']['crawname'],
            'broadcastauthorid': data['crawauthor']['broadcastauthorid'],
            'broadcastauthorname': data['crawauthor']['broadcastauthorname'],
            'bio': data['crawauthor']['bio'],
            'dob': data['crawauthor']['dob'],
            'region': data['crawauthor']['region'],
            'role': data['crawauthor']['role'],
            'fans': data['crawauthor']['fans'],
            'follow': data['crawauthor']['follow'],
        }
        ES2 = (
            "INSERT INTO {table} ( `createtime`, `updatetime`, `tvcbookauthorid`, `infofrom`, "
            "`crawname`, `broadcastauthorid`, `broadcastauthorname`, `bio`, `dob`, `region`, "
            "`role`, `fans`, `follow`) "
            "VALUES "
            "( %(createtime)s, %(updatetime)s, %(tvcbookauthorid)s, %(infofrom)s, "
            "%(crawname)s, %(broadcastauthorid)s, %(broadcastauthorname)s, %(bio)s, %(dob)s, %(region)s, "
            "%(role)s, %(fans)s, %(follow)s);".format(table=tables[1]))

        self.cur_local.execute(ES2, D2)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(
        os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'Config.ini'))
    # connection to redis and mysql database
    Pump_In=config.get('pump', 'DOWNLOADED_PIPE')
    host = config.get("redis", "host")
    port = config.getint("redis", "port")
    db = config.getint("redis", "db")
    r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    total = r.scard(Pump_In)

    database = Database(config)
    try:
        for n, i in enumerate(r.smembers(Pump_In)):
            print('Processing {n}/{total}...'.format(n=n,total=total))
            data = eval(i)
            # pprint(data)
            user_id = database.CreateUserDB(data)
            # print(user_id)
            video_id = database.InsertOnline(data, user_id)
            # print(video_id)
            database.InsertLocal(data, user_id, video_id)
            # break
    except Exception as e:
        print('Exception raised: {e}'.format(e=e))
        # rollback all operations if error exists
        database.conn.rollback()
        database.cur.close()
        database.conn.close()
        database.conn_local.rollback()
        database.cur_local.close()
        database.conn_local.close()

    print('Finshed!')

    # # commit the operations if all pass
    # database.conn.commit()
    # database.cur.close()
    # database.conn.close()
    # database.conn_local.commit()
    # database.cur_local.close()
    # database.conn_local.close()
