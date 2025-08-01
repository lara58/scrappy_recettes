# Scrapy settings for recettes_scrapy project

BOT_NAME = "recettes_scrapy"

SPIDER_MODULES = ["recettes_scrapy.spiders"]
NEWSPIDER_MODULE = "recettes_scrapy.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = True

FEEDS = {
    'recettes.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 2,
    },
}

CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2

TELNETCONSOLE_ENABLED = False

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
