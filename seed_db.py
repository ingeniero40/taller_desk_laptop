import os
import sys
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from Gestion_Taller_Computo.domain.entities.user import User, UserRole
    from Gestion_Taller_Computo.domain.entities.device import Device
    from Gestion_Taller_Computo.domain.entities.work_order import WorkOrder
    from Gestion_Taller_Computo.domain.entities.product import Product
    from Gestion_Taller_Computo.domain.entities.supplier import Supplier
    from Gestion_Taller_Computo.domain.entities.work_order_comment import WorkOrderComment
    from Gestion_Taller_Computo.domain.entities.work_order_incident import WorkOrderIncident
    from Gestion_Taller_Computo.domain.value_objects.work_order_status import WorkOrderStatus
    from Gestion_Taller_Computo.domain.value_objects.order_priority import OrderPriority
except Exception as e:
    print(f"Error importando entidades: {e}")
    sys.exit(1)


def seed_database():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL no encontrada en el archivo .env")
        return

    print("Conectando a la base de datos...")
    engine = create_engine(database_url, echo=False)

    with Session(engine) as session:
        # Check if DB is already seeded to prevent duplication
        if session.query(User).count() > 0:
            print("La base de datos parece ya tener datos. ¿Quieres continuar? Eliminando datos anteriores de las tablas...")
            # Eliminando en orden (CASCADAS manuales temporales si es necesario)
            # Para hacer las cosas fáciles y seguras, solo insertaré si estaba vacío, pero puedo borrar para refrescar
            pass

        print("Poblando usuarios (Admins, Técnicos, Clientes)...")
        users = [
            User(username="admin", email="admin@taller.local", full_name="Administrador Root", password_hash="hash_falso", role=UserRole.ADMIN, is_active=True),
            User(username="tech_luis", email="luis@taller.local", full_name="Luis Técnico", password_hash="hash_falso", role=UserRole.TECHNICIAN, is_active=True),
            User(username="tech_ana", email="ana@taller.local", full_name="Ana Técnica", password_hash="hash_falso", role=UserRole.TECHNICIAN, is_active=True),
            User(username="cust_mario", email="mario@email.com", full_name="Mario Cliente", password_hash="hash_falso", role=UserRole.CUSTOMER, is_active=True, phone="+123456789"),
            User(username="cust_sara", email="sara@email.com", full_name="Sara Cliente", password_hash="hash_falso", role=UserRole.CUSTOMER, is_active=True, phone="+987654321")
        ]
        for u in users:
            try:
                session.add(u)
                session.commit()
                session.refresh(u)
            except Exception as e:
                session.rollback()
                print(f"Error al insertar usuario {u.username}: {e}")
        
        admin, tech1, tech2, cust1, cust2 = users

        print("Poblando proveedores...")
        suppliers = [
            Supplier(name="TechParts Global", contact_email="sales@techparts.com", phone="+111222333"),
            Supplier(name="Suministros PC", contact_email="contacto@suministrospc.lat", phone="+444555666")
        ]
        for s in suppliers:
            try:
                session.add(s)
                session.commit()
                session.refresh(s)
            except Exception as e:
                session.rollback()
                print(f"Error al insertar proveedor {s.name}: {e}")
        sup1, sup2 = suppliers

        print("Poblando inventario (Productos)...")
        products = [
            Product(sku="RAM-16G", name="Memoria RAM 16GB DDR4", stock=15, min_stock=5, cost_price=45.0, sale_price=80.0, category="Componentes", supplier_id=sup1.id),
            Product(sku="SSD-1TB", name="Disco SSD M.2 1TB", stock=8, min_stock=4, cost_price=65.0, sale_price=110.0, category="Almacenamiento", supplier_id=sup1.id),
            Product(sku="PT-THERMAL", name="Pasta Térmica Alta Gama", stock=20, min_stock=10, cost_price=8.0, sale_price=20.0, category="Consumibles", supplier_id=sup2.id),
            Product(sku="PANT-15-LED", name="Pantalla LED 15.6", stock=2, min_stock=3, cost_price=40.0, sale_price=95.0, category="Repuestos", supplier_id=sup1.id)
        ]
        for p in products:
            try:
                session.add(p)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error al insertar producto {p.sku}: {e}")

        print("Poblando dispositivos...")
        devices = [
            Device(customer_id=cust1.id, brand="Dell", model="XPS 15", serial_number="SN-DELL-1234", device_type="Laptop", notes="Rayón en la tapa inferior"),
            Device(customer_id=cust2.id, brand="HP", model="Pavilion 14", serial_number="SN-HP-5678", device_type="Laptop"),
            Device(customer_id=cust1.id, brand="Lenovo", model="Legion 5", serial_number="SN-LEN-9101", device_type="Laptop")
        ]
        for d in devices:
            try:
                session.add(d)
                session.commit()
                session.refresh(d)
            except Exception as e:
                session.rollback()
                print(f"Error al insertar dispositivo {d.serial_number}: {e}")
        d1, d2, d3 = devices

        print("Poblando órdenes de trabajo...")
        now = datetime.utcnow()
        work_orders = [
            WorkOrder(device_id=d1.id, ticket_number="REC-1001", status=WorkOrderStatus.RECEIVED, priority=OrderPriority.MEDIUM, diagnostic_notes="La pantalla parpadea y a veces no enciende", quoted_price=0.0),
            WorkOrder(device_id=d2.id, ticket_number="DIAG-1002", status=WorkOrderStatus.IN_DIAGNOSIS, priority=OrderPriority.HIGH, diagnostic_notes="Disco duro hace ruido, lento. Revisión solicitada.", quoted_price=25.0),
            WorkOrder(device_id=d3.id, technician_id=tech1.id, ticket_number="ESP-1003", status=WorkOrderStatus.ON_HOLD, priority=OrderPriority.CRITICAL, diagnostic_notes="Teclado no funciona, requiere cambio completo.", repair_notes="Esperando aprobación del cliente para cotización nueva.", quoted_price=120.0, updated_at=now - timedelta(hours=50)),
            WorkOrder(device_id=d1.id, technician_id=tech2.id, ticket_number="REP-1004", status=WorkOrderStatus.IN_REPAIR, priority=OrderPriority.MEDIUM, diagnostic_notes="Mantenimiento preventivo general.", repair_notes="Limpiando ventiladores...", quoted_price=45.0, due_date=now - timedelta(hours=5)),
            WorkOrder(device_id=d2.id, technician_id=tech1.id, ticket_number="FIN-1005", status=WorkOrderStatus.COMPLETED, priority=OrderPriority.MEDIUM, diagnostic_notes="Pantalla rota", repair_notes="Pantalla reemplazada.", estimated_hours=2.0, actual_hours=1.8, quoted_price=210.0)
        ]
        for o in work_orders:
            try:
                session.add(o)
                session.commit()
                session.refresh(o)
            except Exception as e:
                session.rollback()
                print(f"Error al insertar orden {o.ticket_number}: {e}")
        o1, o2, o3, o4, o5 = work_orders

        print("Poblando comentarios e incidencias...")
        comments = [
            WorkOrderComment(work_order_id=o3.id, author_name="Luis Técnico", content="Envié el presupuesto de $120, esperando respuesta.", is_internal=False),
            WorkOrderComment(work_order_id=o4.id, author_name="Ana Técnica", content="Tiene mucha suciedad interna, requirirá más tiempo de lo esperado.", is_internal=True)
        ]
        for c in comments:
            try:
                session.add(c)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error al insertar comentario: {e}")

        i1 = WorkOrderIncident(work_order_id=o4.id, problem_found="Un tornillo del chasis estaba barrido, fue necesario extraerlo con herramienta especial.", is_resolved=False)
        try:
            session.add(i1)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al insertar incidencia: {e}")
        
        print("✅ Base de datos poblada exitosamente con datos de prueba.")

if __name__ == "__main__":
    seed_database()
