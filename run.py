import scrapy
from scrapy.crawler import CrawlerProcess
from crawling.spiders.novel_qidian import QidianSpider




from scrapy.utils.project import get_project_settings
process = CrawlerProcess(get_project_settings())

process.crawl(QidianSpider)
process.start()