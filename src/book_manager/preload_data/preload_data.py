"""Carga de los datos iniciales desde la carpeta migrations/csv.

Los datos se dan de alta con los servicios para que pasen por las mismas
validaciones que cuando se cargan a mano.
"""

from __future__ import annotations

import csv
import datetime
from pathlib import Path
from typing import Dict, List

from book_manager.repositories.repositories import DIRECTORIO_DATOS
from book_manager.services.services import ServiciosLibreria

CARPETA_CSV = Path(__file__).resolve().parent.parent / 'migrations' / 'csv'


def leer_csv(nombre: str) -> List[Dict[str, str]]:
    """Lee un archivo de migrations/csv y devuelve sus filas."""
    with open(CARPETA_CSV / nombre, 'r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def cargar_datos_iniciales(
        directorio: Path = DIRECTORIO_DATOS) -> ServiciosLibreria:
    """Borra los datos que haya y carga los de migrations/csv."""
    # borro los datos viejos para no duplicar registros
    if directorio.exists():
        for archivo in directorio.glob('*.csv'):
            archivo.unlink()

    servicios = ServiciosLibreria(directorio)

    # como se arranca de cero, los ids que se generan son los mismos que
    # los del csv, por eso en libros, precios, etc. se usan directamente
    for fila in leer_csv('generos.csv'):
        servicios.generos.crear(fila['nombre'])

    for fila in leer_csv('editoriales.csv'):
        servicios.editoriales.crear(fila['nombre'], fila['contacto'])

    for fila in leer_csv('monedas.csv'):
        servicios.monedas.crear(fila['codigo'], fila['nombre'])

    for fila in leer_csv('tipos_cotizacion.csv'):
        servicios.tipos_cotizacion.crear(fila['nombre'])

    for fila in leer_csv('libros.csv'):
        servicios.libros.crear(fila['isbn'], fila['titulo'], fila['autor'],
                               int(fila['editorial_id']),
                               int(fila['genero_id']))

    for fila in leer_csv('precios.csv'):
        servicios.precios.crear(int(fila['libro_id']),
                                int(fila['moneda_id']),
                                float(fila['valor']))

    for fila in leer_csv('stock.csv'):
        servicios.stock.crear(int(fila['libro_id']), int(fila['cantidad']))

    for fila in leer_csv('cotizaciones.csv'):
        servicios.cotizaciones.crear(
            int(fila['tipo_id']),
            datetime.date.fromisoformat(fila['fecha']),
            float(fila['valor_compra']),
            float(fila['valor_venta']),
        )

    return servicios
