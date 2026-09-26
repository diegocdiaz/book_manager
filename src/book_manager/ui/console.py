"""Interfaz de consola (CLI) del sistema Book Manager.

Acá se arman los menús que operan el CRUD completo de cada entidad y los
reportes de cotización. Este módulo no tiene lógica de negocio: lo que se
carga por teclado se valida como tipo de dato (que sea un entero, una
fecha, etc.) y después se delega en los servicios, que son los que aplican
las reglas y avisan con un ValueError cuando algo no cierra.
"""

from __future__ import annotations

import datetime
from collections import Counter
from functools import reduce, wraps
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)

from book_manager.entities.entities import CotizacionDolar, EntidadBase
from book_manager.services.services import ServiciosLibreria

ANCHO = 74

# una acción de menú no recibe datos ni devuelve nada, todo sale por pantalla
Accion = Callable[..., None]

# texto con el que se muestra una celda vacía en las tablas
SIN_DATO = '-'


def formatear(valor: object) -> str:
    """Devuelve el texto con el que se muestra un valor en una tabla.

    Se usa match sobre el tipo del valor para que los números, las fechas y
    los booleanos salgan siempre con el mismo formato.

    Args:
        valor (object): Valor a mostrar.

    Returns:
        str: El valor convertido a texto.
    """
    match valor:
        case None:
            return SIN_DATO
        case bool():
            # va antes que float porque bool es un int
            return 'Si' if valor else 'No'
        case float():
            return f'{valor:,.2f}'
        case datetime.date():
            return valor.isoformat()
        case _:
            return str(valor)


def imprimir_titulo(texto: str) -> None:
    """Muestra un título centrado entre dos líneas.

    Args:
        texto (str): Título a mostrar.
    """
    print()
    print('=' * ANCHO)
    print(texto.upper().center(ANCHO))
    print('=' * ANCHO)


def imprimir_tabla(encabezados: Sequence[str],
                   filas: Iterable[Sequence[object]]) -> None:
    """Muestra los datos en una tabla con las columnas alineadas.

    Args:
        encabezados (Sequence[str]): Nombre de cada columna.
        filas (Iterable[Sequence[object]]): Filas a mostrar.
    """
    filas_texto = [[formatear(celda) for celda in fila] for fila in filas]
    if not filas_texto:
        print('\n  (no hay registros para mostrar)')
        return

    # con zip agrupo los valores de cada columna para saber cuánto mide
    columnas = zip(encabezados, *filas_texto)
    anchos = [max(len(celda) for celda in columna) for columna in columnas]

    print()
    print('  ' + ' | '.join(titulo.ljust(ancho)
                            for titulo, ancho in zip(encabezados, anchos)))
    print('  ' + '-+-'.join('-' * ancho for ancho in anchos))
    for fila in filas_texto:
        print('  ' + ' | '.join(celda.ljust(ancho)
                                for celda, ancho in zip(fila, anchos)))
    print(f'\n  Total: {len(filas_texto)} registro(s).')


def leer_texto(mensaje: str, actual: Optional[str] = None,
               obligatorio: bool = True) -> str:
    """Pide un texto por teclado y lo devuelve sin espacios de más.

    Args:
        mensaje (str): Mensaje que se muestra al pedir el dato.
        actual (Optional[str]): Valor que queda si se contesta con Enter.
        obligatorio (bool): Si es True no se acepta un texto vacío.

    Returns:
        str: El texto ingresado.

    Raises:
        ValueError: Si se corta la entrada de datos.
    """
    sufijo = f' [{actual}]' if actual else ''
    while True:
        try:
            texto = input(f'{mensaje}{sufijo}: ').strip()
        except EOFError:
            raise ValueError(
                'Se cortó la entrada, operación cancelada.') from None
        if texto:
            return texto
        if actual:
            return actual
        if not obligatorio:
            return ''
        print('  [!] El dato es obligatorio.')


def leer_entero(mensaje: str, actual: Optional[int] = None,
                minimo: Optional[int] = None) -> int:
    """Pide un número entero y no sale hasta que el dato sea válido.

    Args:
        mensaje (str): Mensaje que se muestra al pedir el dato.
        actual (Optional[int]): Valor que queda si se contesta con Enter.
        minimo (Optional[int]): Valor mínimo aceptado.

    Returns:
        int: El número ingresado.
    """
    while True:
        texto = leer_texto(mensaje, None if actual is None else str(actual))
        try:
            numero = int(texto)
        except ValueError:
            print('  [!] Tiene que ser un número entero.')
            continue
        if minimo is not None and numero < minimo:
            print(f'  [!] Tiene que ser mayor o igual a {minimo}.')
            continue
        return numero


def leer_decimal(mensaje: str, actual: Optional[float] = None,
                 minimo: Optional[float] = None) -> float:
    """Pide un número decimal y no sale hasta que el dato sea válido.

    Args:
        mensaje (str): Mensaje que se muestra al pedir el dato.
        actual (Optional[float]): Valor que queda si se contesta con Enter.
        minimo (Optional[float]): Valor mínimo aceptado.

    Returns:
        float: El número ingresado.
    """
    while True:
        texto = leer_texto(mensaje, None if actual is None else f'{actual}')
        try:
            numero = float(texto.replace(',', '.'))
        except ValueError:
            print('  [!] Tiene que ser un número (ej: 1250.50).')
            continue
        if minimo is not None and numero < minimo:
            print(f'  [!] Tiene que ser mayor o igual a {minimo}.')
            continue
        return numero


def leer_fecha(mensaje: str,
               actual: Optional[datetime.date] = None) -> datetime.date:
    """Pide una fecha en formato AAAA-MM-DD.

    Args:
        mensaje (str): Mensaje que se muestra al pedir el dato.
        actual (Optional[datetime.date]): Fecha que queda si se contesta con
            Enter. Si no se indica se propone la fecha de hoy.

    Returns:
        datetime.date: La fecha ingresada.
    """
    por_defecto = actual or datetime.date.today()
    while True:
        texto = leer_texto(f'{mensaje} (AAAA-MM-DD)', por_defecto.isoformat())
        try:
            return datetime.date.fromisoformat(texto)
        except ValueError:
            print('  [!] Fecha inválida, se espera AAAA-MM-DD.')


def confirmar(mensaje: str) -> bool:
    """Pide una confirmación por sí o por no.

    Args:
        mensaje (str): Pregunta que se le hace al usuario.

    Returns:
        bool: True si contestó que sí.
    """
    return leer_texto(f'{mensaje} (s/n)', 'n').lower().startswith('s')


def operacion(titulo: str) -> Callable[[Accion], Accion]:
    """Decorador para las opciones de los menús.

    Muestra el título de la operación y, si los servicios rechazan los
    datos, lo avisa por pantalla en lugar de cortar el programa.

    Args:
        titulo (str): Título que se muestra antes de ejecutar la opción.

    Returns:
        Callable[[Accion], Accion]: El decorador ya armado.
    """
    def decorador(funcion: Accion) -> Accion:
        @wraps(funcion)
        def envoltura(*args: object, **kwargs: object) -> None:
            imprimir_titulo(titulo)
            try:
                funcion(*args, **kwargs)
            except (ValueError, TypeError) as error:
                print(f'\n  [!] {error}')
        return envoltura
    return decorador


def variaciones(historico: List[CotizacionDolar]) -> Iterator[
        Tuple[datetime.date, float, float, Optional[float]]]:
    """Genera las filas del histórico con la variación del valor de venta.

    El histórico se recorre de a pares con zip y cada fila se devuelve con
    yield, así no se arma una lista intermedia.

    Args:
        historico (List[CotizacionDolar]): Cotizaciones ordenadas por fecha.

    Yields:
        Tuple: Fecha, compra, venta y variación contra la fecha anterior. En
            la primera fila la variación es None porque no hay con qué
            comparar.
    """
    if not historico:
        return

    primera = historico[0]
    yield primera.fecha, primera.valor_compra, primera.valor_venta, None

    for anterior, actual in zip(historico, historico[1:]):
        variacion = ((actual.valor_venta - anterior.valor_venta)
                     / anterior.valor_venta * 100)
        yield (actual.fecha, actual.valor_compra, actual.valor_venta,
               round(variacion, 2))


class Menu:
    """Menú numerado de consola.

    Las opciones se guardan en un diccionario que mapea la tecla que hay que
    apretar con la función que se ejecuta.

    Attributes:
        titulo (str): Título del menú.
    """

    def __init__(self, titulo: str, opciones: Sequence[Tuple[str, Accion]],
                 salida: str = 'Volver') -> None:
        self.titulo = titulo
        self._salida = salida
        self._opciones: Dict[str, Tuple[str, Accion]] = {
            str(numero): opcion
            for numero, opcion in enumerate(opciones, start=1)
        }

    def mostrar(self) -> None:
        """Muestra el título y las opciones disponibles."""
        imprimir_titulo(self.titulo)
        for tecla, (etiqueta, _) in self._opciones.items():
            print(f'  {tecla}. {etiqueta}')
        print(f'  0. {self._salida}')

    def ejecutar(self) -> None:
        """Muestra el menú y ejecuta opciones hasta que se elige 0."""
        while True:
            self.mostrar()
            try:
                tecla = input('\nOpción: ').strip()
            except EOFError:
                print('\n  Se cortó la entrada, se cierra el menú.')
                return

            if tecla == '0':
                return
            # con el walrus busco la opción y la guardo en un solo paso
            if (elegida := self._opciones.get(tecla)) is None:
                print('\n  [!] Opción inválida.')
                continue
            _, accion = elegida
            accion()


class ConsolaLibreria:
    """Interfaz de consola que opera los servicios de la librería."""

    def __init__(self, servicios: ServiciosLibreria) -> None:
        self._servicios = servicios

    # ------------------------------------------------------------------
    # armado de los menús
    # ------------------------------------------------------------------
    def ejecutar(self) -> None:
        """Muestra el menú principal del sistema."""
        Menu('Book Manager', [
            ('Libros', self._menu_libros),
            ('Géneros', self._menu_generos),
            ('Editoriales', self._menu_editoriales),
            ('Monedas', self._menu_monedas),
            ('Tipos de cotización', self._menu_tipos_cotizacion),
            ('Precios', self._menu_precios),
            ('Stock', self._menu_stock),
            ('Cotizaciones del dólar', self._menu_cotizaciones),
            ('Reportes', self._menu_reportes),
        ], salida='Salir').ejecutar()
        print('\nHasta luego.')

    def _menu_crud(self, titulo: str, listar: Accion, alta: Accion,
                   modificar: Accion, baja: Accion) -> None:
        """Arma y ejecuta el menú de CRUD de una entidad.

        Args:
            titulo (str): Título del menú.
            listar (Accion): Opción de lectura.
            alta (Accion): Opción de alta.
            modificar (Accion): Opción de modificación.
            baja (Accion): Opción de borrado.
        """
        Menu(titulo, [
            ('Listar', listar),
            ('Nuevo', alta),
            ('Modificar', modificar),
            ('Borrar', baja),
        ]).ejecutar()

    def _menu_libros(self) -> None:
        self._menu_crud('Libros', self._listar_libros, self._alta_libro,
                        self._modificar_libro, self._baja_libro)

    def _menu_generos(self) -> None:
        self._menu_crud('Géneros', self._listar_generos, self._alta_genero,
                        self._modificar_genero, self._baja_genero)

    def _menu_editoriales(self) -> None:
        self._menu_crud('Editoriales', self._listar_editoriales,
                        self._alta_editorial, self._modificar_editorial,
                        self._baja_editorial)

    def _menu_monedas(self) -> None:
        self._menu_crud('Monedas', self._listar_monedas, self._alta_moneda,
                        self._modificar_moneda, self._baja_moneda)

    def _menu_tipos_cotizacion(self) -> None:
        self._menu_crud('Tipos de cotización', self._listar_tipos,
                        self._alta_tipo, self._modificar_tipo,
                        self._baja_tipo)

    def _menu_precios(self) -> None:
        self._menu_crud('Precios', self._listar_precios, self._alta_precio,
                        self._modificar_precio, self._baja_precio)

    def _menu_stock(self) -> None:
        self._menu_crud('Stock', self._listar_stock, self._alta_stock,
                        self._modificar_stock, self._baja_stock)

    def _menu_cotizaciones(self) -> None:
        self._menu_crud('Cotizaciones del dólar', self._listar_cotizaciones,
                        self._alta_cotizacion, self._modificar_cotizacion,
                        self._baja_cotizacion)

    def _menu_reportes(self) -> None:
        Menu('Reportes', [
            ('Cotización de un libro', self._reporte_cotizar_libro),
            ('Cotización de todo el catálogo', self._reporte_catalogo),
            ('Comparación con la competencia', self._reporte_competencia),
            ('Histórico de un tipo de dólar', self._reporte_historico),
            ('Libros con stock bajo', self._reporte_stock_bajo),
        ]).ejecutar()

    # ------------------------------------------------------------------
    # ayudas para elegir un registro que ya existe
    # ------------------------------------------------------------------
    def _pedir_id(
            self, entidades: List[EntidadBase], etiqueta: str,
            descripcion: Optional[Callable[[EntidadBase], str]] = None
    ) -> int:
        """Muestra los registros que hay cargados y pide el id de uno.

        Args:
            entidades (List[EntidadBase]): Registros entre los que elegir.
            etiqueta (str): Nombre de la entidad, para los mensajes.
            descripcion (Optional[Callable[[EntidadBase], str]]): Función con
                la que se arma el texto de cada registro. Si no se pasa se
                usa su __str__.

        Returns:
            int: El id elegido.

        Raises:
            ValueError: Si no hay registros cargados.
        """
        if not entidades:
            raise ValueError(f'No hay {etiqueta} cargada/o para elegir.')

        print(f'\n  Opciones de {etiqueta}:')
        for entidad in entidades:
            texto = descripcion(entidad) if descripcion else str(entidad)
            print(f'    {entidad.id}. {texto}')
        return leer_entero(f'Id de {etiqueta}', minimo=1)

    def _pedir_libro_id(self) -> int:
        """Pide el id de un libro mostrando el catálogo."""
        return self._pedir_id(self._servicios.libros.listar(), 'libro')

    def _pedir_tipo_id(self) -> int:
        """Pide el id de un tipo de cotización del dólar."""
        return self._pedir_id(self._servicios.tipos_cotizacion.listar(),
                              'tipo de dólar')

    def _pedir_libro_con_stock(self) -> int:
        """Pide el id del libro de un registro de stock ya cargado.

        El stock se identifica por el libro, por eso no se pide el id del
        registro sino el del libro.

        Returns:
            int: El id del libro elegido.

        Raises:
            ValueError: Si no hay stock cargado.
        """
        registros = self._servicios.stock.listar()
        if not registros:
            raise ValueError('No hay stock cargado.')

        print('\n  Stock cargado:')
        for registro in registros:
            print(f'    libro {registro.libro.id}. {registro}')
        return leer_entero('Id de libro', minimo=1)

    def _pedir_clave_cotizacion(self) -> Tuple[int, datetime.date]:
        """Pide el tipo y la fecha, que son la clave de una cotización.

        Returns:
            Tuple[int, datetime.date]: El tipo y la fecha elegidos.

        Raises:
            ValueError: Si ese tipo no tiene cotizaciones cargadas.
        """
        tipo_id = self._pedir_tipo_id()
        historico = self._servicios.cotizaciones.historico(tipo_id)
        if not historico:
            raise ValueError('Ese tipo de dólar no tiene cotizaciones.')

        print('\n  Fechas cargadas:')
        for cotizacion in historico:
            print(f'    {cotizacion.fecha} -> venta '
                  f'{cotizacion.valor_venta:,.2f}')
        return tipo_id, leer_fecha('Fecha', historico[-1].fecha)

    # ------------------------------------------------------------------
    # CRUD de libros
    # ------------------------------------------------------------------
    @operacion('Listado de libros')
    def _listar_libros(self) -> None:
        imprimir_tabla(
            ('Id', 'ISBN', 'Título', 'Autor', 'Editorial', 'Género'),
            [(libro.id, libro.isbn, libro.titulo, libro.autor,
              libro.editorial.nombre, libro.genero.nombre)
             for libro in self._servicios.libros.listar()],
        )

    @operacion('Nuevo libro')
    def _alta_libro(self) -> None:
        isbn = leer_texto('ISBN')
        titulo = leer_texto('Título')
        autor = leer_texto('Autor')
        editorial_id = self._pedir_id(self._servicios.editoriales.listar(),
                                      'editorial')
        genero_id = self._pedir_id(self._servicios.generos.listar(), 'género')

        libro = self._servicios.libros.crear(isbn, titulo, autor,
                                             editorial_id, genero_id)
        print(f'\n  Libro creado con id {libro.id}.')

    @operacion('Modificar libro')
    def _modificar_libro(self) -> None:
        libro = self._servicios.libros.obtener(self._pedir_libro_id())
        print('\n  Con Enter queda el valor que está entre corchetes.')

        isbn = leer_texto('ISBN', libro.isbn)
        titulo = leer_texto('Título', libro.titulo)
        autor = leer_texto('Autor', libro.autor)
        editorial_id = self._pedir_id(self._servicios.editoriales.listar(),
                                      'editorial')
        genero_id = self._pedir_id(self._servicios.generos.listar(), 'género')

        self._servicios.libros.actualizar(libro.id, isbn, titulo, autor,
                                          editorial_id, genero_id)
        print('\n  Libro actualizado.')

    @operacion('Borrar libro')
    def _baja_libro(self) -> None:
        libro = self._servicios.libros.obtener(self._pedir_libro_id())
        print('\n  Se borran también sus precios y su stock.')
        if not confirmar(f'¿Borrar "{libro.titulo}"?'):
            print('\n  Operación cancelada.')
            return

        self._servicios.libros.eliminar(libro.id)
        print('\n  Libro borrado.')

    # ------------------------------------------------------------------
    # CRUD de géneros
    # ------------------------------------------------------------------
    @operacion('Listado de géneros')
    def _listar_generos(self) -> None:
        imprimir_tabla(
            ('Id', 'Nombre'),
            [(genero.id, genero.nombre)
             for genero in self._servicios.generos.listar()],
        )

    @operacion('Nuevo género')
    def _alta_genero(self) -> None:
        genero = self._servicios.generos.crear(leer_texto('Nombre'))
        print(f'\n  Género creado con id {genero.id}.')

    @operacion('Modificar género')
    def _modificar_genero(self) -> None:
        servicio = self._servicios.generos
        genero = servicio.obtener(self._pedir_id(servicio.listar(), 'género'))

        servicio.actualizar(genero.id, leer_texto('Nombre', genero.nombre))
        print('\n  Género actualizado.')

    @operacion('Borrar género')
    def _baja_genero(self) -> None:
        servicio = self._servicios.generos
        genero = servicio.obtener(self._pedir_id(servicio.listar(), 'género'))
        if not confirmar(f'¿Borrar "{genero.nombre}"?'):
            print('\n  Operación cancelada.')
            return

        servicio.eliminar(genero.id)
        print('\n  Género borrado.')

    # ------------------------------------------------------------------
    # CRUD de editoriales
    # ------------------------------------------------------------------
    @operacion('Listado de editoriales')
    def _listar_editoriales(self) -> None:
        imprimir_tabla(
            ('Id', 'Nombre', 'Contacto'),
            [(editorial.id, editorial.nombre, editorial.contacto)
             for editorial in self._servicios.editoriales.listar()],
        )

    @operacion('Nueva editorial')
    def _alta_editorial(self) -> None:
        nombre = leer_texto('Nombre')
        contacto = leer_texto('Contacto', obligatorio=False)

        editorial = self._servicios.editoriales.crear(nombre, contacto)
        print(f'\n  Editorial creada con id {editorial.id}.')

    @operacion('Modificar editorial')
    def _modificar_editorial(self) -> None:
        servicio = self._servicios.editoriales
        editorial = servicio.obtener(
            self._pedir_id(servicio.listar(), 'editorial'))

        nombre = leer_texto('Nombre', editorial.nombre)
        contacto = leer_texto('Contacto', editorial.contacto,
                              obligatorio=False)

        servicio.actualizar(editorial.id, nombre, contacto)
        print('\n  Editorial actualizada.')

    @operacion('Borrar editorial')
    def _baja_editorial(self) -> None:
        servicio = self._servicios.editoriales
        editorial = servicio.obtener(
            self._pedir_id(servicio.listar(), 'editorial'))
        if not confirmar(f'¿Borrar "{editorial.nombre}"?'):
            print('\n  Operación cancelada.')
            return

        servicio.eliminar(editorial.id)
        print('\n  Editorial borrada.')

    # ------------------------------------------------------------------
    # CRUD de monedas
    # ------------------------------------------------------------------
    @operacion('Listado de monedas')
    def _listar_monedas(self) -> None:
        imprimir_tabla(
            ('Id', 'Código', 'Nombre'),
            [(moneda.id, moneda.codigo, moneda.nombre)
             for moneda in self._servicios.monedas.listar()],
        )

    @operacion('Nueva moneda')
    def _alta_moneda(self) -> None:
        codigo = leer_texto('Código (3 letras, ej: ARS)')
        nombre = leer_texto('Nombre')

        moneda = self._servicios.monedas.crear(codigo, nombre)
        print(f'\n  Moneda creada con id {moneda.id}.')

    @operacion('Modificar moneda')
    def _modificar_moneda(self) -> None:
        servicio = self._servicios.monedas
        moneda = servicio.obtener(self._pedir_id(servicio.listar(), 'moneda'))

        codigo = leer_texto('Código', moneda.codigo)
        nombre = leer_texto('Nombre', moneda.nombre)

        servicio.actualizar(moneda.id, codigo, nombre)
        print('\n  Moneda actualizada.')

    @operacion('Borrar moneda')
    def _baja_moneda(self) -> None:
        servicio = self._servicios.monedas
        moneda = servicio.obtener(self._pedir_id(servicio.listar(), 'moneda'))
        if not confirmar(f'¿Borrar "{moneda.codigo}"?'):
            print('\n  Operación cancelada.')
            return

        servicio.eliminar(moneda.id)
        print('\n  Moneda borrada.')

    # ------------------------------------------------------------------
    # CRUD de tipos de cotización
    # ------------------------------------------------------------------
    @operacion('Listado de tipos de cotización')
    def _listar_tipos(self) -> None:
        imprimir_tabla(
            ('Id', 'Nombre'),
            [(tipo.id, tipo.nombre)
             for tipo in self._servicios.tipos_cotizacion.listar()],
        )

    @operacion('Nuevo tipo de cotización')
    def _alta_tipo(self) -> None:
        tipo = self._servicios.tipos_cotizacion.crear(leer_texto('Nombre'))
        print(f'\n  Tipo creado con id {tipo.id}.')

    @operacion('Modificar tipo de cotización')
    def _modificar_tipo(self) -> None:
        servicio = self._servicios.tipos_cotizacion
        tipo = servicio.obtener(self._pedir_tipo_id())

        servicio.actualizar(tipo.id, leer_texto('Nombre', tipo.nombre))
        print('\n  Tipo actualizado.')

    @operacion('Borrar tipo de cotización')
    def _baja_tipo(self) -> None:
        servicio = self._servicios.tipos_cotizacion
        tipo = servicio.obtener(self._pedir_tipo_id())
        if not confirmar(f'¿Borrar "{tipo.nombre}"?'):
            print('\n  Operación cancelada.')
            return

        servicio.eliminar(tipo.id)
        print('\n  Tipo borrado.')

    # ------------------------------------------------------------------
    # CRUD de precios
    # ------------------------------------------------------------------
    @operacion('Listado de precios')
    def _listar_precios(self) -> None:
        imprimir_tabla(
            ('Id', 'Libro', 'Moneda', 'Valor'),
            [(precio.id, precio.libro.titulo, precio.moneda.codigo,
              precio.valor)
             for precio in self._servicios.precios.listar()],
        )

    @operacion('Nuevo precio')
    def _alta_precio(self) -> None:
        libro_id = self._pedir_libro_id()
        moneda_id = self._pedir_id(self._servicios.monedas.listar(), 'moneda')
        valor = leer_decimal('Valor', minimo=0)

        precio = self._servicios.precios.crear(libro_id, moneda_id, valor)
        print(f'\n  Precio creado con id {precio.id}.')

    @operacion('Modificar precio')
    def _modificar_precio(self) -> None:
        servicio = self._servicios.precios
        # la lambda arma el texto de cada opción para que se vea el libro
        precio = servicio.obtener(self._pedir_id(
            servicio.listar(), 'precio',
            lambda item: f'{item.libro.titulo} - {item}'))

        servicio.actualizar(precio.id,
                            leer_decimal('Valor', precio.valor, minimo=0))
        print('\n  Precio actualizado.')

    @operacion('Borrar precio')
    def _baja_precio(self) -> None:
        servicio = self._servicios.precios
        precio = servicio.obtener(self._pedir_id(
            servicio.listar(), 'precio',
            lambda item: f'{item.libro.titulo} - {item}'))
        if not confirmar(f'¿Borrar el precio de "{precio.libro.titulo}"?'):
            print('\n  Operación cancelada.')
            return

        servicio.eliminar(precio.id)
        print('\n  Precio borrado.')

    # ------------------------------------------------------------------
    # CRUD de stock
    # ------------------------------------------------------------------
    @operacion('Listado de stock')
    def _listar_stock(self) -> None:
        imprimir_tabla(
            ('Id libro', 'Título', 'Cantidad'),
            [(registro.libro.id, registro.libro.titulo, registro.cantidad)
             for registro in self._servicios.stock.listar()],
        )

    @operacion('Nuevo stock')
    def _alta_stock(self) -> None:
        libro_id = self._pedir_libro_id()
        cantidad = leer_entero('Cantidad', minimo=0)

        self._servicios.stock.crear(libro_id, cantidad)
        print('\n  Stock cargado.')

    @operacion('Modificar stock')
    def _modificar_stock(self) -> None:
        registro = self._servicios.stock.obtener(
            self._pedir_libro_con_stock())

        cantidad = leer_entero('Cantidad', registro.cantidad, minimo=0)
        self._servicios.stock.actualizar(registro.libro.id, cantidad)
        print('\n  Stock actualizado.')

    @operacion('Borrar stock')
    def _baja_stock(self) -> None:
        registro = self._servicios.stock.obtener(
            self._pedir_libro_con_stock())
        if not confirmar(f'¿Borrar el stock de "{registro.libro.titulo}"?'):
            print('\n  Operación cancelada.')
            return

        self._servicios.stock.eliminar(registro.libro.id)
        print('\n  Stock borrado.')

    # ------------------------------------------------------------------
    # CRUD de cotizaciones del dólar
    # ------------------------------------------------------------------
    @operacion('Listado de cotizaciones')
    def _listar_cotizaciones(self) -> None:
        imprimir_tabla(
            ('Id', 'Tipo', 'Fecha', 'Compra', 'Venta'),
            [(cotizacion.id, cotizacion.tipo.nombre, cotizacion.fecha,
              cotizacion.valor_compra, cotizacion.valor_venta)
             for cotizacion in self._servicios.cotizaciones.listar()],
        )

    @operacion('Nueva cotización')
    def _alta_cotizacion(self) -> None:
        tipo_id = self._pedir_tipo_id()
        fecha = leer_fecha('Fecha')
        compra = leer_decimal('Valor de compra', minimo=0)
        venta = leer_decimal('Valor de venta', minimo=0)

        self._servicios.cotizaciones.crear(tipo_id, fecha, compra, venta)
        print('\n  Cotización cargada.')

    @operacion('Modificar cotización')
    def _modificar_cotizacion(self) -> None:
        tipo_id, fecha = self._pedir_clave_cotizacion()
        cotizacion = self._servicios.cotizaciones.obtener(tipo_id, fecha)

        compra = leer_decimal('Valor de compra', cotizacion.valor_compra,
                              minimo=0)
        venta = leer_decimal('Valor de venta', cotizacion.valor_venta,
                             minimo=0)

        self._servicios.cotizaciones.actualizar(tipo_id, fecha, compra, venta)
        print('\n  Cotización actualizada.')

    @operacion('Borrar cotización')
    def _baja_cotizacion(self) -> None:
        tipo_id, fecha = self._pedir_clave_cotizacion()
        cotizacion = self._servicios.cotizaciones.obtener(tipo_id, fecha)
        if not confirmar(f'¿Borrar la cotización {cotizacion}?'):
            print('\n  Operación cancelada.')
            return

        self._servicios.cotizaciones.eliminar(tipo_id, fecha)
        print('\n  Cotización borrada.')

    # ------------------------------------------------------------------
    # reportes
    # ------------------------------------------------------------------
    @operacion('Cotización de un libro')
    def _reporte_cotizar_libro(self) -> None:
        libro_id = self._pedir_libro_id()
        tipo_id = self._pedir_tipo_id()
        datos = self._servicios.cotizador.cotizar_libro(libro_id, tipo_id)

        dolar = datos['dolar']
        print()
        print(f'  {"Libro:":<20}{datos["libro"]}')
        print(f'  {"Tipo de dólar:":<20}{datos["tipo"]} '
              f'(venta {dolar:,.2f})')
        print(f'  {"Precio en ARS:":<20}{datos["ars"]:,.2f}')
        print(f'  {"Precio en USD:":<20}{datos["usd"]:,.2f}')

    @operacion('Cotización de todo el catálogo')
    def _reporte_catalogo(self) -> None:
        tipo_id = self._pedir_tipo_id()
        datos = self._servicios.cotizador.cotizar_todos(tipo_id)
        if not datos:
            raise ValueError('Ningún libro tiene precio cargado.')

        imprimir_tabla(
            ('Libro', 'Autor', 'Precio ARS', 'Precio USD'),
            [(fila['libro'].titulo, fila['libro'].autor, fila['ars'],
              fila['usd']) for fila in datos],
        )

        # reduce acumula el total del catálogo fila por fila
        total = reduce(lambda acumulado, fila: acumulado + fila['ars'],
                       datos, 0.0)
        print(f'\n  Valor total del catálogo: {total:,.2f} ARS')

        # Counter cuenta cuántos libros cotizados hay por género
        por_genero = Counter(fila['libro'].genero.nombre for fila in datos)
        print('  Libros cotizados por género:')
        for nombre, cantidad in por_genero.most_common():
            print(f'    {nombre}: {cantidad}')

    @operacion('Comparación con la competencia')
    def _reporte_competencia(self) -> None:
        libro_id = self._pedir_libro_id()
        tipo_id = self._pedir_tipo_id()
        competidor = leer_texto('Competidor', 'Cuspide')
        precio = leer_decimal('Precio de la competencia en ARS', minimo=0)

        datos = self._servicios.cotizador.comparar_competencia(
            libro_id, tipo_id, precio, competidor)

        # el nombre del competidor cambia de largo, con ljust las columnas
        # quedan igual alineadas
        etiqueta_competidor = f'{datos["competidor"]}:'
        print()
        print(f'  {"Libro:":<20}{datos["libro"]}')
        print(f'  {"Nuestro precio:":<20}{datos["nuestro"]:,.2f} ARS')
        print(f'  {etiqueta_competidor:<20}{datos["competencia"]:,.2f} ARS')
        print(f'  {"Diferencia:":<20}{datos["diferencia"]:,.2f} ARS '
              f'({datos["porcentaje"]:,.2f}%)')
        print(f'  {"¿Somos más baratos?":<20}'
              f'{formatear(datos["mas_barato"])}')

    @operacion('Histórico de un tipo de dólar')
    def _reporte_historico(self) -> None:
        tipo_id = self._pedir_tipo_id()
        historico = self._servicios.cotizaciones.historico(tipo_id)
        if not historico:
            raise ValueError('Ese tipo de dólar no tiene cotizaciones.')

        imprimir_tabla(('Fecha', 'Compra', 'Venta', 'Variación %'),
                       variaciones(historico))

        ultima = self._servicios.cotizaciones.ultima(tipo_id)
        print(f'  Última cotización: {ultima}')

    @operacion('Libros con stock bajo')
    def _reporte_stock_bajo(self) -> None:
        limite = leer_entero('Stock menor o igual a', 5, minimo=0)

        # filter deja solamente los registros que están bajo el límite
        faltantes = list(filter(lambda registro: registro.cantidad <= limite,
                                self._servicios.stock.listar()))
        imprimir_tabla(
            ('Id libro', 'Título', 'Cantidad'),
            [(registro.libro.id, registro.libro.titulo, registro.cantidad)
             for registro in faltantes],
        )
