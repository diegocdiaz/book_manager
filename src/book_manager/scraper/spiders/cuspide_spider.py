"""Spider que busca nuestros libros en el sitio de Cúspide.

Por cada libro del catálogo se busca su título en el sitio y se entra a
los 10 primeros resultados. De cada ficha se extrae el precio (en pesos y
en dólares), la url de la imagen, las formas de pago y la descripción.
Solo se buscan libros que están en nuestra base.
"""

import datetime
import json
from urllib.parse import quote_plus

import scrapy

from book_manager.database.connection import ConexionDB
from book_manager.repositories.repositories import RepositorioLibro
from book_manager.scraper.items import LibroWebItem
from book_manager.scraper.loaders import LibroWebLoader


class CuspideSpider(scrapy.Spider):
    """Scraper de precios de los libros del catálogo en Cúspide."""

    name = 'cuspide'
    allowed_domains = ['cuspide.com']

    URL_BUSQUEDA = 'https://cuspide.com/?s={}&post_type=product'
    MAX_RESULTADOS = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Todos los datos de una ejecución quedan con la misma fecha
        self.fecha_extraccion = datetime.datetime.now()

    async def start(self):
        """Arma un pedido de búsqueda por cada libro del catálogo."""
        conexion = ConexionDB()
        try:
            libros = RepositorioLibro(conexion).leer_todos()
        finally:
            conexion.cerrar()

        for libro in libros:
            # El buscador del sitio no encuentra los títulos con subtítulo
            # ("Murdle 1: resuelve un crimen"), por eso se busca solo la
            # parte anterior a los dos puntos
            titulo = libro.titulo.split(':')[0].strip()
            yield scrapy.Request(
                self.URL_BUSQUEDA.format(quote_plus(titulo)),
                callback=self.parse,
                cb_kwargs={'libro_id': libro.id},
            )

    def parse(self, response, libro_id):
        """Sigue los primeros resultados de la búsqueda de un libro."""
        # Si la búsqueda encuentra un solo producto, el sitio redirige
        # directamente a su ficha
        if response.css('h1.product-title'):
            yield from self.parse_libro(response, libro_id)
            return

        enlaces = response.css(
            '.woocommerce-loop-product__title a::attr(href)').getall()
        if not enlaces:
            self.logger.warning(f'Sin resultados para el libro {libro_id}')

        for enlace in enlaces[:self.MAX_RESULTADOS]:
            # dont_filter: el mismo producto puede aparecer en la búsqueda
            # de dos libros distintos y hay que guardarlo para los dos
            yield response.follow(
                enlace,
                callback=self.parse_libro,
                cb_kwargs={'libro_id': libro_id},
                dont_filter=True,
            )

    def parse_libro(self, response, libro_id):
        """Extrae los datos de la ficha de un libro."""
        producto = self.datos_producto(response)
        ofertas = producto.get('offers') or [{}]

        loader = LibroWebLoader(item=LibroWebItem(), response=response)
        loader.add_value('libro_id', libro_id)
        loader.add_value('fecha_extraccion', self.fecha_extraccion)
        loader.add_value('url', response.url)
        loader.add_css('titulo', 'h1.product-title::text')
        loader.add_value('isbn', producto.get('sku'))
        # El precio se toma del ld+json; si no está, del texto de la página
        loader.add_value('precio', ofertas[0].get('price'))
        loader.add_css('precio', '.product-page-price bdi::text')
        loader.add_xpath(
            'precio_usd', "//span[starts-with(text(), 'U$s')]/span/text()")
        loader.add_css('url_imagen',
                       '.woocommerce-product-gallery__image img::attr(src)')
        loader.add_css('formas_pago', '#contentPaymentsPopUpArg ::text')
        loader.add_value('descripcion', producto.get('description'))
        yield loader.load_item()

    def datos_producto(self, response):
        """Devuelve los datos del producto del bloque ld+json de la ficha.

        WooCommerce publica en la página un JSON (schema.org) con el ISBN
        (sku), el precio y la descripción del libro.

        Returns:
            dict: Los datos del producto, o un dict vacío si no están.
        """
        bloques = response.css(
            'script[type="application/ld+json"]::text').getall()
        for bloque in bloques:
            datos = json.loads(bloque)
            for elemento in datos.get('@graph', [datos]):
                if elemento.get('@type') == 'Product':
                    return elemento
        return {}
