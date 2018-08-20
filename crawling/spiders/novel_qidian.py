# -*- coding: utf-8 -*-
import json
import re
import requests
import scrapy
import os
import time
from fontTools.ttLib import TTFont
from scrapy.http.cookies import CookieJar
from urllib.parse import urlencode

from novelspiders.crawling.items import SpiderNovelItem


class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['qidian.com']
    start_urls = ['https://book.qidian.com/']
    custom_setting = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'e1=%7B%22pid%22%3A%22qd_P_xiangqing%22%2C%22eid%22%3A%22qd_A64%22%2C%22l1%22%3A40%7D; e2=%7B%22pid%22%3A%22qd_P_xiangqing%22%2C%22eid%22%3A%22qd_A64%22%2C%22l1%22%3A40%7D; _csrfToken=alJEyea6iYGVeIYTnZnqw0mEIt0rKtoOFatcrwHd; e2=%7B%22pid%22%3A%22qd_p_qidian%22%2C%22eid%22%3A%22qd_A117%22%2C%22l2%22%3A2%2C%22l1%22%3A11%7D; newstatisticUUID=1534405375_413661442; e1=%7B%22pid%22%3A%22qd_P_Searchresult%22%2C%22eid%22%3A%22qd_S05%22%2C%22l1%22%3A3%7D',
        'Host': 'book.qidian.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    def __init__(self):
        self.max_page = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        self.num_map = {'period': '.', 'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
                        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'}

    def start_requests(self):

        baseurl = 'https://www.qidian.com/rank/yuepiao?style=1&page={}'
        urllist =[]
        for page in range(1, 26):
            url = baseurl.format(page)
            # urllist.append(url)
            # for url in urllist:
            yield scrapy.Request(url,dont_filter=True)

    def parse(self, response):

        bookurllist = response.xpath('//div[@class="book-mid-info"]/h4/a/@href').extract()
        yuepiao = response.xpath('//*[@id="rank-view-list"]/div/ul/li/div[3]/div/p/span/span').extract()
        yuepiaoorder = response.xpath('//span[starts-with(@class,"rank-tag no")]/text()').extract()
        lastupdate = response.xpath('//*[@id="rank-view-list"]/div/ul/li/div[2]/p[3]/span/text()').extract()
        for i, bookurl in enumerate(bookurllist):
            bookurl = 'https:' + bookurl
            yield scrapy.Request(bookurl, meta={'yuepiao': yuepiao[i], 'yuepiaoorder': yuepiaoorder[i],
                                                'lastupdate': lastupdate[i], 'bookurl': bookurl, 'cookiejar': 1},
                                 callback=self.detail_parse)

    def detail_parse(self, response):
        # 获得cookie值，拿到Token
        # Cookie = response.headers.getlist('Set-Cookie')[0].decode()  # 查看一下响应Cookie，也就是第一次访问注册页面时后台写入浏览器的Cookie
        # cookies =Cookie.split(';')
        # #print(cookies)
        # cookies = (cookie.split('=', 1) for cookie in cookies)
        # cookie = dict(cookies)
        # _csrfToken =cookie['_csrfToken']

        font = None
        font_file = response.xpath('/html/body/div[2]/div[6]/div[1]/div[2]/p[3]').re_first(
            r'qidian\.gtimg\.com\/qd_anti_spider\/(\w+\.woff)')
        # print(font_file)
        if font_file:
            font = self.create_font(font_file)
        item = {}
        try:
            item['name'] = response.xpath('//div[@class="book-info "]/h1/em/text()').extract_first()
            item['author'] = response.xpath('//div[@class="book-info "]/h1/span/a/text()').extract_first()
            # item['grade'] =response.xpath('//h4[@id="j_bookScore"]/text()').extract_first()

            yuepiao = response.meta['yuepiao']
            yuepiao = self.modify_data(yuepiao, font)
            # print(yuepiao)
            item['yuepiao'] = re.search('\d+', yuepiao).group(0)
            item['yuepiaoorder'] = response.meta['yuepiaoorder']
            wordcount = response.xpath('//div[@class="book-info "]//p/em[1]').extract_first()
            item['word_count'] = re.search('">(.*)</span></em>', self.modify_data(wordcount, font)).group(1) + \
                                 response.xpath('//div[@class="book-info "]//p/cite[1]/text()').extract_first()
            word_count = re.search('(.*)字', item['word_count']).group(1)
            if r'万' in word_count:
                item['word_count'] = float(word_count.replace(r'万', '')) * 10000
            elif r'亿' in word_count:
                item['word_count'] = float(word_count.replace(r'亿', '')) * 100000000
            else:
                item['word_count']=word_count
            clickcount = response.xpath('//div[@class="book-info "]//p/em[2]').extract_first()

            item['page_view'] = re.search('">(.*)</span></em>', self.modify_data(clickcount, font)).group(1) + \
                                response.xpath('//div[@class="book-info "]//p/cite[2]/text()').extract_first()

            page_view = re.search('(.*)总会员点击', item['page_view']).group(1)
            if r'万' in page_view:
                item['page_view'] = float(page_view.replace(r'万', '')) * 10000
            elif r'亿' in page_view:
                item['page_view'] = float(page_view.replace(r'亿', '')) * 100000000
            else:
                item['page_view']=page_view

            total_recommend = response.xpath('//div[@class="book-info "]//p/em[3]').extract_first()
            item['total_recommend'] = re.search('">(.*)</span></em>', self.modify_data(total_recommend, font)).group(
                1) + \
                                      response.xpath('//div[@class="book-info "]//p/cite[3]/text()').extract_first()

            total_recommend = re.search('(.*)总推荐', item['total_recommend']).group(1)
            if r'万' in total_recommend:
                item['total_recommend'] = float(total_recommend.replace(r'万', '')) * 10000
            elif r'亿' in total_recommend:
                item['total_recommend'] = float(total_recommend.replace(r'亿', '')) * 100000000
            else:
                item['total_recommend']=total_recommend

            item['lastupdate'] = response.meta['lastupdate']
            item['site'] = 'qidian'
            item['type'] = 'novel'
            item['spiderid'] = 'qidian'
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['category'] = ' '.join(response.xpath('//div[starts-with(@class,"crumbs-nav")]/span/a/text()').extract()[1:-1])
            item['status'] = response.xpath(
                '/html/body/div[2]/div[6]/div[1]/div[2]/p[1]/span[1]/text()').extract_first()
            item['description'] = response.xpath('//div[@class="book-intro"]/p/text()').extract_first()

            item['description'] = item['description'].strip().strip('\\r')
            item['biaoqian'] = ' '.join(response.xpath('//p[@class="tag"]/a/text()').extract())
            item['url'] = response.meta['bookurl']
            item['comment_count'] = response.xpath('//span[@id="J-discusCount"]/text()').extract_first()
            item['image'] = response.xpath('//div[@class="book-img"]/a/img/@src').extract_first()
            item['image'] = item['image'].strip().strip('\\r')
            item['banquan'] = ''
            item['hongbao'] = response.xpath('//div[@class="ticket"]/p/i/text()').extract_first()
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['baoqian'] = ' '.join(response.xpath('//p[@class="tag"]/span/text()').extract())
            item['pubtime'] = item['lastupdate']
            item['points'] = 0
            item['haopingzhishu'] = '0.0'
            item['shoucang'] = 0
            item['redpack'] = 0
            item['flower'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpackorder'] = 0
            item['totalrenqi'] = 0
            item['hongbao'] = 0
            item['vipvote'] = 0
            item['review_count'] = 0
            item['printmark'] = 0
            isVIP = response.xpath('//div[@class="book-info "]/p/span[3]/text()').extract_first()
            try:
                item['isvip'] = isVIP
            except:
                item['isvip'] = 'isnotVIP'
        except Exception as e:
            self.logger.error(e)
        try:
            baseurl = 'https://book.qidian.com/ajax/book/GetBookForum?'
            parmas = {
                '_csrfToken': 'alJEyea6iYGVeIYTnZnqw0mEIt0rKtoOFatcrwHd',
                'authorId': response.xpath('/html/body/div[2]/div[6]/div[1]/div[2]/h1/span/a/@href').re('\d+')[0],
                'bookId': re.search('(\d+)', response.meta['bookurl']).group(1),
                'chanId': response.xpath('/html/body/div[2]/div[4]/span/a[3]').re('chanId=(\d+)')[0],
            }
            url = baseurl + urlencode(parmas)

            yield scrapy.Request(url, callback=self.parse_comment, meta={'item': item})
        except:
            item['comment_count'] = None

    def parse_comment(self, response):
        content = json.loads(response.text)
        item = response.meta['item']
        item['comment_count'] = content['data']['threadCnt']

        yield item

    def get_font(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    def create_font(self, font_file):
        if not os.path.exists('./fonts'):
            os.mkdir('./fonts')

        file_list = os.listdir('./fonts')
        if font_file not in file_list:
            url = 'https://qidian.gtimg.com/qd_anti_spider/' + font_file
            new_file = self.get_font(url)
            with open('./fonts/' + font_file, 'wb') as f:
                f.write(new_file)

        return TTFont('./fonts/' + font_file)

    def modify_data(self, data, font):
        """ 把获取到的数据用字体对应起来，得到真实数据 """
        data = data.encode('ascii', 'xmlcharrefreplace').decode()
        # print(data)
        cmap = font['cmap'].getBestCmap()
        # print(cmap)
        for code, name in cmap.items():
            c = '&#%d;' % code
            if c in data:
                data = data.replace(c, self.num_map[name])
        return data
