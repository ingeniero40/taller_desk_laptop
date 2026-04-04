import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.work_order_comment import WorkOrderComment
from ..database.psycopg_db import Psycopg2Database


class Psycopg2WorkOrderCommentRepository:
    _COLS = "id, created_at, updated_at, work_order_id, author_id, author_name, content, is_internal"

    def __init__(self, db: Psycopg2Database = None):
        self.db = db or Psycopg2Database()

    def create(self, comment: WorkOrderComment) -> WorkOrderComment:
        q = f"""
            INSERT INTO work_order_comments
            (id, created_at, updated_at, work_order_id, author_id, author_name, content, is_internal)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;
        """
        self.db.executeRawQuery(
            q,
            (
                str(comment.id),
                comment.created_at,
                comment.updated_at,
                str(comment.work_order_id),
                str(comment.author_id) if comment.author_id else None,
                comment.author_name,
                comment.content,
                comment.is_internal,
            ),
            fetch=True,
        )
        return comment

    def findByOrderId(
        self, order_id: uuid.UUID, include_internal: bool = True
    ) -> List[WorkOrderComment]:
        if include_internal:
            q = f"SELECT {self._COLS} FROM work_order_comments WHERE work_order_id=%s ORDER BY created_at ASC"
            rows = self.db.executeRawQuery(q, (str(order_id),), fetch=True)
        else:
            q = f"SELECT {self._COLS} FROM work_order_comments WHERE work_order_id=%s AND is_internal=FALSE ORDER BY created_at ASC"
            rows = self.db.executeRawQuery(q, (str(order_id),), fetch=True)
        return [self._map(r) for r in rows]

    def _map(self, row) -> WorkOrderComment:
        # 0:id 1:created_at 2:updated_at 3:work_order_id 4:author_id 5:author_name 6:content 7:is_internal
        return WorkOrderComment(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            work_order_id=uuid.UUID(str(row[3])),
            author_id=uuid.UUID(str(row[4])) if row[4] else None,
            author_name=row[5],
            content=row[6],
            is_internal=bool(row[7]),
        )
