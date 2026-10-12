-- Datos de la tabla monedas (generado desde el CSV)
INSERT INTO monedas (id, codigo, nombre) VALUES (1, 'ARS', 'Peso argentino') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (2, 'USD', 'Dólar estadounidense') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (3, 'EUR', 'Euro') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (4, 'BRL', 'Real brasileño') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (5, 'UYU', 'Peso uruguayo') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (6, 'CLP', 'Peso chileno') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (7, 'GBP', 'Libra esterlina') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (8, 'MXN', 'Peso mexicano') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (9, 'JPY', 'Yen japonés') ON CONFLICT (id) DO NOTHING;
INSERT INTO monedas (id, codigo, nombre) VALUES (10, 'CNY', 'Yuan chino') ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('monedas', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM monedas;
