from typing import List, Optional
import uuid
from datetime import datetime
from ..database.psycopg_db import Psycopg2Database
from ...domain.entities.audit_log import AuditLog

class Psycopg2AuditLogRepository:
    """
    Repositorio para el historial de auditoría técnica.
    """
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, log: AuditLog) -> bool:
        """
        Inserta un nuevo registro de auditoría en la BD.
        """
        query = """
            INSERT INTO audit_logs (
                id, user_id, user_name, action, module, 
                entity_id, entity_type, previous_value, 
                new_value, details, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        now = datetime.utcnow()
        return self.db.executeRawQuery(
            query, 
            (
                str(log.id), str(log.user_id) if log.user_id else None, 
                log.user_name, log.action, log.module,
                log.entity_id, log.entity_type, 
                log.previous_value, log.new_value, 
                log.details, now, now
            )
        )

    def get_by_entity(self, entity_id: str, limit: int = 50) -> List[dict]:
        """
        Recupera el historial completo de cambios de un objeto específico.
        """
        query = "SELECT * FROM audit_logs WHERE entity_id = %s ORDER BY created_at DESC LIMIT %s"
        results = self.db.executeRawQuery(query, (entity_id, limit), fetch=True)
        return results

    def get_recent_activity(self, limit: int = 100) -> List[dict]:
        """
        Lista de auditoría global para el administrador.
        """
        query = "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT %s"
        results = self.db.executeRawQuery(query, (limit,), fetch=True)
        return results
