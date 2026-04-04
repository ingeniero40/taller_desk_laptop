import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.quote import Quote
from ...domain.interfaces.quote_repository import IQuoteRepository
from ...domain.value_objects.billing_types import QuoteStatus
from ..database.psycopg_db import Psycopg2Database

class Psycopg2QuoteRepository(IQuoteRepository):
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, quote: Quote) -> Quote:
        query = """
            INSERT INTO quotes (
                id, created_at, updated_at, quote_number, customer_id, 
                work_order_id, items_summary, subtotal, tax, total, 
                status, approval_date, expiry_date, conversion_invoice_id, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(quote.id),
            quote.created_at,
            quote.updated_at,
            quote.quote_number,
            str(quote.customer_id),
            str(quote.work_order_id) if quote.work_order_id else None,
            quote.items_summary,
            quote.subtotal,
            quote.tax,
            quote.total,
            quote.status.value,
            quote.approval_date,
            quote.expiry_date,
            str(quote.conversion_invoice_id) if quote.conversion_invoice_id else None,
            quote.notes
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return quote

    def findById(self, quote_id: uuid.UUID) -> Optional[Quote]:
        query = "SELECT * FROM quotes WHERE id = %s"
        params = (str(quote_id),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row(results[0])
        return None

    def findByQuoteNumber(self, quote_number: str) -> Optional[Quote]:
        query = "SELECT * FROM quotes WHERE quote_number = %s"
        params = (quote_number,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row(results[0])
        return None

    def findByWorkOrderId(self, work_order_id: uuid.UUID) -> List[Quote]:
        query = "SELECT * FROM quotes WHERE work_order_id = %s"
        params = (str(work_order_id),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row(row) for row in results]

    def findByCustomerId(self, customer_id: uuid.UUID) -> List[Quote]:
        query = "SELECT * FROM quotes WHERE customer_id = %s"
        params = (str(customer_id),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row(row) for row in results]

    def update(self, quote: Quote) -> Quote:
        quote.updated_at = datetime.utcnow()
        query = """
            UPDATE quotes 
            SET status = %s, approval_date = %s, expiry_date = %s, 
                conversion_invoice_id = %s, notes = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            quote.status.value,
            quote.approval_date,
            quote.expiry_date,
            str(quote.conversion_invoice_id) if quote.conversion_invoice_id else None,
            quote.notes,
            quote.updated_at,
            str(quote.id)
        )
        self.db.executeRawQuery(query, params)
        return quote

    def findAll(self) -> List[Quote]:
        query = "SELECT * FROM quotes ORDER BY created_at DESC"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row(row) for row in results]

    def _map_row(self, row) -> Quote:
        return Quote(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            quote_number=row[3],
            customer_id=uuid.UUID(str(row[4])),
            work_order_id=uuid.UUID(str(row[5])) if row[5] else None,
            items_summary=row[6],
            subtotal=float(row[7]),
            tax=float(row[8]),
            total=float(row[9]),
            status=QuoteStatus(row[10]),
            approval_date=row[11],
            expiry_date=row[12],
            conversion_invoice_id=uuid.UUID(str(row[13])) if row[13] else None,
            notes=row[14]
        )
