"""
Specialized spiders for different hardware categories.
"""

import scrapy
from hardware_tracker.spiders.base_spider import BaseHardwareSpider
from hardware_tracker.items import HardwareTrackerItem


class GPUHardwareSpider(BaseHardwareSpider):
    """Specialized spider for Graphics Cards (GPUs)"""
    
    name = "gpu_hardware"
    allowed_domains = ["amazon.com", "newegg.com"]
    
    start_urls = [
        "https://www.amazon.com/s?k=graphics+card+nvidia+amd&i=electronics"
    ]
    
    def customize_item(self, item, response):
        """GPU-specific item customization"""
        gpu_specs = item.get('specifications', {}) or {}
        
        gpu_fields = {
            'gpu chipset': ['gpu', 'chipset', 'graphics processor'],
            'memory': ['vram', 'memory', 'video memory'],
            'core clock': ['core clock', 'base clock', 'gpu clock'],
            'boost clock': ['boost clock', 'max clock'],
            'power consumption': ['power', 'tdp', 'wattage'],
        }
        
        enhanced_specs = {}
        for standard_field, keywords in gpu_fields.items():
            for key, value in gpu_specs.items():
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in keywords):
                    enhanced_specs[standard_field] = value
                    break
        
        item['specifications'] = enhanced_specs if enhanced_specs else gpu_specs
        item['category'] = 'GPU'
        item['hardware_type'] = 'graphics_card'
        
        # Add GPU-specific tags
        tags = item.get('tags', []) or []
        tags.extend(['gpu', 'graphics_card', 'graphics'])
        
        if item.get('brand'):
            brand_lower = item['brand'].lower()
            if 'nvidia' in brand_lower:
                tags.append('nvidia')
            elif 'amd' in brand_lower or 'radeon' in brand_lower:
                tags.append('amd')
        
        item['tags'] = tags


class CPUHardwareSpider(BaseHardwareSpider):
    """Specialized spider for CPUs (Processors)"""
    
    name = "cpu_hardware"
    allowed_domains = ["amazon.com", "newegg.com"]
    
    start_urls = [
        "https://www.amazon.com/s?k=cpu+processor+intel+amd&i=electronics"
    ]
    
    def customize_item(self, item, response):
        """CPU-specific item customization"""
        cpu_specs = item.get('specifications', {}) or {}
        
        cpu_fields = {
            'socket': ['socket', 'cpu socket'],
            'cores': ['cores', 'cpu cores'],
            'threads': ['threads', 'logical processors'],
            'base clock': ['base clock', 'base frequency'],
            'boost clock': ['boost clock', 'max turbo'],
            'cache': ['cache', 'l3 cache', 'l2 cache'],
            'tdp': ['tdp', 'power consumption'],
        }
        
        enhanced_specs = {}
        for standard_field, keywords in cpu_fields.items():
            for key, value in cpu_specs.items():
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in keywords):
                    enhanced_specs[standard_field] = value
                    break
        
        item['specifications'] = enhanced_specs if enhanced_specs else cpu_specs
        item['category'] = 'CPU'
        item['hardware_type'] = 'processor'
        
        # Add CPU-specific tags
        tags = item.get('tags', []) or []
        tags.extend(['cpu', 'processor', 'central_processor'])
        
        if item.get('name'):
            name_lower = item['name'].lower()
            if 'core' in name_lower:
                tags.append('intel')
            if 'ryzen' in name_lower or 'athlon' in name_lower:
                tags.append('amd')
        
        item['tags'] = tags


class RAMHardwareSpider(BaseHardwareSpider):
    """Specialized spider for RAM/Memory"""
    
    name = "ram_hardware"
    allowed_domains = ["amazon.com", "newegg.com"]
    
    start_urls = [
        "https://www.amazon.com/s?k=ram+memory+ddr&i=electronics"
    ]
    
    def customize_item(self, item, response):
        """RAM-specific item customization"""
        ram_specs = item.get('specifications', {}) or {}
        
        ram_fields = {
            'capacity': ['capacity', 'size', 'total capacity'],
            'modules': ['modules', 'kit', 'sticks'],
            'type': ['type', 'ddr', 'memory type'],
            'speed': ['speed', 'frequency', 'mhz', 'data rate'],
            'timing': ['timing', 'cas', 'latency'],
        }
        
        enhanced_specs = {}
        for standard_field, keywords in ram_fields.items():
            for key, value in ram_specs.items():
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in keywords):
                    enhanced_specs[standard_field] = value
                    break
        
        item['specifications'] = enhanced_specs if enhanced_specs else ram_specs
        item['category'] = 'RAM'
        item['hardware_type'] = 'memory'
        
        # Add RAM-specific tags
        tags = item.get('tags', []) or []
        tags.extend(['ram', 'memory', 'ddr'])
        
        if item.get('specifications'):
            specs = item['specifications']
            if 'type' in specs:
                ram_type = specs['type'].upper()
                if 'DDR4' in ram_type:
                    tags.append('ddr4')
                elif 'DDR5' in ram_type:
                    tags.append('ddr5')
        
        item['tags'] = tags


class AllHardwareSpider(BaseHardwareSpider):
    """Meta-spider that runs all specialized hardware spiders"""
    
    name = "all_hardware"
    
    def start_requests(self):
        """Start requests by delegating to specialized spiders"""
        spider_classes = [
            GPUHardwareSpider,
            CPUHardwareSpider,
            RAMHardwareSpider
        ]
        
        for spider_class in spider_classes:
            try:
                spider = spider_class()
                for url in spider.start_urls:
                    yield scrapy.Request(
                        url,
                        callback=self.parse_delegated,
                        meta={'spider_class': spider_class.__name__}
                    )
            except Exception as e:
                self.logger.error(f"Failed to initialize {spider_class.__name__}: {e}")
    
    def parse_delegated(self, response):
        """Parse by delegating to the appropriate spider"""
        spider_class_name = response.meta.get('spider_class')
        
        spider_mapping = {
            'GPUHardwareSpider': GPUHardwareSpider,
            'CPUHardwareSpider': CPUHardwareSpider,
            'RAMHardwareSpider': RAMHardwareSpider
        }
        
        if spider_class_name in spider_mapping:
            spider_class = spider_mapping[spider_class_name]
            spider = spider_class()
            
            # Get product links using the specialized spider's selectors
            product_links = response.css(spider.selectors['product_links']).xpath('@href').getall()
            
            for link in product_links:
                from urllib.parse import urljoin
                full_url = urljoin(response.url, link)
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_product_delegated,
                    meta={
                        'crawl_id': self.crawl_id,
                        'spider_class_name': spider_class_name,
                        'spider': spider
                    }
                )
        else:
            self.logger.warning(f"Unknown spider class: {spider_class_name}")
    
    def parse_product_delegated(self, response):
        """Parse product with the appropriate specialized spider logic"""
        spider_class_name = response.meta.get('spider_class_name')
        spider = response.meta.get('spider')
        
        if not spider or not spider_class_name:
            self.logger.error("Missing spider information in delegation")
            return
        
        spider_mapping = {
            'GPUHardwareSpider': GPUHardwareSpider,
            'CPUHardwareSpider': CPUHardwareSpider,
            'RAMHardwareSpider': RAMHardwareSpider
        }
        
        if spider_class_name in spider_mapping:
            # Use the specialized spider's parse_product method
            item = spider.parse_product(response)
            
            # If parse_product yields items, yield them
            if item:
                if hasattr(item, '__iter__'):
                    yield from item
                else:
                    yield item
        else:
            self.logger.warning(f"Unknown spider class in product parsing: {spider_class_name}")