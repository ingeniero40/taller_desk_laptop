import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar el proyecto
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.infrastructure.database.psycopg_db import Psycopg2Database

def testConnection():
    """
    Script de prueba para validar la conexión con Psycopg2.
    """
    print("--- Probando Conexión con Psycopg2 ---")
    load_dotenv()
    
    db = Psycopg2Database()


    isConnected = db.testConnection()
    
    if isConnected:
        print("✅ Conexión exitosa a la base de datos PostgreSQL!")
        
        # Probar una consulta simple
        try:
            results = db.executeRawQuery("SELECT version();", fetch=True)
            print(f"Versión de PostgreSQL: {results[0][0]}")
        except Exception as e:
            print(f"❌ Error al ejecutar consulta: {e}")
    else:
        print("❌ Falló la conexión. Verifique su archivo .env y el estado de PostgreSQL.")

if __name__ == "__main__":
    testConnection()
