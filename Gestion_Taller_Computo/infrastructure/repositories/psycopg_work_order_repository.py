import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.work_order import WorkOrder
from ...domain.interfaces.work_order_repository import IWorkOrderRepository
from ...domain.value_objects.work_order_status import WorkOrderStatus
from ...domain.value_objects.order_priority import OrderPriority
from ..database.psycopg_db import Psycopg2Database


class Psycopg2WorkOrderRepository(IWorkOrderRepository):
    """
    Repositorio de Órdenes de Trabajo — Psycopg2.
    Usa columnas nombradas explícitamente para evitar dependencia en el orden de columnas.
    """

    _COLUMNS = """
        id, created_at, updated_at, ticket_number, status,
        device_id, technician_id, diagnostic_notes, repair_notes,
        quoted_price, priority, due_date,
        estimated_hours, actual_hours, actual_delivery
    """

    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    # ── CREATE ────────────────────────────────────────────────────────────

    def create(self, order: WorkOrder) -> WorkOrder:
        query = f"""
            INSERT INTO work_orders (
                id, created_at, updated_at, ticket_number, status,
                device_id, technician_id, diagnostic_notes, repair_notes,
                quoted_price, priority, due_date,
                estimated_hours, actual_hours, actual_delivery
            )
            VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s, %s,%s,%s)
            RETURNING id;
        """
        params = (
            str(order.id), order.created_at, order.updated_at,
            order.ticket_number, order.status.value,
            str(order.device_id),
            str(order.technician_id) if order.technician_id else None,
            order.diagnostic_notes, order.repair_notes,
            order.quoted_price,
            order.priority.value if hasattr(order.priority, "value") else str(order.priority),
            order.due_date,
            order.estimated_hours, order.actual_hours, order.actual_delivery,
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return order

    # ── READ ──────────────────────────────────────────────────────────────

    def findById(self, orderId: uuid.UUID) -> Optional[WorkOrder]:
        q = f"SELECT {self._COLUMNS} FROM work_orders WHERE id = %s"
        rows = self.db.executeRawQuery(q, (str(orderId),), fetch=True)
        return self._map(rows[0]) if rows else None

    def findByTicketNumber(self, ticket: str) -> Optional[WorkOrder]:
        q = f"SELECT {self._COLUMNS} FROM work_orders WHERE ticket_number = %s"
        rows = self.db.executeRawQuery(q, (ticket,), fetch=True)
        return self._map(rows[0]) if rows else None

    def findByDeviceId(self, deviceId: uuid.UUID) -> List[WorkOrder]:
        q = f"SELECT {self._COLUMNS} FROM work_orders WHERE device_id = %s ORDER BY created_at DESC"
        rows = self.db.executeRawQuery(q, (str(deviceId),), fetch=True)
        return [self._map(r) for r in rows]

    def findByStatus(self, status: WorkOrderStatus) -> List[WorkOrder]:
        q = f"SELECT {self._COLUMNS} FROM work_orders WHERE status = %s ORDER BY created_at DESC"
        rows = self.db.executeRawQuery(q, (status.value,), fetch=True)
        return [self._map(r) for r in rows]

    def findByTechnician(self, technician_id: uuid.UUID) -> List[WorkOrder]:
        q = f"SELECT {self._COLUMNS} FROM work_orders WHERE technician_id = %s ORDER BY created_at DESC"
        rows = self.db.executeRawQuery(q, (str(technician_id),), fetch=True)
        return [self._map(r) for r in rows]

    def findAll(self) -> List[WorkOrder]:
        q = f"SELECT {self._COLUMNS} FROM work_orders ORDER BY created_at DESC"
        rows = self.db.executeRawQuery(q, fetch=True)
        return [self._map(r) for r in rows]

    # ── UPDATE ────────────────────────────────────────────────────────────

    def update(self, order: WorkOrder) -> WorkOrder:
        order.updated_at = datetime.utcnow()
        query = """
            UPDATE work_orders
            SET status = %s, technician_id = %s,
                diagnostic_notes = %s, repair_notes = %s,
                quoted_price = %s, priority = %s, due_date = %s,
                estimated_hours = %s, actual_hours = %s, actual_delivery = %s,
                updated_at = %s
            WHERE id = %s
        """
        params = (
            order.status.value,
            str(order.technician_id) if order.technician_id else None,
            order.diagnostic_notes, order.repair_notes,
            order.quoted_price,
            order.priority.value if hasattr(order.priority, "value") else str(order.priority),
            order.due_date,
            order.estimated_hours, order.actual_hours, order.actual_delivery,
            order.updated_at,
            str(order.id),
        )
        self.db.executeRawQuery(query, params)
        return order

    # ── DELETE ────────────────────────────────────────────────────────────

    def delete(self, orderId: uuid.UUID) -> bool:
        try:
            self.db.executeRawQuery(
                "DELETE FROM work_orders WHERE id = %s", (str(orderId),)
            )
            return True
        except Exception:
            return False

    # ── MAPPING ───────────────────────────────────────────────────────────

    def _map(self, row) -> WorkOrder:
        """
        Mapeo explícito por índice usando _COLUMNS:
        0:id 1:created_at 2:updated_at 3:ticket_number 4:status
        5:device_id 6:technician_id 7:diagnostic_notes 8:repair_notes
        9:quoted_price 10:priority 11:due_date
        12:estimated_hours 13:actual_hours 14:actual_delivery
        """
        try:
            priority = OrderPriority(row[10]) if row[10] else OrderPriority.MEDIUM
        except ValueError:
            priority = OrderPriority.MEDIUM

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
            quoted_price=float(row[9]) if row[9] is not None else 0.0,
            priority=priority,
            due_date=row[11],
            estimated_hours=float(row[12]) if row[12] is not None else None,
            actual_hours=float(row[13]) if row[13] is not None else None,
            actual_delivery=row[14],
        )
