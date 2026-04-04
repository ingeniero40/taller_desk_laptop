import uuid
from typing import List
from ...domain.entities.inventory_movement import InventoryMovement
from ...domain.interfaces.inventory_movement_repository import IInventoryMovementRepository
from ..database.psycopg_db import Psycopg2Database

class Psycopg2InventoryMovementRepository(IInventoryMovementRepository):
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, movement: InventoryMovement) -> InventoryMovement:
        query = """
            INSERT INTO inventory_movements (
                id, created_at, updated_at, product_id, movement_type, 
                quantity, reference_id, notes, created_by_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(movement.id),
            movement.created_at,
            movement.updated_at,
            str(movement.product_id),
            movement.movement_type,
            movement.quantity,
            movement.reference_id,
            movement.notes,
            str(movement.created_by_id) if movement.created_by_id else None,
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return movement

    def findByProductId(self, product_id: uuid.UUID) -> List[InventoryMovement]:
        query = "SELECT * FROM inventory_movements WHERE product_id = %s ORDER BY created_at DESC"
        results = self.db.executeRawQuery(query, (str(product_id),), fetch=True)
        return [self._map_row(row) for row in results]

    def findByReferenceId(self, reference_id: str) -> List[InventoryMovement]:
        query = "SELECT * FROM inventory_movements WHERE reference_id = %s ORDER BY created_at DESC"
        results = self.db.executeRawQuery(query, (reference_id,), fetch=True)
        return [self._map_row(row) for row in results]

    def findAll(self, limit: int = 50) -> List[InventoryMovement]:
        query = "SELECT * FROM inventory_movements ORDER BY created_at DESC LIMIT %s"
        results = self.db.executeRawQuery(query, (limit,), fetch=True)
        return [self._map_row(row) for row in results]

    def _map_row(self, row) -> InventoryMovement:
        return InventoryMovement(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            product_id=uuid.UUID(str(row[3])),
            movement_type=row[4],
            quantity=int(row[5]),
            reference_id=row[6],
            notes=row[7],
            created_by_id=uuid.UUID(str(row[8])) if row[8] else None,
        )
