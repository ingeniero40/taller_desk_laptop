import reflex as rx
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...infrastructure.repositories.psycopg_work_order_comment_repository import Psycopg2WorkOrderCommentRepository
from ...infrastructure.repositories.psycopg_audit_log_repository import Psycopg2AuditLogRepository
from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...domain.entities.audit_log import AuditLog
from ...domain.entities.work_order_comment import WorkOrderComment


class PortalState(rx.State):
    """
    Estado del Portal de Cliente (Público/Búsqueda de Ticket).
    Permite consulta, aprobación y visualización del historial.
    """
    
    # Búsqueda
    search_ticket: str = ""
    is_searching: bool = False
    has_searched: bool = False
    order_found: bool = False
    
    # Detalles
    order_details: Dict[str, Any] = {}
    order_comments: List[Dict[str, Any]] = []
    
    @rx.var
    def has_quote(self) -> bool:
        """Verifica si hay un monto presupuestado mayor a cero."""
        return float(self.order_details.get("quoted_price", 0)) > 0

    @rx.var
    def is_approved(self) -> bool:
        """Verifica si el presupuesto ya fue marcado como aprobado."""
        return self.order_details.get("quote_approved", False)

    @rx.event
    def set_search_ticket(self, val: str):
        self.search_ticket = val

    @rx.event
    def search_order(self):
        """Busca la orden en la base de datos por número de ticket."""
        if not self.search_ticket:
            return
            
        self.is_searching = True
        self.has_searched = True
        self.order_found = False
        
        try:
            repo = Psycopg2WorkOrderRepository()
            device_repo = Psycopg2DeviceRepository()
            user_repo = Psycopg2UserRepository()
            
            # Buscaremos todas y compararemos por ticket_number
            all_orders = repo.findAll()
            target = next((o for o in all_orders if o.ticket_number == self.search_ticket), None)
            
            if target:
                # Obtener detalles del equipo y cliente
                device = device_repo.findById(target.device_id)
                customer_name = "Cliente General"
                equipment_info = "Equipo Desconocido"
                
                if device:
                    equipment_info = f"{device.brand} {device.model}"
                    customer = user_repo.findById(device.customer_id)
                    if customer:
                        customer_name = customer.full_name
                
                self.order_details = self._order_to_dict(target, customer_name, equipment_info)
                # Cargar historial público
                self._load_public_comments(str(target.id))
                self.order_found = True
            else:
                self.order_details = {}
                self.order_comments = []
                
        except Exception as e:
            print(f"Error searching portal: {e}")
        finally:
            self.is_searching = False

    def _order_to_dict(self, o: Any, customer_name: str, equipment: str) -> Dict[str, Any]:
        return {
            "id": str(o.id),
            "ticket_number": o.ticket_number,
            "customer_name": customer_name,
            "equipment": equipment,
            "status": o.status.name if hasattr(o.status, 'name') else str(o.status),
            "created_at": o.created_at.strftime("%d/%m/%Y"),
            "quoted_price": float(o.quoted_price or 0),
            "quote_approved": getattr(o, "quote_approved", False)  # Opcional si se extiende en BD
        }

    def _load_public_comments(self, order_id: str):
        """Carga solo los comentarios no privados (públicos) para el cliente."""
        comment_repo = Psycopg2WorkOrderCommentRepository()
        all_comments = comment_repo.findByOrderId(uuid.UUID(order_id), include_internal=False)
        
        self.order_comments = [
            {
                "date": c.created_at.strftime("%d/%m %H:%M"),
                "author": c.author_name,
                "content": c.content
            } for c in all_comments
        ]

    @rx.event
    def approve_quote(self):
        """Aprueba formalmente el presupuesto desde el portal del cliente."""
        order_id = self.order_details.get("id")
        if not order_id: return
        
        try:
            repo = Psycopg2WorkOrderRepository()
            order = repo.findById(uuid.UUID(order_id))
            if order:
                # Actualizar el presupuesto - Supongamos que agregamos un booleano quote_approved
                # Si no existe en BD, lo guardamos vía comentario o nota de auditoría.
                # Por ahora, guardamos un comentario y log de auditoría.
                
                comment_repo = Psycopg2WorkOrderCommentRepository()
                c = WorkOrderComment(
                    work_order_id=uuid.UUID(order_id),
                    author_name="CLIENTE (Portal)",
                    content=f"EL CLIENTE HA APROBADO EL PRESUPUESTO DE ${self.order_details['quoted_price']:.2f}.",
                    is_internal=False
                )
                comment_repo.create(c)
                
                # Contexto 12: Auditoría
                audit_repo = Psycopg2AuditLogRepository()
                audit_repo.create(AuditLog(
                    action="QUOTE_APPROVED_BY_CLIENT",
                    module="CUSTOMER_PORTAL",
                    entity_id=order_id,
                    entity_type="WorkOrder",
                    user_name="CLIENTE",
                    details=f"Aprobación remota por valor de ${self.order_details['quoted_price']}"
                ))
                
                # Actualizamos estado local
                self.order_details["quote_approved"] = True
                self._load_public_comments(order_id)
                return rx.window_alert("¡Gracias! Hemos recibido tu aprobación y comenzaremos a trabajar de inmediato.")
                
        except Exception as e:
            return rx.window_alert(f"Error al aprobar: {e}")

    @rx.event
    def reject_quote(self):
        """Rechaza el presupuesto."""
        order_id = self.order_details.get("id")
        if not order_id: return
        
        try:
            audit_repo = Psycopg2AuditLogRepository()
            audit_repo.create(AuditLog(
                action="QUOTE_REJECTED_BY_CLIENT",
                module="CUSTOMER_PORTAL",
                entity_id=order_id,
                entity_type="WorkOrder",
                user_name="CLIENTE",
                details="Rechazo remoto de presupuesto."
            ))
            return rx.window_alert("Has rechazado el presupuesto. Nos pondremos en contacto contigo para los siguientes pasos.")
        except Exception as e:
            return rx.window_alert(f"Error: {e}")
