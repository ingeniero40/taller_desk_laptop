import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.work_order_incident import WorkOrderIncident
from ..database.psycopg_db import Psycopg2Database


class Psycopg2WorkOrderIncidentRepository:
    _COLS = """
        id, created_at, updated_at, work_order_id, reported_by_id,
        problem_found, solution_applied, is_resolved, resolved_at
    """

    def __init__(self, db: Psycopg2Database = None):
        self.db = db or Psycopg2Database()

    def create(self, incident: WorkOrderIncident) -> WorkOrderIncident:
        q = """
            INSERT INTO work_order_incidents
            (id, created_at, updated_at, work_order_id, reported_by_id,
             problem_found, solution_applied, is_resolved, resolved_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;
        """
        self.db.executeRawQuery(
            q,
            (
                str(incident.id),
                incident.created_at,
                incident.updated_at,
                str(incident.work_order_id),
                str(incident.reported_by_id) if incident.reported_by_id else None,
                incident.problem_found,
                incident.solution_applied,
                incident.is_resolved,
                incident.resolved_at,
            ),
            fetch=True,
        )
        return incident

    def findByOrderId(self, order_id: uuid.UUID) -> List[WorkOrderIncident]:
        q = f"SELECT {self._COLS} FROM work_order_incidents WHERE work_order_id=%s ORDER BY created_at ASC"
        rows = self.db.executeRawQuery(q, (str(order_id),), fetch=True)
        return [self._map(r) for r in rows]

    def resolve(self, incident_id: uuid.UUID, solution: str) -> bool:
        q = """
            UPDATE work_order_incidents
            SET is_resolved=TRUE, solution_applied=%s, resolved_at=NOW(), updated_at=NOW()
            WHERE id=%s
        """
        try:
            self.db.executeRawQuery(q, (solution, str(incident_id)))
            return True
        except Exception:
            return False

    def _map(self, row) -> WorkOrderIncident:
        # 0:id 1:created_at 2:updated_at 3:work_order_id 4:reported_by_id
        # 5:problem_found 6:solution_applied 7:is_resolved 8:resolved_at
        return WorkOrderIncident(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            work_order_id=uuid.UUID(str(row[3])),
            reported_by_id=uuid.UUID(str(row[4])) if row[4] else None,
            problem_found=row[5],
            solution_applied=row[6],
            is_resolved=bool(row[7]),
            resolved_at=row[8],
        )
