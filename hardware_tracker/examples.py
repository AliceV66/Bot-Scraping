"""
Example usage script for the Hardware Tracker template.
This demonstrates how to use the template for various scraping scenarios.
"""

import scrapy
import time
import sys
import os
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hardware_tracker.spiders.amazon_spider import AmazonHardwareSpider
from hardware_tracker.spiders.newegg_spider import NeweggHardwareSpider
from hardware_tracker.spiders.specialized_spiders import (
    GPUHardwareSpider, CPUHardwareSpider, RAMHardwareSpider
)
from hardware_tracker.config import get_config, create_sample_config
from hardware_tracker.monitoring import get_monitor


def example_basic_usage():
    """Example of basic spider usage"""
    print("=== Basic Usage Example ===")
    
    # Create and run a simple spider
    spider = AmazonHardwareSpider()
    print(f"Spider created: {spider.name}")
    print(f"Start URLs: {spider.start_urls}")
    print(f"Allowed domains: {spider.allowed_domains}")


def example_configuration():
    """Example of configuration management"""
    print("\n=== Configuration Example ===")
    
    # Get configuration manager
    config = get_config()
    
    # Show current configuration
    print("Current rate limits:")
    rate_config = config.get_rate_limit_config()
    for domain, delay in rate_config.domains.items():
        print(f"  {domain}: {delay}s")
    
    # Show database configuration
    db_config = config.get_database_config()
    print(f"Database: {db_config.url}")
    print(f"Backup enabled: {db_config.backup_enabled}")
    
    # Show logging configuration
    log_config = config.get_logging_config()
    print(f"Log level: {log_config.level}")
    print(f"Log file: {log_config.file}")
    
    # Create sample configuration file
    create_sample_config("sample_config.yaml")
    print("Created sample configuration file: sample_config.yaml")


def example_monitoring():
    """Example of monitoring and statistics"""
    print("\n=== Monitoring Example ===")
    
    # Get monitoring instance
    monitor = get_monitor()
    
    # Start a mock crawl
    crawl_id = monitor.start_crawl("example_spider")
    print(f"Started monitoring crawl: {crawl_id[:8]}")
    
    # Simulate some crawling activity
    monitor.update_crawl(crawl_id, 
                        total_requests=100,
                        successful_requests=95,
                        items_scraped=45,
                        failed_requests=5)
    
    # Simulate some domain-specific stats
    monitor.update_crawl(crawl_id, 
                        domains_scraped=['amazon.com', 'newegg.com'],
                        rate_limit_hits=2)
    
    # End monitoring
    stats = monitor.end_crawl(crawl_id)
    if stats:
        print(f"Crawl completed:")
        print(f"  Duration: {stats.duration:.1f}s")
        print(f"  Success rate: {stats.success_rate:.1f}%")
        print(f"  Items scraped: {stats.items_scraped}")
        print(f"  Items per second: {stats.items_per_second:.2f}")


def example_custom_spider():
    """Example of creating a custom spider"""
    print("\n=== Custom Spider Example ===")
    
    from hardware_tracker.spiders.base_spider import BaseHardwareSpider
    
    class ExampleCustomSpider(BaseHardwareSpider):
        """Example custom spider for demonstration"""
        name = "example_custom"
        allowed_domains = ["example.com"]
        
        start_urls = [
            "https://example.com/hardware/gpu",
            "https://example.com/hardware/cpu"
        ]
        
        # Customize selectors for the example site
        selectors = {
            'product_links': '.product-item a',
            'next_page': '.pagination .next',
            'price': '.price-amount',
            'title': 'h1.product-title',
            'brand': '.brand-name',
            'description': '.product-description',
            'availability': '.stock-status',
            'rating': '.rating-score',
            'image': '.product-image img',
        }
        
        def customize_item(self, item, response):
            """Customize item for this example"""
            # Add example-specific metadata
            item['example_field'] = "This is from the custom spider"
            item['response_url'] = response.url
            item['scrape_example'] = True
            
            return item
    
    spider = ExampleCustomSpider()
    print(f"Custom spider created: {spider.name}")
    print(f"Custom selectors: {list(spider.selectors.keys())}")


def example_database_query():
    """Example of querying the scraped data"""
    print("\n=== Database Query Example ===")
    
    import sqlite3
    from pathlib import Path
    
    db_path = "hardware_data.db"
    
    if Path(db_path).exists():
        print(f"Database exists: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='hardware_items'
            """)
            
            if cursor.fetchone():
                # Get some sample data
                cursor.execute("""
                    SELECT name, brand, price, category, source_domain 
                    FROM hardware_items 
                    LIMIT 5
                """)
                
                print("Sample data from database:")
                for row in cursor.fetchall():
                    print(f"  {row[0]} | {row[1]} | ${row[2]} | {row[3]} | {row[4]}")
                
                # Get statistics
                cursor.execute("""
                    SELECT category, COUNT(*), AVG(price)
                    FROM hardware_items 
                    WHERE price IS NOT NULL
                    GROUP BY category
                """)
                
                print("\nStatistics by category:")
                for row in cursor.fetchall():
                    print(f"  {row[0]}: {row[1]} items, avg price: ${row[2]:.2f}")
            
            else:
                print("No data found. Run a spider to populate the database.")
            
            conn.close()
            
        except Exception as e:
            print(f"Database query error: {e}")
    else:
        print(f"Database not found: {db_path}")
        print("Run a spider first to create and populate the database.")


def run_example_spider():
    """Example of running a spider programmatically"""
    print("\n=== Running Spider Example ===")
    
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add spiders to run
    # Note: In a real scenario, you would only run one spider at a time
    print("Spiders configured:")
    print("  - amazon_hardware")
    print("  - newegg_hardware") 
    print("  - gpu_hardware")
    
    print("\nTo run spiders, use command line:")
    print("  scrapy crawl amazon_hardware")
    print("  scrapy crawl gpu_hardware")
    
    # Uncomment to run programmatically (use with caution!)
    # process.crawl(AmazonHardwareSpider)
    # process.crawl(GPUHardwareSpider)
    # process.start()


def demonstrate_ethical_scraping():
    """Demonstrate ethical scraping features"""
    print("\n=== Ethical Scraping Features ===")
    
    from hardware_tracker.middlewares import EthicalDownloaderMiddleware
    
    middleware = EthicalDownloaderMiddleware()
    
    print("User Agent Rotation:")
    print(f"  Total user agents: {len(middleware.user_agents)}")
    print(f"  Sample user agent: {middleware.user_agents[0][:60]}...")
    
    print("\nRate Limiting:")
    print(f"  Domain delays: {list(middleware.domain_delays.keys())[:3]}...")
    
    print("\nRobots.txt Compliance:")
    print("  All spiders respect robots.txt by default")
    print("  Robots.txt middleware available for strict enforcement")
    
    print("\nSession Management:")
    print("  Cookies enabled for proper session handling")
    print("  Respectful headers automatically added")


def main():
    """Main demonstration function"""
    print("Hardware Tracker Template - Usage Examples")
    print("=" * 50)
    
    try:
        # Run all examples
        example_basic_usage()
        example_configuration()
        example_monitoring()
        example_custom_spider()
        demonstrate_ethical_scraping()
        example_database_query()
        run_example_spider()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install scrapy pyyaml")
        print("2. Run a spider: scrapy crawl amazon_hardware")
        print("3. Check exported data in exports/ directory")
        print("4. View database: sqlite3 hardware_data.db")
        print("5. Check logs in logs/ directory")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()