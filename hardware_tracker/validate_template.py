#!/usr/bin/env python3
"""
Quick validation test for the hardware tracker template.
Run this script to test if all components are working correctly.
"""

import sys
import os
import time
import inspect
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import hardware_tracker
        print("  ✓ Package import successful")
    except ImportError as e:
        print(f"  ✗ Package import failed: {e}")
        return False
    
    # Test core components
    modules_to_test = [
        'hardware_tracker.items',
        'hardware_tracker.middlewares', 
        'hardware_tracker.pipelines',
        'hardware_tracker.settings',
        'hardware_tracker.config',
        'hardware_tracker.monitoring',
        'hardware_tracker.spiders.base_spider',
        'hardware_tracker.spiders.amazon_spider',
        'hardware_tracker.spiders.newegg_spider',
        'hardware_tracker.spiders.specialized_spiders'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except ImportError as e:
            print(f"  ✗ {module_name}: {e}")
            return False
    
    return True

def test_class_definitions():
    """Test that key classes are properly defined"""
    print("\nTesting class definitions...")
    
    # Test items
    try:
        from hardware_tracker.items import HardwareTrackerItem, PriceHistoryItem
        print("  ✓ HardwareTrackerItem classes defined")
    except ImportError as e:
        print(f"  ✗ Item classes: {e}")
        return False
    
    # Test middlewares
    try:
        from hardware_tracker.middlewares import EthicalSpiderMiddleware, EthicalDownloaderMiddleware
        print("  ✓ Ethical scraping middleware classes defined")
    except ImportError as e:
        print(f"  ✗ Middleware classes: {e}")
        return False
    
    # Test pipelines
    try:
        from hardware_tracker.pipelines import DataValidationPipeline, DatabaseStoragePipeline
        print("  ✓ Pipeline classes defined")
    except ImportError as e:
        print(f"  ✗ Pipeline classes: {e}")
        return False
    
    # Test spiders
    try:
        from hardware_tracker.spiders.base_spider import BaseHardwareSpider
        from hardware_tracker.spiders.amazon_spider import AmazonHardwareSpider
        print("  ✓ Spider classes defined")
    except ImportError as e:
        print(f"  ✗ Spider classes: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration management"""
    print("\nTesting configuration...")
    
    try:
        from hardware_tracker.config import ConfigManager, get_config
        
        # Test config creation
        config = get_config()
        print("  ✓ Configuration manager created")
        
        # Test getting configs
        spider_config = config.get_spider_config('amazon_hardware')
        print(f"  ✓ Retrieved spider config: {spider_config.name}")
        
        rate_config = config.get_rate_limit_config()
        print(f"  ✓ Retrieved rate limit config with {len(rate_config.domains)} domains")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False

def test_monitoring():
    """Test monitoring and logging"""
    print("\nTesting monitoring...")
    
    try:
        from hardware_tracker.monitoring import CrawlMonitor, get_monitor
        
        monitor = get_monitor()
        print("  ✓ Monitoring system created")
        
        # Test crawl tracking
        crawl_id = monitor.start_crawl("test_spider")
        print(f"  ✓ Started crawl tracking: {crawl_id[:8]}")
        
        stats = monitor.end_crawl(crawl_id)
        if stats:
            print(f"  ✓ Ended crawl tracking: {stats.spider_name}")
        
        return True
    except Exception as e:
        print(f"  ✗ Monitoring test failed: {e}")
        return False

def test_spider_instantiation():
    """Test spider instantiation"""
    print("\nTesting spider instantiation...")
    
    try:
        # Test base spider
        from hardware_tracker.spiders.base_spider import BaseHardwareSpider
        
        spider = BaseHardwareSpider()
        print(f"  ✓ Base spider created: {spider.name}")
        print(f"    - Start URLs: {len(spider.start_urls)}")
        print(f"    - Allowed domains: {len(spider.allowed_domains)}")
        
        # Test specialized spider
        from hardware_tracker.spiders.specialized_spiders import GPUHardwareSpider
        
        gpu_spider = GPUHardwareSpider()
        print(f"  ✓ GPU spider created: {gpu_spider.name}")
        
        return True
    except Exception as e:
        print(f"  ✗ Spider instantiation failed: {e}")
        return False

def test_item_creation():
    """Test item creation and validation"""
    print("\nTesting item creation...")
    
    try:
        from hardware_tracker.items import HardwareTrackerItem
        
        # Create a test item
        item = HardwareTrackerItem()
        item['name'] = "Test GPU"
        item['brand'] = "TestBrand"
        item['price'] = 299.99
        item['source_url'] = "https://example.com/test"
        item['category'] = "GPU"
        
        print(f"  ✓ Created test item with fields: {list(item.keys())[:5]}...")
        
        return True
    except Exception as e:
        print(f"  ✗ Item creation failed: {e}")
        return False

def test_directory_structure():
    """Test that all expected files exist"""
    print("\nTesting directory structure...")
    
    expected_files = [
        'hardware_tracker/__init__.py',
        'hardware_tracker/items.py',
        'hardware_tracker/middlewares.py',
        'hardware_tracker/pipelines.py',
        'hardware_tracker/settings.py',
        'hardware_tracker/config.py',
        'hardware_tracker/monitoring.py',
        'hardware_tracker/spiders/__init__.py',
        'hardware_tracker/spiders/base_spider.py',
        'hardware_tracker/spiders/amazon_spider.py',
        'hardware_tracker/spiders/newegg_spider.py',
        'hardware_tracker/spiders/specialized_spiders.py',
        'hardware_tracker/README.md',
        'hardware_tracker/examples.py',
        'hardware_tracker/requirements.txt'
    ]
    
    all_good = True
    for file_path in expected_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ Missing: {file_path}")
            all_good = False
    
    return all_good

def run_validation():
    """Run all validation tests"""
    print("Hardware Tracker Template Validation")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Class Definition Test", test_class_definitions),
        ("Configuration Test", test_configuration),
        ("Monitoring Test", test_monitoring),
        ("Spider Instantiation Test", test_spider_instantiation),
        ("Item Creation Test", test_item_creation),
        ("Directory Structure Test", test_directory_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        start_time = time.time()
        success = test_func()
        duration = time.time() - start_time
        
        results.append((test_name, success, duration))
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success, duration in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:30} {status:4} ({duration:.2f}s)")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Template is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run a spider: scrapy crawl amazon_hardware")
        print("3. View results in exports/ and logs/ directories")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)