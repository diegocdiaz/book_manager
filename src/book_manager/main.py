"""Punto de entrada del sistema Book Manager.

Se encarga de armar los servicios, resolver de dónde salen los datos y
abrir la interfaz de consola.
"""

from __future__ import annotations

from pathlib import Path

from book_manager.preload_data.preload_data import cargar_datos_iniciales
from book_manager.repositories.repositories import DIRECTORIO_DATOS
from book_manager.services.services import ServiciosLibreria
from book_manager.ui.console import ConsolaLibreria


def hay_datos(directorio: Path) -> bool:
    """Dice si en el directorio ya hay datos guardados.

    Args:
        directorio (Path): Carpeta donde se persisten los csv.

    Returns:
        bool: True si hay al menos un archivo csv guardado.
    """
    return directorio.exists() and any(directorio.glob('*.csv'))


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
        return cargar_datos_iniciales(directorio)

    if not hay_datos(directorio):
        # la carpeta data/ está en el .gitignore, así que en un clon nuevo
        # no existe. Se hace la carga inicial para no arrancar vacío.
        print('No hay datos guardados, se cargan los de migrations/csv...')
        return cargar_datos_iniciales(directorio)

    print('Se usan los datos que ya estaban guardados.')
    return ServiciosLibreria(directorio)


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
