# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
import sqlite3
import logging
from datetime import datetime
from urllib.parse import urlparse
from decimal import Decimal
from itemadapter import ItemAdapter


class DatabaseStoragePipeline:
    """Pipeline for storing items in SQLite database"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or 'hardware_data.db'
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(database_url=crawler.settings.get('DATABASE_URL'))
    
    def open_spider(self, spider):
        """Initialize database connection with WAL mode for concurrent access"""
        self.conn = sqlite3.connect(self.database_url, timeout=30.0)
        # Enable WAL mode for better concurrent access (crucial for AllHardwareSpider)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
        self.create_tables()
        self.logger.info(f"Database connection opened: {self.database_url}")
    
    def close_spider(self, spider):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            self.logger.info("Database connection closed")
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Main hardware items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hardware_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                category TEXT,
                price REAL,
                currency TEXT DEFAULT 'USD',
                availability_status TEXT,
                specifications TEXT,
                key_features TEXT,
                image_urls TEXT,
                primary_image TEXT,
                description TEXT,
                rating REAL,
                review_count INTEGER,
                source_url TEXT,
                source_domain TEXT,
                scraped_timestamp REAL,
                spider_name TEXT,
                crawl_id TEXT,
                tags TEXT,
                is_complete INTEGER,
                data_quality_score REAL,
                validation_errors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                price REAL,
                currency TEXT,
                timestamp REAL,
                source_url TEXT,
                availability_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES hardware_items (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON hardware_items(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_brand ON hardware_items(brand)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON hardware_items(source_domain)')
        
        self.conn.commit()
    
    def process_item(self, item, spider):
        """Store item in database"""
        adapter = ItemAdapter(item)
        item_dict = dict(adapter)
        
        # Convert JSON fields
        json_fields = ['specifications', 'key_features', 'image_urls', 'tags', 'validation_errors']
        for field in json_fields:
            if item_dict.get(field) is not None:
                item_dict[field] = json.dumps(item_dict[field])
        
        # Insert or update item
        product_id = self.insert_or_update_item(item_dict)
        
        # Store price history
        if item_dict.get('price') is not None:
            self.store_price_history(product_id, item_dict)
        
        return item
    
    def insert_or_update_item(self, item):
        """Insert or update item in database"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id FROM hardware_items
            WHERE source_url = ?
        ''', (item['source_url'],))
        
        existing = cursor.fetchone()
        
        if existing:
            item_id = existing[0]
            update_fields = [f"{k} = ?" for k in item.keys() if k != 'id']
            update_values = [v for k, v in item.items() if k != 'id']
            update_values.append(item_id)
            
            cursor.execute(f'''
                UPDATE hardware_items 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)
        else:
            insert_fields = list(item.keys())
            insert_values = list(item.values())
            placeholders = ', '.join(['?' for _ in insert_fields])
            
            cursor.execute(f'''
                INSERT INTO hardware_items ({', '.join(insert_fields)})
                VALUES ({placeholders})
            ''', insert_values)
            
            item_id = cursor.lastrowid
        
        self.conn.commit()
        return item_id
    
    def store_price_history(self, product_id, item):
        """Store price history"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT price FROM price_history 
            WHERE product_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (product_id,))
        
        last_price = cursor.fetchone()
        current_price = item.get('price')
        
        if not last_price or last_price[0] != current_price:
            cursor.execute('''
                INSERT INTO price_history 
                (product_id, price, currency, timestamp, source_url, availability_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                product_id, current_price, item.get('currency', 'USD'),
                item.get('scraped_timestamp', datetime.now().timestamp()),
                item.get('source_url'), item.get('availability_status')
            ))
            
            self.conn.commit()


class DataValidationPipeline:
    """Pipeline for validating and cleaning scraped data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_item(self, item, spider):
        """Validate and clean item data"""
        adapter = ItemAdapter(item)
        item_dict = dict(adapter)
        
        # Basic validation
        errors = []
        self.validate_required_fields(item_dict, errors)
        
        # Clean data
        self.clean_price_data(item_dict)
        self.normalize_text_fields(item_dict)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(item_dict, errors)
        
        # Set validation metadata
        item['validation_errors'] = errors
        item['data_quality_score'] = quality_score
        item['is_complete'] = len(errors) == 0
        
        return item
    
    def validate_required_fields(self, item, errors):
        """Validate required fields"""
        if not item.get('name') or len(item['name'].strip()) < 3:
            errors.append("Product name is missing or too short")
        
        if item.get('price') is not None:
            try:
                if float(item['price']) <= 0:
                    errors.append("Price must be positive")
            except (ValueError, TypeError):
                errors.append("Invalid price format")
    
    def clean_price_data(self, item):
        """Clean price data"""
        price_fields = ['price', 'original_price']
        
        for field in price_fields:
            value = item.get(field)
            if value is not None and isinstance(value, str):
                import re
                price_match = re.search(r'[\d,]+\.?\d*', value.replace(',', ''))
                if price_match:
                    try:
                        item[field] = float(price_match.group())
                    except ValueError:
                        item[field] = None
    
    def normalize_text_fields(self, item):
        """Normalize text fields"""
        text_fields = ['name', 'brand', 'description', 'availability_status']
        
        for field in text_fields:
            value = item.get(field)
            if isinstance(value, str):
                item[field] = ' '.join(value.split())
    
    def calculate_quality_score(self, item, errors):
        """Calculate data quality score"""
        score = 1.0
        score -= len(errors) * 0.1
        
        # Bonus for completeness
        important_fields = ['name', 'price', 'brand', 'category', 'source_url']
        present_fields = sum(1 for field in important_fields if item.get(field) is not None)
        score += (present_fields / len(important_fields)) * 0.2
        
        return max(0.0, min(1.0, score))


class ExportPipeline:
    """Pipeline for exporting data to various formats"""
    
    def __init__(self, export_formats=None):
        self.export_formats = export_formats or ['json', 'csv']
        self.exported_items = []
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('EXPORT_FORMATS', ['json', 'csv']))
    
    def process_item(self, item, spider):
        """Collect items for export"""
        self.exported_items.append(dict(item))
        return item
    
    def close_spider(self, spider):
        """Export all collected items"""
        if not self.exported_items:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        spider_name = spider.name
        
        for format_type in self.export_formats:
            try:
                if format_type.lower() == 'json':
                    self.export_json(spider_name, timestamp, self.exported_items)
                elif format_type.lower() == 'csv':
                    self.export_csv(spider_name, timestamp, self.exported_items)
            except Exception as e:
                self.logger.error(f"Failed to export {format_type}: {e}")
        
        self.exported_items = []
    
    def export_json(self, spider_name, timestamp, items):
        """Export to JSON"""
        import os
        os.makedirs("exports", exist_ok=True)
        
        filename = f"exports/{spider_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False, default=str)
    
    def export_csv(self, spider_name, timestamp, items):
        """Export to CSV"""
        import os
        os.makedirs("exports", exist_ok=True)
        
        filename = f"exports/{spider_name}_{timestamp}.csv"
        
        if not items:
            return
        
        fieldnames = set()
        for item in items:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in items:
                row = {}
                for key, value in item.items():
                    if isinstance(value, (list, dict)):
                        row[key] = json.dumps(value, default=str)
                    else:
                        row[key] = str(value) if value is not None else ''
                writer.writerow(row)


class HardwareTrackerPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_item(self, item, spider):
        """Main item processing"""
        return item
