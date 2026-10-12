"""Carga de los datos iniciales desde la carpeta migrations/csv.

Desde el Sprint 2 los datos viven en la base de datos, así que la carga
inicial es la migración de los CSV del Sprint 1 (ver migrations.py): genera
los archivos .sql y carga las tablas sin duplicar registros.
"""

from __future__ import annotations

from pathlib import Path

from book_manager.database.connection import ConexionDB
from book_manager.migrations.migrations import migrar_datos

CARPETA_MIGRACIONES = Path(__file__).resolve().parent.parent / 'migrations'
CARPETA_CSV = CARPETA_MIGRACIONES / 'csv'
CARPETA_SQL = CARPETA_MIGRACIONES / 'sql'


def cargar_datos_iniciales(conexion: ConexionDB) -> None:
    """Migra los datos de migrations/csv a la base de datos.

    Args:
        conexion (ConexionDB): Conexión a la base donde se cargan los datos.
    """
    migrar_datos(str(CARPETA_CSV), str(CARPETA_SQL), conexion)
