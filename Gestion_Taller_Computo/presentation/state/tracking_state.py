import reflex as rx
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

from ...domain.entities.audit_log import AuditLog
from ...infrastructure.repositories.psycopg_audit_log_repository import Psycopg2AuditLogRepository
from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_work_order_comment_repository import Psycopg2WorkOrderCommentRepository
from ...infrastructure.repositories.psycopg_work_order_incident_repository import Psycopg2WorkOrderIncidentRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...infrastructure.services.notification_service import NotificationService
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

    @rx.var
    def first_entry_image(self) -> str:
        """Extrae la primera foto de entrada a nivel de servidor."""
        imgs = self.selected_order.get("entry_images", "")
        if not imgs: return ""
        return imgs.split(";")[0]

    @rx.var
    def first_exit_image(self) -> str:
        """Extrae la primera foto de salida a nivel de servidor."""
        imgs = self.selected_order.get("exit_images", "")
        if not imgs: return ""
        return imgs.split(";")[0]

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
    
    # ── Entrega (Check-out) (Contexto 9) ──────────────────────────────────
    show_checkout_modal: bool = False
    exit_images_urls:    List[str] = []
    checkout_signature:  str = ""  # Base64 representativo
    delivery_notes:      str = ""

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

    @rx.event
    def open_checkout(self):
        """Prepara el modal de entrega."""
        self.show_checkout_modal = True
        self.exit_images_urls = []
        self.checkout_signature = ""
        self.delivery_notes = ""

    @rx.event
    def set_checkout_signature(self, signature_data: str):
        """Recibe la firma digital en base64."""
        self.checkout_signature = signature_data

    @rx.event
    def set_delivery_notes(self, val: str):
        self.delivery_notes = val

    @rx.event
    async def handle_exit_image_upload(self, files: List[rx.UploadFile]):
        """Sube y registra imágenes del equipo al entregarse."""
        import os
        upload_dir = os.path.join("assets", "uploads", "check_out")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for file in files:
            upload_data = await file.read()
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            outfile = os.path.join(upload_dir, filename)
            with open(outfile, "wb") as f:
                f.write(upload_data)
            self.exit_images_urls.append(f"/uploads/check_out/{filename}")

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
    def order_qr_url(self) -> str:
        """URL del código QR para el portal del cliente."""
        ticket = self.selected_order.get("ticket")
        if not ticket:
            return ""
        # Link real al portal local (en producción sería la URL pública)
        portal_url = f"http://localhost:3000/portal?ticket={ticket}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={portal_url}"

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
                    "customer_id":    str(customer.id) if customer else "",
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
        self.quote_amount   = order.get("price", 0.0)
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

    # ─────────────────────────────────────────────────────────────────────
    # Consumo de Repuestos (Inventario)
    # ─────────────────────────────────────────────────────────────────────
    available_products: List[Dict[str, Any]] = []
    show_consume_form: bool = False
    consume_product_id: str = ""
    consume_quantity: int = 1

    @rx.event
    def toggle_consume_form(self):
        self.show_consume_form = not self.show_consume_form
        self.consume_quantity = 1
        if self.show_consume_form and not self.available_products:
            self._load_products()

    product_labels: List[str] = []
    selected_product_label: str = ""

    @rx.event
    def set_selected_product_label(self, val: str):
        self.selected_product_label = val
        for p in self.available_products:
            if p["label"] == val:
                self.consume_product_id = p["id"]
                break

    @rx.event
    def set_consume_quantity(self, val: str):
        try:
            self.consume_quantity = int(val) if val else 1
        except ValueError:
            self.consume_quantity = 1

    def _load_products(self):
        try:
            from ...infrastructure.repositories.psycopg_product_repository import Psycopg2ProductRepository
            repo = Psycopg2ProductRepository()
            self.available_products = []
            self.product_labels = []
            for p in repo.findAll():
                if p.stock > 0:
                    label = f"{p.sku} | {p.name} (Stock: {p.stock})"
                    self.available_products.append({
                        "id": str(p.id),
                        "name": p.name,
                        "stock": p.stock,
                        "label": label
                    })
                    self.product_labels.append(label)
                    
            if self.available_products:
                self.consume_product_id = self.available_products[0]["id"]
                self.selected_product_label = self.available_products[0]["label"]
        except Exception as e:
            print(f"[TrackingState] load_products error: {e}")

    @rx.event
    def consume_part(self):
        if not self.consume_product_id:
            return rx.window_alert("Selecciona un repuesto.")
        if self.consume_quantity <= 0:
            return rx.window_alert("La cantidad debe ser mayor a 0.")
        
        order_id = self.selected_order.get("id", "")
        if not order_id:
            return

        try:
            from ...infrastructure.repositories.psycopg_product_repository import Psycopg2ProductRepository
            from ...infrastructure.repositories.psycopg_supplier_repository import Psycopg2SupplierRepository
            from ...infrastructure.repositories.psycopg_inventory_movement_repository import Psycopg2InventoryMovementRepository
            from ...application.use_cases.inventory_manager import InventoryManager
            
            prod_repo = Psycopg2ProductRepository()
            supp_repo = Psycopg2SupplierRepository()
            mov_repo = Psycopg2InventoryMovementRepository()
            mgr = InventoryManager(prod_repo, supp_repo, mov_repo)
            
            # Executing consumption
            mgr.consume_part_for_order(
                product_id=uuid.UUID(self.consume_product_id),
                quantity=self.consume_quantity,
                order_id=uuid.UUID(order_id),
                user_id=None # Optionally pass technician ID
            )
            
            # Find product name to log in a comment
            prod_name = next((p["name"] for p in self.available_products if p["id"] == self.consume_product_id), "Repuesto")
            
            # Auto-comment about consumed part
            comment_repo = Psycopg2WorkOrderCommentRepository()
            comment = WorkOrderComment(
                work_order_id=uuid.UUID(order_id),
                author_name="Sistema (Inventario)",
                content=f"Se consumieron {self.consume_quantity} unid. de {prod_name}. Stock deducido automáticamente.",
                is_internal=True,
            )
            comment_repo.create(comment)
            
            # Reset UI and refresh
            self.show_consume_form = False
            self.consume_quantity = 1
            self._load_products() # refresh stock logic 
            self._load_comments(order_id)
            return rx.window_alert("Repuesto consumido y descontado del inventario exitosamente.")
            
        except Exception as e:
            return rx.window_alert(f"Error al consumir repuesto: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # Presupuestos y Facturación
    # ─────────────────────────────────────────────────────────────────────
    quote_amount: float = 0.0

    @rx.event
    def set_quote_amount(self, val: str):
        try:
            self.quote_amount = float(val) if val else 0.0
        except ValueError:
            self.quote_amount = 0.0

    @rx.event
    def update_quote(self):
        order_id = self.selected_order.get("id")
        if not order_id: return
        try:
            from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
            repo = Psycopg2WorkOrderRepository()
            order = repo.findById(uuid.UUID(order_id))
            if order:
                order.quoted_price = self.quote_amount
                repo.update(order)
                
                # Auto-comentario
                comment_repo = Psycopg2WorkOrderCommentRepository()
                c = WorkOrderComment(
                    work_order_id=uuid.UUID(order_id),
                    author_name="Sistema (Finanzas)",
                    content=f"La cotización fue actualizada a ${self.quote_amount:.2f}. Pendiente de aprobación del cliente.",
                    is_internal=True
                )
                comment_repo.create(c)
                
                self.fetch_all_data()
                # Actualizar el precio de la selección_actual
                self.selected_order["price"] = self.quote_amount
                self._load_comments(order_id)
                return rx.window_alert(f"Cotización actualizada a ${self.quote_amount:.2f}")
        except Exception as e:
            return rx.window_alert(f"Error al actualizar cotización: {e}")

    # ── Extras Context: IA y Sugerencias ───────────────────────────────────────
    ai_suggestion: str = ""
    is_analyzing: bool = False
    recurrence_prediction: str = ""

    @rx.event
    def get_suggested_diagnostic(self):
        """Pide a la IA una sugerencia basada en el problema reportado."""
        problem = self.selected_order.get("problem_found")
        if not problem:
            self.ai_suggestion = "No hay descripción del problema para analizar."
            return
            
        self.is_analyzing = True
        yield
        
        try:
            from ...infrastructure.repositories.psycopg_analytics_repository import Psycopg2AnalyticsRepository
            analytics_repo = Psycopg2AnalyticsRepository()
            freq = analytics_repo.get_frequent_problems()
            matches = [f for f in freq if problem.lower() in f["problem"].lower()]
            if matches:
                self.recurrence_prediction = f"⚠ Este problema ha ocurrido {matches[0]['frequency']} veces antes en el taller."
            else:
                self.recurrence_prediction = "✓ Problema poco común registrado."
                
            # Simulación de IA (En un entorno real llamaríamos a Gemini/OpenAI)
            self.ai_suggestion = f"Basado en '{problem}', se recomienda: 1. Revisar voltajes de entrada. 2. Realizar limpieza de contactos. 3. Verificar última actualización de BIOS."
            
        except Exception as e:
            self.ai_suggestion = f"Error al analizar: {e}"
        finally:
            self.is_analyzing = False

    @rx.event
    def generate_invoice(self):
        order_id = self.selected_order.get("id")
        customer_id = self.selected_order.get("customer_id")
        amount = self.selected_order.get("price", 0.0)

        if not order_id or not customer_id:
            return rx.window_alert("Faltan datos de la orden o del cliente.")

        try:
            from ...infrastructure.repositories.psycopg_invoice_repository import Psycopg2InvoiceRepository
            from ...infrastructure.repositories.psycopg_payment_repository import Psycopg2PaymentRepository
            from ...application.use_cases.billing_manager import BillingManager

            mgr = BillingManager(Psycopg2InvoiceRepository(), Psycopg2PaymentRepository())
            invoice = mgr.create_invoice_from_work_order(
                work_order_id=uuid.UUID(order_id),
                customer_id=uuid.UUID(customer_id),
                amount=float(amount)
            )
            
            # Auto-comentario
            c = WorkOrderComment(
                work_order_id=uuid.UUID(order_id),
                author_name="Sistema (Finanzas)",
                content=f"Se generó la factura {invoice.invoice_number} por el importe de ${amount:.2f}.",
                is_internal=False
            )
            Psycopg2WorkOrderCommentRepository().create(c)
            self._load_comments(order_id)

            return rx.window_alert(f"¡Factura {invoice.invoice_number} generada con éxito!")
        except Exception as e:
            return rx.window_alert(f"Error al generar factura: {e}")

    @rx.event
    def confirm_delivery(self):
        """Finaliza el proceso de entrega: actualiza estado y registra firma/fotos."""
        order_id = self.selected_order.get("id")
        if not order_id:
            return

        # Validación mínima: firma es requerida para entrega formal en POS
        if not self.checkout_signature:
            return rx.window_alert("Se requiere la firma del cliente para proceder con la entrega.")

        try:
            repo = Psycopg2WorkOrderRepository()
            order = repo.findById(uuid.UUID(order_id))
            if order:
                order.status = WorkOrderStatus.DELIVERED
                order.actual_delivery = datetime.utcnow()
                order.is_delivered = True
                
                # Guardar evidencia Contexto 9
                if self.exit_images_urls:
                    order.exit_images = ";".join(self.exit_images_urls)
                
                order.client_signature = self.checkout_signature
                
                if self.delivery_notes:
                    if order.repair_notes:
                        order.repair_notes += f"\nNotas de entrega: {self.delivery_notes}"
                    else:
                        order.repair_notes = f"Notas de entrega: {self.delivery_notes}"

                repo.update(order)
                
                # Contexto 12: Auditoría
                audit_repo = Psycopg2AuditLogRepository()
                audit_repo.create(AuditLog(
                    action="WORK_ORDER_DELIVERED",
                    module="TRACKING",
                    entity_id=order_id,
                    entity_type="WorkOrder",
                    user_name="Administrador", # Debería venir del AuthState en producción 
                    details=f"Entrega confirmada. Firma registrada: {bool(self.checkout_signature)}"
                ))

                # Contexto 12: Notificación
                notif = NotificationService()
                customer_name = self.selected_order.get("customer_name", "Cliente")
                ticket = self.selected_order.get("ticket_number", "---")
                notif.notify_order_status_change(
                    customer_name=customer_name,
                    phone="5551234567", # placeholder
                    ticket=ticket,
                    new_status="ENTREGADO"
                )

                # Auto-comentario de cierre
                comment_repo = Psycopg2WorkOrderCommentRepository()
                c = WorkOrderComment(
                    work_order_id=uuid.UUID(order_id),
                    author_name="Sistema",
                    content=f"Equipo entregado al cliente satisfactoriamente. Evidencia fotográfica y firma registradas.",
                    is_internal=False
                )
                comment_repo.create(c)
                
                self.show_checkout_modal = False
                self.close_detail()
                self.fetch_all_data()
                return rx.window_alert(f"¡Equipo {ticket} entregado con éxito! Notificación enviada.")
        except Exception as e:
            return rx.window_alert(f"Error en la entrega: {e}")
