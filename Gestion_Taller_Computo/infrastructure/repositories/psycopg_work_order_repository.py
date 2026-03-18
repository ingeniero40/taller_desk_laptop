import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.work_order import WorkOrder
from ...domain.interfaces.work_order_repository import IWorkOrderRepository
from ...domain.value_objects.work_order_status import WorkOrderStatus
from ..database.psycopg_db import Psycopg2Database

class Psycopg2WorkOrderRepository(IWorkOrderRepository):
    """
    Implementación del repositorio de órdenes de trabajo con Psycopg2.
    """
    
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, order: WorkOrder) -> WorkOrder:
        query = """
            INSERT INTO work_orders (
                id, created_at, updated_at, ticket_number, status, 
                device_id, technician_id, diagnostic_notes, repair_notes, 
                estimated_delivery, quoted_price
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(order.id), order.created_at, order.updated_at, order.ticket_number,
            order.status.value, str(order.device_id), 
            str(order.technician_id) if order.technician_id else None,
            order.diagnostic_notes, order.repair_notes,
            order.estimated_delivery, order.quoted_price
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return order

    def findById(self, orderId: uuid.UUID) -> Optional[WorkOrder]:
        query = "SELECT * FROM work_orders WHERE id = %s"
        params = (str(orderId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByTicketNumber(self, ticket: str) -> Optional[WorkOrder]:
        query = "SELECT * FROM work_orders WHERE ticket_number = %s"
        params = (ticket,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByDeviceId(self, deviceId: uuid.UUID) -> List[WorkOrder]:
        query = "SELECT * FROM work_orders WHERE device_id = %s"
        params = (str(deviceId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def findByStatus(self, status: WorkOrderStatus) -> List[WorkOrder]:
        query = "SELECT * FROM work_orders WHERE status = %s"
        params = (status.value,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def findAll(self) -> List[WorkOrder]:
        query = "SELECT * FROM work_orders"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def update(self, order: WorkOrder) -> WorkOrder:
        order.updated_at = datetime.utcnow()
        query = """
            UPDATE work_orders 
            SET status = %s, technician_id = %s, diagnostic_notes = %s, 
                repair_notes = %s, estimated_delivery = %s, quoted_price = %s, 
                updated_at = %s
            WHERE id = %s
        """
        params = (
            order.status.value, 
            str(order.technician_id) if order.technician_id else None,
            order.diagnostic_notes, order.repair_notes,
            order.estimated_delivery, order.quoted_price,
            order.updated_at, str(order.id)
        )
        self.db.executeRawQuery(query, params)
        return order

    def _map_row_to_entity(self, row) -> WorkOrder:
        """
        Mapea fila de DB a WorkOrder.
        Orden: id, created_at, updated_at, ticket_number, status, device_id, 
               technician_id, diagnostic_notes, repair_notes, estimated_delivery, quoted_price
        """
        return WorkOrder(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            ticket_number=row[3],
            status=WorkOrderStatus(row[4]),
            device_id=uuid.UUID(str(row[5])),
            technician_id=uuid.UUID(str(row[6])) if row[6] else None,
            diagnostic_notes=row[7],
            repair_notes=row[8],
            estimated_delivery=row[9],
            quoted_price=float(row[10])
        )
