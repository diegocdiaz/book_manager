"""Repositorios responsables de la persistencia de las entidades.

A partir del Sprint 2 los datos se guardan en la base de datos relacional
usando SQLAlchemy. Cada repositorio recibe una ConexionDB y trabaja dentro
de una transacción (context manager ``transaccion``) por operación: si algo
falla se hace rollback y no queda nada guardado a medias.

Los repositorios convierten los modelos de tabla (models.py) en las
entidades del dominio (entities.py) y viceversa, así los servicios y la
consola siguen trabajando con las mismas clases que en el Sprint 1.
"""

from __future__ import annotations

import abc
import datetime
import functools
from typing import (
    Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar,
)

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.base import ExecutableOption

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import (
    Auditoria,
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    PrecioWeb,
    Stock,
    TipoCotizacion,
)
from book_manager.models.models import (
    AuditoriaModelo,
    Base,
    CotizacionDolarModelo,
    EditorialModelo,
    GeneroModelo,
    LibroModelo,
    MonedaModelo,
    PrecioModelo,
    PrecioWebModelo,
    StockModelo,
    TipoCotizacionModelo,
)

T = TypeVar('T', bound=EntidadBase)
M = TypeVar('M', bound=Base)


# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------

class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios que manejan entidades con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad en el repositorio.

        Args:
            entidad (T): La entidad a crear.

        Returns:
            T: La entidad creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo ID.
        """

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a leer.

        Returns:
            Optional[T]: La entidad si se encuentra, None en caso contrario.
        """

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades del repositorio.

        Returns:
            List[T]: Una lista de todas las entidades.
        """

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente en el repositorio.

        Args:
            entidad (T): La entidad a actualizar (debe tener un ID existente).

        Returns:
            T: La entidad actualizada.

        Raises:
            ValueError: Si no se encuentra la entidad para actualizar.
        """

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad del repositorio por su ID.

        Args:
            id (int): El ID de la entidad a eliminar.

        Returns:
            bool: True si la entidad fue eliminada, False si no se encontró.
        """


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un nuevo registro de stock.

        Args:
            stock (Stock): El objeto Stock a crear.

        Returns:
            Stock: El objeto Stock creado.

        Raises:
            ValueError: Si ya existe un registro de stock para el mismo libro.
        """

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock.

        Returns:
            Optional[Stock]: El objeto Stock si se encuentra, None en caso contrario.
        """

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un registro de stock existente.

        Args:
            stock (Stock): El objeto Stock a actualizar (debe tener un libro_id existente).

        Returns:
            Stock: El objeto Stock actualizado.

        Raises:
            ValueError: Si no se encuentra el stock para actualizar.
        """

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock a eliminar.

        Returns:
            bool: True si el stock fue eliminado, False si no se encontró.
        """


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo RepositorioCotizacionDolar."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una nueva cotización de dólar.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar creado.

        Raises:
            ValueError: Si ya existe una cotización para el mismo tipo y fecha.
        """

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización (e.g., 'Oficial', 'Blue').
            fecha (datetime.date): La fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización si se encuentra, None en caso contrario.
        """

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones para un tipo específico.

        Args:
            tipo_id (int): El ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Una lista de cotizaciones históricas para el tipo dado.
        """

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización de dólar existente.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a actualizar.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.
        """

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (datetime.date): La fecha de la cotización a eliminar.

        Returns:
            bool: True si la cotización fue eliminada, False si no se encontró.
        """


# ---------------------------------------------------------------------------
# Conversión de modelos de tabla a entidades
# ---------------------------------------------------------------------------

def _a_genero(modelo: GeneroModelo) -> Genero:
    """Convierte una fila de la tabla generos en la entidad Genero."""
    return Genero(modelo.id, modelo.nombre)


def _a_editorial(modelo: EditorialModelo) -> Editorial:
    """Convierte una fila de la tabla editoriales en la entidad Editorial."""
    return Editorial(modelo.id, modelo.nombre, modelo.contacto)


def _a_moneda(modelo: MonedaModelo) -> Moneda:
    """Convierte una fila de la tabla monedas en la entidad Moneda."""
    return Moneda(modelo.id, modelo.codigo, modelo.nombre)


def _a_tipo(modelo: TipoCotizacionModelo) -> TipoCotizacion:
    """Convierte una fila de tipos_cotizacion en la entidad TipoCotizacion."""
    return TipoCotizacion(modelo.id, modelo.nombre)


def _a_libro(modelo: LibroModelo) -> Libro:
    """Convierte una fila de la tabla libros en la entidad Libro."""
    return Libro(modelo.id, modelo.isbn, modelo.titulo, modelo.autor,
                 _a_editorial(modelo.editorial), _a_genero(modelo.genero))


def _a_precio(modelo: PrecioModelo) -> Precio:
    """Convierte una fila de la tabla precios en la entidad Precio."""
    return Precio(modelo.id, _a_libro(modelo.libro),
                  _a_moneda(modelo.moneda), float(modelo.valor))


def _a_stock(modelo: StockModelo) -> Stock:
    """Convierte una fila de la tabla stock en la entidad Stock."""
    return Stock(modelo.id, _a_libro(modelo.libro), modelo.cantidad)


def _a_precio_web(modelo: PrecioWebModelo) -> PrecioWeb:
    """Convierte una fila de precios_web en la entidad PrecioWeb."""
    return PrecioWeb(modelo.id, _a_libro(modelo.libro), modelo.titulo,
                     modelo.isbn, modelo.url, float(modelo.precio),
                     modelo.fecha_extraccion)


def _a_auditoria(modelo: AuditoriaModelo) -> Auditoria:
    """Convierte una fila de la tabla auditoria en la entidad Auditoria."""
    return Auditoria(modelo.id, modelo.accion, modelo.fecha, modelo.detalles)


def _a_cotizacion(modelo: CotizacionDolarModelo) -> CotizacionDolar:
    """Convierte una fila de la tabla cotizaciones en CotizacionDolar."""
    return CotizacionDolar(modelo.id, _a_tipo(modelo.tipo), modelo.fecha,
                           float(modelo.valor_compra),
                           float(modelo.valor_venta))


# Códigos de error de PostgreSQL para los problemas de integridad
_MENSAJES_INTEGRIDAD = {
    '23505': 'Ya existe un registro con esos datos (valor repetido).',
    '23503': 'El registro se relaciona con otro que no existe o que está '
             'en uso.',
    '23502': 'Falta un dato obligatorio.',
    '23514': 'Hay un valor que no cumple las reglas de la tabla.',
}


def _traducir_errores_db(funcion):
    """Convierte los errores de integridad de la base en ValueError.

    La base de datos puede rechazar una operación aunque el repositorio no
    lo haya detectado antes (ISBN repetido, clave foránea inexistente,
    valor fuera de rango). Ese error sale de SQLAlchemy como
    IntegrityError; acá se transforma en ValueError con un mensaje claro,
    así los servicios y la consola lo manejan igual que las demás
    validaciones.

    Args:
        funcion: Método del repositorio que escribe en la base.

    Returns:
        El método envuelto.
    """
    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except IntegrityError as error:
            codigo = getattr(error.orig, 'pgcode', None)
            mensaje = _MENSAJES_INTEGRIDAD.get(
                codigo, 'La base de datos rechazó la operación.')
            raise ValueError(mensaje) from error
    return envoltura


def _siguiente_id(sesion: Session, modelo: Type[Base]) -> int:
    """Devuelve el máximo id de la tabla más uno."""
    maximo = sesion.scalar(select(func.max(modelo.id)))
    return (maximo or 0) + 1


# ---------------------------------------------------------------------------
# Repositorio genérico sobre la base de datos
# ---------------------------------------------------------------------------

class RepositorioDB(IRepositorio[T], Generic[T, M]):
    """Implementación genérica de IRepositorio sobre una tabla de la base.

    Las subclases indican el modelo de la tabla, cómo pasar de fila a
    entidad y qué columnas se guardan de cada entidad.
    """

    MODELO: Type[Base]

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @abc.abstractmethod
    def _a_entidad(self, modelo: M) -> T:
        """Construye la entidad a partir de la fila de la tabla."""

    @abc.abstractmethod
    def _columnas(self, entidad: T) -> Dict[str, Any]:
        """Devuelve los valores de las columnas a guardar de la entidad."""

    def _opciones_carga(self) -> Sequence[ExecutableOption]:
        """Relaciones que se traen en la misma consulta que la fila.

        Así no se hace una consulta extra por cada fila al convertirla en
        entidad. Por defecto no hay ninguna.
        """
        return []

    def _consulta(self):
        """SELECT de la tabla con sus relaciones, ordenado por id."""
        return (select(self.MODELO).options(*self._opciones_carga())
                .order_by(self.MODELO.id))

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID disponible en la tabla."""
        with self._conexion.transaccion() as sesion:
            return _siguiente_id(sesion, self.MODELO)

    @_traducir_errores_db
    def crear(self, entidad: T) -> T:
        with self._conexion.transaccion() as sesion:
            if sesion.get(self.MODELO, entidad.id) is not None:
                raise ValueError(
                    f'Ya existe {type(entidad).__name__} con id {entidad.id}.'
                )
            sesion.add(self.MODELO(id=entidad.id, **self._columnas(entidad)))
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        with self._conexion.transaccion() as sesion:
            modelo = sesion.scalar(
                self._consulta().where(self.MODELO.id == id)
            )
            return None if modelo is None else self._a_entidad(modelo)

    def leer_todos(self) -> List[T]:
        with self._conexion.transaccion() as sesion:
            modelos = sesion.scalars(self._consulta())
            return [self._a_entidad(m) for m in modelos]

    @_traducir_errores_db
    def actualizar(self, entidad: T) -> T:
        with self._conexion.transaccion() as sesion:
            modelo = sesion.get(self.MODELO, entidad.id)
            if modelo is None:
                raise ValueError(
                    f'No existe {type(entidad).__name__} con id {entidad.id}.'
                )
            for columna, valor in self._columnas(entidad).items():
                setattr(modelo, columna, valor)
        return entidad

    @_traducir_errores_db
    def eliminar(self, id: int) -> bool:
        with self._conexion.transaccion() as sesion:
            modelo = sesion.get(self.MODELO, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioGenero(RepositorioDB[Genero, GeneroModelo]):
    """Persistencia de géneros literarios (tabla generos)."""

    MODELO = GeneroModelo

    def _a_entidad(self, modelo: GeneroModelo) -> Genero:
        return _a_genero(modelo)

    def _columnas(self, entidad: Genero) -> Dict[str, Any]:
        return {'nombre': entidad.nombre}


class RepositorioEditorial(RepositorioDB[Editorial, EditorialModelo]):
    """Persistencia de editoriales (tabla editoriales)."""

    MODELO = EditorialModelo

    def _a_entidad(self, modelo: EditorialModelo) -> Editorial:
        return _a_editorial(modelo)

    def _columnas(self, entidad: Editorial) -> Dict[str, Any]:
        return {'nombre': entidad.nombre, 'contacto': entidad.contacto}


class RepositorioMoneda(RepositorioDB[Moneda, MonedaModelo]):
    """Persistencia de monedas (tabla monedas)."""

    MODELO = MonedaModelo

    def _a_entidad(self, modelo: MonedaModelo) -> Moneda:
        return _a_moneda(modelo)

    def _columnas(self, entidad: Moneda) -> Dict[str, Any]:
        return {'codigo': entidad.codigo, 'nombre': entidad.nombre}


class RepositorioTipoCotizacion(
        RepositorioDB[TipoCotizacion, TipoCotizacionModelo]):
    """Persistencia de tipos de cotización (tabla tipos_cotizacion)."""

    MODELO = TipoCotizacionModelo

    def _a_entidad(self, modelo: TipoCotizacionModelo) -> TipoCotizacion:
        return _a_tipo(modelo)

    def _columnas(self, entidad: TipoCotizacion) -> Dict[str, Any]:
        return {'nombre': entidad.nombre}


class RepositorioLibro(RepositorioDB[Libro, LibroModelo]):
    """Persistencia de libros (tabla libros)."""

    MODELO = LibroModelo

    def _opciones_carga(self) -> Sequence[ExecutableOption]:
        return [selectinload(LibroModelo.editorial),
                selectinload(LibroModelo.genero)]

    def _a_entidad(self, modelo: LibroModelo) -> Libro:
        return _a_libro(modelo)

    def _columnas(self, entidad: Libro) -> Dict[str, Any]:
        return {'isbn': entidad.isbn, 'titulo': entidad.titulo,
                'autor': entidad.autor,
                'editorial_id': entidad.editorial.id,
                'genero_id': entidad.genero.id}

    def leer_por_isbn(self, isbn: str) -> Optional[Libro]:
        """Busca un libro por su ISBN."""
        with self._conexion.transaccion() as sesion:
            modelo = sesion.scalar(
                self._consulta().where(LibroModelo.isbn == isbn.strip())
            )
            return None if modelo is None else _a_libro(modelo)


class RepositorioAuditoria(RepositorioDB[Auditoria, AuditoriaModelo]):
    """Persistencia de los registros de auditoría (tabla auditoria)."""

    MODELO = AuditoriaModelo

    def _a_entidad(self, modelo: AuditoriaModelo) -> Auditoria:
        return _a_auditoria(modelo)

    def _columnas(self, entidad: Auditoria) -> Dict[str, Any]:
        return {'accion': entidad.accion, 'fecha': entidad.fecha,
                'detalles': entidad.detalles}

    def leer_ultimos(self, cantidad: int) -> List[Auditoria]:
        """Devuelve los registros más recientes, del más nuevo al más viejo.

        Args:
            cantidad (int): Cantidad máxima de registros a devolver.

        Returns:
            List[Auditoria]: Los últimos registros de la auditoría.
        """
        with self._conexion.transaccion() as sesion:
            consulta = (select(AuditoriaModelo)
                        .order_by(AuditoriaModelo.id.desc())
                        .limit(cantidad))
            return [_a_auditoria(m) for m in sesion.scalars(consulta)]


class RepositorioPrecio(RepositorioDB[Precio, PrecioModelo]):
    """Persistencia de precios (tabla precios)."""

    MODELO = PrecioModelo

    def _opciones_carga(self) -> Sequence[ExecutableOption]:
        libro = selectinload(PrecioModelo.libro)
        return [libro.selectinload(LibroModelo.editorial),
                libro.selectinload(LibroModelo.genero),
                selectinload(PrecioModelo.moneda)]

    def _a_entidad(self, modelo: PrecioModelo) -> Precio:
        return _a_precio(modelo)

    def _columnas(self, entidad: Precio) -> Dict[str, Any]:
        return {'libro_id': entidad.libro.id,
                'moneda_id': entidad.moneda.id,
                'valor': entidad.valor}

    def leer_por_libro(self, libro_id: int) -> List[Precio]:
        """Devuelve los precios de un libro en todas sus monedas."""
        with self._conexion.transaccion() as sesion:
            consulta = self._consulta().where(
                PrecioModelo.libro_id == libro_id
            )
            return [_a_precio(m) for m in sesion.scalars(consulta)]


class RepositorioStock(IRepositorioStock):
    """Persistencia de stock (tabla stock). Un único registro por libro."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @staticmethod
    def _consulta():
        libro = selectinload(StockModelo.libro)
        return (select(StockModelo)
                .options(libro.selectinload(LibroModelo.editorial),
                         libro.selectinload(LibroModelo.genero))
                .order_by(StockModelo.id))

    @staticmethod
    def _buscar(sesion: Session, libro_id: int) -> Optional[StockModelo]:
        return sesion.scalar(
            select(StockModelo).where(StockModelo.libro_id == libro_id)
        )

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID disponible en la tabla."""
        with self._conexion.transaccion() as sesion:
            return _siguiente_id(sesion, StockModelo)

    @_traducir_errores_db
    def crear(self, stock: Stock) -> Stock:
        with self._conexion.transaccion() as sesion:
            if self._buscar(sesion, stock.libro.id) is not None:
                raise ValueError(
                    f'Ya existe stock para el libro {stock.libro.id}.'
                )
            sesion.add(StockModelo(id=stock.id, libro_id=stock.libro.id,
                                   cantidad=stock.cantidad))
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        with self._conexion.transaccion() as sesion:
            modelo = sesion.scalar(
                self._consulta().where(StockModelo.libro_id == libro_id)
            )
            return None if modelo is None else _a_stock(modelo)

    def leer_todos(self) -> List[Stock]:
        """Devuelve todos los registros de stock ordenados por ID."""
        with self._conexion.transaccion() as sesion:
            return [_a_stock(m) for m in sesion.scalars(self._consulta())]

    @_traducir_errores_db
    def actualizar(self, stock: Stock) -> Stock:
        with self._conexion.transaccion() as sesion:
            modelo = self._buscar(sesion, stock.libro.id)
            if modelo is None:
                raise ValueError(
                    f'No existe stock para el libro {stock.libro.id}.'
                )
            modelo.cantidad = stock.cantidad
        return stock

    @_traducir_errores_db
    def eliminar(self, libro_id: int) -> bool:
        with self._conexion.transaccion() as sesion:
            modelo = self._buscar(sesion, libro_id)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Persistencia del histórico de cotizaciones (clave: tipo + fecha)."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @staticmethod
    def _consulta():
        return (select(CotizacionDolarModelo)
                .options(selectinload(CotizacionDolarModelo.tipo)))

    @staticmethod
    def _buscar(sesion: Session, tipo_id: int,
                fecha: datetime.date) -> Optional[CotizacionDolarModelo]:
        return sesion.scalar(
            select(CotizacionDolarModelo).where(
                CotizacionDolarModelo.tipo_id == tipo_id,
                CotizacionDolarModelo.fecha == fecha,
            )
        )

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID disponible en la tabla."""
        with self._conexion.transaccion() as sesion:
            return _siguiente_id(sesion, CotizacionDolarModelo)

    @_traducir_errores_db
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self._conexion.transaccion() as sesion:
            if self._buscar(sesion, cotizacion.tipo.id,
                            cotizacion.fecha) is not None:
                raise ValueError(
                    f'Ya existe cotización {cotizacion.tipo} para '
                    f'{cotizacion.fecha}.'
                )
            sesion.add(CotizacionDolarModelo(
                id=cotizacion.id, tipo_id=cotizacion.tipo.id,
                fecha=cotizacion.fecha,
                valor_compra=cotizacion.valor_compra,
                valor_venta=cotizacion.valor_venta,
            ))
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        with self._conexion.transaccion() as sesion:
            modelo = sesion.scalar(self._consulta().where(
                CotizacionDolarModelo.tipo_id == tipo_id,
                CotizacionDolarModelo.fecha == fecha,
            ))
            return None if modelo is None else _a_cotizacion(modelo)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        with self._conexion.transaccion() as sesion:
            consulta = (self._consulta()
                        .where(CotizacionDolarModelo.tipo_id == tipo_id)
                        .order_by(CotizacionDolarModelo.fecha))
            return [_a_cotizacion(m) for m in sesion.scalars(consulta)]

    def leer_todos(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones ordenadas por fecha y tipo."""
        with self._conexion.transaccion() as sesion:
            consulta = self._consulta().order_by(
                CotizacionDolarModelo.fecha, CotizacionDolarModelo.tipo_id
            )
            return [_a_cotizacion(m) for m in sesion.scalars(consulta)]

    @_traducir_errores_db
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        with self._conexion.transaccion() as sesion:
            modelo = self._buscar(sesion, cotizacion.tipo.id,
                                  cotizacion.fecha)
            if modelo is None:
                raise ValueError(
                    f'No existe cotización {cotizacion.tipo} para '
                    f'{cotizacion.fecha}.'
                )
            modelo.valor_compra = cotizacion.valor_compra
            modelo.valor_venta = cotizacion.valor_venta
        return cotizacion

    @_traducir_errores_db
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        with self._conexion.transaccion() as sesion:
            modelo = self._buscar(sesion, tipo_id, fecha)
            if modelo is None:
                return False
            sesion.delete(modelo)
        return True


class IRepositorioPrecioWeb(abc.ABC):
    """Interfaz del repositorio de los precios extraídos del sitio."""

    @abc.abstractmethod
    def leer_ultima_extraccion(self) -> List[PrecioWeb]:
        """Devuelve los precios de la ejecución más reciente del scraper.

        Returns:
            List[PrecioWeb]: Los resultados que comparten la fecha de
                extracción más nueva. Vacía si el scraper nunca se ejecutó.
        """


class RepositorioPrecioWeb(IRepositorioPrecioWeb):
    """Lectura de la tabla precios_web, que llena el scraper."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    def leer_ultima_extraccion(self) -> List[PrecioWeb]:
        with self._conexion.transaccion() as sesion:
            ultima = sesion.scalar(
                select(func.max(PrecioWebModelo.fecha_extraccion)))
            if ultima is None:
                return []
            libro = selectinload(PrecioWebModelo.libro)
            consulta = (
                select(PrecioWebModelo)
                .options(libro.selectinload(LibroModelo.editorial),
                         libro.selectinload(LibroModelo.genero))
                .where(PrecioWebModelo.fecha_extraccion == ultima)
                .order_by(PrecioWebModelo.libro_id, PrecioWebModelo.id)
            )
            return [_a_precio_web(m) for m in sesion.scalars(consulta)]
