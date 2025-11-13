"""
Amazon hardware spider using the base template.
"""

import scrapy
import time
import re
from urllib.parse import urljoin
from hardware_tracker.spiders.base_spider import BaseHardwareSpider
from hardware_tracker.items import HardwareTrackerItem


class AmazonHardwareSpider(BaseHardwareSpider):
    """Amazon hardware spider with site-specific selectors"""
    
    name = "amazon_hardware"
    allowed_domains = ["amazon.com"]
    
    start_urls = [
        "https://www.amazon.com/s?k=graphics+card&i=electronics",
        "https://www.amazon.com/s?k=cpu+processor&i=electronics", 
        "https://www.amazon.com/s?k=ram+memory&i=electronics"
    ]
    
    selectors = {
        'product_links': 'h2 a[href*="/dp/"], h2 a[href*="/gp/product/"]',
        'next_page': 'a.s-pagination-next::attr(href)',
        'price': '.a-price-whole, .a-offscreen, [data-cy="price-recipe"]',
        'title': 'h1#productTitle, h1.a-size-large',
        'brand': '.po-brand .po-break-word, .brand::text',
        'description': '#feature-bullets ul, #aplus',
        'availability': '#availability span::text, .a-color-success',
        'rating': '[data-hook="rating-out-of-text"]::text',
        'image': '#main-image, .a-button-thumbnail img',
        'features': '#feature-bullets ul li::text',
    }
    
    def parse_product(self, response):
        item = HardwareTrackerItem()
        
        item['name'] = self.extract_text(response, self.selectors['title'])
        item['brand'] = self.extract_amazon_brand(response)
        item['source_url'] = response.url
        item['source_domain'] = 'amazon.com'
        item['spider_name'] = self.name
        item['crawl_id'] = self.crawl_id
        item['scraped_timestamp'] = time.time()
        
        price_data = self.extract_amazon_price(response)
        item['price'] = price_data.get('price')
        item['currency'] = price_data.get('currency', 'USD')
        
        availability_text = self.extract_text(response, self.selectors['availability'])
        item['availability_status'] = availability_text
        item['in_stock'] = self.determine_amazon_stock_status(availability_text)
        
        item['image_urls'] = self.extract_amazon_images(response)
        if item['image_urls']:
            item['primary_image'] = item['image_urls'][0]
            item['image_count'] = len(item['image_urls'])
        
        item['description'] = self.extract_amazon_description(response)
        item['rating'] = self.extract_amazon_rating(response)
        item['specifications'] = self.extract_amazon_specifications(response)
        item['key_features'] = self.extract_amazon_features(response)
        
        item['category'] = self.determine_category(item['name'], item['description'])
        
        if self.is_valid_item(item):
            yield item
    
    def extract_amazon_price(self, response):
        price_data = {'price': None, 'currency': 'USD'}
        
        price_selectors = [
            '.a-price-whole::text',
            '.a-offscreen::text',
            '[data-cy="price-recipe"] .a-price-whole::text'
        ]
        
        for selector in price_selectors:
            price_text = response.css(selector).get()
            if price_text:
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        price_data['price'] = float(price_match.group())
                        break
                    except ValueError:
                        continue
        
        return price_data
    
    def extract_amazon_brand(self, response):
        brand_selectors = [
            '#bylineInfo::text',
            '.po-brand .po-break-word::text',
            '.brand::text'
        ]
        
        for selector in brand_selectors:
            brand = response.css(selector).get()
            if brand:
                brand = brand.strip()
                if 'Brand:' in brand:
                    brand = brand.replace('Brand:', '').strip()
                elif brand.startswith('Visit the '):
                    brand = brand.replace('Visit the ', '').replace(' Store', '')
                elif 'by' in brand.lower():
                    brand = brand.split('by')[-1].strip()
                
                if len(brand) > 1 and brand != 'Amazon.com':
                    return brand
        
        return None
    
    def extract_amazon_images(self, response):
        image_urls = []
        
        main_image = response.css('#main-image::attr(src)').get()
        if main_image:
            image_urls.append(main_image)
        
        thumb_images = response.css('#altImages img::attr(src)').getall()
        for img in thumb_images:
            if img and img not in image_urls:
                full_size_img = re.sub(r'\._[^.]+\.jpg', '._SL1500_.jpg', img)
                image_urls.append(full_size_img)
        
        return image_urls
    
    def extract_amazon_rating(self, response):
        rating_selectors = [
            '[data-hook="rating-out-of-text"]::text',
            '.a-icon-alt::text'
        ]
        
        for selector in rating_selectors:
            rating_text = response.css(selector).get()
            if rating_text:
                rating_match = re.search(r'(\d+\.?\d*)\s*out of\s*5', rating_text)
                if rating_match:
                    try:
                        return float(rating_match.group(1))
                    except ValueError:
                        continue
        
        return None
    
    def extract_amazon_description(self, response):
        description_selectors = [
            '#aplus::text',
            '#aplusV2::text',
            '#productDescription::text'
        ]
        
        for selector in description_selectors:
            description = response.css(selector).get()
            if description:
                description = ' '.join(description.split())
                if len(description) > 50:
                    return description
        
        return None
    
    def extract_amazon_specifications(self, response):
        specs = {}
        
        spec_rows = response.css('#productDetails_feature_div tr, .prodDetTable tr')
        
        for row in spec_rows:
            cells = row.css('td')
            if len(cells) >= 2:
                key = cells[0].css('::text').get()
                value = cells[1].css('::text').get()
                if key and value:
                    specs[key.strip()] = value.strip()
        
        return specs if specs else None
    
    def extract_amazon_features(self, response):
        bullets = response.css('#feature-bullets ul li::text').getall()
        if bullets:
            return [bullet.strip() for bullet in bullets if bullet.strip()]
        return None
    
    def determine_amazon_stock_status(self, availability_text):
        if not availability_text:
            return None
        
        text_lower = availability_text.lower()
        
        if any(phrase in text_lower for phrase in [
            'in stock', 'in stock and ready to ship', 'available'
        ]):
            return True
        
        if any(phrase in text_lower for phrase in [
            'out of stock', 'temporarily unavailable', 'we don\'t know when'
        ]):
            return False
        
        return None