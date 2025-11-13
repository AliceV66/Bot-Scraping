"""
Base spider template for hardware tracking with ethical scraping practices.
"""

import scrapy
import time
import uuid
from urllib.parse import urljoin, urlparse
from hardware_tracker.items import HardwareTrackerItem


class BaseHardwareSpider(scrapy.Spider):
    """Base spider for hardware tracking"""
    
    name = "base_hardware"
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 2,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504],
        'COOKIES_ENABLED': True,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawl_id = str(uuid.uuid4())
        self.start_time = time.time()
        
        self.categories = {
            'gpu': ['GPU', 'Graphics Card', 'Video Card'],
            'cpu': ['CPU', 'Processor'],
            'ram': ['RAM', 'Memory', 'DDR'],
            'storage': ['SSD', 'HDD', 'Storage'],
            'motherboard': ['Motherboard', 'MB'],
            'psu': ['PSU', 'Power Supply'],
        }
        
        self.selectors = {
            'product_links': 'a[href*="/product"]',
            'next_page': '.pagination .next',
            'price': '.price, .product-price',
            'title': 'h1, .product-title',
            'brand': '.brand, [class*="brand"]',
            'description': '.description',
            'availability': '.availability',
            'rating': '.rating',
            'image': '.product-image img',
        }
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    'start_time': time.time(),
                    'crawl_id': self.crawl_id,
                    'depth': 0
                }
            )
    
    def parse(self, response):
        product_links = response.css(self.selectors['product_links']).xpath('@href').getall()
        
        for link in product_links:
            full_url = urljoin(response.url, link)
            yield scrapy.Request(
                full_url,
                callback=self.parse_product,
                meta={'crawl_id': self.crawl_id}
            )
        
        # Handle pagination
        next_page = response.css(self.selectors['next_page']).xpath('@href').get()
        if next_page:
            next_url = urljoin(response.url, next_page)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={
                    'crawl_id': self.crawl_id,
                    'depth': response.meta.get('depth', 0) + 1
                }
            )
    
    def parse_product(self, response):
        item = HardwareTrackerItem()
        
        item['name'] = self.extract_text(response, self.selectors['title'])
        item['brand'] = self.extract_text(response, self.selectors['brand'])
        item['source_url'] = response.url
        item['source_domain'] = urlparse(response.url).netloc
        item['spider_name'] = self.name
        item['crawl_id'] = self.crawl_id
        item['scraped_timestamp'] = time.time()
        
        item['price'] = self.extract_price(response, self.selectors['price'])
        item['currency'] = self.detect_currency(response, self.selectors['price'])
        
        availability_text = self.extract_text(response, self.selectors['availability'])
        item['availability_status'] = availability_text
        item['in_stock'] = self.determine_stock_status(availability_text)
        
        item['image_urls'] = self.extract_image_urls(response, self.selectors['image'])
        if item['image_urls']:
            item['primary_image'] = item['image_urls'][0]
        
        item['description'] = self.extract_text(response, self.selectors['description'])
        item['rating'] = self.extract_rating(response, self.selectors['rating'])
        
        item['category'] = self.determine_category(item['name'], item['description'])
        item['specifications'] = self.extract_specifications(response)
        
        if self.is_valid_item(item):
            yield item
    
    def extract_text(self, response, selector):
        try:
            text = response.css(selector).get()
            if text:
                return ' '.join(text.split())
        except Exception:
            pass
        return None
    
    def extract_price(self, response, selector):
        try:
            price_text = response.css(selector).get()
            if price_text:
                import re
                price_pattern = r'[\d,]+\.?\d*'
                match = re.search(price_pattern, price_text.replace(',', ''))
                if match:
                    return float(match.group())
        except Exception:
            pass
        return None
    
    def detect_currency(self, response, selector):
        try:
            price_text = response.css(selector).get() or ''
            if '$' in price_text:
                return 'USD'
            elif '€' in price_text:
                return 'EUR'
            elif '£' in price_text:
                return 'GBP'
            else:
                return 'USD'
        except Exception:
            return 'USD'
    
    def determine_stock_status(self, availability_text):
        if not availability_text:
            return False
        
        availability_lower = availability_text.lower()
        
        if any(word in availability_lower for word in ['in stock', 'available', 'buy']):
            return True
        
        if any(word in availability_lower for word in ['out of stock', 'sold out', 'unavailable']):
            return False
        
        return None
    
    def extract_image_urls(self, response, selector):
        try:
            img_elements = response.css(selector)
            image_urls = []
            
            for img in img_elements:
                src = img.xpath('@src').get()
                if src:
                    full_url = urljoin(response.url, src)
                    image_urls.append(full_url)
            
            return image_urls
        except Exception:
            return []
    
    def extract_rating(self, response, selector):
        try:
            rating_text = response.css(selector).get()
            if rating_text:
                import re
                rating_pattern = r'(\d+\.?\d*)\s*out of\s*5'
                match = re.search(rating_pattern, rating_text, re.IGNORECASE)
                if match:
                    rating_value = float(match.group(1))
                    if 0 <= rating_value <= 5:
                        return rating_value
        except Exception:
            pass
        return None
    
    def determine_category(self, name, description):
        if not name and not description:
            return 'Other'
        
        text = f"{name or ''} {description or ''}".lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return category.upper()
        
        return 'Other'
    
    def extract_specifications(self, response):
        specs = {}
        spec_rows = response.css('table tr, .spec-row')
        
        for row in spec_rows:
            cells = row.css('td, th')
            if len(cells) >= 2:
                key = cells[0].css('::text').get()
                value = cells[1].css('::text').get()
                if key and value:
                    specs[key.strip()] = value.strip()
        
        return specs if specs else None
    
    def is_valid_item(self, item):
        if not item.get('name') or len(item['name']) < 3:
            return False
        
        if not item.get('source_url'):
            return False
        
        if item.get('price') is not None and item['price'] <= 0:
            return False
        
        return True
    
    def closed(self, reason):
        duration = time.time() - float(self.start_time)
        self.logger.info(f"Crawl {self.crawl_id} completed. Reason: {reason}, Duration: {duration}s")