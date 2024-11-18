import scrapy
import sys
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
from multiprocessing import Process, Queue

class SiteSpider(CrawlSpider):
    name = 'site_spider'
    
    def __init__(self, start_url, max_pages=10, *args, **kwargs):
        super(SiteSpider, self).__init__(*args, **kwargs)
        self.start_url = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc]
        self.max_pages = max_pages
        self.pages_crawled = 0
        self.results = []

        self.rules = (
            scrapy.spiders.Rule(
                scrapy.linkextractors.LinkExtractor(
                    deny=(
                        r'\.pdf$', r'\.zip$', r'\.rar$', r'\.doc$', r'\.docx$',
                        r'\.xls$', r'\.xlsx$'
                    )
                ),
                callback='parse_page',
                follow=True
            ),
        )
        self._compile_rules()

    def parse_page(self, response):
        if self.pages_crawled >= self.max_pages:
            raise scrapy.exceptions.CloseSpider('reached_page_limit')

        # Extract text content
        text_content = ' '.join([
            text.strip() 
            for text in response.css('body ::text').getall() 
            if text.strip()
        ])

        # Store results
        self.results.append({
            'url': response.url,
            'content': text_content
        })

        self.pages_crawled += 1
        return self.results

class SiteNavigator:
    def __init__(self):
        self.process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 1,
            'DOWNLOAD_DELAY': 2,
        })
        self.results = []

    def crawl(self, start_url, max_pages=10):
        try:
            spider = SiteSpider
            self.process.crawl(
                spider,
                start_url=start_url,
                max_pages=max_pages
            )
            self.process.start()  # Blocks until crawling is finished

            # Aggregate results from all crawlers/spiders
            for crawler in self.process.crawlers:
                spider_instance = crawler.spider
                self.results.extend(spider_instance.results)

            return self.results

        except Exception as e:
            logging.error(f"Error crawling site {start_url}: {str(e)}")
            return []