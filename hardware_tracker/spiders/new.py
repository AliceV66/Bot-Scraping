"""
Newegg hardware spider using the base template.
Demonstrates how to adapt the base spider for different retailer structures.
"""

import scrapy
import re
from urllib.parse import urljoin
from hardware_tracker.spiders.base_spider import BaseHardwareSpider
from hardware_tracker.items import HardwareTrackerItem


class NeweggHardwareSpider(BaseHardwareSpider):
    """Newegg hardware spider with site-specific selectors and logic"""
    
    name = "newegg_hardware"
    allowed_domains = ["newegg.com"]
    
    # Newegg-specific start URLs
    start_urls = [
        "https://www.newegg.com/p/pl?d=graphics+cards",
        "https://www.newegg.com/p/pl?d=cpus+processors",
        "https://www.newegg.com/p/pl?d=memory+ram",
        "https://www.newegg.com/p/pl?d=motherboards"
    ]
    
    # Newegg-specific CSS selectors
    selectors = {
        'product_links': 'a.item-title[href*="/Product/"]',
        'next_page': 'a.btn[title="Next"]::attr(href)',
        'price': '.price-current strong::text, .price-current::text',
        'title': 'h1.product-title::text, .product-title::text',
        'brand': '.item-brand img::attr(title), .product-brand::text',
        'description': '.product-bullets, .product-brief, .product-description',
        'availability': '.product-purchase-availability::text, .inventory::text',
        'rating': '.rating::attr(title), .item-rating::attr(title)',
        'image': '.product-image img::attr(src), .product-photo-main img::attr(src)',
        'specs_table': '.product-specs, .specs-table',
        'features': '.product-bullets li::text'
    }
    
    def parse_product(self, response):
        """Enhanced product parsing for Newegg structure"""
        item = HardwareTrackerItem()
        
        # Extract Newegg-specific information
        item['name'] = self.extract_text(response, self.selectors['title'])
        item['brand'] = self.extract_newegg_brand(response)
        item['source_url'] = response.url
        item['source_domain'] = 'newegg.com'
        item['spider_name'] = self.name
        item['crawl_id'] = self.crawl_id
        item['scraped_timestamp'] = time.time()
        
        # Newegg-specific price extraction
        price_data = self.extract_newegg_price(response)
        item['price'] = price_data.get('price')
        item['currency'] = price_data.get('currency', 'USD')
        
        # Newegg availability
        availability_text = self.extract_text(response, self.selectors['availability'])
        item['availability_status'] = availability_text
        item['in_stock'] = self.determine_newegg_stock_status(availability_text)
        
        # Newegg images
        item['image_urls'] = self.extract_newegg_images(response)
        if item['image_urls']:
            item['primary_image'] = item['image_urls'][0]
            item['image_count'] = len(item['image_urls'])
        
        # Newegg description
        item['description'] = self.extract_newegg_description(response)
        item['short_description'] = self.extract_newegg_short_description(response)
        
        # Newegg ratings
        rating_data = self.extract_newegg_rating(response)
        item['rating'] = rating_data.get('rating')
        item['review_count'] = rating_data.get('count')
        
        # Extract Newegg-specific data
        item['specifications'] = self.extract_newegg_specifications(response)
        item['key_features'] = self.extract_newegg_features(response)
        
        # Newegg-specific metadata
        item['sku'] = self.extract_newegg_sku(response)
        item['part_number'] = self.extract_newegg_part_number(response)
        item['seller'] = 'Newegg'
        item['warranty'] = self.extract_newegg_warranty(response)
        
        # Determine category
        item['category'] = self.determine_category(item['name'], item['description'])
        
        if self.is_valid_item(item):
            yield item
        else:
            self.logger.warning(f"Invalid Newegg item skipped: {item.get('name', 'Unknown')}")
    
    def extract_newegg_price(self, response):
        """Extract price from Newegg-specific selectors"""
        price_data = {'price': None, 'currency': 'USD'}
        
        # Try different Newegg price selectors
        price_selectors = [
            '.price-current strong::text',
            '.price-current::text',
            '.price-linecurrent::text'
        ]
        
        for selector in price_selectors:
            price_text = response.css(selector).get()
            if price_text:
                # Clean price text and extract number
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    try:
                        price_data['price'] = float(price_match.group())
                        break
                    except ValueError:
                        continue
        
        # Check for original/discount price
        was_price = response.css('.price-was::text').get()
        if was_price and price_data['price']:
            was_match = re.search(r'[\d,]+\.?\d*', was_price.replace(',', ''))
            if was_match:
                try:
                    original_price = float(was_match.group())
                    if original_price > price_data['price']:
                        price_data['original_price'] = original_price
                        discount = ((original_price - price_data['price']) / original_price) * 100
                        price_data['discount_percentage'] = round(discount, 2)
                except ValueError:
                    pass
        
        return price_data
    
    def extract_newegg_brand(self, response):
        """Extract brand from Newegg product page"""
        # Try multiple brand extraction methods
        brand_selectors = [
            '.item-brand img::attr(title)',
            '.product-brand::text',
            '.brand-info::text',
            '.item-brand::text'
        ]
        
        for selector in brand_selectors:
            brand = response.css(selector).get()
            if brand:
                brand = brand.strip()
                if len(brand) > 1 and brand.lower() != 'newegg':
                    return brand
        
        return None
    
    def extract_newegg_images(self, response):
        """Extract product images from Newegg"""
        image_urls = []
        
        # Main product image
        main_image = response.css('.product-image img::attr(src)').get()
        if main_image:
            image_urls.append(main_image)
        
        # Thumbnail images
        thumb_images = response.css('.product-photos img::attr(src)').getall()
        for img in thumb_images:
            if img and img not in image_urls:
                # Convert thumbnail to full size (Newegg specific)
                full_size_img = img.replace('_128', '_500') if '_128' in img else img
                image_urls.append(full_size_img)
        
        return image_urls
    
    def extract_newegg_rating(self, response):
        """Extract rating and review count from Newegg"""
        rating_data = {'rating': None, 'count': None}
        
        # Extract rating from alt text or title attribute
        rating_selectors = [
            '.rating::attr(title)',
            '.item-rating::attr(title)',
            '.rating::text'
        ]
        
        for selector in rating_selectors:
            rating_text = response.css(selector).get()
            if rating_text:
                # Look for "X stars" or "X.X stars out of 5 stars"
                rating_match = re.search(r'(\d+\.?\d*)\s*stars?.*?out of 5', rating_text, re.IGNORECASE)
                if rating_match:
                    try:
                        rating_data['rating'] = float(rating_match.group(1))
                        break
                    except ValueError:
                        continue
        
        # Extract review count
        review_selectors = [
            '.rating::text',
            '.review-count::text',
            '.total-reviews::text'
        ]
        
        for selector in review_selectors:
            count_text = response.css(selector).get()
            if count_text:
                # Look for number of reviews
                count_match = re.search(r'(\d+)', count_text.replace(',', ''))
                if count_match:
                    try:
                        rating_data['count'] = int(count_match.group(1))
                        break
                    except ValueError:
                        continue
        
        return rating_data
    
    def extract_newegg_description(self, response):
        """Extract product description from Newegg"""
        # Try multiple description selectors
        description_selectors = [
            '.product-brief::text',
            '.product-description::text',
            '.item-description::text',
            '#bulletsTop::text'
        ]
        
        for selector in description_selectors:
            description = response.css(selector).get()
            if description:
                description = ' '.join(description.split())
                if len(description) > 50:
                    return description
        
        return None
    
    def extract_newegg_short_description(self, response):
        """Extract short description from Newegg"""
        # From bullet points
        bullets = response.css('.product-bullets li::text').getall()
        if bullets:
            bullet_text = ' '.join(bullets[:2])  # First 2 bullets
            if len(bullet_text) < 200:
                return bullet_text
        
        return None
    
    def extract_newegg_specifications(self, response):
        """Extract specifications from Newegg product details"""
        specs = {}
        
        # Product specifications table
        spec_rows = response.css('.product-specs tr, .specs-table tr')
        
        for row in spec_rows:
            cells = row.css('td, th')
            if len(cells) >= 2:
                key = cells[0].css('::text').get()
                value = cells[1].css('::text').get()
                if key and value:
                    specs[key.strip()] = value.strip()
        
        # Extract from meta description
        meta_desc = response.css('meta[name="description"]::attr(content)').get()
        if meta_desc:
            # Look for spec patterns in meta description
            spec_matches = re.findall(r'([^,]+):\s*([^,]+)', meta_desc)
            for key, value in spec_matches:
                if len(key) < 50 and len(value) < 100:
                    specs[key.strip()] = value.strip()
        
        return specs if specs else None
    
    def extract_newegg_features(self, response):
        """Extract key features from Newegg bullet points"""
        bullets = response.css('.product-bullets li::text').getall()
        if bullets:
            return [bullet.strip() for bullet in bullets if bullet.strip()]
        return None
    
    def extract_newegg_sku(self, response):
        """Extract product SKU"""
        # Newegg SKU patterns
        sku_patterns = [
            r'/Product/([^?]+)',
            r'\?Item=(\d+[^&]*)'
        ]
        
        for pattern in sku_patterns:
            match = re.search(pattern, response.url)
            if match:
                return match.group(1)
        
        # Look in meta tags or product info
        sku_meta = response.css('meta[itemprop="sku"]::attr(content)').get()
        if sku_meta:
            return sku_meta
        
        return None
    
    def extract_newegg_part_number(self, response):
        """Extract part number"""
        # Look in specifications or model number fields
        part_selectors = [
            '.product-specs td::text',
            '.specs-table td::text'
        ]
        
        for selector in part_selectors:
            texts = response.css(selector).getall()
            for text in texts:
                if 'model' in text.lower() or 'mpn' in text.lower():
                    # Extract alphanumeric code
                    part_match = re.search(r'[A-Z0-9\-]+', text)
                    if part_match and len(part_match.group()) > 3:
                        return part_match.group()
        
        return None
    
    def extract_newegg_warranty(self, response):
        """Extract warranty information"""
        warranty_text = response.css('*::text').re(r'warranty.*?\d+.*?year', re.IGNORECASE)
        if warranty_text:
            return warranty_text[0] if warranty_text else None
        return None
    
    def determine_newegg_stock_status(self, availability_text):
        """Determine stock status for Newegg"""
        if not availability_text:
            return None
        
        text_lower = availability_text.lower()
        
        # Newegg-specific stock indicators
        if any(phrase in text_lower for phrase in [
            'in stock', 'available', 'in stock now', 'ready to ship'
        ]):
            return True
        
        if any(phrase in text_lower for phrase in [
            'out of stock', 'discontinued', 'no longer available'
        ]):
            return False
        
        if any(phrase in text_lower for phrase in [
            'backorder', 'pre-order', 'coming soon'
        ]):
            return None  # Unknown status
        
        return None
    
    def customize_item(self, item, response):
        """Newegg-specific customization"""
        # Add Newegg-specific tags
        tags = ['newegg', item.get('category', 'other').lower()]
        
        # Add deal tags if it's a sale
        if item.get('discount_percentage', 0) > 0:
            tags.append('sale')
            if item['discount_percentage'] > 20:
                tags.append('hot-deal')
        
        # Add price tier tags
        if item.get('price'):
            if item['price'] < 100:
                tags.append('budget')
            elif item['price'] < 300:
                tags.append('mid-range')
            else:
                tags.append('high-end')
        
        item['tags'] = tags
        
        # Set meta tags for SEO
        item['slug'] = self.generate_newegg_slug(item.get('name', ''))
        item['meta_title'] = f"{item.get('name', '')} - {item.get('brand', '')} | Newegg"
        item['meta_description'] = f"Buy {item.get('name', '')} from Newegg. {item.get('short_description', '')}"
        
        # Newegg-specific seller info
        if not item.get('seller'):
            item['seller'] = 'Newegg'
    
    def generate_newegg_slug(self, name):
        """Generate URL slug for Newegg product"""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50] if slug else None


class NeweggBestBuySpider(BaseHardwareSpider):
    """Example spider showing how to create a hybrid scraper for multiple similar sites"""
    
    name = "newegg_bestbuy_hardware"
    allowed_domains = ["newegg.com", "bestbuy.com"]
    
    start_urls = [
        # Newegg URLs
        "https://www.newegg.com/p/pl?d=graphics+cards",
        # Best Buy URLs  
        "https://www.bestbuy.com/site/searchpage.jsp?st=graphics+cards"
    ]
    
    def parse(self, response):
        """Parse based on domain to use appropriate logic"""
        domain = urlparse(response.url).netloc
        
        if 'newegg.com' in domain:
            # Use Newegg logic
            yield from self.parse_newegg_listing(response)
        elif 'bestbuy.com' in domain:
            # Use Best Buy logic
            yield from self.parse_bestbuy_listing(response)
        else:
            # Default to base parsing
            yield from super().parse(response)
    
    def parse_newegg_listing(self, response):
        """Parse Newegg listing page"""
        # Newegg-specific parsing logic
        products = response.css('.item-container')
        for product in products:
            product_url = product.css('a.item-title::attr(href)').get()
            if product_url:
                yield response.follow(
                    product_url, 
                    callback=self.parse_newegg_product,
                    meta={'crawl_id': self.crawl_id}
                )
    
    def parse_bestbuy_listing(self, response):
        """Parse Best Buy listing page"""
        # Best Buy-specific parsing logic (simplified)
        products = response.css('.sku-item')
        for product in products:
            product_url = product.css('a::attr(href)').get()
            if product_url:
                yield response.follow(
                    product_url,
                    callback=self.parse_bestbuy_product, 
                    meta={'crawl_id': self.crawl_id}
                )
    
    def parse_newegg_product(self, response):
        """Parse individual Newegg product"""
        # Use Newegg spider logic
        yield from NeweggHardwareSpider().parse_product(response)
    
    def parse_bestbuy_product(self, response):
        """Parse individual Best Buy product"""
        # Basic parsing for Best Buy (would need full implementation)
        item = HardwareTrackerItem()
        item['name'] = response.css('h1::text').get()
        item['source_url'] = response.url
        item['source_domain'] = 'bestbuy.com'
        item['spider_name'] = self.name
        item['crawl_id'] = self.crawl_id
        yield item