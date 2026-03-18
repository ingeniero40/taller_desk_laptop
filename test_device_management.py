import os
import sys
import uuid
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar el proyecto
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.domain.value_objects.user_role import UserRole
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from Gestion_Taller_Computo.application.use_cases.user_manager import UserManager
from Gestion_Taller_Computo.application.use_cases.device_manager import DeviceManager

def test_device_management():
    """
    Script para validar la gestión de dispositivos y su relación con clientes.
    """
    print("--- 💻 Probando Gestión de Dispositivos (Psycopg2) ---")
    load_dotenv()
    
    # Inicializar componentes
    user_repo = Psycopg2UserRepository()
    user_manager = UserManager(user_repo)
    
    device_repo = Psycopg2DeviceRepository()
    device_manager = DeviceManager(device_repo)
    
    # Datos de prueba
    test_customer_name = f"cliente_{uuid.uuid4().hex[:6]}"
    test_serial = f"SERIAL-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # 1. Crear Cliente
        print(f"1. Creando cliente de prueba '{test_customer_name}'...")
        customer = user_manager.create_user(
            username=test_customer_name,
            email=f"{test_customer_name}@gmail.com",
            password_hash="pwd123",
            full_name="Juan Perez Cliente",
            role=UserRole.CUSTOMER,
            phone="555-9001"
        )
        print(f"✅ Cliente creado con ID: {customer.id}")
        
        # 2. Registrar Dispositivo
        print(f"2. Registrando dispositivo con serie '{test_serial}'...")
        device = device_manager.register_device(
            brand="DELL",
            model="Latitude 5420",
            serial_number=test_serial,
            customer_id=customer.id
        )
        print(f"✅ Dispositivo registrado con ID: {device.id}")
        
        # 3. Listar por cliente
        print(f"3. Listando dispositivos para el cliente {customer.id}...")
        devices = device_manager.get_devices_by_customer(customer.id)
        if len(devices) > 0 and devices[0].serial_number == test_serial:
            print(f"✅ Se encontró {len(devices)} dispositivo(s) para el cliente.")
        else:
            print("❌ No se encontraron dispositivos para el cliente.")
            
        # 4. Actualizar información
        print("4. Actualizando modelo del dispositivo...")
        updated = device_manager.update_device_info(device.id, model="Latitude 5420 Pro")
        if updated.model == "Latitude 5420 Pro":
            print("✅ Información de dispositivo actualizada.")
        else:
            print("❌ Falló la actualización de información.")
            
        # 5. Listar todos
        print("5. Listando todos los dispositivos del taller...")
        all_devices = device_manager.get_all_devices()
        print(f"   Total en taller: {len(all_devices)}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_device_management()
