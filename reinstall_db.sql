-- -----------------------------------------------------------------------------
-- SCRIPT DE REINSTALACIÓN: taller_db
-- -----------------------------------------------------------------------------
-- IMPORTANTE: Este script debe ejecutarse desde una conexión 
-- a la base de datos maestra 'postgres'.
-- -----------------------------------------------------------------------------

-- 1. Intentar forzar el cierre de todas las conexiones activas a la base de datos 'taller_db'
-- Esto es crítico si hay otros procesos o clientes (como pgAdmin) conectados.
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'taller_db'
  AND pid <> pg_backend_pid();

-- 2. Eliminar la base de datos si ya existe para asegurar un inicio limpio.
DROP DATABASE IF EXISTS taller_db;

-- 3. Crear la base de datos de nuevo con los parámetros predeterminados.
CREATE DATABASE taller_db;

-- Mensaje de éxito
DO $$
BEGIN
    RAISE NOTICE 'Base de datos taller_db restablecida exitosamente.';
    RAISE NOTICE 'Ahora puede ejecutar el script de sincronización de tablas: python sync_db.py';
END $$;
