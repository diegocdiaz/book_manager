"""Loaders del scraper: limpian los datos antes de cargarlos en el item.

Cada campo tiene un procesador de entrada (se aplica a cada valor que se
extrae de la página) y uno de salida (arma el valor final del campo).
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader


def limpiar_texto(texto: str) -> Optional[str]:
    """Saca los espacios de más (también los &nbsp;) de un texto.

    Returns:
        Optional[str]: El texto limpio, o None si queda vacío (así el loader
        lo descarta).
    """
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto or None


def a_numero(texto: str) -> Optional[Decimal]:
    """Convierte un precio del sitio en número.

    El sitio muestra los precios con formato argentino ("$ 42.500,00" o
    "27,42"), pero en los datos ld+json vienen con punto decimal
    ("42500.00"). Si el texto tiene coma, los puntos son de miles.

    Returns:
        Optional[Decimal]: El precio, o None si el texto no es un número.
    """
    texto = re.sub(r'[^\d.,]', '', texto)
    if ',' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def forma_de_pago(texto: str) -> Optional[str]:
    """Se queda solo con los renglones de la lista de formas de pago.

    En el cuadro de medios de pago cada forma de pago empieza con ">"; el
    resto del texto es una explicación sobre la seguridad de los pagos.
    """
    texto = texto.strip()
    if not texto.startswith('>'):
        return None
    return limpiar_texto(texto.lstrip('> '))


def sacar_encabezado(texto: str) -> str:
    """Saca el "Sinopsis del producto" con el que empieza la descripción."""
    return re.sub(r'^Sinopsis del producto', '', texto.strip())


class LibroWebLoader(ItemLoader):
    """Loader de LibroWebItem.

    Por defecto se limpia el texto y se toma el primer valor encontrado.
    """

    default_input_processor = MapCompose(limpiar_texto)
    default_output_processor = TakeFirst()

    # libro_id y fecha_extraccion los pone el spider, no hay que limpiarlos
    libro_id_in = MapCompose()
    fecha_extraccion_in = MapCompose()

    precio_in = MapCompose(a_numero)
    precio_usd_in = MapCompose(a_numero)

    formas_pago_in = MapCompose(forma_de_pago)
    formas_pago_out = Join('\n')

    descripcion_in = MapCompose(sacar_encabezado, limpiar_texto)
