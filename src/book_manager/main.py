"""Punto de entrada del sistema Book Manager.

Se encarga de abrir la conexión a la base de datos, armar los repositorios
y los servicios, resolver con qué datos se arranca y abrir la interfaz de
consola.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, inspect, select

from book_manager.database.connection import ConexionDB
from book_manager.models.models import LibroModelo, crear_tablas
from book_manager.preload_data.preload_data import cargar_datos_iniciales
from book_manager.repositories.repositories import (
    RepositorioAuditoria,
    RepositorioCotizacionDolar,
    RepositorioEditorial,
    RepositorioGenero,
    RepositorioLibro,
    RepositorioMoneda,
    RepositorioPrecio,
    RepositorioPrecioWeb,
    RepositorioStock,
    RepositorioTipoCotizacion,
)
from book_manager.services.services import (
    ServicioAuditoria,
    ServicioComparacionPrecios,
    ServicioCotizacionDolar,
    ServicioCotizador,
    ServicioEditorial,
    ServicioGenero,
    ServiciosLibreria,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)
from book_manager.ui.console import ConsolaLibreria


def hay_datos(conexion: ConexionDB) -> bool:
    """Dice si la base ya tiene las tablas creadas y libros cargados.

    Args:
        conexion (ConexionDB): Conexión a la base de datos.

    Returns:
        bool: True si la tabla libros existe y tiene al menos un registro.
    """
    if not inspect(conexion.engine).has_table(LibroModelo.__tablename__):
        return False
    with conexion.transaccion() as sesion:
        return bool(sesion.scalar(select(func.count(LibroModelo.id))))


def armar_servicios(conexion: ConexionDB) -> ServiciosLibreria:
    """Crea los repositorios sobre la base y les inyecta los servicios.

    Args:
        conexion (ConexionDB): Conexión a la base de datos que comparten
            todos los repositorios.

    Returns:
        ServiciosLibreria: Los servicios listos para usar.
    """
    repo_genero = RepositorioGenero(conexion)
    repo_editorial = RepositorioEditorial(conexion)
    repo_moneda = RepositorioMoneda(conexion)
    repo_tipo = RepositorioTipoCotizacion(conexion)
    repo_libro = RepositorioLibro(conexion)
    repo_precio = RepositorioPrecio(conexion)
    repo_stock = RepositorioStock(conexion)
    repo_cotizacion = RepositorioCotizacionDolar(conexion)
    repo_precio_web = RepositorioPrecioWeb(conexion)
    repo_auditoria = RepositorioAuditoria(conexion)

    generos = ServicioGenero(repo_genero, repo_libro)
    editoriales = ServicioEditorial(repo_editorial, repo_libro)
    monedas = ServicioMoneda(repo_moneda, repo_precio)
    tipos_cotizacion = ServicioTipoCotizacion(repo_tipo, repo_cotizacion)
    libros = ServicioLibro(repo_libro, editoriales, generos, repo_precio,
                           repo_stock)
    precios = ServicioPrecio(repo_precio, libros, monedas)
    stock = ServicioStock(repo_stock, libros)
    cotizaciones = ServicioCotizacionDolar(repo_cotizacion, tipos_cotizacion)
    cotizador = ServicioCotizador(libros, precios, cotizaciones)
    comparador = ServicioComparacionPrecios(repo_precio_web, libros, cotizador,
                                            tipos_cotizacion)
    auditoria = ServicioAuditoria(repo_auditoria)

    return ServiciosLibreria(generos, editoriales, monedas, tipos_cotizacion,
                             libros, precios, stock, cotizaciones, cotizador,
                             comparador, auditoria)


def preparar_servicios(
        import_default_data: bool = False,
        conexion: Optional[ConexionDB] = None) -> ServiciosLibreria:
    """Arma los servicios y decide con qué datos se arranca.

    Args:
        import_default_data (bool): Si es True se vuelven a migrar los datos
            de migrations/csv a la base. Si es False se usan los datos que
            ya están en la base, salvo que esté vacía.
        conexion (Optional[ConexionDB]): Conexión a usar. Si no se indica,
            se crea una con la variable de entorno DATABASE_URL.

    Returns:
        ServiciosLibreria: Los servicios listos para usar.
    """
    conexion = conexion or ConexionDB()
    # crea las tablas nuevas (por ejemplo auditoria) si la base es de un
    # sprint anterior
    crear_tablas(conexion.engine)
    migrar = import_default_data or not hay_datos(conexion)
    if import_default_data:
        print('Se migran de nuevo los datos de migrations/csv...')
    elif migrar:
        print('La base está vacía, se migran los datos de migrations/csv...')
    else:
        print('Se usan los datos que ya están en la base.')

    servicios = armar_servicios(conexion)
    if migrar:
        cargar_datos_iniciales(conexion)
        servicios.auditoria.registrar(
            'Migracion de datos iniciales',
            'Se cargaron los datos de migrations/csv en la base.')
    return servicios


def main(import_default_data: bool = False,
         conexion: Optional[ConexionDB] = None) -> None:
    """Ejecuta el sistema de gestión de la librería.

    Args:
        import_default_data (bool): Si es True se vuelven a migrar los
            datos iniciales antes de abrir el menú.
        conexion (Optional[ConexionDB]): Conexión a usar. Si no se indica,
            se crea una con la variable de entorno DATABASE_URL.
    """
    servicios = preparar_servicios(import_default_data, conexion)
    ConsolaLibreria(servicios).ejecutar()


if __name__ == '__main__':
    main()

