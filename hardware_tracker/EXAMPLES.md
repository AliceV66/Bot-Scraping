# Hardware Tracker - Example Usage

## Quick Examples

### 1. Basic Spider Usage

```python
from hardware_tracker.spiders.amazon_spider import AmazonHardwareSpider

# Create spider instance
spider = AmazonHardwareSpider()
print(f"Running {spider.name} spider")

# Run via command line
# scrapy crawl amazon_hardware
```

### 2. Create Custom Spider

```python
from hardware_tracker.spiders.base_spider import BaseHardwareSpider

class MySpider(BaseHardwareSpider):
    name = "my_hardware"
    start_urls = ["https://example.com/hardware"]
    
    selectors = {
        'product_links': '.product a',
        'price': '.price',
        'title': 'h1.product-title'
    }

# Run spider
# scrapy crawl my_hardware
```

### 3. Data Structure Example

```python
from hardware_tracker.items import HardwareTrackerItem

item = HardwareTrackerItem()
item['name'] = "NVIDIA RTX 4070"
item['brand'] = "NVIDIA"
item['price'] = 599.99
item['category'] = "GPU"
```

## Running Spiders

```bash
# Install dependencies
pip install -r requirements.txt

# Run available spiders
scrapy crawl amazon_hardware      # Amazon hardware products
scrapy crawl gpu_hardware        # GPU-specific scraper
scrapy crawl cpu_hardware        # CPU-specific scraper
scrapy crawl ram_hardware        # RAM-specific scraper
scrapy crawl all_hardware        # Run all specialized spiders

# View results
ls exports/                      # JSON/CSV exports
sqlite3 hardware_data.db         # Database queries
```

## Key Features

- **Ethical Scraping**: Built-in rate limiting and robots.txt compliance
- **Multi-Site Support**: Pre-built spiders for major retailers
- **Hardware Categories**: Specialized parsers for different component types
- **Data Validation**: Automatic cleaning and quality scoring
- **Multiple Exports**: SQLite database + JSON/CSV files