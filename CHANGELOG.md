# Changelog

## Sprint 2

### [Ejercicio 08]
- Nuevas opciones en el menú principal: obtener las cotizaciones por API, ver la lista de precios bimonetaria y exportar los precios a CSV.
- Lista de precios bimonetaria: muestra el precio de cada libro en pesos y en dólares según el tipo de cotización elegido.
- Exportación a CSV con el precio en ARS y USD de cada libro para todos los tipos de dólar que tienen cotización (por defecto en exports/precios_libros.csv).
- En los servicios se agregan ultimas(), precios_por_libro() y exportar_precios_csv(), y el cotizador reutiliza la misma regla de conversión para todos los cálculos.
- Se agrega la carpeta exports/ al .gitignore.

### [Ejercicio 07]
- Archivo .env con la URL de la API del dólar (API_URL). La URL de la base no se guarda ahí porque tiene la contraseña.
- Función obtener_cotizaciones en ServicioCotizacionDolar: descarga las cotizaciones de la API y las registra en la base (si ya existe la del día, la actualiza).
- Relación entre las casas de la API (oficial, blue, bolsa, etc.) y los tipos de cotización del sistema.
- Se agregan requests y python-dotenv a requirements.txt.


### [Ejercicio 06]
- Los repositorios pasan a guardar los datos en la base de datos con SQLAlchemy en lugar de archivos CSV.
- Repositorio genérico RepositorioDB que convierte los modelos de tabla en entidades y usa el context manager transaccion() en cada operación.
- Se mantienen los mismos métodos de los repositorios, así los servicios y la consola no cambian.
- main.py arma los repositorios con ConexionDB y, si la base está vacía, migra los datos de migrations/csv.
- La carga inicial de preload_data.py usa la función migrar_datos.

### [Ejercicio 05]
- Migración de los datos de los CSV a la base de datos con la función migrar_datos en migrations/migrations.py.
- Generación de un archivo .sql con los INSERT de cada tabla en migrations/sql.
- Carga respetando el orden de las claves foráneas, sin duplicar registros si se ejecuta más de una vez.
- Ajuste de las secuencias de id de PostgreSQL luego de la carga.

### [Ejercicio 04]
- Definición de las tablas del sistema con sus tipos de datos y relaciones en models/models.py.
- Restricciones para que precios, stock y cotizaciones no admitan valores negativos.
- Función crear_tablas para generar las tablas en la base.
- Se agrega la restricción única (tipo_id, fecha) en la tabla cotizaciones: hay una sola cotización por tipo de dólar y por día.
- La relación libro-stock pasa a ser 1 a 1: se agrega unique en stock.libro_id y la relación LibroModelo.stock deja de ser una lista.
- Las restricciones se aplican con ALTER TABLE a las tablas ya creadas en Supabase, porque create_all no modifica tablas que ya existen.

### [Ejercicio 03]
- Context manager transaccion() en ConexionDB para manejar las
  transacciones: hace commit si todo sale bien y rollback si hay un error.
- La sesión se cierra siempre al terminar el bloque with.

### [Ejercicio 02]
- Creación de la clase ConexionDB en database/connection.py, que maneja la
  conexión a la base PostgreSQL de Supabase con SQLAlchemy.
- La URL de conexión se lee de la variable de entorno DATABASE_URL.
- Se agregan SQLAlchemy y psycopg2-binary a requirements.txt.
- ConexionDB carga el archivo .env por sí misma con python-dotenv (ruta RUTA_ENV), en lugar de depender de que quien la use lo cargue antes.

### [Ejercicio 01]
- Creación de la rama Sprint_2 a partir de la rama Sprint_1.
- Nuevas carpetas database/ y models/ con los archivos connection.py y
  models.py, y la carpeta migrations/sql.
- Creación del archivo .env con la configuración de la base de datos SQLite.
- Actualización del README.md con el objetivo y el contexto del Sprint 2.

## Sprint 1

[Ejercicio 07]
- Creación de main.py, que arma los servicios y abre la interfaz de consola.
- Parámetro import_default_data para volver a importar los datos de
  migrations/csv cuando se lo pide.
- Si todavía no hay datos guardados se hace la carga inicial sola, porque la
  carpeta data/ no se versiona y en un clon nuevo no existe.

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
