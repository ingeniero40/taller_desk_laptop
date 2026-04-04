import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv
from ...domain.interfaces.database_handler import IDatabaseHandler

# Cargar variables de entorno siguiendo los estándares de seguridad
load_dotenv()


class Psycopg2Database(IDatabaseHandler):
    """
    Gestor de conexiones para PostgreSQL utilizando Psycopg2.
    Implementa la interfaz IDatabaseHandler siguiendo Clean Architecture.
    """

    _pool = None

    @classmethod
    def getPool(cls):
        """
        Inicializa y retorna el pool de conexiones seguras para hilos.
        """
        if cls._pool is None:
            # Forzar mensajes de error en inglés para evitar conflictos de encoding con caracteres especiales (ó, é, ñ)
            os.environ["PGMESSAGELANG"] = "English"

            # Recuperar URL de conexión desde variables de entorno
            databaseUrl = os.getenv("DATABASE_URL")

            if not databaseUrl:
                raise ValueError(
                    "DATABASE_URL no encontrada en las variables de entorno."
                )

            try:
                # Inicialización del pool de conexiones (Threaded para concurrencia en Reflex)
                cls._pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1, maxconn=20, dsn=databaseUrl
                )
            except Exception as e:
                # Manejo centralizado de errores de conexión
                print(f"Error crítico al inicializar el pool de base de datos: {e}")
                raise
        return cls._pool

    @classmethod
    @contextmanager
    def getConnection(cls):
        """
        Generador de contexto para obtener y liberar conexiones del pool de manera segura.
        """
        connPool = cls.getPool()
        connection = connPool.getconn()
        # Asegurar codificación UTF8 para evitar errores de caracteres especiales
        connection.set_client_encoding("UTF8")

        try:
            yield connection
        except Exception as e:
            # Rollback automático en caso de error durante la transacción
            connection.rollback()
            raise e
        finally:
            # Retorno obligatorio de la conexión al pool
            connPool.putconn(connection)

    @classmethod
    def executeRawQuery(cls, query, params=None, fetch=False):
        """
        Ejecuta una consulta SQL nativa de manera segura contra inyecciones SQL.

        Args:
            query (str): Sentencia SQL a ejecutar.
            params (tuple, optional): Parámetros para la consulta.
            fetch (bool): Si se desea retornar los resultados.

        Returns:
            list: Resultados de la consulta si fetch=True, de lo contrario None.
        """
        with cls.getConnection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall() if fetch else None
                conn.commit()
                return results

    @classmethod
    def testConnection(cls):
        """
        Valida la conectividad básica con la base de datos.
        """
        try:
            results = cls.executeRawQuery("SELECT 1", fetch=True)
            return results is not None and len(results) > 0 and results[0][0] == 1
        except Exception:
            return False
