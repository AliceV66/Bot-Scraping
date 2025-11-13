# PRODUCTION DEPLOYMENT GUIDE

**CRITICAL: Read this before deploying the Hardware Tracker to production!**

##  Pre-Production Checklist

###  Must Do Before Production:

1. **Verify HTTPCACHE_ENABLED = False**
   ```python
   # In settings.py
   HTTPCACHE_ENABLED = False  # CRITICAL: Get fresh price data
   ```

2. **Test SQLite Performance**
   ```bash
   # Test AllHardwareSpider with concurrent database writes
   scrapy crawl all_hardware
   ```

3. **Database Backup Strategy**
   ```bash
   # Schedule regular backups
   cp hardware_data.db hardware_data_backup_$(date +%Y%m%d).db
   ```

4. **Monitor for Database Locks**
   ```bash
   # Watch for "database is locked" errors in logs
   tail -f logs/scrapy.log | grep -i "locked"
   ```

5. **Test Individual Spiders First**
   ```bash
   scrapy crawl amazon_hardware    # Test single spider
   scrapy crawl gpu_hardware      # Test specialized spider
   scrapy crawl all_hardware      # Test concurrent spiders
   ```

##  Database Optimization

### For High-Volume Scraping:
- Use PostgreSQL instead of SQLite for better concurrency
- Implement connection pooling
- Monitor database growth and performance

### SQLite Performance Tuning:
```sql
-- In DatabaseStoragePipeline.create_tables():
-- Already implemented:
PRAGMA journal_mode=WAL;        -- Better concurrent access
PRAGMA busy_timeout=30000;      -- 30 second timeout
PRAGMA synchronous=OFF;         -- Faster writes (acceptable for scraper)
```

##  Production Monitoring

### Key Metrics to Monitor:
- **Database locks**: `grep -i "locked" logs/scrapy.log`
- **Response times**: Check scraping performance
- **Data freshness**: Verify prices are current, not cached
- **Error rates**: Monitor HTTP errors and parsing failures

### Recommended Alerts:
- Database connection failures
- Scraping timeout rates > 10%
- Cache hit rates > 0% (should be 0% in production)
- Concurrent spider conflicts

##  Security Considerations

### Rate Limiting:
- Already implemented with ethical scraping settings
- Monitor `CONCURRENT_REQUESTS_PER_DOMAIN = 1`
- Adjust delays based on server response

### Data Validation:
- Already implemented with `DataValidationPipeline`
- Monitor `data_quality_score` distribution
- Alert on low-quality scores

##  Deployment Workflow

1. **Development**: Use `HTTPCACHE_ENABLED = True`
2. **Staging**: Test with `HTTPCACHE_ENABLED = False`
3. **Production**: Keep `HTTPCACHE_ENABLED = False`

### Quick Production Check:
```bash
# Verify cache is disabled
grep -n "HTTPCACHE_ENABLED" settings.py
# Should show: HTTPCACHE_ENABLED = False

# Test single spider first
scrapy crawl amazon_hardware

# Monitor for database issues
tail -f logs/scrapy.log
```

## Ready for Production

After completing this checklist, your Hardware Tracker is ready for production use!