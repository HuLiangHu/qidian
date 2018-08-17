from builtins import object
# -*- coding: utf-8 -*-

# Define your item pipelines here

# import ujson
import datetime as dt
import sys
import traceback
import base64
from builtins import bytes, str

from datetime import datetime
from hashlib import md5
from scrapy.exceptions import DropItem
from crawling.items import SpiderNovelItem
from twisted.enterprise import adbapi
import logging


class MySqlPipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool
        logging.debug("setup MySql Pipeline")
    
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
            cp_reconnect = True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)
        
    def process_item(self,item,spider): 
        # item['appid'] = spider.appid
        # item['crawlid'] = spider.crawlid
        # run db query in the thread pool
        logging.debug("Processing item in MySqlPipeline")
        if isinstance(item, SpiderNovelItem):
            d = self.dbpool.runInteraction(self._do_novel_upsert, item, spider)
        
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d
    def _do_novel_upsert(self, conn, item, spider):

        # now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        try:
            if item['current_date']:
                now = item['current_date']
            else:
                now = datetime.today()
            if 'pubtime' not in item.keys():
                item['pubtime'] = None
            conn.execute("""
                        replace INTO `rawdata`
                                    (`name`,
                                    `url`,
                                    `author`,
                                    `category`,
                                    `page_view`,
                                    `word_count`,
                                    `description`,
                                    `points`,
                                    `yuepiao`,
                                    `shoucang`,
                                    `comment_count`,
                                    `review_count`,
                                    `redpack`,
                                    `yuepiaoorder`,
                                    `flower`,
                                    `diamondnum`,
                                    `coffeenum`,
                                    `eggnum`,
                                    `redpackorder`,
                                    `isvip`,
                                    `status`,
                                    `imageurl`,
                                    `banquan`,
                                    `biaoqian`,
                                    `haopingzhishu`,
                                    `total_recommend`,
                                    `totalrenqi`,
                                    `pubtime`,
                                    `lastupdate`,
                                    `crawldate`,
                                    `hongbao`,
                                    `vipvote`,
                                    `printmark`,
                                    `site`)
                                    VALUES
                                    (%s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s)
                    """, (
                item['name'], item['url'], item['author'], item['category'], item['page_view'], item['word_count'],
                item['description'], item['points'], item['yuepiao'], item['shoucang'], item['comment_count'],
                item['review_count'],item['redpack'], item['yuepiaoorder'], item['flower'], item['diamondnum'],
                item['coffeenum'], item['eggnum'], item['redpackorder'], item['isvip'], item['status'], item['image'],
                item['banquan'], item['biaoqian'], item['haopingzhishu'], item['total_recommend'], item['totalrenqi'],
                item['pubtime'], item['lastupdate'], now, item['hongbao'], item['vipvote'], item['printmark'],item['site']))
            #result = conn.fetchall()
        except Exception as e:
            logging.error("Insert item to Mysql faild.")
            logging.error('$$'*100)
            print(e)
