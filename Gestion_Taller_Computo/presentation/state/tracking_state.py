import reflex as rx
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_work_order_comment_repository import Psycopg2WorkOrderCommentRepository
from ...infrastructure.repositories.psycopg_work_order_incident_repository import Psycopg2WorkOrderIncidentRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...domain.entities.work_order_comment import WorkOrderComment
from ...domain.entities.work_order_incident import WorkOrderIncident
from ...domain.value_objects.work_order_status import WorkOrderStatus

# ── Constantes de estado ──────────────────────────────────────────────────────
STATUS_LABELS = {
    "RECEIVED":     "Recibido",
    "IN_DIAGNOSIS": "Diagnóstico",
    "IN_REPAIR":    "En reparación",
    "ON_HOLD":      "En espera",
    "COMPLETED":    "Finalizado",
    "DELIVERED":    "Entregado",
}
STATUS_COLORS = {
    "RECEIVED":     "gray",
    "IN_DIAGNOSIS": "amber",
    "IN_REPAIR":    "cyan",
    "ON_HOLD":      "orange",
    "COMPLETED":    "indigo",
    "DELIVERED":    "green",
}
PRIORITY_COLORS = {"Baja": "blue", "Media": "amber", "Alta": "orange", "Crítica": "red"}
STATUS_ICONS = {
    "RECEIVED":     "package",
    "IN_DIAGNOSIS": "stethoscope",
    "IN_REPAIR":    "wrench",
    "ON_HOLD":      "clock",
    "COMPLETED":    "circle-check",
    "DELIVERED":    "hand-metal",
}
STATUS_PIPELINE = ["RECEIVED", "IN_DIAGNOSIS", "IN_REPAIR", "ON_HOLD", "COMPLETED", "DELIVERED"]
ACTIVE_STATUSES = {"RECEIVED", "IN_DIAGNOSIS", "IN_REPAIR", "ON_HOLD"}

HOLD_ALERT_HOURS = 48   # Tiempo en espera que dispara alerta


class TrackingState(rx.State):
    """
    Estado del módulo Seguimiento de Reparaciones.
    Gestiona el dashboard en tiempo real, comentarios e incidencias.
    """

    # ── Datos principales ─────────────────────────────────────────────────
    all_orders: List[Dict[str, Any]] = []

    # ── Alertas (calculadas en fetch, no en @rx.var) ──────────────────────
    overdue_orders:     List[Dict[str, Any]] = []   # Fecha vencida
    blocked_orders:     List[Dict[str, Any]] = []   # En espera > HOLD_ALERT_HOURS h
    unassigned_orders:  List[Dict[str, Any]] = []   # Activas sin técnico

    # ── Selección del detalle ─────────────────────────────────────────────
    selected_order: Dict[str, Any] = {}
    show_detail:    bool = False
    active_tab:     str  = "info"   # info | comments | incidents

    # ── Comentarios ───────────────────────────────────────────────────────
    comments:              List[Dict[str, Any]] = []
    new_comment_text:      str  = ""
    new_comment_internal:  bool = True

    # ── Incidencias ───────────────────────────────────────────────────────
    incidents:            List[Dict[str, Any]] = []
    show_incident_form:   bool = False
    new_problem_text:     str  = ""
    new_solution_text:    str  = ""  # para resolución inline
    resolving_incident_id: str = ""
    show_resolve_form:    bool = False

    # ── Metadata ──────────────────────────────────────────────────────────
    is_loading:   bool = False
    last_refresh: str  = ""

    # ── Filtro kanban ─────────────────────────────────────────────────────
    kanban_filter: str = ""   # Vacío = todos; o ticket/cliente search

    # ─────────────────────────────────────────────────────────────────────
    # Setters explícitos
    # ─────────────────────────────────────────────────────────────────────

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def set_new_comment_text(self, val: str):
        self.new_comment_text = val

    @rx.event
    def toggle_comment_internal(self, val: bool):
        self.new_comment_internal = val

    @rx.event
    def set_new_problem_text(self, val: str):
        self.new_problem_text = val

    @rx.event
    def set_new_solution_text(self, val: str):
        self.new_solution_text = val

    @rx.event
    def set_kanban_filter(self, val: str):
        self.kanban_filter = val

    @rx.event
    def close_detail(self):
        self.show_detail = False
        self.selected_order = {}
        self.comments = []
        self.incidents = []
        self.show_incident_form = False
        self.show_resolve_form = False
        self.active_tab = "info"

    @rx.event
    def toggle_incident_form(self):
        self.show_incident_form = not self.show_incident_form
        self.new_problem_text = ""

    @rx.event
    def start_resolving(self, incident_id: str):
        self.resolving_incident_id = incident_id
        self.new_solution_text = ""
        self.show_resolve_form = True

    @rx.event
    def cancel_resolve(self):
        self.show_resolve_form = False
        self.resolving_incident_id = ""
        self.new_solution_text = ""

    # ─────────────────────────────────────────────────────────────────────
    # Computed vars — Kanban por status
    # ─────────────────────────────────────────────────────────────────────

    def _filtered(self) -> List[Dict[str, Any]]:
        if not self.kanban_filter:
            return self.all_orders
        q = self.kanban_filter.lower()
        return [
            o for o in self.all_orders
            if q in o["ticket"].lower()
            or q in o.get("customer", "").lower()
            or q in o.get("device", "").lower()
        ]

    @rx.var
    def received(self) -> List[Dict[str, Any]]:
        return [o for o in self._filtered() if o["status"] == "RECEIVED"]

    @rx.var
    def in_diagnosis(self) -> List[Dict[str, Any]]:
        return [o for o in self._filtered() if o["status"] == "IN_DIAGNOSIS"]

    @rx.var
    def in_repair(self) -> List[Dict[str, Any]]:
        return [o for o in self._filtered() if o["status"] == "IN_REPAIR"]

    @rx.var
    def on_hold(self) -> List[Dict[str, Any]]:
        return [o for o in self._filtered() if o["status"] == "ON_HOLD"]

    @rx.var
    def completed(self) -> List[Dict[str, Any]]:
        return [o for o in self._filtered() if o["status"] == "COMPLETED"]

    @rx.var
    def delivered(self) -> List[Dict[str, Any]]:
        return [o for o in self._filtered() if o["status"] == "DELIVERED"]

    @rx.var
    def total_active(self) -> int:
        return sum(1 for o in self.all_orders if o["status"] in ACTIVE_STATUSES)

    @rx.var
    def alert_count(self) -> int:
        return (
            len(self.overdue_orders)
            + len(self.blocked_orders)
            + len(self.unassigned_orders)
        )

    # ─────────────────────────────────────────────────────────────────────
    # Carga de datos
    # ─────────────────────────────────────────────────────────────────────

    def on_load(self):
        self.fetch_all_data()

    @rx.event
    def fetch_all_data(self):
        self.is_loading = True
        try:
            order_repo = Psycopg2WorkOrderRepository()
            user_repo  = Psycopg2UserRepository()
            dev_repo   = Psycopg2DeviceRepository()

            all_users = {str(u.id): u for u in user_repo.findAll()}
            all_devs  = {str(d.id): d for d in dev_repo.findAll()}
            now       = datetime.utcnow()

            enriched       = []
            overdue        = []
            blocked        = []
            unassigned     = []

            for o in order_repo.findAll():
                status_val  = o.status.value
                device      = all_devs.get(str(o.device_id))
                tech        = all_users.get(str(o.technician_id)) if o.technician_id else None
                customer    = all_users.get(str(device.customer_id)) if device else None
                priority_v  = o.priority.value if hasattr(o.priority, "value") else str(o.priority)

                # Flags de alerta
                is_overdue   = (
                    o.due_date is not None
                    and o.due_date < now
                    and status_val in ACTIVE_STATUSES
                )
                hours_on_hold = (
                    (now - o.updated_at).total_seconds() / 3600
                    if status_val == "ON_HOLD" and o.updated_at else 0
                )
                is_blocked   = hours_on_hold > HOLD_ALERT_HOURS
                is_unassigned = (
                    o.technician_id is None
                    and status_val in {"IN_DIAGNOSIS", "IN_REPAIR"}
                )

                row = {
                    "id":             str(o.id),
                    "ticket":         o.ticket_number,
                    "status":         status_val,
                    "status_label":   STATUS_LABELS.get(status_val, status_val),
                    "status_color":   STATUS_COLORS.get(status_val, "gray"),
                    "priority":       priority_v,
                    "priority_color": PRIORITY_COLORS.get(priority_v, "gray"),
                    "device":         f"{device.brand} {device.model}" if device else "—",
                    "serial":         device.serial_number if device else "—",
                    "customer":       customer.full_name if customer else "—",
                    "technician":     tech.full_name if tech else "Sin asignar",
                    "description":    o.diagnostic_notes or "",
                    "repair_notes":   o.repair_notes or "",
                    "price":          float(o.quoted_price),
                    "estimated_hours": o.estimated_hours,
                    "actual_hours":   o.actual_hours,
                    "due_date":       o.due_date.strftime("%d/%m/%Y") if o.due_date else "—",
                    "actual_delivery": o.actual_delivery.strftime("%d/%m/%Y") if o.actual_delivery else "—",
                    "date":           o.created_at.strftime("%d/%m/%Y %H:%M"),
                    # Alert flags
                    "is_overdue":     is_overdue,
                    "is_blocked":     is_blocked,
                    "is_unassigned":  is_unassigned,
                    "hours_on_hold":  round(hours_on_hold, 1),
                }
                enriched.append(row)
                if is_overdue:   overdue.append(row)
                if is_blocked:   blocked.append(row)
                if is_unassigned: unassigned.append(row)

            self.all_orders      = enriched
            self.overdue_orders  = overdue
            self.blocked_orders  = blocked
            self.unassigned_orders = unassigned
            self.last_refresh    = datetime.now().strftime("%H:%M:%S")

        except Exception as e:
            print(f"[TrackingState] fetch_all_data error: {e}")
        finally:
            self.is_loading = False

    # ─────────────────────────────────────────────────────────────────────
    # Selección de orden — panel de detalle
    # ─────────────────────────────────────────────────────────────────────

    @rx.event
    def open_detail(self, order: Dict[str, Any]):
        self.selected_order = order
        self.show_detail    = True
        self.active_tab     = "info"
        self._load_comments(order["id"])
        self._load_incidents(order["id"])

    def _load_comments(self, order_id: str):
        try:
            repo = Psycopg2WorkOrderCommentRepository()
            self.comments = [
                {
                    "id":          str(c.id),
                    "author":      c.author_name or "Sistema",
                    "content":     c.content,
                    "is_internal": c.is_internal,
                    "date":        c.created_at.strftime("%d/%m/%Y %H:%M") if c.created_at else "",
                    "initials":    (c.author_name or "S")[0].upper(),
                    "tag_color":   "amber" if c.is_internal else "blue",
                    "tag_label":   "Interno" if c.is_internal else "Visible al cliente",
                }
                for c in repo.findByOrderId(uuid.UUID(order_id))
            ]
        except Exception as e:
            self.comments = []
            print(f"[TrackingState] load_comments error: {e}")

    def _load_incidents(self, order_id: str):
        try:
            repo = Psycopg2WorkOrderIncidentRepository()
            self.incidents = [
                {
                    "id":              str(i.id),
                    "problem":         i.problem_found,
                    "solution":        i.solution_applied or "",
                    "is_resolved":     i.is_resolved,
                    "resolved_at":     i.resolved_at.strftime("%d/%m/%Y %H:%M") if i.resolved_at else "",
                    "date":            i.created_at.strftime("%d/%m/%Y %H:%M") if i.created_at else "",
                    "status_label":    "Resuelto" if i.is_resolved else "Pendiente",
                    "status_color":    "green" if i.is_resolved else "red",
                }
                for i in repo.findByOrderId(uuid.UUID(order_id))
            ]
        except Exception as e:
            self.incidents = []
            print(f"[TrackingState] load_incidents error: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # Comentarios — CRUD
    # ─────────────────────────────────────────────────────────────────────

    @rx.event
    def add_comment(self):
        if not self.new_comment_text.strip():
            return rx.window_alert("El comentario no puede estar vacío.")
        order_id = self.selected_order.get("id", "")
        if not order_id:
            return
        try:
            repo = Psycopg2WorkOrderCommentRepository()
            comment = WorkOrderComment(
                work_order_id=uuid.UUID(order_id),
                author_name="Técnico",   # TODO: reemplazar con usuario autenticado
                content=self.new_comment_text.strip(),
                is_internal=self.new_comment_internal,
            )
            repo.create(comment)
            self.new_comment_text = ""
            self._load_comments(order_id)
        except Exception as e:
            return rx.window_alert(f"Error al añadir comentario: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # Incidencias — CRUD
    # ─────────────────────────────────────────────────────────────────────

    @rx.event
    def add_incident(self):
        if not self.new_problem_text.strip():
            return rx.window_alert("Describe el problema encontrado.")
        order_id = self.selected_order.get("id", "")
        if not order_id:
            return
        try:
            repo = Psycopg2WorkOrderIncidentRepository()
            incident = WorkOrderIncident(
                work_order_id=uuid.UUID(order_id),
                problem_found=self.new_problem_text.strip(),
            )
            repo.create(incident)
            self.new_problem_text  = ""
            self.show_incident_form = False
            self._load_incidents(order_id)
        except Exception as e:
            return rx.window_alert(f"Error al registrar incidencia: {e}")

    @rx.event
    def resolve_incident(self):
        if not self.new_solution_text.strip():
            return rx.window_alert("Describe la solución aplicada.")
        if not self.resolving_incident_id:
            return
        try:
            repo = Psycopg2WorkOrderIncidentRepository()
            repo.resolve(uuid.UUID(self.resolving_incident_id), self.new_solution_text.strip())
            self.show_resolve_form      = False
            self.resolving_incident_id  = ""
            self.new_solution_text      = ""
            self._load_incidents(self.selected_order.get("id", ""))
        except Exception as e:
            return rx.window_alert(f"Error al resolver incidencia: {e}")
