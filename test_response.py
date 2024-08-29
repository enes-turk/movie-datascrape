from scraper import MovieTitleScraper
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess()
process.crawl(MovieTitleScraper)
process.start()