import os
import sys
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

# Añadir el directorio raíz al path para poder importar los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar todas las entidades para que SQLModel las registre en el metadata
try:
    from Gestion_Taller_Computo.domain.entities.user import User
    from Gestion_Taller_Computo.domain.entities.device import Device
    from Gestion_Taller_Computo.domain.entities.work_order import WorkOrder
    from Gestion_Taller_Computo.domain.entities.product import Product
    from Gestion_Taller_Computo.domain.entities.supplier import Supplier
    from Gestion_Taller_Computo.domain.entities.invoice import Invoice
    from Gestion_Taller_Computo.domain.entities.payment import Payment
except UnicodeDecodeError as e:
    print(f"Error de codificación al importar entidades: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado al importar entidades: {e}")
    sys.exit(1)


def sync_database():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL no encontrada en el archivo .env")
        return

    # No imprimimos la URL completa por seguridad y para evitar errores de codificación en consola
    print("Conectando a la base de datos...")

    try:
        engine = create_engine(database_url, echo=False)

        print("Probando conexión básica...")
        with engine.connect() as connection:
            from sqlmodel import text
            connection.execute(text("SELECT 1"))
        print("✅ Conexión básica exitosa.")

        print("Creando tablas en la base de datos...")
        SQLModel.metadata.create_all(engine)
        print("¡Sincronización exitosa! Todas las tablas han sido creadas o ya existen.")
    except Exception as e:
        print(f"Error durante la sincronización: {type(e).__name__}")
        # Intentamos imprimir el error de forma segura
        try:
            print(f"Detalle: {str(e)}")
        except:
            print("No se pudo mostrar el detalle del error por problemas de codificación.")


if __name__ == "__main__":
    sync_database()
