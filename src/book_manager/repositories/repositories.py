"""Repositorios responsables de la persistencia de las entidades.

Cada entidad se guarda en un archivo CSV propio dentro de la carpeta
``data``. Los repositorios mantienen una copia en memoria y reescriben el
archivo en cada operación de escritura (crear, actualizar, eliminar).
"""

from __future__ import annotations

import abc
import csv
import datetime
from pathlib import Path
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)

T = TypeVar('T', bound=EntidadBase)

DIRECTORIO_DATOS = Path(__file__).resolve().parent.parent / 'data'


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
# Persistencia en archivos CSV
# ---------------------------------------------------------------------------

class ArchivoCSV:
    """Lee y escribe filas de un archivo CSV con encabezado fijo.

    Attributes:
        ruta (Path): Ruta del archivo CSV.
        campos (List[str]): Nombres de las columnas.
    """

    def __init__(self, nombre_archivo: str, campos: List[str],
                 directorio: Path = DIRECTORIO_DATOS) -> None:
        self._ruta = directorio / nombre_archivo
        self._campos = campos

    @property
    def ruta(self) -> Path:
        """Path: Ruta del archivo CSV."""
        return self._ruta

    def leer(self) -> List[Dict[str, str]]:
        """Devuelve todas las filas del archivo (lista vacía si no existe)."""
        if not self._ruta.exists():
            return []
        with self._ruta.open('r', encoding='utf-8', newline='') as archivo:
            return list(csv.DictReader(archivo))

    def escribir(self, filas: List[Dict[str, object]]) -> None:
        """Reescribe el archivo completo con las filas recibidas."""
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        with self._ruta.open('w', encoding='utf-8', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=self._campos)
            escritor.writeheader()
            escritor.writerows(filas)


class RepositorioCSV(IRepositorio[T]):
    """Implementación genérica de IRepositorio persistida en un CSV.

    Las subclases definen cómo convertir una entidad en fila y viceversa.
    """

    NOMBRE_ARCHIVO: str = ''
    CAMPOS: List[str] = []

    def __init__(self, directorio: Path = DIRECTORIO_DATOS) -> None:
        self._archivo = ArchivoCSV(self.NOMBRE_ARCHIVO, self.CAMPOS, directorio)
        self._entidades: Dict[int, T] = {}
        self._cargar()

    @abc.abstractmethod
    def _a_fila(self, entidad: T) -> Dict[str, object]:
        """Convierte una entidad en un diccionario serializable."""

    @abc.abstractmethod
    def _desde_fila(self, fila: Dict[str, str]) -> T:
        """Construye una entidad a partir de una fila del CSV."""

    def _cargar(self) -> None:
        """Carga en memoria las entidades guardadas en el archivo."""
        for fila in self._archivo.leer():
            entidad = self._desde_fila(fila)
            self._entidades[entidad.id] = entidad

    def _guardar(self) -> None:
        """Persiste en el archivo el estado actual del repositorio."""
        self._archivo.escribir(
            [self._a_fila(e) for e in self.leer_todos()]
        )

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID disponible."""
        return max(self._entidades, default=0) + 1

    def crear(self, entidad: T) -> T:
        if entidad.id in self._entidades:
            raise ValueError(
                f'Ya existe {type(entidad).__name__} con id {entidad.id}.'
            )
        self._entidades[entidad.id] = entidad
        self._guardar()
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        return self._entidades.get(id)

    def leer_todos(self) -> List[T]:
        return sorted(self._entidades.values(), key=lambda e: e.id)

    def actualizar(self, entidad: T) -> T:
        if entidad.id not in self._entidades:
            raise ValueError(
                f'No existe {type(entidad).__name__} con id {entidad.id}.'
            )
        self._entidades[entidad.id] = entidad
        self._guardar()
        return entidad

    def eliminar(self, id: int) -> bool:
        if id not in self._entidades:
            return False
        del self._entidades[id]
        self._guardar()
        return True


def _buscar(repositorio: IRepositorio[T], id_: int, nombre: str) -> T:
    """Obtiene una entidad relacionada o lanza error si no existe."""
    entidad = repositorio.leer_por_id(id_)
    if entidad is None:
        raise ValueError(f'No existe {nombre} con id {id_}.')
    return entidad


class RepositorioGenero(RepositorioCSV[Genero]):
    """Persistencia de géneros literarios."""

    NOMBRE_ARCHIVO = 'generos.csv'
    CAMPOS = ['id', 'nombre']

    def _a_fila(self, entidad: Genero) -> Dict[str, object]:
        return {'id': entidad.id, 'nombre': entidad.nombre}

    def _desde_fila(self, fila: Dict[str, str]) -> Genero:
        return Genero(int(fila['id']), fila['nombre'])


class RepositorioEditorial(RepositorioCSV[Editorial]):
    """Persistencia de editoriales."""

    NOMBRE_ARCHIVO = 'editoriales.csv'
    CAMPOS = ['id', 'nombre', 'contacto']

    def _a_fila(self, entidad: Editorial) -> Dict[str, object]:
        return {'id': entidad.id, 'nombre': entidad.nombre,
                'contacto': entidad.contacto or ''}

    def _desde_fila(self, fila: Dict[str, str]) -> Editorial:
        return Editorial(int(fila['id']), fila['nombre'],
                         fila['contacto'] or None)


class RepositorioMoneda(RepositorioCSV[Moneda]):
    """Persistencia de monedas."""

    NOMBRE_ARCHIVO = 'monedas.csv'
    CAMPOS = ['id', 'codigo', 'nombre']

    def _a_fila(self, entidad: Moneda) -> Dict[str, object]:
        return {'id': entidad.id, 'codigo': entidad.codigo,
                'nombre': entidad.nombre}

    def _desde_fila(self, fila: Dict[str, str]) -> Moneda:
        return Moneda(int(fila['id']), fila['codigo'], fila['nombre'])


class RepositorioTipoCotizacion(RepositorioCSV[TipoCotizacion]):
    """Persistencia de tipos de cotización del dólar."""

    NOMBRE_ARCHIVO = 'tipos_cotizacion.csv'
    CAMPOS = ['id', 'nombre']

    def _a_fila(self, entidad: TipoCotizacion) -> Dict[str, object]:
        return {'id': entidad.id, 'nombre': entidad.nombre}

    def _desde_fila(self, fila: Dict[str, str]) -> TipoCotizacion:
        return TipoCotizacion(int(fila['id']), fila['nombre'])


class RepositorioLibro(RepositorioCSV[Libro]):
    """Persistencia de libros. Resuelve editorial y género por ID."""

    NOMBRE_ARCHIVO = 'libros.csv'
    CAMPOS = ['id', 'isbn', 'titulo', 'autor', 'editorial_id', 'genero_id']

    def __init__(self, repo_editorial: RepositorioEditorial,
                 repo_genero: RepositorioGenero,
                 directorio: Path = DIRECTORIO_DATOS) -> None:
        self._repo_editorial = repo_editorial
        self._repo_genero = repo_genero
        super().__init__(directorio)

    def _a_fila(self, entidad: Libro) -> Dict[str, object]:
        return {'id': entidad.id, 'isbn': entidad.isbn,
                'titulo': entidad.titulo, 'autor': entidad.autor,
                'editorial_id': entidad.editorial.id,
                'genero_id': entidad.genero.id}

    def _desde_fila(self, fila: Dict[str, str]) -> Libro:
        return Libro(
            int(fila['id']), fila['isbn'], fila['titulo'], fila['autor'],
            _buscar(self._repo_editorial, int(fila['editorial_id']), 'Editorial'),
            _buscar(self._repo_genero, int(fila['genero_id']), 'Genero'),
        )

    def leer_por_isbn(self, isbn: str) -> Optional[Libro]:
        """Busca un libro por su ISBN."""
        return next(
            (libro for libro in self._entidades.values()
             if libro.isbn == isbn.strip()),
            None,
        )


class RepositorioPrecio(RepositorioCSV[Precio]):
    """Persistencia de precios. Resuelve libro y moneda por ID."""

    NOMBRE_ARCHIVO = 'precios.csv'
    CAMPOS = ['id', 'libro_id', 'moneda_id', 'valor']

    def __init__(self, repo_libro: RepositorioLibro,
                 repo_moneda: RepositorioMoneda,
                 directorio: Path = DIRECTORIO_DATOS) -> None:
        self._repo_libro = repo_libro
        self._repo_moneda = repo_moneda
        super().__init__(directorio)

    def _a_fila(self, entidad: Precio) -> Dict[str, object]:
        return {'id': entidad.id, 'libro_id': entidad.libro.id,
                'moneda_id': entidad.moneda.id, 'valor': entidad.valor}

    def _desde_fila(self, fila: Dict[str, str]) -> Precio:
        return Precio(
            int(fila['id']),
            _buscar(self._repo_libro, int(fila['libro_id']), 'Libro'),
            _buscar(self._repo_moneda, int(fila['moneda_id']), 'Moneda'),
            float(fila['valor']),
        )

    def leer_por_libro(self, libro_id: int) -> List[Precio]:
        """Devuelve los precios de un libro en todas sus monedas."""
        return [p for p in self.leer_todos() if p.libro.id == libro_id]


class RepositorioStock(IRepositorioStock):
    """Persistencia de stock. Un único registro por libro."""

    CAMPOS = ['id', 'libro_id', 'cantidad']

    def __init__(self, repo_libro: RepositorioLibro,
                 directorio: Path = DIRECTORIO_DATOS) -> None:
        self._repo_libro = repo_libro
        self._archivo = ArchivoCSV('stock.csv', self.CAMPOS, directorio)
        self._stocks: Dict[int, Stock] = {}
        for fila in self._archivo.leer():
            libro = _buscar(repo_libro, int(fila['libro_id']), 'Libro')
            self._stocks[libro.id] = Stock(int(fila['id']), libro,
                                           int(fila['cantidad']))

    def _guardar(self) -> None:
        self._archivo.escribir([
            {'id': s.id, 'libro_id': s.libro.id, 'cantidad': s.cantidad}
            for s in self.leer_todos()
        ])

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID disponible."""
        return max((s.id for s in self._stocks.values()), default=0) + 1

    def crear(self, stock: Stock) -> Stock:
        if stock.libro.id in self._stocks:
            raise ValueError(
                f'Ya existe stock para el libro {stock.libro.id}.'
            )
        self._stocks[stock.libro.id] = stock
        self._guardar()
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        return self._stocks.get(libro_id)

    def leer_todos(self) -> List[Stock]:
        """Devuelve todos los registros de stock ordenados por ID."""
        return sorted(self._stocks.values(), key=lambda s: s.id)

    def actualizar(self, stock: Stock) -> Stock:
        if stock.libro.id not in self._stocks:
            raise ValueError(
                f'No existe stock para el libro {stock.libro.id}.'
            )
        self._stocks[stock.libro.id] = stock
        self._guardar()
        return stock

    def eliminar(self, libro_id: int) -> bool:
        if libro_id not in self._stocks:
            return False
        del self._stocks[libro_id]
        self._guardar()
        return True


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Persistencia del histórico de cotizaciones (clave: tipo + fecha)."""

    CAMPOS = ['id', 'tipo_id', 'fecha', 'valor_compra', 'valor_venta']

    def __init__(self, repo_tipo: RepositorioTipoCotizacion,
                 directorio: Path = DIRECTORIO_DATOS) -> None:
        self._repo_tipo = repo_tipo
        self._archivo = ArchivoCSV('cotizaciones.csv', self.CAMPOS, directorio)
        self._cotizaciones: Dict[Tuple[int, datetime.date], CotizacionDolar] = {}
        for fila in self._archivo.leer():
            cotizacion = CotizacionDolar(
                int(fila['id']),
                _buscar(repo_tipo, int(fila['tipo_id']), 'TipoCotizacion'),
                datetime.date.fromisoformat(fila['fecha']),
                float(fila['valor_compra']),
                float(fila['valor_venta']),
            )
            self._cotizaciones[self._clave(cotizacion)] = cotizacion

    @staticmethod
    def _clave(cotizacion: CotizacionDolar) -> Tuple[int, datetime.date]:
        return cotizacion.tipo.id, cotizacion.fecha

    def _guardar(self) -> None:
        self._archivo.escribir([
            {'id': c.id, 'tipo_id': c.tipo.id, 'fecha': c.fecha.isoformat(),
             'valor_compra': c.valor_compra, 'valor_venta': c.valor_venta}
            for c in self.leer_todos()
        ])

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID disponible."""
        return max((c.id for c in self._cotizaciones.values()), default=0) + 1

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = self._clave(cotizacion)
        if clave in self._cotizaciones:
            raise ValueError(
                f'Ya existe cotización {cotizacion.tipo} para {cotizacion.fecha}.'
            )
        self._cotizaciones[clave] = cotizacion
        self._guardar()
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        return self._cotizaciones.get((tipo_id, fecha))

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        return sorted(
            (c for c in self._cotizaciones.values() if c.tipo.id == tipo_id),
            key=lambda c: c.fecha,
        )

    def leer_todos(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones ordenadas por fecha y tipo."""
        return sorted(self._cotizaciones.values(),
                      key=lambda c: (c.fecha, c.tipo.id))

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = self._clave(cotizacion)
        if clave not in self._cotizaciones:
            raise ValueError(
                f'No existe cotización {cotizacion.tipo} para {cotizacion.fecha}.'
            )
        self._cotizaciones[clave] = cotizacion
        self._guardar()
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        if (tipo_id, fecha) not in self._cotizaciones:
            return False
        del self._cotizaciones[(tipo_id, fecha)]
        self._guardar()
        return True
