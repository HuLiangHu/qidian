# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class SpiderNovelItem(Item):
    # define the fields for your item here like:
    name = Field(default=None)  # 小说书名
    url = Field(default=None)  # 小说链接
    author = Field(default=None)  # 小说作者
    category = Field(default=None)  # 小说类别
    page_view = Field(default=0)  # 小说阅读量
    word_count = Field(default=0)  # 小说字数
    description = Field(default=None)  # 小说描述
    points = Field(default=0)  # 小说积分
    yuepiao = Field(default=0)  # 小说月票
    shoucang = Field(default=0)  # 收藏
    comment_count = Field(default=0)  # 评论数
    review_count = Field(default=0)  # 主题数
    redpack = Field(default=0)  # 荷包
    yuepiaoorder = Field(default=0)  # 月票排名
    flower = Field(default=0)  # 鲜花
    diamondnum = Field(default=0)  # 钻石
    coffeenum = Field(default=0)  # 咖啡
    eggnum = Field(default=0)  # 鸡蛋
    redpackorder = Field(default=0)  # 荷包收入排名
    isvip = Field(default=None)  # VIP书籍
    status = Field(default=None)  # 小说状态
    image = Field(default=None)  # 小说图片
    banquan = Field(default=None)  # 小说版权
    hongbao = Field(default=0)  # 红包
    vipvote = Field(default=0)  # 投贵宾
    biaoqian = Field(default=None)  # 小说标签
    haopingzhishu = Field(default=0)  # 小说好评指数
    weekclickCount = Field(default=0)  # 本周阅读数
    monthclickCount = Field(default=0)  # 本月阅读数
    bookSignInCount = Field(default=0)  # 累计签到数
    printmark = Field(default=0)  # 盖个章
    total_recommend = Field(default=0)  # 小说总推荐
    totalrenqi = Field(default=0)  # 小说人气
    pubtime = Field(default=None)  # 小说上线时间
    lastupdate = Field(default=None)  # 小说最新更新日期
    current_date = Field(default=None)  # 抓取数据日期
    site = Field(default=None)  # 小说所在网站