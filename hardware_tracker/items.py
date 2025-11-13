# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HardwareTrackerItem(scrapy.Item):
    """Universal hardware item schema for tracking various hardware components"""
    
    # Basic Product Information
    name = scrapy.Field()                    # Product name/title
    brand = scrapy.Field()                   # Manufacturer/brand
    model = scrapy.Field()                   # Product model
    category = scrapy.Field()                # Hardware category (GPU, CPU, RAM, etc.)
    sku = scrapy.Field()                     # Product SKU or identifier
    part_number = scrapy.Field()             # Part number
    
    # Pricing Information
    price = scrapy.Field()                   # Current price (numeric)
    currency = scrapy.Field()                # Currency (USD, EUR, etc.)
    original_price = scrapy.Field()          # Original price before discount
    discount_percentage = scrapy.Field()     # Discount percentage
    price_history = scrapy.Field()           # List of price changes with timestamps
    
    # Availability Information
    in_stock = scrapy.Field()                # Boolean: is item available
    availability_status = scrapy.Field()     # Text status (in stock, out of stock, preorder)
    quantity_available = scrapy.Field()      # Stock quantity (if available)
    availability_date = scrapy.Field()       # Expected availability date
    
    # Shipping Information
    shipping_cost = scrapy.Field()           # Shipping cost
    shipping_info = scrapy.Field()           # Shipping details/restrictions
    delivery_time = scrapy.Field()           # Expected delivery time
    
    # Product Specifications (flexible for different hardware types)
    specifications = scrapy.Field()          # Dict of technical specifications
    key_features = scrapy.Field()            # List of key features
    
    # Visual Information
    image_urls = scrapy.Field()              # List of image URLs
    primary_image = scrapy.Field()           # Main product image URL
    image_count = scrapy.Field()             # Number of available images
    
    # Description and Content
    description = scrapy.Field()             # Product description
    short_description = scrapy.Field()       # Short/brief description
    specifications_table = scrapy.Field()    # Structured specs data
    
    # Ratings and Reviews
    rating = scrapy.Field()                  # Average rating (numeric)
    review_count = scrapy.Field()            # Number of reviews
    review_score = scrapy.Field()            # Review score/out of total
    
    # Source and Metadata
    source_url = scrapy.Field()              # Original product URL
    source_domain = scrapy.Field()           # Website domain
    scraped_timestamp = scrapy.Field()       # When the item was scraped
    spider_name = scrapy.Field()             # Which spider scraped this
    crawl_id = scrapy.Field()                # Unique crawl identifier
    
    # Additional Metadata
    tags = scrapy.Field()                    # Product tags/categories
    seller = scrapy.Field()                  # Seller/vendor information
    warranty = scrapy.Field()                # Warranty information
    condition = scrapy.Field()               # Product condition (new, used, refurbished)
    
    # Performance and SEO
    slug = scrapy.Field()                    # URL slug for the product
    meta_title = scrapy.Field()              # SEO meta title
    meta_description = scrapy.Field()        # SEO meta description
    
    # Price Comparison
    price_rank = scrapy.Field()              # Price rank among similar products
    best_price = scrapy.Field()              # If this is the best price available
    
    # Validation and Quality
    is_complete = scrapy.Field()             # Boolean: all required fields filled
    data_quality_score = scrapy.Field()      # Data quality score (0-1)
    validation_errors = scrapy.Field()       # List of validation issues


class PriceHistoryItem(scrapy.Item):
    """Item for tracking price changes over time"""
    product_id = scrapy.Field()              # Reference to product
    price = scrapy.Field()                   # Price at this timestamp
    currency = scrapy.Field()                # Currency
    timestamp = scrapy.Field()               # When this price was recorded
    source_url = scrapy.Field()              # Where this price was observed
    availability_status = scrapy.Field()     # Stock status at this price


class ProductComparisonItem(scrapy.Item):
    """Item for storing product comparison data"""
    products = scrapy.Field()                # List of product IDs being compared
    comparison_type = scrapy.Field()         # Type of comparison (specs, price, etc.)
    comparison_data = scrapy.Field()         # Structured comparison results
    created_timestamp = scrapy.Field()       # When comparison was created