-- Datos de la tabla stock (generado desde el CSV)
INSERT INTO stock (id, libro_id, cantidad) VALUES (1, 1, 12) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (2, 2, 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (3, 3, 8) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (4, 4, 15) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (5, 5, 6) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (6, 6, 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (7, 7, 20) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (8, 8, 9) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (9, 9, 7) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (10, 10, 5) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (11, 11, 10) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (12, 12, 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (13, 13, 11) ON CONFLICT (id) DO NOTHING;
INSERT INTO stock (id, libro_id, cantidad) VALUES (14, 14, 18) ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('stock', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM stock;
