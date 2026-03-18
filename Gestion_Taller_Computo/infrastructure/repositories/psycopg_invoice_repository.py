import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.invoice import Invoice
from ...domain.interfaces.invoice_repository import IInvoiceRepository
from ...domain.value_objects.billing_types import InvoiceStatus
from ..database.psycopg_db import Psycopg2Database

class Psycopg2InvoiceRepository(IInvoiceRepository):
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, invoice: Invoice) -> Invoice:
        query = """
            INSERT INTO invoices (
                id, created_at, updated_at, invoice_number, customer_id, 
                work_order_id, subtotal, tax, total, amount_paid, status, due_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(invoice.id), invoice.created_at, invoice.updated_at,
            invoice.invoice_number, str(invoice.customer_id),
            str(invoice.work_order_id) if invoice.work_order_id else None,
            invoice.subtotal, invoice.tax, invoice.total, invoice.amount_paid,
            invoice.status.value, invoice.due_date
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return invoice

    def findById(self, invoiceId: uuid.UUID) -> Optional[Invoice]:
        query = "SELECT * FROM invoices WHERE id = %s"
        params = (str(invoiceId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByInvoiceNumber(self, invoiceNumber: str) -> Optional[Invoice]:
        query = "SELECT * FROM invoices WHERE invoice_number = %s"
        params = (invoiceNumber,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByCustomerId(self, customerId: uuid.UUID) -> List[Invoice]:
        query = "SELECT * FROM invoices WHERE customer_id = %s"
        params = (str(customerId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def findByWorkOrderId(self, workOrderId: uuid.UUID) -> Optional[Invoice]:
        query = "SELECT * FROM invoices WHERE work_order_id = %s"
        params = (str(workOrderId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def update(self, invoice: Invoice) -> Invoice:
        invoice.updated_at = datetime.utcnow()
        query = """
            UPDATE invoices 
            SET amount_paid = %s, status = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            invoice.amount_paid, invoice.status.value, invoice.updated_at,
            str(invoice.id)
        )
        self.db.executeRawQuery(query, params)
        return invoice

    def findAll(self) -> List[Invoice]:
        query = "SELECT * FROM invoices"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def _map_row_to_entity(self, row) -> Invoice:
        # id, created_at, updated_at, invoice_number, customer_id, work_order_id, 
        # subtotal, tax, total, amount_paid, status, due_date
        return Invoice(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            invoice_number=row[3],
            customer_id=uuid.UUID(str(row[4])),
            work_order_id=uuid.UUID(str(row[5])) if row[5] else None,
            subtotal=float(row[6]),
            tax=float(row[7]),
            total=float(row[8]),
            amount_paid=float(row[9]),
            status=InvoiceStatus(row[10]),
            due_date=row[11]
        )
