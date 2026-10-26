"""Pipelines del scraper: procesan cada item que devuelve el spider.

Se ejecutan en el orden de ITEM_PIPELINES (settings.py): primero se valida
el item y después se guarda en la base de datos. Al terminar, la ejecución
del scraping queda registrada en la tabla de auditoría.
"""

from scrapy.exceptions import DropItem

from book_manager.database.connection import ConexionDB
from book_manager.models.models import PrecioWebModelo, crear_tablas
from book_manager.repositories.repositories import RepositorioAuditoria
from book_manager.services.services import ServicioAuditoria


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
        # Si las tablas precios_web o auditoria todavía no existen, se crean
        crear_tablas(self.conexion.engine)
        self.auditoria = ServicioAuditoria(RepositorioAuditoria(self.conexion))
        self.guardados = 0

    def close_spider(self):
        self.auditoria.registrar(
            'Ejecucion del scraping',
            f'Se guardaron {self.guardados} resultado(s) de Cuspide en '
            'precios_web.')
        self.conexion.cerrar()

    def process_item(self, item):
        with self.conexion.transaccion() as sesion:
            sesion.add(PrecioWebModelo(**item))
        self.guardados += 1
        return item
