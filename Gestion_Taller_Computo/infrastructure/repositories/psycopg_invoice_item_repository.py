import uuid
from typing import List
from ...domain.entities.invoice_item import InvoiceItem
from ...domain.interfaces.invoice_item_repository import IInvoiceItemRepository
from ..database.psycopg_db import Psycopg2Database


class Psycopg2InvoiceItemRepository(IInvoiceItemRepository):
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, item: InvoiceItem) -> InvoiceItem:
        query = """
            INSERT INTO invoice_items (
                id, invoice_id, product_id, description, 
                quantity, unit_price, subtotal, tax, total
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            str(item.id),
            str(item.invoice_id),
            str(item.product_id) if item.product_id else None,
            item.description,
            item.quantity,
            item.unit_price,
            item.subtotal,
            item.tax,
            item.total
        )
        self.db.executeRawQuery(query, params)
        return item

    def findByInvoiceId(self, invoice_id: uuid.UUID) -> List[InvoiceItem]:
        query = "SELECT * FROM invoice_items WHERE invoice_id = %s"
        params = (str(invoice_id),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row(row) for row in results]

    def delete(self, item_id: uuid.UUID) -> bool:
        query = "DELETE FROM invoice_items WHERE id = %s"
        params = (str(item_id),)
        self.db.executeRawQuery(query, params)
        return True

    def _map_row(self, row) -> InvoiceItem:
        return InvoiceItem(
            id=uuid.UUID(str(row[0])),
            invoice_id=uuid.UUID(str(row[3])),
            product_id=uuid.UUID(str(row[4])) if row[4] else None,
            description=row[5],
            quantity=int(row[6]),
            unit_price=float(row[7]),
            subtotal=float(row[8]),
            tax=float(row[9]),
            total=float(row[10]) or 0.0 # Standard order based on schema
        )
        # Note: Need to be careful with column indices if schema changed.
        # id, created_at, updated_at, invoice_id, product_id, description, quantity, unit_price, subtotal, tax, total
