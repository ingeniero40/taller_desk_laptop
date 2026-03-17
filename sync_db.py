import os
import sys
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

# Añadir el directorio raíz al path para poder importar los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar todas las entidades para que SQLModel las registre en el metadata
from Gestion_Taller_Computo.domain.entities.user import User
from Gestion_Taller_Computo.domain.entities.device import Device
from Gestion_Taller_Computo.domain.entities.work_order import WorkOrder
from Gestion_Taller_Computo.domain.entities.product import Product
from Gestion_Taller_Computo.domain.entities.supplier import Supplier
from Gestion_Taller_Computo.domain.entities.invoice import Invoice
from Gestion_Taller_Computo.domain.entities.payment import Payment

def sync_database():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("Error: DATABASE_URL no encontrada en el archivo .env")
        return

    print(f"Conectando a: {database_url}...")
    engine = create_engine(database_url)
    
    print("Creando tablas en la base de datos...")
    try:
        SQLModel.metadata.create_all(engine)
        print("¡Sincronización exitosa! Todas las tablas han sido creadas.")
    except Exception as e:
        print(f"Error durante la sincronización: {e}")

if __name__ == "__main__":
    sync_database()
