# Book Manager

## Sprint actual: Sprint 2

## Objetivo
Ampliar el sistema de gestión de inventario de la librería para que persista
sus datos en una base de datos relacional usando el ORM SQLAlchemy,
consolidando el manejo de bases de datos, la normalización, la conexión segura
y la carga inicial de datos.

## Introducción y contexto
Una librería con venta al público necesita modernizar su sistema de gestión de
inventario de libros. Debido a la fluctuación en los costos de importación de
material bibliográfico, el sistema debe gestionar precios en diferentes
monedas (ARS, USD) y seguir de cerca la cotización del dólar (Oficial, Blue,
MEP, etc.) para actualizar sus valores en tiempo real.

En el Sprint 1 se desarrolló una aplicación de consola (CLI) en Python que
permite gestionar el inventario, cotizar los libros según el valor del dólar y
comparar precios con la competencia, guardando los datos en archivos csv.

En este Sprint 2, partiendo del último push del Sprint 1, se migran todos los
datos de los archivos a tablas de una base de datos relacional (PostgreSQL
en Supabase) con SQLAlchemy, y se incorporan consultas a APIs externas.
