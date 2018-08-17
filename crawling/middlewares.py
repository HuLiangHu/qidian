# -*- coding: utf-8 -*-

import random

class RandomUserAgent(object):
    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        # 从settings中加载USER_AGENT的值
        return cls(
            user_agent=crawler.settings.getlist('USER_AGENT')
        )

    def process_request(self, request, spider):
        # 在process_request中设置User-Agent的值
        request.headers.setdefault('User-Agent', random.choice(self.user_agent))

class RandomProxy(object):

    def __init__(self, iplist):
        self.iplist = iplist

    @classmethod
    def from_crawler(cls, crawler):
        # 在settings中加载IPLIST的值
        return cls(
            iplist=crawler.settings.getlist('IPLIST')
        )

    def process_request(self, request, spider):
        # 在请求上添加代理
        proxy = random.choice(self.iplist)
        print('代理ip:',proxy)
