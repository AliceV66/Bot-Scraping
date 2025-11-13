# Hardware Tracker 

 **CRITICAL FOR PRODUCTION**: Read `PRODUCTION.md` before deploying!

A clean, ethical web scraping template for tracking computer hardware components across multiple e-commerce platforms.

## Features

- **Ethical Scraping**: Built-in rate limiting, robots.txt compliance, and respectful crawling
- **Multi-Platform Support**: Spiders for Amazon, Newegg, and other major retailers  
- **Hardware Categories**: Specialized scrapers for GPUs, CPUs, RAM, storage, and motherboards
- **Data Management**: SQLite database with automatic data validation and export
- **Monitoring**: Comprehensive logging and performance tracking
- **Extensible**: Easy to add new sites and hardware types

##  Quick Start

```bash
# Install dependencies
pip install scrapy pyyaml

# Run a spider
scrapy crawl amazon_hardware

# View results
ls exports/        # Data exports
ls logs/          # Scraping logs
```



##  Project Structure

```
hardware_tracker/
├── README.md
├── requirements.txt
├── scrapy.cfg
├─ hardware_tracker/
│   ├── __init__.py
│   ├── items.py           # Data models
│   ├── middlewares.py     # Scraping middleware  
│   ├── pipelines.py       # Data processing
│   ├── settings.py        # Scrapy configuration
│   ├── config.py          # Settings management
│   ├── monitoring.py      # Logging system
│   └── spiders/
│       ├── __init__.py
│       ├── base_spider.py     # Template spider
│       ├── amazon_spider.py   # Amazon scraper
│       └── specialized_spiders.py  # Hardware-specific
```

##  Available Spiders

- `amazon_hardware` - Amazon hardware products
- `gpu_hardware` - Graphics cards and GPUs  
- `cpu_hardware` - Processors and CPUs
- `ram_hardware` - Memory modules
- `storage_hardware` - SSDs and HDDs
- `all_hardware` - Run all specialized spiders

##  Data Output

- **SQLite Database**: `hardware_data.db`
- **JSON Exports**: `exports/hardware_timestamp.json`
- **CSV Exports**: `exports/hardware_timestamp.csv`

##  Customization

### Create a Custom Spider

```python
from hardware_tracker.spiders.base_spider import BaseHardwareSpider

class MySpider(BaseHardwareSpider):
    name = "my_hardware"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/hardware"]
    
    selectors = {
        'product_links': '.product a',
        'price': '.price',
        'title': 'h1.product-title',
        # Customize for your site
    }
```

### Configuration

Edit `config.yaml` to customize:
- Rate limiting per domain
- Spider settings
- Export formats
- Monitoring options

##  Ethical Guidelines

This template follows ethical scraping practices:
- Respects robots.txt rules
- Uses appropriate rate limiting (1-3 seconds between requests)
- Rotates user agents for realistic browsing
- Handles errors gracefully
- Identifies as a bot appropriately

##  Data Schema

Each scraped item includes:
- Product name, brand, model
- Price and currency
- Availability status  
- Technical specifications
- Images and ratings
- Source URL and metadata

##  Example Output

```json
{
  "name": "NVIDIA GeForce RTX 4070",
  "brand": "NVIDIA", 
  "price": 599.99,
  "currency": "USD",
  "category": "GPU",
  "availability_status": "In Stock",
  "specifications": {
    "memory": "12GB GDDR6X",
    "base_clock": "1920 MHz",
    "boost_clock": "2475 MHz"
  },
  "source_url": "https://amazon.com/product-link",
  "scraped_timestamp": 1699574400
}
```

##  Contributing

1. Fork the repository
2. Create a feature branch  
3. Follow ethical scraping guidelines
4. Add tests for new features
5. Submit a pull request

##  License

This template is provided for educational purposes. Users must comply with:
- Website terms of service
- robots.txt rules  
- Local laws and regulations

##  Disclaimer

Users are responsible for ensuring their usage complies with all applicable laws and website terms of service. The authors are not responsible for any misuse.

---

**Happy Scraping!**
