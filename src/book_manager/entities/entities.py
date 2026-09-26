"""Definición de las entidades de dominio del sistema Book Manager.

Este módulo contiene las clases que representan las entidades principales
del sistema de gestión de inventario de una librería: Libro, Genero,
Editorial, Moneda, TipoCotizacion, Precio, Stock y CotizacionDolar.
"""

from __future__ import annotations

import datetime
from typing import Optional


class EntidadBase:
    """Clase base para todas las entidades del sistema.

    Encapsula el identificador único que comparten todas las entidades.

    Attributes:
        id (int): Identificador único de la entidad.
    """

    def __init__(self, id_: int) -> None:
        self._id = id_

    @property
    def id(self) -> int:
        """int: Identificador único de la entidad (solo lectura)."""
        return self._id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"


class Genero(EntidadBase):
    """Representa una categoría literaria (novela, ensayo, infantil, etc.).

    Attributes:
        nombre (str): Nombre de la categoría literaria.
    """

    def __init__(self, id_: int, nombre: str) -> None:
        super().__init__(id_)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        """str: Nombre del género literario."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre del género no puede estar vacío.")
        self._nombre = valor.strip()

    def __str__(self) -> str:
        return self.nombre


class Editorial(EntidadBase):
    """Representa una editorial/distribuidora que provee libros.

    Attributes:
        nombre (str): Razón social de la editorial.
        contacto (Optional[str]): Email o teléfono de contacto.
    """

    def __init__(self, id_: int, nombre: str, contacto: Optional[str] = None) -> None:
        super().__init__(id_)
        self.nombre = nombre
        self.contacto = contacto

    @property
    def nombre(self) -> str:
        """str: Nombre de la editorial."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre de la editorial no puede estar vacío.")
        self._nombre = valor.strip()

    def __str__(self) -> str:
        return self.nombre


class Moneda(EntidadBase):
    """Representa una moneda en la que se pueden expresar precios.

    Attributes:
        codigo (str): Código ISO de la moneda (ARS, USD, etc.).
        nombre (str): Nombre descriptivo de la moneda.
    """

    def __init__(self, id_: int, codigo: str, nombre: str) -> None:
        super().__init__(id_)
        self.codigo = codigo
        self.nombre = nombre

    @property
    def codigo(self) -> str:
        """str: Código ISO de la moneda (ARS, USD, etc.)."""
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        if not valor or len(valor.strip()) != 3:
            raise ValueError(
                "El código de moneda debe tener 3 caracteres (ej: ARS, USD)."
            )
        self._codigo = valor.strip().upper()

    @property
    def nombre(self) -> str:
        """str: Nombre descriptivo de la moneda."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre de la moneda no puede estar vacío.")
        self._nombre = valor.strip()

    def __str__(self) -> str:
        return self.codigo


class TipoCotizacion(EntidadBase):
    """Representa un tipo de cotización del dólar (Oficial, Blue, MEP, etc.).

    Attributes:
        nombre (str): Nombre del tipo de cotización.
    """

    def __init__(self, id_: int, nombre: str) -> None:
        super().__init__(id_)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        """str: Nombre del tipo de cotización."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError(
                "El nombre del tipo de cotización no puede estar vacío."
            )
        self._nombre = valor.strip()

    def __str__(self) -> str:
        return self.nombre


class Libro(EntidadBase):
    """Representa un título del catálogo de la librería.

    Attributes:
        isbn (str): Código ISBN del libro.
        titulo (str): Título del libro.
        autor (str): Autor/es del libro.
        editorial (Editorial): Editorial que provee el libro.
        genero (Genero): Categoría literaria del libro.
    """

    def __init__(
        self,
        id_: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial: Editorial,
        genero: Genero,
    ) -> None:
        super().__init__(id_)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.genero = genero

    @property
    def isbn(self) -> str:
        """str: Código ISBN del libro."""
        return self._isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El ISBN no puede estar vacío.")
        self._isbn = valor.strip()

    @property
    def titulo(self) -> str:
        """str: Título del libro."""
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El título no puede estar vacío.")
        self._titulo = valor.strip()

    @property
    def autor(self) -> str:
        """str: Autor/es del libro."""
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El autor no puede estar vacío.")
        self._autor = valor.strip()

    @property
    def editorial(self) -> Editorial:
        """Editorial: Editorial que provee el libro."""
        return self._editorial

    @editorial.setter
    def editorial(self, valor: Editorial) -> None:
        if not isinstance(valor, Editorial):
            raise TypeError("editorial debe ser una instancia de Editorial.")
        self._editorial = valor

    @property
    def genero(self) -> Genero:
        """Genero: Categoría literaria del libro."""
        return self._genero

    @genero.setter
    def genero(self, valor: Genero) -> None:
        if not isinstance(valor, Genero):
            raise TypeError("genero debe ser una instancia de Genero.")
        self._genero = valor

    def __str__(self) -> str:
        return f"{self.titulo} ({self.autor}) - {self.editorial}"


class Precio(EntidadBase):
    """Representa el valor monetario de un libro en una moneda determinada.

    Attributes:
        libro (Libro): Libro al que corresponde el precio.
        moneda (Moneda): Moneda en la que está expresado el precio.
        valor (float): Monto del precio.
    """

    def __init__(self, id_: int, libro: Libro, moneda: Moneda, valor: float) -> None:
        super().__init__(id_)
        self.libro = libro
        self.moneda = moneda
        self.valor = valor

    @property
    def libro(self) -> Libro:
        """Libro: Libro asociado al precio."""
        return self._libro

    @libro.setter
    def libro(self, valor: Libro) -> None:
        if not isinstance(valor, Libro):
            raise TypeError("libro debe ser una instancia de Libro.")
        self._libro = valor

    @property
    def moneda(self) -> Moneda:
        """Moneda: Moneda en la que está expresado el precio."""
        return self._moneda

    @moneda.setter
    def moneda(self, valor: Moneda) -> None:
        if not isinstance(valor, Moneda):
            raise TypeError("moneda debe ser una instancia de Moneda.")
        self._moneda = valor

    @property
    def valor(self) -> float:
        """float: Monto del precio."""
        return self._valor

    @valor.setter
    def valor(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El valor del precio no puede ser negativo.")
        self._valor = float(valor)

    def __str__(self) -> str:
        return f"{self.valor:.2f} {self.moneda}"


class Stock(EntidadBase):
    """Representa la cantidad disponible de un libro en inventario.

    Attributes:
        libro (Libro): Libro asociado al registro de stock.
        cantidad (int): Cantidad disponible del libro.
    """

    def __init__(self, id_: int, libro: Libro, cantidad: int) -> None:
        super().__init__(id_)
        self.libro = libro
        self.cantidad = cantidad

    @property
    def libro(self) -> Libro:
        """Libro: Libro asociado al registro de stock."""
        return self._libro

    @libro.setter
    def libro(self, valor: Libro) -> None:
        if not isinstance(valor, Libro):
            raise TypeError("libro debe ser una instancia de Libro.")
        self._libro = valor

    @property
    def cantidad(self) -> int:
        """int: Cantidad disponible del libro."""
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("La cantidad de stock no puede ser negativa.")
        self._cantidad = int(valor)

    def __str__(self) -> str:
        return f"{self.libro.titulo}: {self.cantidad} unidades"


class CotizacionDolar(EntidadBase):
    """Representa un registro histórico de la cotización del dólar.

    Attributes:
        tipo (TipoCotizacion): Tipo de cotización (Oficial, Blue, MEP, etc.).
        fecha (datetime.date): Fecha de la cotización.
        valor_compra (float): Valor de compra del dólar.
        valor_venta (float): Valor de venta del dólar.
    """

    def __init__(
        self,
        id_: int,
        tipo: TipoCotizacion,
        fecha: datetime.date,
        valor_compra: float,
        valor_venta: float,
    ) -> None:
        super().__init__(id_)
        self.tipo = tipo
        self.fecha = fecha
        self.valor_compra = valor_compra
        self.valor_venta = valor_venta

    @property
    def tipo(self) -> TipoCotizacion:
        """TipoCotizacion: Tipo de cotización del dólar."""
        return self._tipo

    @tipo.setter
    def tipo(self, valor: TipoCotizacion) -> None:
        if not isinstance(valor, TipoCotizacion):
            raise TypeError("tipo debe ser una instancia de TipoCotizacion.")
        self._tipo = valor

    @property
    def fecha(self) -> datetime.date:
        """datetime.date: Fecha de la cotización."""
        return self._fecha

    @fecha.setter
    def fecha(self, valor: datetime.date) -> None:
        if not isinstance(valor, datetime.date):
            raise TypeError("fecha debe ser una instancia de datetime.date.")
        self._fecha = valor

    @property
    def valor_compra(self) -> float:
        """float: Valor de compra del dólar."""
        return self._valor_compra

    @valor_compra.setter
    def valor_compra(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El valor de compra no puede ser negativo.")
        self._valor_compra = float(valor)

    @property
    def valor_venta(self) -> float:
        """float: Valor de venta del dólar."""
        return self._valor_venta

    @valor_venta.setter
    def valor_venta(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El valor de venta no puede ser negativo.")
        self._valor_venta = float(valor)

    def __str__(self) -> str:
        return (
            f"{self.tipo} ({self.fecha}): "
            f"compra {self.valor_compra} / venta {self.valor_venta}"
        )
        