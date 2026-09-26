# Changelog
[Ejercicio 06]
- Interfaz de consola en ui/console.py con el menú principal y un menú de
  CRUD por cada entidad (listar, nuevo, modificar y borrar).
- Funciones para leer texto, enteros, decimales y fechas por teclado, que
  no dejan seguir hasta que el dato es válido.
- Decorador para las opciones del menú, que muestra el error de los
  servicios en pantalla en lugar de cortar el programa.
- Menú de reportes: cotización de un libro, cotización del catálogo,
  comparación con la competencia, histórico de un tipo de dólar y libros
  con stock bajo.

[Ejercicio 05]
- Creación de los archivos csv con los datos iniciales de cada entidad en
  la carpeta migrations/csv (mínimo 10 registros por clase).
- Carga de los datos iniciales en preload_data.py.
- Se quitan de los servicios métodos que no se usaban.
- Corrección del docstring y los type hints de los servicios.

[Ejercicio 04]
- Definición de las clases de servicio con la lógica de cada entidad.
- Validaciones antes de guardar (datos repetidos, ISBN, precios y stock).
- Control para no borrar registros que están en uso.
- Cálculo de precios en ARS/USD según el tipo de dólar y reportes.

[Ejercicio 03]
- Definición de las clases de persistencia con CRUD completo para cada entidad.

[Ejercicio 02]
- Definición de las clases entidad: EntidadBase, Genero, Editorial, Moneda,
  TipoCotizacion, Libro, Precio, Stock y CotizacionDolar.
- Aplicación de encapsulamiento mediante propiedades con validación.


[Ejercicio 01]
- Inicialización del repositorio y configuración del control de versiones.
- Creación de la rama Sprint_1.
- Definición de la estructura de directorios del proyecto.
- Creación de README.md y CHANGELOG.md.
