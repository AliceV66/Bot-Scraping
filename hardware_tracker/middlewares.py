# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import time
import logging
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from urllib.parse import urlparse

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EthicalSpiderMiddleware:
    """Middleware for ethical scraping practices"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # User agent rotation for realistic browsing
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Domain-specific delays for respectful crawling
        self.domain_delays = {
            'amazon.com': 2,
            'newegg.com': 1.5,
            'microcenter.com': 1,
            'bestbuy.com': 1,
            'walmart.com': 2,
        }

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        """Validate response and add metadata"""
        response.meta['scraped_at'] = time.time()
        response.meta['crawl_id'] = getattr(spider, 'crawl_id', None)
        return None

    def process_spider_output(self, response, result, spider):
        """Process spider output with rate limiting awareness"""
        domain = urlparse(response.url).netloc
        if domain in self.domain_delays:
            delay = self.domain_delays[domain]
            self.logger.info(f"Rate limiting for {domain}: {delay}s delay")
        
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        """Handle spider exceptions with logging"""
        self.logger.error(f"Spider exception for {response.url}: {exception}")
        return None

    def spider_opened(self, spider):
        self.logger.info(f"Ethical spider middleware opened for: {spider.name}")
        self.logger.info("Respectful scraping practices enabled")


class EthicalDownloaderMiddleware:
    """Middleware for ethical web scraping with user agent rotation and rate limiting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # User agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Domain-specific delays
        self.domain_delays = {
            'amazon.com': 3,
            'newegg.com': 2,
            'microcenter.com': 2,
            'bestbuy.com': 2,
            'walmart.com': 3,
        }
        
        self.last_request_times = {}
        self.request_counts = {}

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """Process each request with ethical scraping practices"""
        # Rotate user agent
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        
        # Add polite headers
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        request.headers['Accept-Language'] = 'en-US,en;q=0.5'
        request.headers['Connection'] = 'keep-alive'
        
        # Rate limiting per domain
        domain = urlparse(request.url).netloc
        
        if domain in self.domain_delays:
            current_time = time.time()
            last_time = self.last_request_times.get(domain, 0)
            delay = self.domain_delays[domain]
            
            if current_time - last_time < delay:
                sleep_time = delay - (current_time - last_time)
                time.sleep(sleep_time)
                self.logger.debug(f"Applied {sleep_time:.2f}s delay for {domain}")
            
            self.last_request_times[domain] = time.time()
            self.request_counts[domain] = self.request_counts.get(domain, 0) + 1
        
        return None

    def process_response(self, request, response, spider):
        """Process response with error handling"""
        domain = urlparse(request.url).netloc
        
        # Handle different response codes
        if response.status == 429:  # Too Many Requests
            self.logger.warning(f"Rate limit hit for {domain}. Adding extra delay.")
            time.sleep(10)
        
        elif response.status == 403:  # Forbidden
            self.logger.error(f"Access forbidden for {domain}. Check robots.txt and terms.")
        
        elif response.status >= 500:  # Server Error
            self.logger.warning(f"Server error {response.status} for {domain}")
        
        response.meta['response_time'] = time.time() - request.meta.get('start_time', time.time())
        response.meta['domain'] = domain
        
        return response

    def process_exception(self, request, exception, spider):
        """Handle downloader exceptions gracefully"""
        domain = urlparse(request.url).netloc
        self.logger.error(f"Downloader exception for {domain}: {exception}")
        return None

    def spider_opened(self, spider):
        self.logger.info(f"Ethical downloader middleware opened for: {spider.name}")
        self.logger.info("Ethical scraping practices active")
