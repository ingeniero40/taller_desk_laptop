from typing import List, Optional
from datetime import datetime, timedelta
from ...domain.entities.work_order import WorkOrder
from ...domain.entities.work_order_history import WorkOrderHistory
from ...domain.value_objects.work_order_status import WorkOrderStatus
from ...domain.interfaces.work_order_repository import IWorkOrderRepository
import uuid


class WorkOrderManager:
    """
    Caso de uso para la gestión operativa de Órdenes de Trabajo.
    Implementa el ciclo de vida completo con auditoría de historial.
    """

    def __init__(self, repository: IWorkOrderRepository, history_repository=None):
        self.repository = repository
        self.history_repository = history_repository  # Opcional: registro de auditoría

    # ── Apertura de Orden ─────────────────────────────────────────────────

    def open_order(
        self,
        device_id: uuid.UUID,
        diagnostic_notes: str = None,
        priority: str = "Media",
        estimated_hours: float = None,
        due_date: datetime = None,
        technician_id: uuid.UUID = None,
    ) -> WorkOrder:
        """
        Crea y registra una nueva Orden de Trabajo.
        Genera número de ticket único basado en timestamp.
        """
        ticket = f"TK-{datetime.now().strftime('%y%m%d%H%M%S')}"

        new_order = WorkOrder(
            ticket_number=ticket,
            device_id=device_id,
            status=WorkOrderStatus.RECEIVED,
            diagnostic_notes=diagnostic_notes,
            priority=priority,
            estimated_hours=estimated_hours,
            due_date=due_date or (datetime.utcnow() + timedelta(days=3)),
            technician_id=technician_id,
        )
        created = self.repository.create(new_order)

        # Registrar apertura en historial
        self._record_history(
            order_id=created.id,
            from_status=None,
            to_status=WorkOrderStatus.RECEIVED.value,
            notes="Orden de trabajo creada.",
            changed_by_id=technician_id,
        )
        return created

    # ── Asignación de Técnico ─────────────────────────────────────────────

    def assign_technician(
        self,
        order_id: uuid.UUID,
        technician_id: uuid.UUID,
        notes: str = None,
    ) -> WorkOrder:
        """Asigna el técnico responsable y transiciona a IN_DIAGNOSIS."""
        order = self._get_or_raise(order_id)

        from_status = order.status.value
        order.technician_id = technician_id
        if order.status == WorkOrderStatus.RECEIVED:
            order.status = WorkOrderStatus.IN_DIAGNOSIS

        updated = self.repository.update(order)

        self._record_history(
            order_id=order_id,
            from_status=from_status,
            to_status=order.status.value,
            notes=notes or "Técnico asignado.",
            changed_by_id=technician_id,
        )
        return updated

    # ── Actualización de Estado ───────────────────────────────────────────

    def update_status(
        self,
        order_id: uuid.UUID,
        status: WorkOrderStatus,
        notes: str = None,
        price: float = None,
        actual_hours: float = None,
        changed_by_id: uuid.UUID = None,
    ) -> WorkOrder:
        """Actualiza el estado de la orden con registro automático de historial."""
        order = self._get_or_raise(order_id)

        from_status = order.status.value
        order.status = status

        if notes:
            order.repair_notes = notes
        if price is not None:
            order.quoted_price = price
        if actual_hours is not None:
            order.actual_hours = actual_hours

        # Marcar fecha real de entrega si se marca como DELIVERED
        if status == WorkOrderStatus.DELIVERED:
            order.actual_delivery = datetime.utcnow()

        updated = self.repository.update(order)

        self._record_history(
            order_id=order_id,
            from_status=from_status,
            to_status=status.value,
            notes=notes,
            changed_by_id=changed_by_id,
        )
        return updated

    # ── Actualización de Tiempos y Precio ─────────────────────────────────

    def update_details(
        self,
        order_id: uuid.UUID,
        estimated_hours: float = None,
        actual_hours: float = None,
        quoted_price: float = None,
        due_date: datetime = None,
    ) -> WorkOrder:
        """Actualiza campos de tiempo y costo sin cambiar estado."""
        order = self._get_or_raise(order_id)

        if estimated_hours is not None:
            order.estimated_hours = estimated_hours
        if actual_hours is not None:
            order.actual_hours = actual_hours
        if quoted_price is not None:
            order.quoted_price = quoted_price
        if due_date is not None:
            order.due_date = due_date

        return self.repository.update(order)

    # ── Consultas ─────────────────────────────────────────────────────────

    def get_order_by_ticket(self, ticket: str) -> Optional[WorkOrder]:
        return self.repository.findByTicketNumber(ticket)

    def get_pending_orders(self) -> List[WorkOrder]:
        """Órdenes activas (no terminadas ni canceladas)."""
        pending_states = [
            WorkOrderStatus.RECEIVED,
            WorkOrderStatus.IN_DIAGNOSIS,
            WorkOrderStatus.IN_REPAIR,
            WorkOrderStatus.ON_HOLD,
        ]
        return [o for o in self.repository.findAll() if o.status in pending_states]

    # ── Auditoría Interna ─────────────────────────────────────────────────

    def _record_history(
        self,
        order_id: uuid.UUID,
        from_status: Optional[str],
        to_status: str,
        notes: Optional[str] = None,
        changed_by_id: Optional[uuid.UUID] = None,
    ):
        """Registra un cambio en el historial (si el repo está disponible)."""
        if self.history_repository is None:
            return
        try:
            entry = WorkOrderHistory(
                work_order_id=order_id,
                changed_by_id=changed_by_id,
                from_status=from_status,
                to_status=to_status,
                notes=notes,
            )
            self.history_repository.create(entry)
        except Exception as e:
            # El historial no debe bloquear la operación principal
            print(f"[WorkOrderManager] Historial no registrado: {e}")

    def _get_or_raise(self, order_id: uuid.UUID) -> WorkOrder:
        order = self.repository.findById(order_id)
        if not order:
            raise ValueError(f"Orden no encontrada: {order_id}")
        return order
