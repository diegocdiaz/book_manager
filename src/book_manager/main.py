"""Punto de entrada del sistema Book Manager.

Se encarga de armar los repositorios y los servicios, resolver de dónde
salen los datos y abrir la interfaz de consola.
"""

from __future__ import annotations

from pathlib import Path

from book_manager.preload_data.preload_data import (
    borrar_datos_guardados,
    cargar_datos_iniciales,
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
from book_manager.services.services import (
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


def hay_datos(directorio: Path) -> bool:
    """Dice si en el directorio ya hay datos guardados.

    Args:
        directorio (Path): Carpeta donde se persisten los csv.

    Returns:
        bool: True si hay al menos un archivo csv guardado.
    """
    return directorio.exists() and any(directorio.glob('*.csv'))


def armar_servicios(directorio: Path = DIRECTORIO_DATOS) -> ServiciosLibreria:
    """Crea los repositorios y les inyecta a los servicios lo que necesitan.

    Los repositorios que dependen de otros (libro, precio, stock y
    cotización) reciben los que ya se crearon, así todos comparten los
    mismos objetos en memoria.

    Args:
        directorio (Path): Carpeta donde se persisten los csv.

    Returns:
        ServiciosLibreria: Los servicios listos para usar.
    """
    repo_genero = RepositorioGenero(directorio)
    repo_editorial = RepositorioEditorial(directorio)
    repo_moneda = RepositorioMoneda(directorio)
    repo_tipo = RepositorioTipoCotizacion(directorio)
    repo_libro = RepositorioLibro(repo_editorial, repo_genero, directorio)
    repo_precio = RepositorioPrecio(repo_libro, repo_moneda, directorio)
    repo_stock = RepositorioStock(repo_libro, directorio)
    repo_cotizacion = RepositorioCotizacionDolar(repo_tipo, directorio)

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

    return ServiciosLibreria(generos, editoriales, monedas, tipos_cotizacion,
                             libros, precios, stock, cotizaciones, cotizador)


def preparar_servicios(
        import_default_data: bool = False,
        directorio: Path = DIRECTORIO_DATOS) -> ServiciosLibreria:
    """Arma los servicios y decide con qué datos se arranca.

    Args:
        import_default_data (bool): Si es True se vuelven a importar los
            datos de migrations/csv, borrando lo que hubiera guardado. Si es
            False se usan los datos que ya están persistidos, salvo que no
            haya ninguno.
        directorio (Path): Carpeta donde se persisten los csv.

    Returns:
        ServiciosLibreria: Los servicios listos para usar.
    """
    if import_default_data:
        print('Se importan de nuevo los datos de migrations/csv...')
    elif not hay_datos(directorio):
        # la carpeta data/ está en el .gitignore, así que en un clon nuevo
        # no existe. Se hace la carga inicial para no arrancar vacío.
        print('No hay datos guardados, se cargan los de migrations/csv...')
    else:
        print('Se usan los datos que ya estaban guardados.')
        return armar_servicios(directorio)

    # se borra antes de armar los repositorios porque leen el csv al crearse
    borrar_datos_guardados(directorio)
    servicios = armar_servicios(directorio)
    cargar_datos_iniciales(servicios)
    return servicios


def main(import_default_data: bool = False,
         directorio: Path = DIRECTORIO_DATOS) -> None:
    """Ejecuta el sistema de gestión de la librería.

    Args:
        import_default_data (bool): Si es True se vuelven a importar los
            datos iniciales antes de abrir el menú.
        directorio (Path): Carpeta donde se persisten los csv.
    """
    servicios = preparar_servicios(import_default_data, directorio)
    ConsolaLibreria(servicios).ejecutar()


if __name__ == '__main__':
    main()
