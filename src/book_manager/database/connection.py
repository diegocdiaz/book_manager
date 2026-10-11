"""Conexión a la base de datos del sistema Book Manager.

Se usa SQLAlchemy contra una base PostgreSQL de Supabase. La URL de conexión
tiene usuario y clave, por eso no se escribe en el código: se lee de la
variable de entorno DATABASE_URL.
"""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker


class ConexionDB:
    """Maneja la conexión a la base de datos usando SQLAlchemy."""

    def __init__(self, url: Optional[str] = None) -> None:
        """Crea el engine y la fábrica de sesiones.

        Args:
            url (Optional[str]): URL de conexión a la base. Si no se pasa,
                se toma de la variable de entorno DATABASE_URL.

        Raises:
            ValueError: Si no hay URL de conexión.
        """
        if url is None:
            url = os.getenv('DATABASE_URL')
        if not url:
            raise ValueError('Falta la URL de conexion (DATABASE_URL).')

        # Supabase da la URL como postgresql://, se indica el driver
        # psycopg2 para que no dependa de la versión de SQLAlchemy
        if url.startswith('postgresql://'):
            url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)

        # pool_pre_ping prueba la conexión antes de usarla, porque Supabase
        # corta las que quedan mucho tiempo sin usar
        self._engine = create_engine(url, pool_pre_ping=True)
        self._fabrica_sesiones = sessionmaker(bind=self._engine)

    @property
    def engine(self) -> Engine:
        """Devuelve el engine de SQLAlchemy."""
        return self._engine

    def obtener_sesion(self) -> Session:
        """Devuelve una sesión nueva para trabajar con la base."""
        return self._fabrica_sesiones()

    def probar_conexion(self) -> bool:
        """Hace una consulta simple para saber si la base responde.

        Returns:
            bool: True si se pudo conectar.
        """
        with self._engine.connect() as conexion:
            conexion.execute(text('SELECT 1'))
        return True

    def cerrar(self) -> None:
        """Cierra todas las conexiones abiertas del engine."""
        self._engine.dispose()
