from typing import List, Optional
from datetime import datetime, timedelta
from ...domain.entities.work_order import WorkOrder
from ...domain.value_objects.work_order_status import WorkOrderStatus
from ...domain.interfaces.work_order_repository import IWorkOrderRepository
import uuid

class WorkOrderManager:
    """
    Caso de uso para la gestión operativa de órdenes de trabajo.
    """
    
    def __init__(self, repository: IWorkOrderRepository):
        self.repository = repository

    def open_order(self, device_id: uuid.UUID, diagnostic_notes: str = None) -> WorkOrder:
        """
        Apertura de una nueva orden de servicio.
        Genera un número de ticket único basado en timestamp.
        """
        ticket = f"TK-{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        new_order = WorkOrder(
            ticket_number=ticket,
            device_id=device_id,
            status=WorkOrderStatus.RECEIVED,
            diagnostic_notes=diagnostic_notes,
            estimated_delivery=datetime.utcnow() + timedelta(days=3)
        )
        return self.repository.create(new_order)

    def assign_technician(self, order_id: uuid.UUID, technician_id: uuid.UUID) -> WorkOrder:
        """
        Asigna el técnico responsable de la reparación.
        """
        order = self.repository.findById(order_id)
        if not order:
            raise ValueError("Orden no encontrada.")
            
        order.technician_id = technician_id
        order.status = WorkOrderStatus.IN_DIAGNOSIS
        return self.repository.update(order)

    def update_status(self, order_id: uuid.UUID, status: WorkOrderStatus, 
                     notes: str = None, price: float = None) -> WorkOrder:
        """
        Actualiza el progreso técnico de la orden.
        """
        order = self.repository.findById(order_id)
        if not order:
            raise ValueError("Orden no encontrada.")
            
        order.status = status
        if notes: order.repair_notes = notes
        if price is not None: order.quoted_price = price
        
        return self.repository.update(order)

    def get_order_by_ticket(self, ticket: str) -> Optional[WorkOrder]:
        return self.repository.findByTicketNumber(ticket)

    def get_pending_orders(self) -> List[WorkOrder]:
        """Recupera órdenes que no han sido terminadas."""
        all_orders = self.repository.findAll()
        pending_states = [
            WorkOrderStatus.RECEIVED, 
            WorkOrderStatus.IN_DIAGNOSIS, 
            WorkOrderStatus.IN_REPAIR, 
            WorkOrderStatus.ON_HOLD
        ]
        return [o for o in all_orders if o.status in pending_states]
