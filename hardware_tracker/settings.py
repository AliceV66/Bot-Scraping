# Scrapy settings for hardware_tracker project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "hardware_tracker"

SPIDER_MODULES = ["hardware_tracker.spiders"]
NEWSPIDER_MODULE = "hardware_tracker.spiders"

ADDONS = {}


# =============================================================================
# ETHICAL SCRAPING SETTINGS
# =============================================================================

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "HardwareTracker/1.0 (+https://github.com/yourusername/hardware-tracker)"

# Obey robots.txt rules - ALWAYS keep this True for ethical scraping
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings for ethical scraping
CONCURRENT_REQUESTS = 8  # Overall concurrent requests
CONCURRENT_REQUESTS_PER_DOMAIN = 1  # Be very conservative per domain
DOWNLOAD_DELAY = 3  # Seconds between requests to same domain
DOWNLOAD_TIMEOUT = 30  # Request timeout in seconds

# Retry settings for handling temporary failures
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]  # Retry on these HTTP codes

# Retry with exponential backoff
RETRY_DELAY = 5

# Enable AutoThrottle for adaptive rate limiting
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5  # Start with 5 second delay
AUTOTHROTTLE_MAX_DELAY = 60  # Maximum delay of 60 seconds
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # Target 1 request per domain at a time
AUTOTHROTTLE_DEBUG = False  # Set to True to see throttle stats

# =============================================================================
# COOKIES AND SESSIONS
# =============================================================================

# Enable cookies for sites that require them
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Disable Telnet Console for security
TELNETCONSOLE_ENABLED = False

# =============================================================================
# REQUEST HEADERS
# =============================================================================

# Override the default request headers to be more user-like
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# =============================================================================
# SPIDER MIDDLEWARES
# =============================================================================

# Enable our ethical spider middleware
SPIDER_MIDDLEWARES = {
    "hardware_tracker.middlewares.EthicalSpiderMiddleware": 100,
}

# =============================================================================
# DOWNLOADER MIDDLEWARES
# =============================================================================

# Enable our ethical downloader middleware
DOWNLOADER_MIDDLEWARES = {
    "hardware_tracker.middlewares.EthicalDownloaderMiddleware": 100,
    # Optional: Uncomment if you want strict robots.txt compliance
    # "hardware_tracker.middlewares.RobotsTxtMiddleware": 200,
    # Optional: Enable HTTP caching to reduce server load
    # "scrapy.extensions.httpcache.HttpCacheMiddleware": 300,
}

# =============================================================================
# ITEM PIPELINES
# =============================================================================

# Configure item pipelines - order matters, lower numbers run first
ITEM_PIPELINES = {
    "hardware_tracker.pipelines.DataValidationPipeline": 100,   # Validate and clean data
    "hardware_tracker.pipelines.DatabaseStoragePipeline": 200,   # Store in SQLite database
    "hardware_tracker.pipelines.ExportPipeline": 300,           # Export to JSON/CSV
    "hardware_tracker.pipelines.HardwareTrackerPipeline": 400,   # Final processing
}

# =============================================================================
# FEEDS EXPORT SETTINGS
# =============================================================================

# Feed export settings for automated data output
FEEDS = {
    "exports/hardware_%(time)s.json": {
        "format": "json",
        "encoding": "utf8",
        "overwrite": False,
        "indent": 2,
        "export_empty_fields": True,
    },
    "exports/hardware_%(time)s.csv": {
        "format": "csv",
        "encoding": "utf8",
        "overwrite": False,
        "include_headers_line": True,
    }
}

# Export formats configuration
EXPORT_FORMATS = ["json", "csv"]

# =============================================================================
# DATABASE SETTINGS
# =============================================================================

# SQLite database for storing scraped data
DATABASE_URL = "hardware_data.db"

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

# Configure logging
LOG_LEVEL = "INFO"  # Options: CRITICAL, ERROR, WARNING, INFO, DEBUG
LOG_FILE = "logs/scrapy.log"

# Create logs directory
import os
os.makedirs("logs", exist_ok=True)

# =============================================================================
# MEMORY USAGE SETTINGS
# =============================================================================

# Settings to prevent memory issues during large scrapes
MEMUSAGE_ENABLED = True
MEMUSAGE_CHECK_INTERVAL = 60  # Check memory every 60 seconds
MEMUSAGE_NOTIFY_MAIL = []     # Email notifications (optional)
MEMUSAGE_WARNING_MB = 512     # Warning if memory exceeds 512MB

# =============================================================================
# HTTPCACHE SETTINGS (OPTIONAL)
# =============================================================================

# ⚠️ CRITICAL: For production price tracking, keep this DISABLED to get fresh data
# ⚠️ Only enable during development to avoid overwhelming servers with testing
# ⚠️ Outdated cached data = wrong prices = broken price tracking service
HTTPCACHE_ENABLED = False  # Set to True ONLY for development/testing
HTTPCACHE_EXPIRATION_SECS = 3600  # Cache for 1 hour
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [429, 500, 502, 503, 504]  # Don't cache errors
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
HTTPCACHE_IGNORE_SCHEMES = ["file", "s3", "gs"]

# =============================================================================
# EXTENSIONS
# =============================================================================

# Disable some extensions to reduce overhead
EXTENSIONS = {
    "scrapy.extensions.corestats.CoreStats": None,  # Disable core stats
    "scrapy.extensions.telnet.TelnetConsole": None,  # Disable telnet console
}

# Enable useful extensions
EXTENSIONS.update({
    "scrapy.extensions.closespider.CloseSpider": 10,
    "scrapy.extensions.memusage.MemoryUsage": None,  # Already configured above
})

# Close spider conditions
CLOSESPIDER_ITEMCOUNT = 10000  # Close after scraping 10,000 items
CLOSESPIDER_TIMEOUT = 3600     # Close after 1 hour
CLOSESPIDER_ERRORCOUNT = 100   # Close after 100 errors

# =============================================================================
# DNS CACHE SETTINGS
# =============================================================================

# Enable DNS caching to reduce DNS lookups
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000  # Cache up to 10,000 DNS entries

# =============================================================================
# DEPTH CRAWLING SETTINGS
# =============================================================================

# Limit crawling depth to prevent infinite loops
DEPTH_LIMIT = 3  # Maximum depth to crawl
DEPTH_STATS = True  # Track depth statistics

# =============================================================================
# UNIVERSAL SETTINGS
# =============================================================================

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# Additional settings for better performance and reliability
RANDOMIZE_DOWNLOAD_DELAY = True  # Add randomness to download delays
COOKIES_DEBUG = False  # Keep cookies debug off for production

# =============================================================================
# PROXY SETTINGS (OPTIONAL)
# =============================================================================

# If you want to use proxies, uncomment and configure below
# DOWNLOADER_MIDDLEWARES.update({
#     "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
#     "myproject.middlewares.RotateUserAgentMiddleware": 400,
#     "myproject.middlewares.ProxyMiddleware": 410,
# })

# List of proxy URLs (if using proxies)
# PROXY_LIST = ["http://proxy1:port", "http://proxy2:port"]

# =============================================================================
# CRAWLERA SETTINGS (OPTIONAL)
# =============================================================================

# If using Scrapy Cloud or Crawlera for smart proxy management
# CRAWLERA_ENABLED = True
# CRAWLERA_APIKEY = "your_api_key"
# CRAWLERA_APPID = "your_app_id"

# =============================================================================
# MORGAN SETTINGS (OPTIONAL)
# =============================================================================

# For detailed request/response logging
# MORGAN_LOG_LEVEL = "DEBUG"
# MORGAN_FORMAT = "%(method)s %(url)s %(status)s %(time).2fs %(length)s %(referer)s"
