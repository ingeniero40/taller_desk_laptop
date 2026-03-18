import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Añadir el raíz del proyecto para importar
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.domain.value_objects.user_role import UserRole
from Gestion_Taller_Computo.domain.value_objects.work_order_status import WorkOrderStatus
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from Gestion_Taller_Computo.application.use_cases.user_manager import UserManager
from Gestion_Taller_Computo.application.use_cases.device_manager import DeviceManager
from Gestion_Taller_Computo.application.use_cases.work_order_manager import WorkOrderManager

def test_work_order_flow():
    """
    Test de integración del flujo completo de taller.
    """
    print("--- 🛠️ Probando Flujo de Órdenes de Trabajo ---")
    load_dotenv()
    
    # 1. Setup inicial (Repo/Manager)
    user_mgr = UserManager(Psycopg2UserRepository())
    device_mgr = DeviceManager(Psycopg2DeviceRepository())
    order_mgr = WorkOrderManager(Psycopg2WorkOrderRepository())
    
    try:
        # A. Crear Técnico y Cliente
        print("A. Creando técnicos y clientes...")
        tech = user_mgr.create_user(f"tech_{uuid.uuid4().hex[:4]}", "t@t.com", "h", "Pedro Técnico", UserRole.TECHNICIAN)
        cust = user_mgr.create_user(f"cust_{uuid.uuid4().hex[:4]}", "c@c.com", "h", "Maria Cliente", UserRole.CUSTOMER)
        
        # B. Registrar dispositivo
        print(f"B. Registrando dispositivo para cliente {cust.full_name}...")
        dev = device_mgr.register_device("HP", "EliteBook 840", f"SN-{uuid.uuid4().hex[:6].upper()}", cust.id)
        
        # C. Abrir Orden de Trabajo
        print("C. Apertura de orden (recepción)...")
        order = order_mgr.open_order(dev.id, "No enciende, posible falla de board.")
        print(f"✅ Orden abierta. Ticket: {order.ticket_number}")
        
        # D. Asignar Técnico
        print(f"D. Asignando a {tech.full_name}...")
        order = order_mgr.assign_technician(order.id, tech.id)
        if order.status == WorkOrderStatus.IN_DIAGNOSIS:
            print("✅ Estado: En diagnóstico.")
            
        # E. Actualizar a Reparación
        print("E. Actualizando diagnóstico y presupuesto...")
        order = order_mgr.update_status(
            order.id, 
            WorkOrderStatus.IN_REPAIR, 
            notes="Cambio de condensadores en etapa de carga.", 
            price=1200.00
        )
        print(f"✅ Reparación en curso. Presupuesto: ${order.quoted_price}")
        
        # F. Finalizar
        print("F. Marcando como completado...")
        order = order_mgr.update_status(order.id, WorkOrderStatus.COMPLETED, notes="Equipo reparado y testeado 24h.")
        if order.status == WorkOrderStatus.COMPLETED:
            print("✅ Orden finalizada con éxito.")
            
        # G. Consultar Pendientes
        print("G. Consultando órdenes pendientes en taller...")
        pendings = order_mgr.get_pending_orders()
        print(f"   Órdenes en proceso actualmente: {len(pendings)}")
        
    except Exception as e:
        print(f"❌ Fallo en el flujo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_work_order_flow()
