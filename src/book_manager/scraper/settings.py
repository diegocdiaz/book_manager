"""Configuración de Scrapy para el scraper de Cúspide."""

BOT_NAME = 'cuspide'

SPIDER_MODULES = ['book_manager.scraper.spiders']

# Se respeta el robots.txt del sitio y se espera 1 segundo entre pedidos
# para no cargar el servidor
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 2

ITEM_PIPELINES = {
    'book_manager.scraper.pipelines.ValidarLibroWebPipeline': 100,
    'book_manager.scraper.pipelines.GuardarLibroWebPipeline': 200,
}

LOG_LEVEL = 'INFO'
FEED_EXPORT_ENCODING = 'utf-8'
