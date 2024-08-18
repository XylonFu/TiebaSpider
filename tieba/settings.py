# 爬虫设置
BOT_NAME = "tieba"
SPIDER_MODULES = ["tieba.spiders"]
NEWSPIDER_MODULE = "tieba.spiders"

# 管道和中间件设置
ITEM_PIPELINES = {
    'tieba.pipelines.TiebaPipeline': 300,
}
DOWNLOADER_MIDDLEWARES = {
    'tieba.middlewares.CustomProxyMiddleware': 345,
}

# 代理API配置
PROXY_API_SECRET = 'your_api_secret'
PROXY_API_SIGN = 'your_api_sign'
PROXY_API_KEY = 'your_api_key'

# 请求和下载设置
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 0.1
DOWNLOAD_TIMEOUT = 10
CONCURRENT_REQUESTS = 10

# MySQL 相关设置
MYSQL_DB_NAME = 'tieba'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_HOST = 'localhost'

# Scrapy-Redis 相关设置
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# REDIS_URL = 'redis://localhost:6379'
# SCHEDULER_PERSIST = True
# REDIS_START_URLS_KEY = 'tieba:requests'
# DUPEFILTER_KEY = 'tieba:dupefilter'

# 其他设置
LOG_LEVEL = "INFO"
