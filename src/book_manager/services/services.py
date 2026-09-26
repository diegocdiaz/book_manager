"""Servicios del sistema Book Manager.

Aca va la logica de negocio: validaciones antes de guardar, controles para
no borrar datos que se estan usando, movimientos de stock y los calculos
de precios segun la cotizacion del dolar.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Dict, List, Optional

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    DIRECTORIO_DATOS,
    RepositorioCotizacionDolar,
    RepositorioEditorial,
    RepositorioGenero,
    RepositorioLibro,
    RepositorioMoneda,
    RepositorioPrecio,
    RepositorioStock,
    RepositorioTipoCotizacion,
)


class ServicioBase:
    """Metodos que comparten los servicios de las entidades con id."""

    nombre_entidad = 'registro'

    def __init__(self, repositorio) -> None:
        self._repositorio = repositorio

    def listar(self) -> list:
        """Devuelve todos los registros."""
        return self._repositorio.leer_todos()

    def obtener(self, id_: int):
        """Busca por id. Si no existe lanza ValueError."""
        entidad = self._repositorio.leer_por_id(id_)
        if entidad is None:
            raise ValueError(f'No existe {self.nombre_entidad} con id {id_}.')
        return entidad


class ServicioGenero(ServicioBase):
    """Logica de los generos."""

    nombre_entidad = 'genero'

    def __init__(self, repositorio: RepositorioGenero,
                 repo_libro: RepositorioLibro) -> None:
        super().__init__(repositorio)
        self._repo_libro = repo_libro

    def _existe_nombre(self, nombre: str, id_actual: int = 0) -> bool:
        for genero in self.listar():
            if (genero.nombre.lower() == nombre.strip().lower()
                    and genero.id != id_actual):
                return True
        return False

    def crear(self, nombre: str) -> Genero:
        """Da de alta un genero nuevo."""
        if self._existe_nombre(nombre):
            raise ValueError(f'Ya existe el genero {nombre}.')
        genero = Genero(self._repositorio.siguiente_id(), nombre)
        return self._repositorio.crear(genero)

    def actualizar(self, id_: int, nombre: str) -> Genero:
        """Cambia el nombre de un genero."""
        genero = self.obtener(id_)
        if self._existe_nombre(nombre, id_):
            raise ValueError(f'Ya existe el genero {nombre}.')
        genero.nombre = nombre
        return self._repositorio.actualizar(genero)

    def eliminar(self, id_: int) -> bool:
        """Borra un genero si ningun libro lo usa."""
        self.obtener(id_)
        for libro in self._repo_libro.leer_todos():
            if libro.genero.id == id_:
                raise ValueError('No se puede borrar, hay libros con ese '
                                 'genero.')
        return self._repositorio.eliminar(id_)


class ServicioEditorial(ServicioBase):
    """Logica de las editoriales."""

    nombre_entidad = 'editorial'

    def __init__(self, repositorio: RepositorioEditorial,
                 repo_libro: RepositorioLibro) -> None:
        super().__init__(repositorio)
        self._repo_libro = repo_libro

    def _existe_nombre(self, nombre: str, id_actual: int = 0) -> bool:
        for editorial in self.listar():
            if (editorial.nombre.lower() == nombre.strip().lower()
                    and editorial.id != id_actual):
                return True
        return False

    def crear(self, nombre: str, contacto: Optional[str] = None) -> Editorial:
        """Da de alta una editorial nueva."""
        if self._existe_nombre(nombre):
            raise ValueError(f'Ya existe la editorial {nombre}.')
        editorial = Editorial(self._repositorio.siguiente_id(), nombre,
                              contacto or None)
        return self._repositorio.crear(editorial)

    def actualizar(self, id_: int, nombre: str,
                   contacto: Optional[str] = None) -> Editorial:
        """Modifica nombre y contacto de una editorial."""
        editorial = self.obtener(id_)
        if self._existe_nombre(nombre, id_):
            raise ValueError(f'Ya existe la editorial {nombre}.')
        editorial.nombre = nombre
        editorial.contacto = contacto or None
        return self._repositorio.actualizar(editorial)

    def eliminar(self, id_: int) -> bool:
        """Borra una editorial si no tiene libros."""
        self.obtener(id_)
        for libro in self._repo_libro.leer_todos():
            if libro.editorial.id == id_:
                raise ValueError('No se puede borrar, la editorial tiene '
                                 'libros cargados.')
        return self._repositorio.eliminar(id_)


class ServicioMoneda(ServicioBase):
    """Logica de las monedas."""

    nombre_entidad = 'moneda'

    def __init__(self, repositorio: RepositorioMoneda,
                 repo_precio: RepositorioPrecio) -> None:
        super().__init__(repositorio)
        self._repo_precio = repo_precio

    def _existe_codigo(self, codigo: str, id_actual: int = 0) -> bool:
        for moneda in self.listar():
            if (moneda.codigo == codigo.strip().upper()
                    and moneda.id != id_actual):
                return True
        return False

    def crear(self, codigo: str, nombre: str) -> Moneda:
        """Da de alta una moneda nueva."""
        if self._existe_codigo(codigo):
            raise ValueError(f'Ya existe la moneda {codigo.upper()}.')
        moneda = Moneda(self._repositorio.siguiente_id(), codigo, nombre)
        return self._repositorio.crear(moneda)

    def actualizar(self, id_: int, codigo: str, nombre: str) -> Moneda:
        """Modifica codigo y nombre de una moneda."""
        moneda = self.obtener(id_)
        if self._existe_codigo(codigo, id_):
            raise ValueError(f'Ya existe la moneda {codigo.upper()}.')
        # primero pruebo con una moneda auxiliar para que si algun dato
        # esta mal no quede la original cambiada a medias
        Moneda(id_, codigo, nombre)
        moneda.codigo = codigo
        moneda.nombre = nombre
        return self._repositorio.actualizar(moneda)

    def eliminar(self, id_: int) -> bool:
        """Borra una moneda si no hay precios en esa moneda."""
        self.obtener(id_)
        for precio in self._repo_precio.leer_todos():
            if precio.moneda.id == id_:
                raise ValueError('No se puede borrar, hay precios en esa '
                                 'moneda.')
        return self._repositorio.eliminar(id_)


class ServicioTipoCotizacion(ServicioBase):
    """Logica de los tipos de dolar (Oficial, Blue, MEP, etc)."""

    nombre_entidad = 'tipo de cotizacion'

    def __init__(self, repositorio: RepositorioTipoCotizacion,
                 repo_cotizacion: RepositorioCotizacionDolar) -> None:
        super().__init__(repositorio)
        self._repo_cotizacion = repo_cotizacion

    def _existe_nombre(self, nombre: str, id_actual: int = 0) -> bool:
        for tipo in self.listar():
            if (tipo.nombre.lower() == nombre.strip().lower()
                    and tipo.id != id_actual):
                return True
        return False

    def crear(self, nombre: str) -> TipoCotizacion:
        """Da de alta un tipo de cotizacion."""
        if self._existe_nombre(nombre):
            raise ValueError(f'Ya existe el tipo {nombre}.')
        tipo = TipoCotizacion(self._repositorio.siguiente_id(), nombre)
        return self._repositorio.crear(tipo)

    def actualizar(self, id_: int, nombre: str) -> TipoCotizacion:
        """Cambia el nombre de un tipo de cotizacion."""
        tipo = self.obtener(id_)
        if self._existe_nombre(nombre, id_):
            raise ValueError(f'Ya existe el tipo {nombre}.')
        tipo.nombre = nombre
        return self._repositorio.actualizar(tipo)

    def eliminar(self, id_: int) -> bool:
        """Borra un tipo si no tiene cotizaciones cargadas."""
        self.obtener(id_)
        if self._repo_cotizacion.leer_historico_por_tipo(id_):
            raise ValueError('No se puede borrar, ese tipo tiene '
                             'cotizaciones cargadas.')
        return self._repositorio.eliminar(id_)


class ServicioLibro(ServicioBase):
    """Logica de los libros."""

    nombre_entidad = 'libro'

    def __init__(self, repositorio: RepositorioLibro,
                 servicio_editorial: ServicioEditorial,
                 servicio_genero: ServicioGenero,
                 repo_precio: RepositorioPrecio,
                 repo_stock: RepositorioStock) -> None:
        super().__init__(repositorio)
        self._servicio_editorial = servicio_editorial
        self._servicio_genero = servicio_genero
        self._repo_precio = repo_precio
        self._repo_stock = repo_stock

    def limpiar_isbn(self, isbn: str) -> str:
        """Saca guiones y espacios y controla que tenga 10 o 13 digitos.

        El ISBN-10 puede terminar en X.
        """
        isbn = isbn.replace('-', '').replace(' ', '').upper()
        if len(isbn) == 13 and isbn.isdigit():
            return isbn
        if len(isbn) == 10 and isbn[:9].isdigit() and (
                isbn[9].isdigit() or isbn[9] == 'X'):
            return isbn
        raise ValueError('El ISBN tiene que tener 10 o 13 digitos.')

    def crear(self, isbn: str, titulo: str, autor: str,
              editorial_id: int, genero_id: int) -> Libro:
        """Da de alta un libro. El ISBN no se puede repetir."""
        isbn = self.limpiar_isbn(isbn)
        if self._repositorio.leer_por_isbn(isbn) is not None:
            raise ValueError(f'Ya existe un libro con ISBN {isbn}.')
        editorial = self._servicio_editorial.obtener(editorial_id)
        genero = self._servicio_genero.obtener(genero_id)
        libro = Libro(self._repositorio.siguiente_id(), isbn, titulo, autor,
                      editorial, genero)
        return self._repositorio.crear(libro)

    def actualizar(self, id_: int, isbn: str, titulo: str, autor: str,
                   editorial_id: int, genero_id: int) -> Libro:
        """Modifica los datos de un libro."""
        libro = self.obtener(id_)
        isbn = self.limpiar_isbn(isbn)
        otro = self._repositorio.leer_por_isbn(isbn)
        if otro is not None and otro.id != id_:
            raise ValueError(f'Ya existe un libro con ISBN {isbn}.')
        editorial = self._servicio_editorial.obtener(editorial_id)
        genero = self._servicio_genero.obtener(genero_id)
        # pruebo los datos con un libro auxiliar antes de tocar el original.
        # No reemplazo el objeto porque Precio y Stock apuntan a este mismo
        Libro(id_, isbn, titulo, autor, editorial, genero)
        libro.isbn = isbn
        libro.titulo = titulo
        libro.autor = autor
        libro.editorial = editorial
        libro.genero = genero
        return self._repositorio.actualizar(libro)

    def eliminar(self, id_: int) -> bool:
        """Borra un libro y tambien sus precios y su stock."""
        self.obtener(id_)
        for precio in self._repo_precio.leer_por_libro(id_):
            self._repo_precio.eliminar(precio.id)
        self._repo_stock.eliminar(id_)
        return self._repositorio.eliminar(id_)


class ServicioPrecio(ServicioBase):
    """Logica de los precios. Cada libro tiene un solo precio por moneda."""

    nombre_entidad = 'precio'

    def __init__(self, repositorio: RepositorioPrecio,
                 servicio_libro: ServicioLibro,
                 servicio_moneda: ServicioMoneda) -> None:
        super().__init__(repositorio)
        self._servicio_libro = servicio_libro
        self._servicio_moneda = servicio_moneda

    def buscar_precio(self, libro_id: int, codigo: str) -> Optional[Precio]:
        """Devuelve el precio del libro en esa moneda o None si no tiene."""
        for precio in self._repositorio.leer_por_libro(libro_id):
            if precio.moneda.codigo == codigo.upper():
                return precio
        return None

    def crear(self, libro_id: int, moneda_id: int, valor: float) -> Precio:
        """Carga el precio de un libro en una moneda."""
        libro = self._servicio_libro.obtener(libro_id)
        moneda = self._servicio_moneda.obtener(moneda_id)
        if self.buscar_precio(libro_id, moneda.codigo) is not None:
            raise ValueError(f'{libro.titulo} ya tiene precio en '
                             f'{moneda.codigo}.')
        if valor <= 0:
            raise ValueError('El precio tiene que ser mayor a 0.')
        precio = Precio(self._repositorio.siguiente_id(), libro, moneda,
                        valor)
        return self._repositorio.crear(precio)

    def actualizar(self, id_: int, valor: float) -> Precio:
        """Cambia el valor de un precio."""
        precio = self.obtener(id_)
        if valor <= 0:
            raise ValueError('El precio tiene que ser mayor a 0.')
        precio.valor = valor
        return self._repositorio.actualizar(precio)

    def eliminar(self, id_: int) -> bool:
        """Borra un precio."""
        self.obtener(id_)
        return self._repositorio.eliminar(id_)


class ServicioStock:
    """Logica del stock. Se busca por el id del libro."""

    def __init__(self, repositorio: RepositorioStock,
                 servicio_libro: ServicioLibro) -> None:
        self._repositorio = repositorio
        self._servicio_libro = servicio_libro

    def listar(self) -> List[Stock]:
        """Devuelve todo el stock."""
        return self._repositorio.leer_todos()

    def obtener(self, libro_id: int) -> Stock:
        """Devuelve el stock de un libro."""
        stock = self._repositorio.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError(f'El libro {libro_id} no tiene stock cargado.')
        return stock

    def crear(self, libro_id: int, cantidad: int) -> Stock:
        """Carga el stock inicial de un libro."""
        libro = self._servicio_libro.obtener(libro_id)
        stock = Stock(self._repositorio.siguiente_id(), libro, cantidad)
        return self._repositorio.crear(stock)

    def actualizar(self, libro_id: int, cantidad: int) -> Stock:
        """Pone la cantidad que se indica (por ejemplo despues de contar)."""
        stock = self.obtener(libro_id)
        stock.cantidad = cantidad
        return self._repositorio.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        """Borra el stock de un libro."""
        self.obtener(libro_id)
        return self._repositorio.eliminar(libro_id)


class ServicioCotizacionDolar:
    """Logica de las cotizaciones del dolar."""

    def __init__(self, repositorio: RepositorioCotizacionDolar,
                 servicio_tipo: ServicioTipoCotizacion) -> None:
        self._repositorio = repositorio
        self._servicio_tipo = servicio_tipo

    def listar(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones."""
        return self._repositorio.leer_todos()

    def historico(self, tipo_id: int) -> List[CotizacionDolar]:
        """Cotizaciones de un tipo ordenadas por fecha."""
        self._servicio_tipo.obtener(tipo_id)
        return self._repositorio.leer_historico_por_tipo(tipo_id)

    def obtener(self, tipo_id: int, fecha: datetime.date) -> CotizacionDolar:
        """Busca la cotizacion de un tipo en una fecha."""
        cotizacion = self._repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)
        if cotizacion is None:
            raise ValueError(f'No hay cotizacion para esa fecha ({fecha}).')
        return cotizacion

    def ultima(self, tipo_id: int) -> CotizacionDolar:
        """Devuelve la cotizacion mas nueva de un tipo."""
        historico = self.historico(tipo_id)
        if not historico:
            raise ValueError('Ese tipo de dolar no tiene cotizaciones.')
        return historico[-1]

    def _validar(self, fecha: datetime.date, compra: float,
                 venta: float) -> None:
        if fecha > datetime.date.today():
            raise ValueError('La fecha no puede ser futura.')
        if compra <= 0 or venta <= 0:
            raise ValueError('Compra y venta tienen que ser mayores a 0.')
        if venta < compra:
            raise ValueError('La venta no puede ser menor que la compra.')

    def crear(self, tipo_id: int, fecha: datetime.date, compra: float,
              venta: float) -> CotizacionDolar:
        """Carga una cotizacion nueva."""
        tipo = self._servicio_tipo.obtener(tipo_id)
        self._validar(fecha, compra, venta)
        cotizacion = CotizacionDolar(self._repositorio.siguiente_id(), tipo,
                                     fecha, compra, venta)
        return self._repositorio.crear(cotizacion)

    def actualizar(self, tipo_id: int, fecha: datetime.date, compra: float,
                   venta: float) -> CotizacionDolar:
        """Corrige los valores de una cotizacion."""
        cotizacion = self.obtener(tipo_id, fecha)
        self._validar(fecha, compra, venta)
        cotizacion.valor_compra = compra
        cotizacion.valor_venta = venta
        return self._repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Borra una cotizacion."""
        self.obtener(tipo_id, fecha)
        return self._repositorio.eliminar(tipo_id, fecha)


class ServicioCotizador:
    """Calcula los precios de los libros en pesos y dolares.

    Si el libro tiene precio en USD se pasa a pesos con el dolar venta de
    la ultima cotizacion del tipo elegido. Si solo tiene precio en ARS se
    hace la cuenta al reves.
    """

    def __init__(self, servicio_libro: ServicioLibro,
                 servicio_precio: ServicioPrecio,
                 servicio_cotizacion: ServicioCotizacionDolar) -> None:
        self._servicio_libro = servicio_libro
        self._servicio_precio = servicio_precio
        self._servicio_cotizacion = servicio_cotizacion

    def cotizar_libro(self, libro_id: int, tipo_id: int) -> Dict:
        """Devuelve un diccionario con el precio del libro en ARS y USD."""
        libro = self._servicio_libro.obtener(libro_id)
        cotizacion = self._servicio_cotizacion.ultima(tipo_id)
        dolar = cotizacion.valor_venta

        precio_usd = self._servicio_precio.buscar_precio(libro_id, 'USD')
        precio_ars = self._servicio_precio.buscar_precio(libro_id, 'ARS')
        if precio_usd is not None:
            usd = precio_usd.valor
            ars = usd * dolar
        elif precio_ars is not None:
            ars = precio_ars.valor
            usd = ars / dolar
        else:
            raise ValueError(f'{libro.titulo} no tiene precio cargado.')

        return {
            'libro': libro,
            'tipo': cotizacion.tipo.nombre,
            'dolar': dolar,
            'ars': round(ars, 2),
            'usd': round(usd, 2),
        }

    def cotizar_todos(self, tipo_id: int) -> List[Dict]:
        """Cotiza todos los libros que tienen precio."""
        resultado = []
        for libro in self._servicio_libro.listar():
            try:
                resultado.append(self.cotizar_libro(libro.id, tipo_id))
            except ValueError:
                pass  # si no tiene precio lo salteo
        return resultado

    def comparar_competencia(self, libro_id: int, tipo_id: int,
                             precio_competencia: float,
                             competidor: str = 'Cuspide') -> Dict:
        """Compara nuestro precio en pesos con el de otra libreria."""
        if precio_competencia <= 0:
            raise ValueError('El precio de la competencia tiene que ser '
                             'mayor a 0.')
        nuestro = self.cotizar_libro(libro_id, tipo_id)['ars']
        diferencia = nuestro - precio_competencia
        return {
            'libro': self._servicio_libro.obtener(libro_id),
            'competidor': competidor,
            'nuestro': nuestro,
            'competencia': precio_competencia,
            'diferencia': round(diferencia, 2),
            'porcentaje': round(diferencia / precio_competencia * 100, 2),
            'mas_barato': nuestro < precio_competencia,
        }


class ServiciosLibreria:
    """Arma todos los repositorios y servicios juntos.

    Asi desde la consola y el main se usa un solo objeto.
    """

    def __init__(self, directorio: Path = DIRECTORIO_DATOS) -> None:
        repo_genero = RepositorioGenero(directorio)
        repo_editorial = RepositorioEditorial(directorio)
        repo_moneda = RepositorioMoneda(directorio)
        repo_tipo = RepositorioTipoCotizacion(directorio)
        repo_libro = RepositorioLibro(repo_editorial, repo_genero, directorio)
        repo_precio = RepositorioPrecio(repo_libro, repo_moneda, directorio)
        repo_stock = RepositorioStock(repo_libro, directorio)
        repo_cotizacion = RepositorioCotizacionDolar(repo_tipo, directorio)

        self.generos = ServicioGenero(repo_genero, repo_libro)
        self.editoriales = ServicioEditorial(repo_editorial, repo_libro)
        self.monedas = ServicioMoneda(repo_moneda, repo_precio)
        self.tipos_cotizacion = ServicioTipoCotizacion(repo_tipo,
                                                       repo_cotizacion)
        self.libros = ServicioLibro(repo_libro, self.editoriales,
                                    self.generos, repo_precio, repo_stock)
        self.precios = ServicioPrecio(repo_precio, self.libros, self.monedas)
        self.stock = ServicioStock(repo_stock, self.libros)
        self.cotizaciones = ServicioCotizacionDolar(repo_cotizacion,
                                                    self.tipos_cotizacion)
        self.cotizador = ServicioCotizador(self.libros, self.precios,
                                           self.cotizaciones)
