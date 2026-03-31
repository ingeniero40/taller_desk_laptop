import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
import sys

# Configuración de codificación para evitar errores en Windows
if sys.platform == "win32":
    import subprocess
    # Asegurar que los mensajes de PG estén en inglés para evitar problemas de encoding
    os.environ['PGMESSAGELANG'] = 'English'

# Añadir el path del proyecto para importaciones relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar entidades para que SQLModel las registre
try:
    from Gestion_Taller_Computo.domain.entities.user import User
    from Gestion_Taller_Computo.domain.entities.device import Device
    from Gestion_Taller_Computo.domain.entities.work_order import WorkOrder
    from Gestion_Taller_Computo.domain.entities.product import Product
    from Gestion_Taller_Computo.domain.entities.supplier import Supplier
    from Gestion_Taller_Computo.domain.entities.invoice import Invoice
    from Gestion_Taller_Computo.domain.entities.payment import Payment
except Exception as e:
    print(f"⚠️ Advertencia al importar entidades: {e}")

def reinstall_database():
    """
    Script de automatización para reinstalar la base de datos local.
    Realiza un drop completo, creación de DB y generación de esquema.
    """
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ Error: DATABASE_URL no encontrada en el archivo .env")
        return

    # Extraer componentes de la URL
    # Formato esperado: postgresql://user:pass@host:port/dbname
    try:
        parts = db_url.rsplit('/', 1)
        base_url = parts[0]
        db_name = parts[1]
        postgres_url = f"{base_url}/postgres"
    except Exception:
        print("❌ Error: Formato de DATABASE_URL inválido.")
        return

    print(f"\n🚀 Iniciando reinstalación de: {db_name}")
    print("-" * 40)
    
    try:
        # 1. Conectar a la BD 'postgres' para realizar operaciones administrativas
        print("🔗 Conectando al servidor PostgreSQL...")
        conn = psycopg2.connect(postgres_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 2. Terminar conexiones activas (evita el error 'database is being accessed by other users')
        print(f"🔒 Terminando sesiones activas en '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
              AND pid <> pg_backend_pid();
        """, (db_name,))

        # 3. Drop y Create
        print(f"🗑️  Borrando base de datos '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        
        print(f"✨ Creando base de datos '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name}")

        cursor.close()
        conn.close()
        print("✅ Base de datos base lista.")

        # 4. Crear esquema (Tablas y Relaciones) usando SQLModel
        print("🏗️  Generando tablas y relaciones desde modelos...")
        engine = create_engine(db_url, echo=False)
        SQLModel.metadata.create_all(engine)
        
        print("-" * 40)
        print("✅ REINSTALACIÓN EXITOSA")
        print(f"La base de datos '{db_name}' ha sido reiniciada con el esquema actual.")
        print("-" * 40)

    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    reinstall_database()
