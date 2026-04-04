import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.work_order_history import WorkOrderHistory
from ..database.psycopg_db import Psycopg2Database


class Psycopg2WorkOrderHistoryRepository:
    """
    Repositorio de Historial de Órdenes de Trabajo — Psycopg2.
    Registra cambios de estado de forma inmutable para auditoría.
    """

    _COLUMNS = """
        id, created_at, updated_at,
        work_order_id, changed_by_id,
        from_status, to_status, notes, changed_at
    """

    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, entry: WorkOrderHistory) -> WorkOrderHistory:
        query = f"""
            INSERT INTO work_order_history (
                id, created_at, updated_at,
                work_order_id, changed_by_id,
                from_status, to_status, notes, changed_at
            )
            VALUES (%s,%s,%s, %s,%s, %s,%s,%s,%s)
            RETURNING id;
        """
        params = (
            str(entry.id),
            entry.created_at,
            entry.updated_at,
            str(entry.work_order_id),
            str(entry.changed_by_id) if entry.changed_by_id else None,
            entry.from_status,
            entry.to_status,
            entry.notes,
            entry.changed_at,
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return entry

    def findByOrderId(self, order_id: uuid.UUID) -> List[WorkOrderHistory]:
        q = f"""
            SELECT {self._COLUMNS}
            FROM work_order_history
            WHERE work_order_id = %s
            ORDER BY changed_at ASC
        """
        rows = self.db.executeRawQuery(q, (str(order_id),), fetch=True)
        return [self._map(r) for r in rows]

    def findAll(self) -> List[WorkOrderHistory]:
        q = f"SELECT {self._COLUMNS} FROM work_order_history ORDER BY changed_at DESC"
        rows = self.db.executeRawQuery(q, fetch=True)
        return [self._map(r) for r in rows]

    def _map(self, row) -> WorkOrderHistory:
        """
        0:id 1:created_at 2:updated_at
        3:work_order_id 4:changed_by_id
        5:from_status 6:to_status 7:notes 8:changed_at
        """
        return WorkOrderHistory(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            work_order_id=uuid.UUID(str(row[3])),
            changed_by_id=uuid.UUID(str(row[4])) if row[4] else None,
            from_status=row[5],
            to_status=row[6],
            notes=row[7],
            changed_at=row[8],
        )
