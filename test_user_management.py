import os
import sys
import uuid
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar el proyecto
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.domain.value_objects.user_role import UserRole
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from Gestion_Taller_Computo.application.use_cases.user_manager import UserManager

def test_user_management():
    """
    Script para validar la gestión de usuarios desde el caso de uso hasta la base de datos.
    """
    print("--- 👤 Probando Gestión de Usuarios (Psycopg2) ---")
    load_dotenv()
    
    # Inicializar componentes
    repository = Psycopg2UserRepository()
    manager = UserManager(repository)
    
    test_username = f"tecnico_{uuid.uuid4().hex[:6]}"
    
    try:
        # 1. Crear Usuario
        print(f"1. Creando usuario '{test_username}'...")
        user = manager.create_user(
            username=test_username,
            email=f"{test_username}@taller.com",
            password_hash="hashed_password_123",
            full_name="Técnico de Pruebas",
            role=UserRole.TECHNICIAN,
            phone="555-0102"
        )
        print(f"✅ Usuario creado con ID: {user.id}")
        
        # 2. Listar todos los usuarios
        print("2. Listando usuarios...")
        all_users = manager.get_all_users()
        print(f"   Total usuarios encontrados: {len(all_users)}")
        
        # 3. Buscar por ID
        print(f"3. Buscando usuario por ID {user.id}...")
        found = manager.get_user_by_id(user.id)
        if found and found.username == test_username:
            print(f"✅ Usuario {found.username} recuperado correctamente.")
        else:
            print("❌ No se encontró el usuario recién creado.")
            
        # 4. Actualizar estado
        print("4. Cambiando estado del usuario (inactivo)...")
        updated = manager.update_user_status(user.id, is_active=False)
        if not updated.is_active:
            print("✅ Estado actualizado satisfactoriamente.")
        else:
            print("❌ No se pudo actualizar el estado.")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_management()
