"""Pipelines del scraper: procesan cada item que devuelve el spider.

Se ejecutan en el orden de ITEM_PIPELINES (settings.py): primero se valida
el item y después se guarda en la base de datos.
"""

from scrapy.exceptions import DropItem

from book_manager.database.connection import ConexionDB
from book_manager.models.models import PrecioWebModelo, crear_tablas


class ValidarLibroWebPipeline:
    """Descarta los items que no sirven para comparar precios."""

    def process_item(self, item):
        if item.get('precio') is None:
            raise DropItem(f"Sin precio: {item.get('url')}")
        if not item.get('titulo'):
            raise DropItem(f"Sin título: {item.get('url')}")
        return item


class GuardarLibroWebPipeline:
    """Guarda cada item en la tabla precios_web."""

    def open_spider(self):
        self.conexion = ConexionDB()
        # Si la tabla precios_web todavía no existe, se crea
        crear_tablas(self.conexion.engine)

    def close_spider(self):
        self.conexion.cerrar()

    def process_item(self, item):
        with self.conexion.transaccion() as sesion:
            sesion.add(PrecioWebModelo(**item))
        return item
