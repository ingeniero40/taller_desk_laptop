# diagnostic_conexion.py
import os
from dotenv import load_dotenv
import psycopg2


def diagnosticar():
    print("🔍 DIAGNÓSTICO DE CONEXIÓN")
    print("-" * 50)

    # 1. Verificar variables de entorno
    print("\n1. Variables de entorno:")
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        print(f"   DATABASE_URL encontrada: {database_url}")
        print(f"   Tipo: {type(database_url)}")
        print(f"   Longitud: {len(database_url)}")

        # Mostrar la URL como bytes para ver caracteres problemáticos
        url_bytes = database_url.encode("utf-8", errors="backslashreplace")
        print(f"   Como bytes: {url_bytes[:100]}...")

        # Buscar el byte 0xf3
        if 0xF3 in database_url.encode("latin1", errors="ignore"):
            pos = database_url.encode("latin1").index(0xF3)
            print(f"   ⚠️  Encontrado byte 0xf3 en posición: {pos}")
            print(f"   Caracteres alrededor: {database_url[max(0, pos-20):pos+20]}")
    else:
        print("   ❌ DATABASE_URL no encontrada")
        return

    # 2. Extraer componentes manualmente
    print("\n2. Componentes de la conexión:")
    try:
        # postgresql://user:password@host:port/database
        if database_url.startswith("postgresql://"):
            resto = database_url[13:]  # quitar 'postgresql://'
            user_pass, host_db = resto.split("@")
            user, password = user_pass.split(":")
            host_port, database = host_db.split("/")

            print(f"   Usuario: {user}")
            print(f"   Password: {'*' * len(password)}")
            print(f"   Host:Port: {host_port}")
            print(f"   Database: {database}")

            # Verificar si hay caracteres especiales en password
            for char in password:
                if ord(char) > 127:
                    print(
                        f"   ⚠️  Carácter especial en password: '{char}' (ASCII: {ord(char)})"
                    )
    except Exception as e:
        print(f"   Error al parsear URL: {e}")

    # 3. Probar conexión con diferentes enfoques
    print("\n3. Probando diferentes métodos de conexión:")

    # Método 1: Conectar con parámetros individuales (evita el DSN)
    try:
        # Extraer componentes para conexión manual
        resto = database_url[13:]
        user_pass, host_db = resto.split("@")
        user, password = user_pass.split(":")
        host_port, database = host_db.split("/")
        host, port = host_port.split(":")

        print(f"   Intentando conexión con parámetros individuales...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            client_encoding="latin1",  # Forzar codificación Latin1
        )
        print("   ✅ Conexión exitosa con parámetros individuales!")
        conn.close()
    except Exception as e:
        print(f"   ❌ Error con parámetros: {e}")

    # Método 2: Conectar con DSN pero forzando bytes
    try:
        print(f"\n   Intentando conexión con DSN en bytes...")
        conn = psycopg2.connect(database_url.encode("latin1").decode("latin1"))
        print("   ✅ Conexión exitosa con DSN en bytes!")
        conn.close()
    except Exception as e:
        print(f"   ❌ Error con DSN: {e}")


if __name__ == "__main__":
    diagnosticar()
