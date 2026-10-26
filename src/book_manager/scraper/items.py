"""Items del scraper: los datos que se extraen de cada libro de Cúspide."""

import scrapy


class LibroWebItem(scrapy.Item):
    """Datos de un libro tal como aparecen en el sitio de Cúspide.

    Los campos coinciden con las columnas de la tabla precios_web, así el
    pipeline los guarda directamente.
    """

    libro_id = scrapy.Field()  # id de nuestro libro que se buscó
    titulo = scrapy.Field()
    isbn = scrapy.Field()
    url = scrapy.Field()
    precio = scrapy.Field()  # precio en pesos
    precio_usd = scrapy.Field()
    url_imagen = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    fecha_extraccion = scrapy.Field()
