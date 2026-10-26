"""Modelos de las tablas de la base de datos del sistema Book Manager.

Cada clase representa una tabla y define sus columnas, tipos de datos y
relaciones. Los nombres de las tablas coinciden con los de los archivos CSV
del Sprint 1, que se migran a estas tablas.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Engine,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos de tabla."""


class GeneroModelo(Base):
    """Tabla de géneros literarios."""

    __tablename__ = 'generos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)

    libros: Mapped[List[LibroModelo]] = relationship(back_populates='genero')


class EditorialModelo(Base):
    """Tabla de editoriales."""

    __tablename__ = 'editoriales'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True)
    contacto: Mapped[Optional[str]] = mapped_column(String(255))

    libros: Mapped[List[LibroModelo]] = relationship(
        back_populates='editorial'
    )


class MonedaModelo(Base):
    """Tabla de monedas en las que se expresan los precios."""

    __tablename__ = 'monedas'

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(3), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))

    precios: Mapped[List[PrecioModelo]] = relationship(
        back_populates='moneda'
    )


class TipoCotizacionModelo(Base):
    """Tabla de tipos de cotización del dólar (Oficial, Blue, MEP, etc.)."""

    __tablename__ = 'tipos_cotizacion'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)

    cotizaciones: Mapped[List[CotizacionDolarModelo]] = relationship(
        back_populates='tipo'
    )


class LibroModelo(Base):
    """Tabla de libros del catálogo."""

    __tablename__ = 'libros'

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    titulo: Mapped[str] = mapped_column(String(255))
    autor: Mapped[str] = mapped_column(String(255))
    editorial_id: Mapped[int] = mapped_column(ForeignKey('editoriales.id'))
    genero_id: Mapped[int] = mapped_column(ForeignKey('generos.id'))

    editorial: Mapped[EditorialModelo] = relationship(back_populates='libros')
    genero: Mapped[GeneroModelo] = relationship(back_populates='libros')
    precios: Mapped[List[PrecioModelo]] = relationship(back_populates='libro')
    # Relación 1 a 1: un libro tiene a lo sumo un registro de stock
    stock: Mapped[Optional[StockModelo]] = relationship(
        back_populates='libro', uselist=False
    )
    precios_web: Mapped[List[PrecioWebModelo]] = relationship(
        back_populates='libro'
    )


class PrecioModelo(Base):
    """Tabla de precios de un libro en una moneda."""

    __tablename__ = 'precios'
    __table_args__ = (
        CheckConstraint('valor >= 0', name='ck_precios_valor'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey('libros.id'))
    moneda_id: Mapped[int] = mapped_column(ForeignKey('monedas.id'))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    libro: Mapped[LibroModelo] = relationship(back_populates='precios')
    moneda: Mapped[MonedaModelo] = relationship(back_populates='precios')


class StockModelo(Base):
    """Tabla con la cantidad disponible de cada libro."""

    __tablename__ = 'stock'
    __table_args__ = (
        CheckConstraint('cantidad >= 0', name='ck_stock_cantidad'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey('libros.id'), unique=True)
    cantidad: Mapped[int]

    libro: Mapped[LibroModelo] = relationship(back_populates='stock')


class CotizacionDolarModelo(Base):
    """Tabla del histórico de cotizaciones del dólar."""

    __tablename__ = 'cotizaciones'
    __table_args__ = (
        CheckConstraint('valor_compra >= 0', name='ck_cotiz_compra'),
        CheckConstraint('valor_venta >= 0', name='ck_cotiz_venta'),
        # Una sola cotización por tipo de dólar y por día
        UniqueConstraint('tipo_id', 'fecha', name='uq_cotiz_tipo_fecha'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_id: Mapped[int] = mapped_column(ForeignKey('tipos_cotizacion.id'))
    fecha: Mapped[datetime.date] = mapped_column(Date)
    valor_compra: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    valor_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    tipo: Mapped[TipoCotizacionModelo] = relationship(
        back_populates='cotizaciones'
    )


class PrecioWebModelo(Base):
    """Tabla con los datos de los libros extraídos del sitio de Cúspide.

    Cada fila es un resultado de la búsqueda por título de uno de nuestros
    libros. Se guarda la fecha de extracción para poder comparar los precios
    de cada ejecución del scraper.
    """

    __tablename__ = 'precios_web'

    id: Mapped[int] = mapped_column(primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey('libros.id'))
    titulo: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[Optional[str]] = mapped_column(String(20))
    url: Mapped[str] = mapped_column(String(500))
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    precio_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    url_imagen: Mapped[Optional[str]] = mapped_column(String(500))
    formas_pago: Mapped[Optional[str]] = mapped_column(Text)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    fecha_extraccion: Mapped[datetime.datetime] = mapped_column(DateTime)

    libro: Mapped[LibroModelo] = relationship(back_populates='precios_web')


def crear_tablas(engine: Engine) -> None:
    """Crea en la base las tablas definidas que todavía no existan.

    Args:
        engine (Engine): Engine de SQLAlchemy conectado a la base.
    """
    Base.metadata.create_all(engine)
    