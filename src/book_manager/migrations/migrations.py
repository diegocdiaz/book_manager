"""Migración de los datos del Sprint 1 (archivos CSV) a la base de datos.

La función principal, migrar_datos, hace dos cosas con los CSV de cada tabla:

1. Genera un archivo .sql con las sentencias INSERT equivalentes.
2. Carga los mismos datos en la base de datos relacional.

Las tablas se procesan respetando las claves foráneas: primero las que no
dependen de ninguna otra y después las que referencian a las anteriores.
La migración se puede ejecutar más de una vez sin duplicar registros.
"""

import csv
import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from sqlalchemy import text
from sqlalchemy.orm import Session

from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    Base,
    CotizacionDolarModelo,
    EditorialModelo,
    GeneroModelo,
    LibroModelo,
    MonedaModelo,
    PrecioModelo,
    StockModelo,
    TipoCotizacionModelo,
    crear_tablas,
)

Conversor = Callable[[str], Any]
Fila = Dict[str, Any]


def _a_entero(valor: str) -> int:
    """Convierte un texto a número entero."""
    return int(valor)


def _a_decimal(valor: str) -> Decimal:
    """Convierte un texto a número decimal exacto."""
    return Decimal(valor)


def _a_fecha(valor: str) -> datetime.date:
    """Convierte un texto con formato AAAA-MM-DD a fecha."""
    return datetime.date.fromisoformat(valor)


def _a_texto_opcional(valor: str) -> Optional[str]:
    """Devuelve el texto, o None si el campo está vacío."""
    return valor or None


# Orden de migración: primero las tablas sin dependencias y luego las que
# tienen claves foráneas. Cada elemento indica el nombre del CSV (igual al de
# la tabla), el modelo y cómo convertir las columnas que no son texto.
TABLAS: List[Tuple[str, Type[Base], Dict[str, Conversor]]] = [
    ('generos', GeneroModelo, {'id': _a_entero}),
    (
        'editoriales',
        EditorialModelo,
        {'id': _a_entero, 'contacto': _a_texto_opcional},
    ),
    ('monedas', MonedaModelo, {'id': _a_entero}),
    ('tipos_cotizacion', TipoCotizacionModelo, {'id': _a_entero}),
    (
        'libros',
        LibroModelo,
        {
            'id': _a_entero,
            'editorial_id': _a_entero,
            'genero_id': _a_entero,
        },
    ),
    (
        'precios',
        PrecioModelo,
        {
            'id': _a_entero,
            'libro_id': _a_entero,
            'moneda_id': _a_entero,
            'valor': _a_decimal,
        },
    ),
    (
        'stock',
        StockModelo,
        {'id': _a_entero, 'libro_id': _a_entero, 'cantidad': _a_entero},
    ),
    (
        'cotizaciones',
        CotizacionDolarModelo,
        {
            'id': _a_entero,
            'tipo_id': _a_entero,
            'fecha': _a_fecha,
            'valor_compra': _a_decimal,
            'valor_venta': _a_decimal,
        },
    ),
]


def _leer_csv(ruta: Path) -> List[Dict[str, str]]:
    """Lee un archivo CSV y devuelve sus filas como diccionarios de texto."""
    with open(ruta, newline='', encoding='utf-8-sig') as archivo:
        lector = csv.DictReader(archivo)
        return [
            {columna: (valor or '').strip() for columna, valor in fila.items()}
            for fila in lector
        ]


def _convertir_fila(fila: Dict[str, str],
                    conversores: Dict[str, Conversor]) -> Fila:
    """Convierte los valores de una fila a los tipos de la tabla."""
    return {
        columna: conversores.get(columna, str)(valor)
        for columna, valor in fila.items()
    }


def _literal_sql(valor: Any) -> str:
    """Devuelve un valor escrito como literal SQL."""
    if valor is None:
        return 'NULL'
    if isinstance(valor, (int, Decimal)):
        return str(valor)
    if isinstance(valor, datetime.date):
        return f"'{valor.isoformat()}'"
    texto = str(valor).replace("'", "''")
    return f"'{texto}'"


def _escribir_sql(ruta: Path, tabla: str, filas: List[Fila]) -> None:
    """Escribe el archivo .sql con los INSERT de una tabla.

    Las sentencias usan ON CONFLICT DO NOTHING para poder ejecutarse más de
    una vez, y al final se ajusta la secuencia del id de la tabla.
    """
    lineas = [f'-- Datos de la tabla {tabla} (generado desde el CSV)']
    if filas:
        columnas = ', '.join(filas[0].keys())
        for fila in filas:
            valores = ', '.join(_literal_sql(v) for v in fila.values())
            lineas.append(
                f'INSERT INTO {tabla} ({columnas}) VALUES ({valores}) '
                'ON CONFLICT (id) DO NOTHING;'
            )
        lineas.append(_sentencia_secuencia(tabla) + ';')
    ruta.write_text('\n'.join(lineas) + '\n', encoding='utf-8')


def _sentencia_secuencia(tabla: str) -> str:
    """Devuelve el SELECT que ajusta la secuencia del id al máximo cargado."""
    return (
        f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), "
        f'COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {tabla}'
    )


def _reiniciar_secuencias(sesion: Session) -> None:
    """Ajusta las secuencias de id de PostgreSQL tras insertar ids explícitos.

    Sin este paso, el próximo alta sin id intentaría usar el 1 y fallaría por
    clave duplicada. En otros motores de base no hace falta.
    """
    if sesion.get_bind().dialect.name != 'postgresql':
        return
    for tabla, _, _ in TABLAS:
        sesion.execute(text(_sentencia_secuencia(tabla)))


def migrar_datos(carpeta_csvs: str, carpeta_sqls: str,
                 conexion: Optional[ConexionDB] = None) -> None:
    """Migra los datos de los CSV a archivos .sql y a la base de datos.

    Args:
        carpeta_csvs (str): Carpeta con los archivos CSV de origen.
        carpeta_sqls (str): Carpeta donde se escriben los archivos .sql.
        conexion (Optional[ConexionDB]): Conexión a usar. Si no se indica,
            se crea una con la variable de entorno DATABASE_URL.
    """
    origen = Path(carpeta_csvs)
    destino = Path(carpeta_sqls)
    destino.mkdir(parents=True, exist_ok=True)

    conexion_propia = conexion is None
    conexion = conexion or ConexionDB()
    try:
        crear_tablas(conexion.engine)
        with conexion.transaccion() as sesion:
            for numero, (tabla, modelo, conversores) in enumerate(TABLAS, 1):
                filas = [
                    _convertir_fila(fila, conversores)
                    for fila in _leer_csv(origen / f'{tabla}.csv')
                ]
                _escribir_sql(destino / f'{numero:02d}_{tabla}.sql',
                              tabla, filas)
                for fila in filas:
                    sesion.merge(modelo(**fila))
                sesion.flush()
                print(f'{tabla}: {len(filas)} registros migrados')
            _reiniciar_secuencias(sesion)
    finally:
        if conexion_propia:
            conexion.cerrar()
