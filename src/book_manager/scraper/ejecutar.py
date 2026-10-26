"""Ejecuta el spider de Cúspide.

Se usa desde la carpeta src con:

    python -m book_manager.scraper.ejecutar

Scrapy no se puede ejecutar dos veces en el mismo proceso de Python, por
eso desde el menú conviene lanzarlo en un proceso aparte con este módulo.
"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from book_manager.scraper.spiders.cuspide_spider import CuspideSpider


def ejecutar_scraping() -> None:
    """Corre el CuspideSpider con la configuración de settings.py."""
    configuracion = Settings()
    configuracion.setmodule('book_manager.scraper.settings')
    proceso = CrawlerProcess(configuracion)
    proceso.crawl(CuspideSpider)
    proceso.start()


if __name__ == '__main__':
    ejecutar_scraping()
