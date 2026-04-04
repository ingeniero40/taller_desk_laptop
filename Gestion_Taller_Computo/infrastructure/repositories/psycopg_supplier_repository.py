import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.supplier import Supplier
from ...domain.interfaces.supplier_repository import ISupplierRepository
from ..database.psycopg_db import Psycopg2Database


class Psycopg2SupplierRepository(ISupplierRepository):
    """
    Implementación del repositorio de proveedores con Psycopg2.
    """

    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, supplier: Supplier) -> Supplier:
        query = """
            INSERT INTO suppliers (id, created_at, updated_at, name, contact_name, email, phone, address, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(supplier.id),
            supplier.created_at,
            supplier.updated_at,
            supplier.name,
            supplier.contact_name,
            supplier.email,
            supplier.phone,
            supplier.address,
            supplier.is_active,
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return supplier

    def findById(self, supplierId: uuid.UUID) -> Optional[Supplier]:
        query = "SELECT * FROM suppliers WHERE id = %s"
        params = (str(supplierId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findAll(self, only_active: bool = True) -> List[Supplier]:
        if only_active:
            query = "SELECT * FROM suppliers WHERE is_active = TRUE"
        else:
            query = "SELECT * FROM suppliers"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def update(self, supplier: Supplier) -> Supplier:
        supplier.updated_at = datetime.utcnow()
        query = """
            UPDATE suppliers 
            SET name = %s, contact_name = %s, email = %s, phone = %s, address = %s, is_active = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            supplier.name,
            supplier.contact_name,
            supplier.email,
            supplier.phone,
            supplier.address,
            supplier.is_active,
            supplier.updated_at,
            str(supplier.id),
        )
        self.db.executeRawQuery(query, params)
        return supplier

    def delete(self, supplierId: uuid.UUID) -> bool:
        # Por seguridad y trazabilidad, muchas veces es mejor desactivar en lugar de borrar físicamente
        query = "UPDATE suppliers SET is_active = FALSE, updated_at = %s WHERE id = %s"
        params = (datetime.utcnow(), str(supplierId))
        try:
            self.db.executeRawQuery(query, params)
            return True
        except:
            return False

    def _map_row_to_entity(self, row) -> Supplier:
        """
        Mapea fila de DB a Supplier.
        Orden esperado: id, created_at, updated_at, name, contact_name, email, phone, address, is_active
        """
        return Supplier(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            name=row[3],
            contact_name=row[4],
            email=row[5],
            phone=row[6],
            address=row[7],
            is_active=row[8],
        )
