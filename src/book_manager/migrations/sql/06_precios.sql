-- Datos de la tabla precios (generado desde el CSV)
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (1, 1, 1, 34900) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (2, 2, 2, 26) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (3, 2, 3, 24) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (4, 3, 1, 43500) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (5, 4, 1, 44999) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (6, 5, 1, 44500) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (7, 6, 2, 15) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (8, 6, 3, 14) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (9, 7, 1, 39900) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (10, 8, 1, 35500) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (11, 9, 1, 38900) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (12, 10, 1, 47900) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (13, 11, 1, 23900) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (14, 12, 1, 36500) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (15, 13, 1, 41500) ON CONFLICT (id) DO NOTHING;
INSERT INTO precios (id, libro_id, moneda_id, valor) VALUES (16, 14, 1, 52900) ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('precios', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM precios;
