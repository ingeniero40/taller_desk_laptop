import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_work_order_history_repository import Psycopg2WorkOrderHistoryRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...application.use_cases.work_order_manager import WorkOrderManager
from ...application.use_cases.user_manager import UserManager
from ...domain.value_objects.work_order_status import WorkOrderStatus

# Mapa estado → etiqueta en español
STATUS_LABELS: Dict[str, str] = {
    "RECEIVED":     "Recibido",
    "IN_DIAGNOSIS": "Diagnóstico",
    "IN_REPAIR":    "En reparación",
    "ON_HOLD":      "En espera",
    "COMPLETED":    "Finalizado",
    "DELIVERED":    "Entregado",
}

STATUS_COLORS: Dict[str, str] = {
    "RECEIVED":     "gray",
    "IN_DIAGNOSIS": "amber",
    "IN_REPAIR":    "cyan",
    "ON_HOLD":      "orange",
    "COMPLETED":    "indigo",
    "DELIVERED":    "green",
}

PRIORITY_COLORS: Dict[str, str] = {
    "Baja":    "blue",
    "Media":   "amber",
    "Alta":    "orange",
    "Crítica": "red",
}

# Pipeline de estados ordenado
STATUS_PIPELINE = [
    "RECEIVED", "IN_DIAGNOSIS", "IN_REPAIR",
    "ON_HOLD", "COMPLETED", "DELIVERED",
]


class OrderState(rx.State):
    """
    Estado de Gestión de Órdenes de Trabajo.
    Ciclo de vida completo: recepción → diagnóstico → reparación → espera → finalizado → entregado.
    """

    # ── Datos ─────────────────────────────────────────────────────────────
    orders: List[Dict[str, Any]] = []
    order_history: List[Dict[str, Any]] = []

    # ── Filtros ───────────────────────────────────────────────────────────
    search_query: str = ""
    status_filter: str = "Todas"

    # ── UI Modales y Panel ────────────────────────────────────────────────
    show_order_modal: bool = False
    show_status_modal: bool = False
    show_detail_panel: bool = False

    # ── Selección y Detalle ───────────────────────────────────────────────
    selected_order: Dict[str, Any] = {}
    new_status: str = "IN_DIAGNOSIS"
    status_notes: str = ""
    new_price: float = 0.0
    new_estimated_hours: float = 0.0
    new_actual_hours: float = 0.0

    # ── Loading ───────────────────────────────────────────────────────────
    is_loading: bool = True

    # ── Datos Maestros ────────────────────────────────────────────────────
    customers: List[Dict[str, Any]] = []
    customer_devices: List[Dict[str, Any]] = []
    technicians: List[Dict[str, Any]] = []

    # ── Nueva Orden ───────────────────────────────────────────────────────
    selected_customer_id: str = ""
    selected_device_id: str = ""
    order_description: str = ""
    new_order_priority: str = "Media"
    selected_technician_id: str = ""

    # ── Setters explícitos (Reflex 0.8.9+ deprecation fix) ────────────────

    @rx.event
    def set_search_query(self, val: str):
        self.search_query = val

    @rx.event
    def set_status_filter(self, val: str):
        self.status_filter = val

    @rx.event
    def set_show_order_modal(self, val: bool):
        self.show_order_modal = val

    @rx.event
    def set_show_status_modal(self, val: bool):
        self.show_status_modal = val

    @rx.event
    def set_new_status(self, val: str):
        self.new_status = val

    @rx.event
    def set_status_notes(self, val: str):
        self.status_notes = val

    @rx.event
    def set_new_price(self, val: str):
        try:
            self.new_price = float(val) if val else 0.0
        except ValueError:
            self.new_price = 0.0

    @rx.event
    def set_new_estimated_hours(self, val: str):
        try:
            self.new_estimated_hours = float(val) if val else 0.0
        except ValueError:
            self.new_estimated_hours = 0.0

    @rx.event
    def set_new_actual_hours(self, val: str):
        try:
            self.new_actual_hours = float(val) if val else 0.0
        except ValueError:
            self.new_actual_hours = 0.0

    @rx.event
    def set_selected_technician(self, val: str):
        self.selected_technician_id = val

    @rx.event
    def set_order_description(self, val: str):
        self.order_description = val

    @rx.event
    def set_new_order_priority(self, val: str):
        self.new_order_priority = val

    # ── Computed Vars ─────────────────────────────────────────────────────

    @rx.var
    def customer_names(self) -> List[str]:
        return [c["name"] for c in self.customers]

    @rx.var
    def device_labels(self) -> List[str]:
        return [d["label"] for d in self.customer_devices]

    @rx.var
    def technician_names(self) -> List[str]:
        return [t["name"] for t in self.technicians]

    @rx.var
    def filtered_orders(self) -> List[Dict[str, Any]]:
        result = self.orders
        if self.search_query:
            q = self.search_query.lower()
            result = [
                o for o in result
                if q in o["ticket"].lower()
                or q in o.get("customer", "").lower()
                or q in o.get("device", "").lower()
            ]
        if self.status_filter != "Todas":
            result = [o for o in result if o["status"] == self.status_filter]
        return result

    @rx.var
    def status_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {s: 0 for s in STATUS_PIPELINE}
        for o in self.orders:
            s = o.get("status", "RECEIVED")
            if s in counts:
                counts[s] += 1
        return counts

    @rx.var
    def selected_status_index(self) -> int:
        status = self.selected_order.get("status", "RECEIVED")
        try:
            return STATUS_PIPELINE.index(status)
        except ValueError:
            return 0

    # ── Carga Inicial ─────────────────────────────────────────────────────

    def on_load(self):
        self.is_loading = True
        self.fetch_orders()
        self.fetch_master_data()

    @rx.event
    def fetch_master_data(self):
        try:
            user_repo = Psycopg2UserRepository()
            all_users = user_repo.findAll()

            # Build customer → device lookup
            dev_repo = Psycopg2DeviceRepository()

            self.customers = [
                {"id": str(u.id), "name": u.full_name, "email": u.email}
                for u in all_users if u.role.value == "CUSTOMER"
            ]
            self.technicians = [
                {"id": str(u.id), "name": u.full_name}
                for u in all_users if u.role.value in ["ADMIN", "TECHNICIAN"]
            ]
        except Exception as e:
            print(f"[OrderState] fetch_master_data error: {e}")

    @rx.event
    def fetch_orders(self):
        try:
            repo = Psycopg2WorkOrderRepository()
            user_repo = Psycopg2UserRepository()
            dev_repo = Psycopg2DeviceRepository()

            all_users = {str(u.id): u for u in user_repo.findAll()}
            all_devs = {str(d.id): d for d in dev_repo.findAll()}

            self.orders = [
                self._order_to_dict(o, all_users, all_devs)
                for o in repo.findAll()
            ]
        except Exception as e:
            print(f"[OrderState] fetch_orders error: {e}")
        finally:
            self.is_loading = False

    # ── Detalle de Orden ──────────────────────────────────────────────────

    @rx.event
    def open_order_detail(self, order: Dict[str, Any]):
        self.selected_order = order
        self.new_status = order["status"]
        self.new_price = order["price"]
        self.new_estimated_hours = order.get("estimated_hours") or 0.0
        self.new_actual_hours = order.get("actual_hours") or 0.0
        self.status_notes = ""
        self.show_detail_panel = True
        self._fetch_history(order["id"])

    @rx.event
    def close_detail_panel(self):
        self.show_detail_panel = False
        self.selected_order = {}
        self.order_history = []

    def _fetch_history(self, order_id: str):
        try:
            repo = Psycopg2WorkOrderHistoryRepository()
            entries = repo.findByOrderId(uuid.UUID(order_id))
            self.order_history = [
                {
                    "from": STATUS_LABELS.get(e.from_status, e.from_status or "Inicio"),
                    "to": STATUS_LABELS.get(e.to_status, e.to_status),
                    "to_raw": e.to_status,
                    "notes": e.notes or "",
                    "date": e.changed_at.strftime("%d/%m/%Y %H:%M") if e.changed_at else "",
                    "color": STATUS_COLORS.get(e.to_status, "gray"),
                }
                for e in entries
            ]
        except Exception as e:
            self.order_history = []
            print(f"[OrderState] fetch_history error: {e}")

    # ── Modal Nueva Orden ─────────────────────────────────────────────────

    @rx.event
    def open_new_order_modal(self):
        self.order_description = ""
        self.new_order_priority = "Media"
        self.selected_technician_id = ""
        if self.customers:
            self.selected_customer_id = self.customers[0]["id"]
            self._load_customer_devices(self.selected_customer_id)
        self.show_order_modal = True

    @rx.event
    def set_selected_customer(self, name: str):
        match = next((c for c in self.customers if c["name"] == name), None)
        if match:
            self.selected_customer_id = match["id"]
            self._load_customer_devices(match["id"])

    def _load_customer_devices(self, customer_id: str):
        try:
            repo = Psycopg2DeviceRepository()
            devs = repo.findByCustomerId(uuid.UUID(customer_id))
            self.customer_devices = [
                {"id": str(d.id), "label": f"{d.brand} {d.model} — {d.serial_number}"}
                for d in devs
            ]
            self.selected_device_id = self.customer_devices[0]["id"] if self.customer_devices else ""
        except Exception as e:
            self.customer_devices = []
            self.selected_device_id = ""

    @rx.event
    def set_selected_device_label(self, label: str):
        match = next((d for d in self.customer_devices if d["label"] == label), None)
        if match:
            self.selected_device_id = match["id"]

    @rx.event
    def save_new_order(self):
        if not self.selected_device_id:
            return rx.window_alert("Debe seleccionar un equipo.")
        try:
            order_repo = Psycopg2WorkOrderRepository()
            history_repo = Psycopg2WorkOrderHistoryRepository()
            mgr = WorkOrderManager(order_repo, history_repo)

            tech_id = uuid.UUID(self.selected_technician_id) if self.selected_technician_id else None

            mgr.open_order(
                device_id=uuid.UUID(self.selected_device_id),
                diagnostic_notes=self.order_description,
                priority=self.new_order_priority,
                technician_id=tech_id,
            )
            self.show_order_modal = False
            return self.fetch_orders()
        except Exception as e:
            return rx.window_alert(f"Error al crear orden: {str(e)}")

    # ── Modal Actualización de Estado ─────────────────────────────────────

    @rx.event
    def open_status_modal(self, order: Dict[str, Any]):
        self.selected_order = order
        self.new_status = order["status"]
        self.status_notes = order.get("repair_notes", "")
        self.new_price = order["price"]
        self.new_estimated_hours = order.get("estimated_hours") or 0.0
        self.new_actual_hours = order.get("actual_hours") or 0.0
        self.show_status_modal = True

    @rx.event
    def update_order_status(self):
        try:
            order_repo = Psycopg2WorkOrderRepository()
            history_repo = Psycopg2WorkOrderHistoryRepository()
            mgr = WorkOrderManager(order_repo, history_repo)

            status_enum = WorkOrderStatus[self.new_status]

            mgr.update_status(
                order_id=uuid.UUID(self.selected_order["id"]),
                status=status_enum,
                notes=self.status_notes,
                price=float(self.new_price),
                actual_hours=float(self.new_actual_hours) if self.new_actual_hours else None,
            )
            self.show_status_modal = False

            # Actualizar el panel de detalle si está abierto
            if self.show_detail_panel:
                self._fetch_history(self.selected_order["id"])

            return self.fetch_orders()
        except Exception as e:
            return rx.window_alert(f"Error al actualizar: {str(e)}")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _order_to_dict(self, o, all_users: dict, all_devs: dict) -> Dict[str, Any]:
        device = all_devs.get(str(o.device_id))
        tech = all_users.get(str(o.technician_id)) if o.technician_id else None
        # Buscar cliente del dispositivo
        customer = all_users.get(str(device.customer_id)) if device else None

        priority_val = o.priority.value if hasattr(o.priority, "value") else str(o.priority)
        status_val = o.status.value if hasattr(o.status, "value") else str(o.status)

        return {
            "id":              str(o.id),
            "ticket":          o.ticket_number,
            "status":          status_val,
            "status_label":    STATUS_LABELS.get(status_val, status_val),
            "status_color":    STATUS_COLORS.get(status_val, "gray"),
            "priority":        priority_val,
            "priority_color":  PRIORITY_COLORS.get(priority_val, "gray"),
            "device":          f"{device.brand} {device.model}" if device else "—",
            "serial":          device.serial_number if device else "—",
            "customer":        customer.full_name if customer else "—",
            "technician":      tech.full_name if tech else "Sin asignar",
            "description":     o.diagnostic_notes or "",
            "repair_notes":    o.repair_notes or "",
            "price":           float(o.quoted_price),
            "estimated_hours": o.estimated_hours,
            "actual_hours":    o.actual_hours,
            "due_date":        o.due_date.strftime("%d/%m/%Y") if o.due_date else "—",
            "actual_delivery": o.actual_delivery.strftime("%d/%m/%Y") if o.actual_delivery else "—",
            "date":            o.created_at.strftime("%d/%m/%Y %H:%M"),
        }
