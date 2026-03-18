import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Añadir el raíz del proyecto para importar
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.domain.value_objects.user_role import UserRole
from Gestion_Taller_Computo.domain.value_objects.billing_types import InvoiceStatus, PaymentMethod
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_invoice_repository import Psycopg2InvoiceRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_payment_repository import Psycopg2PaymentRepository
from Gestion_Taller_Computo.application.use_cases.user_manager import UserManager
from Gestion_Taller_Computo.application.use_cases.work_order_manager import WorkOrderManager
from Gestion_Taller_Computo.application.use_cases.billing_manager import BillingManager

def test_billing_flow():
    """
    Test de integración para el flujo de facturación y cobros.
    """
    print("--- 💸 Probando Flujo de Facturación y Cobros ---")
    load_dotenv()
    
    # 1. Setup inicial (Repo/Manager)
    user_mgr = UserManager(Psycopg2UserRepository())
    order_mgr = WorkOrderManager(Psycopg2WorkOrderRepository())
    billing_mgr = BillingManager(Psycopg2InvoiceRepository(), Psycopg2PaymentRepository())
    device_mgr = DeviceManager(Psycopg2DeviceRepository())
    
    try:
        # A. Crear Cliente y Dispositivo
        print("A. Creando cliente y dispositivo para facturar...")
        cust = user_mgr.create_user(f"bill_{uuid.uuid4().hex[:4]}", "b@b.com", "h", "Luis Facturas", UserRole.CUSTOMER)
        dev = device_mgr.register_device("Apple", "MacBook Pro M1", f"SN-MBP-{uuid.uuid4().hex[:4].upper()}", cust.id)
        
        # B. Crear Orden y Cerrarla para Cobro
        print("B. Abriendo orden de trabajo...")
        order = order_mgr.open_order(dev.id, "Mantenimiento preventivo.")
        order = order_mgr.update_status(order.id, WorkOrderStatus.COMPLETED, notes="Limpieza y pasta térmica aplicada.", price=850.50)
        
        # C. Generar Factura
        print(f"C. Generando factura para la orden {order.ticket_number}...")
        invoice = billing_mgr.create_invoice_from_work_order(order.id, cust.id, order.quoted_price)
        print(f"✅ Factura creada: {invoice.invoice_number}")
        print(f"   Total a pagar: ${invoice.total}")
        
        # D. Pago Parcial
        print("D. Realizando pago parcial ($400.00 en efectivo)...")
        billing_mgr.process_payment(invoice.id, 400.00, PaymentMethod.CASH, "REC-001")
        
        details = billing_mgr.get_invoice_details(invoice.id)
        print(f"   Saldo pendiente: ${details['balance_due']}")
        print(f"   Estado factura: {details['invoice'].status}")
        
        # E. Pago Final (Tarjeta)
        total_remaining = details['balance_due']
        print(f"E. Liquidando saldo restante (${total_remaining} con tarjeta)...")
        billing_mgr.process_payment(invoice.id, total_remaining, PaymentMethod.CARD, "TRANS-MB123")
        
        details_final = billing_mgr.get_invoice_details(invoice.id)
        print(f"✅ Saldo final: ${details_final['balance_due']}")
        print(f"✅ Estado factura final: {details_final['invoice'].status}")
        
    except Exception as e:
        print(f"❌ Fallo en el flujo de facturación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from Gestion_Taller_Computo.application.use_cases.device_manager import DeviceManager
    from Gestion_Taller_Computo.domain.value_objects.work_order_status import WorkOrderStatus
    test_billing_flow()
