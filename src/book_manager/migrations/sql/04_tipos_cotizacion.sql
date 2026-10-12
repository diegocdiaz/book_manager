-- Datos de la tabla tipos_cotizacion (generado desde el CSV)
INSERT INTO tipos_cotizacion (id, nombre) VALUES (1, 'Oficial') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (2, 'Blue') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (3, 'MEP') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (4, 'CCL') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (5, 'Mayorista') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (6, 'Cripto') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (7, 'Tarjeta') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (8, 'Ahorro') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (9, 'Turista') ON CONFLICT (id) DO NOTHING;
INSERT INTO tipos_cotizacion (id, nombre) VALUES (10, 'Qatar') ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('tipos_cotizacion', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM tipos_cotizacion;
