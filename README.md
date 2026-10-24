# Book Manager

## Sprint actual: Sprint 3

## Objetivo
Ampliar el sistema de gestión de inventario de la librería para que obtenga
datos de la web: extraer con Scrapy los precios de los libros del catálogo en
el sitio de Cúspide, compararlos con los precios internos, generar alertas y
reportes en Excel, y registrar en una tabla de auditoría cada operación del
sistema.

## Introducción y contexto
Una librería con venta al público necesita modernizar su sistema de gestión de
inventario de libros. Debido a la fluctuación en los costos de importación de
material bibliográfico, el sistema debe gestionar precios en diferentes
monedas (ARS, USD) y seguir de cerca la cotización del dólar (Oficial, Blue,
MEP, etc.) para actualizar sus valores en tiempo real.

En el Sprint 1 se desarrolló una aplicación de consola (CLI) en Python que
permite gestionar el inventario, cotizar los libros según el valor del dólar y
comparar precios con la competencia, guardando los datos en archivos csv.

En el Sprint 2 se migraron los datos a una base de datos relacional
(PostgreSQL en Supabase) con SQLAlchemy y se incorporó la consulta de las
cotizaciones del dólar a una API externa.

En este Sprint 3, partiendo del último push del Sprint 2, se obtienen los
precios de los competidores (librerías con venta online) para poder
compararse con ellos y competir de forma más informada. Solo se buscan en
Cúspide los libros que están en el catálogo propio.
