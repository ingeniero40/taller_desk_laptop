import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.work_order_manager import WorkOrderManager
from ...domain.entities.work_order import WorkOrder
from ...domain.value_objects.work_order_status import WorkOrderStatus

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

    def on_load(self):
        """Carga las órdenes al iniciar."""
        self.is_loading = True
        self.fetch_orders()

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
            "RECEIVED": "slate",
            "IN_DIAGNOSIS": "amber",
            "IN_REPAIR": "cyan",
            "COMPLETED": "indigo",
            "DELIVERED": "emerald",
            "CANCELLED": "red"
        }
        return colors.get(status, "slate")

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
    def update_order_status(self):
        """Actualiza el estado de la reparación con notas y precio."""
        try:
            repo = Psycopg2WorkOrderRepository()
            mgr = WorkOrderManager(repo)
            
            # Convertir string de enum a enum real
            status_enum = WorkOrderStatus[self.new_status]
            
            mgr.update_status(
                order_id=uuid.UUID(self.selected_order["id"]),
                new_status=status_enum,
                notes=self.status_notes,
                price=float(self.new_price)
            )
            
            self.show_status_modal = False
            return self.fetch_orders()
        except Exception as e:
            return rx.window_alert(f"Error al actualizar orden: {str(e)}")
