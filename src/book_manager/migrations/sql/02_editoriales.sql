-- Datos de la tabla editoriales (generado desde el CSV)
INSERT INTO editoriales (id, nombre, contacto) VALUES (1, 'Random House', 'penguinlibros.com/ar') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (2, 'Anagrama', 'anagrama-ed.es') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (3, 'Planeta', 'planetadelibros.com.ar') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (4, 'Alfaguara', 'penguinlibros.com/ar') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (5, 'Penguin Random House', 'penguinlibros.com/ar') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (6, 'Herder', 'herdereditorial.com') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (7, 'Urano', NULL) ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (8, 'Booket', 'planetadelibros.com.ar') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (9, 'Plaza & Janés', 'penguinlibros.com/ar') ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (10, 'Little Rex', NULL) ON CONFLICT (id) DO NOTHING;
INSERT INTO editoriales (id, nombre, contacto) VALUES (11, 'Siglo XXI', NULL) ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('editoriales', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM editoriales;
