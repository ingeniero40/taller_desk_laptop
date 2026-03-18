import reflex as rx
from typing import List, Dict, Any, Optional
import datetime
import calendar

from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.work_order_manager import WorkOrderManager
from ...domain.value_objects.work_order_status import WorkOrderStatus
from ...domain.value_objects.order_priority import OrderPriority


class AgendaState(rx.State):
    """
    Estado del módulo de Agenda y Gestión de Tickets.
    Maneja el calendario interactivo y el ciclo de vida de los tickets de servicio.
    """

    # ── Vista de Calendario ──────────────────────────────────────────────
    view_mode: str = "week"          # "day" | "week" | "month"
    current_year: int = datetime.datetime.now().year
    current_month: int = datetime.datetime.now().month
    current_week: int = int(datetime.datetime.now().strftime("%U"))
    current_day: int = datetime.datetime.now().day

    is_loading: bool = True

    # ── Datos de Tickets ─────────────────────────────────────────────────
    tickets: List[Dict[str, Any]] = []
    technicians: List[Dict[str, str]] = []

    # ── Filtros ──────────────────────────────────────────────────────────
    filter_priority: str = "Todas"
    filter_status: str = "Todas"
    filter_technician: str = "Todos"

    # ── Modal Nuevo Ticket ────────────────────────────────────────────────
    show_ticket_modal: bool = False
    new_ticket_description: str = ""
    new_ticket_priority: str = OrderPriority.MEDIUM.value
    new_ticket_technician_id: str = ""
    new_ticket_due_date: str = ""
    new_ticket_device_label: str = ""

    # ── Modal Detalle ─────────────────────────────────────────────────────
    selected_ticket: Dict[str, Any] = {}
    show_detail_modal: bool = False

    # ── Notificaciones ────────────────────────────────────────────────────
    notifications: List[Dict[str, str]] = []

    def on_load(self):
        """Carga datos al entrar a la página de agenda."""
        self.is_loading = True
        self.fetch_tickets()
        self.fetch_technicians()
        self._generate_notifications()

    # ─── Computed Vars ────────────────────────────────────────────────────

    @rx.var
    def month_label(self) -> str:
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return f"{months[self.current_month - 1]} {self.current_year}"

    @rx.var
    def filtered_tickets(self) -> List[Dict[str, Any]]:
        result = self.tickets
        if self.filter_priority != "Todas":
            result = [t for t in result if t["priority"] == self.filter_priority]
        if self.filter_status != "Todas":
            result = [t for t in result if t["status"] == self.filter_status]
        if self.filter_technician != "Todos":
            result = [t for t in result if t.get("technician", "") == self.filter_technician]
        return result

    @rx.var
    def high_priority_count(self) -> int:
        return len([t for t in self.tickets if t.get("priority") in ["Alta", "Crítica"]])

    @rx.var
    def pending_count(self) -> int:
        pending = [WorkOrderStatus.RECEIVED.value, WorkOrderStatus.IN_DIAGNOSIS.value,
                   WorkOrderStatus.IN_REPAIR.value, WorkOrderStatus.ON_HOLD.value]
        return len([t for t in self.tickets if t.get("status") in pending])

    @rx.var
    def technician_ids(self) -> List[str]:
        return [t["full_name"] for t in self.technicians]

    # ─── Eventos de Carga ─────────────────────────────────────────────────

    @rx.event
    def fetch_tickets(self):
        """Carga todas las órdenes de trabajo y las mapea como tickets de agenda."""
        try:
            repo = Psycopg2WorkOrderRepository()
            orders = repo.findAll()

            self.tickets = []
            for o in orders:
                # Color/badge según prioridad
                priority_val = o.priority.value if hasattr(o, "priority") and o.priority else "Media"
                priority_color = {
                    "Crítica": "red", "Alta": "orange",
                    "Media": "amber", "Baja": "blue"
                }.get(priority_val, "gray")

                status_label = {
                    "RECEIVED": "Recibido",
                    "IN_DIAGNOSIS": "En Diagnóstico",
                    "IN_REPAIR": "En Reparación",
                    "ON_HOLD": "En Espera",
                    "COMPLETED": "Completado",
                    "DELIVERED": "Entregado",
                }.get(o.status.value, o.status.value)

                due = o.due_date.strftime("%d/%m/%Y %H:%M") if hasattr(o, "due_date") and o.due_date else "--"

                self.tickets.append({
                    "id": str(o.id),
                    "ticket_number": o.ticket_number,
                    "status": o.status.value,
                    "status_label": status_label,
                    "priority": priority_val,
                    "priority_color": priority_color,
                    "description": o.diagnostic_notes or "Sin descripción",
                    "due_date": due,
                    "technician": str(o.technician_id) if o.technician_id else "Sin asignar",
                    "device_id": str(o.device_id),
                })
        except Exception as e:
            print(f"AgendaState.fetch_tickets error: {e}")
        finally:
            self.is_loading = False

    @rx.event
    def fetch_technicians(self):
        """Carga la lista de técnicos disponibles para asignación."""
        try:
            from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
            from ...domain.value_objects.user_role import UserRole
            repo = Psycopg2UserRepository()
            users = repo.findAll()
            self.technicians = [
                {"id": str(u.id), "full_name": u.full_name}
                for u in users if u.role == UserRole.TECHNICIAN and u.is_active
            ]
        except Exception as e:
            print(f"AgendaState.fetch_technicians error: {e}")

    # ─── Modal Nuevo Ticket ───────────────────────────────────────────────

    @rx.event
    def open_ticket_modal(self):
        self.new_ticket_description = ""
        self.new_ticket_priority = OrderPriority.MEDIUM.value
        self.new_ticket_technician_id = ""
        self.new_ticket_due_date = ""
        self.show_ticket_modal = True

    @rx.event
    def close_ticket_modal(self):
        self.show_ticket_modal = False

    @rx.event
    def set_ticket_description(self, val: str):
        self.new_ticket_description = val

    @rx.event
    def set_ticket_priority(self, val: str):
        self.new_ticket_priority = val

    @rx.event
    def set_ticket_technician(self, val: str):
        self.new_ticket_technician_id = val

    @rx.event
    def set_ticket_due_date(self, val: str):
        self.new_ticket_due_date = val

    # ─── Modal Detalle ────────────────────────────────────────────────────

    @rx.event
    def open_ticket_detail(self, ticket_id: str):
        match = [t for t in self.tickets if t["id"] == ticket_id]
        if match:
            self.selected_ticket = match[0]
            self.show_detail_modal = True

    @rx.event
    def close_detail_modal(self):
        self.show_detail_modal = False

    # ─── Filtros ──────────────────────────────────────────────────────────

    @rx.event
    def set_filter_priority(self, val: str):
        self.filter_priority = val

    @rx.event
    def set_filter_status(self, val: str):
        self.filter_status = val

    @rx.event
    def set_filter_technician(self, val: str):
        self.filter_technician = val

    # ─── Navegación de Calendario ─────────────────────────────────────────

    @rx.event
    def set_view_mode(self, mode: str):
        self.view_mode = mode

    @rx.event
    def prev_period(self):
        if self.view_mode == "month":
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -= 1

    @rx.event
    def next_period(self):
        if self.view_mode == "month":
            if self.current_month == 12:
                self.current_month = 1
                self.current_year += 1
            else:
                self.current_month += 1

    # ─── Notificaciones ───────────────────────────────────────────────────

    def _generate_notifications(self):
        """Genera alertas de tickets críticos o próximos a vencer."""
        self.notifications = []
        high = [t for t in self.tickets if t.get("priority") in ["Crítica", "Alta"]]
        for t in high[:3]:
            self.notifications.append({
                "message": f"Ticket {t['ticket_number']} con prioridad {t['priority']}",
                "color": "red" if t["priority"] == "Crítica" else "orange",
                "icon": "alert-triangle",
            })
