import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.work_order_manager import WorkOrderManager
from ...domain.entities.work_order import WorkOrder
from ...domain.value_objects.work_order_status import WorkOrderStatus
from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.device_manager import DeviceManager
from ...application.use_cases.user_manager import UserManager

class OrderState(rx.State):
    """
    Estado de Gestión de Órdenes de Trabajo.
    Maneja el ciclo de vida de las reparaciones (recepción -> diagnóstico -> reparación -> entrega).
    """
    
    orders: List[Dict[str, Any]] = []
    
    # Búsqueda y Filtros
    search_query: str = ""
    status_filter: str = "Todas"
    
    # Modales
    show_order_modal: bool = False
    show_status_modal: bool = False
    
    # Detalle / Formulario
    selected_order: Dict[str, Any] = {}
    new_status: str = "IN_DIAGNOSIS"
    status_notes: str = ""
    new_price: float = 0.0
    
    is_loading: bool = True
    
    # Datos para nueva orden
    customers: List[Dict[str, Any]] = []
    customer_devices: List[Dict[str, Any]] = []
    technicians: List[Dict[str, Any]] = []
    
    selected_customer_id: str = ""
    selected_device_id: str = ""
    order_description: str = ""
    
    @rx.var
    def customer_ids(self) -> List[str]:
        return [c["id"] for c in self.customers]

    @rx.var
    def device_ids(self) -> List[str]:
        return [d["id"] for d in self.customer_devices]
    
    @rx.var
    def technician_ids(self) -> List[str]:
        return [t["id"] for t in self.technicians]

    def on_load(self):
        """Carga las órdenes y datos maestros al iniciar."""
        self.is_loading = True
        self.fetch_orders()
        self.fetch_master_data()

    @rx.event
    def fetch_master_data(self):
        """Carga clientes y técnicos para los selectores."""
        try:
            user_repo = Psycopg2UserRepository()
            all_users = user_repo.findAll()
            
            self.customers = [
                {"id": str(u.id), "name": u.full_name} 
                for u in all_users if u.role.value == "CUSTOMER"
            ]
            
            self.technicians = [
                {"id": str(u.id), "name": u.full_name} 
                for u in all_users if u.role.value in ["ADMIN", "TECHNICIAN"]
            ]
        except Exception as e:
            print(f"Error fetching master data: {e}")

    @rx.event
    def fetch_orders(self):
        """Obtiene todas las órdenes de trabajo."""
        try:
            repo = Psycopg2WorkOrderRepository()
            mgr = WorkOrderManager(repo)
            
            all_orders = repo.findAll() # Asumamos que findAll() implementado
            self.orders = [self._order_to_dict(o) for o in all_orders]
            
        except Exception as e:
            print(f"Error fetching orders: {e}")
        finally:
            self.is_loading = False

    def _order_to_dict(self, o: WorkOrder) -> Dict[str, Any]:
        """Formatea la entidad para el frontend."""
        return {
            "id": str(o.id),
            "ticket": o.ticket_number,
            "device_id": str(o.device_id),
            "status": o.status.value,
            "description": o.description,
            "price": float(o.quoted_price),
            "date": o.created_at.strftime("%Y-%m-%d %H:%M"),
            "status_color": self._get_status_color(o.status.value)
        }

    def _get_status_color(self, status: str) -> str:
        colors = {
            "RECEIVED": "gray",
            "IN_DIAGNOSIS": "amber",
            "IN_REPAIR": "cyan",
            "COMPLETED": "indigo",
            "DELIVERED": "green",
            "CANCELLED": "red"
        }
        return colors.get(status, "gray")

    @rx.var
    def filtered_orders(self) -> List[Dict[str, Any]]:
        orders = self.orders
        if self.search_query:
            q = self.search_query.lower()
            orders = [o for o in orders if q in o["ticket"].lower()]
        
        if self.status_filter != "Todas":
            orders = [o for o in orders if o["status"] == self.status_filter]
            
        return orders

    @rx.event
    def open_status_modal(self, order: Dict[str, Any]):
        self.selected_order = order
        self.new_status = order["status"]
        self.status_notes = ""
        self.new_price = order["price"]
        self.show_status_modal = True

    @rx.event
    def set_selected_customer(self, customer_id: str):
        self.selected_customer_id = customer_id
        self._load_customer_devices(customer_id)

    def _load_customer_devices(self, customer_id: str):
        """Carga los equipos pertenecientes a un cliente."""
        try:
            dev_repo = Psycopg2DeviceRepository()
            all_devs = dev_repo.findByCustomerId(uuid.UUID(customer_id))
            self.customer_devices = [
                {"id": str(d.id), "name": f"{d.brand} {d.model}"} 
                for d in all_devs
            ]
            if self.customer_devices:
                self.selected_device_id = self.customer_devices[0]["id"]
            else:
                self.selected_device_id = ""
        except Exception as e:
            print(f"Error loading devices: {e}")

    @rx.event
    def open_new_order_modal(self):
        self.order_description = ""
        if self.customers:
            self.selected_customer_id = self.customers[0]["id"]
            self._load_customer_devices(self.selected_customer_id)
        self.show_order_modal = True

    @rx.event
    def save_new_order(self):
        """Crea una nueva orden de trabajo."""
        if not self.selected_device_id:
            return rx.window_alert("Debe seleccionar un equipo.")
            
        try:
            repo = Psycopg2WorkOrderRepository()
            mgr = WorkOrderManager(repo)
            
            mgr.open_order(
                device_id=uuid.UUID(self.selected_device_id),
                diagnostic_notes=self.order_description
            )
            
            self.show_order_modal = False
            return self.fetch_orders()
        except Exception as e:
            return rx.window_alert(f"Error al crear orden: {str(e)}")

    @rx.event
    def set_new_price(self, value: str):
        try:
            self.new_price = float(value) if value else 0.0
        except ValueError:
            self.new_price = 0.0

    @rx.event
    def update_order_status(self):
        """Actualiza el estado de la reparación con notas y precio."""
        try:
            repo = Psycopg2WorkOrderRepository()
            mgr = WorkOrderManager(repo)
            
            # Convertir string de enum a enum real
            status_enum = WorkOrderStatus[self.new_status]
            
            mgr.update_status(
                order_id=uuid.UUID(self.selected_order["id"]),
                status=status_enum,
                notes=self.status_notes,
                price=float(self.new_price)
            )
            
            self.show_status_modal = False
            return self.fetch_orders()
        except Exception as e:
            return rx.window_alert(f"Error al actualizar orden: {str(e)}")
