-- Datos de la tabla generos (generado desde el CSV)
INSERT INTO generos (id, nombre) VALUES (1, 'Novela') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (2, 'Cuentos') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (3, 'Historia') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (4, 'Policial y misterio') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (5, 'Psicología') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (6, 'Autoayuda') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (7, 'Acertijos y juegos') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (8, 'Infantil') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (9, 'Poesía') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (10, 'Ciencia ficción') ON CONFLICT (id) DO NOTHING;
INSERT INTO generos (id, nombre) VALUES (11, 'Biografía') ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('generos', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM generos;
