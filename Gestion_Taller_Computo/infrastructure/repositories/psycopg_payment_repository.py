import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.payment import Payment
from ...domain.interfaces.payment_repository import IPaymentRepository
from ...domain.value_objects.billing_types import PaymentMethod
from ..database.psycopg_db import Psycopg2Database

class Psycopg2PaymentRepository(IPaymentRepository):
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, payment: Payment) -> Payment:
        query = """
            INSERT INTO payments (
                id, created_at, updated_at, invoice_id, amount, 
                payment_method, transaction_reference, payment_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(payment.id), payment.created_at, payment.updated_at,
            str(payment.invoice_id), payment.amount, 
            payment.payment_method.value, payment.transaction_reference,
            payment.payment_date
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return payment

    def findById(self, paymentId: uuid.UUID) -> Optional[Payment]:
        query = "SELECT * FROM payments WHERE id = %s"
        params = (str(paymentId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByInvoiceId(self, invoiceId: uuid.UUID) -> List[Payment]:
        query = "SELECT * FROM payments WHERE invoice_id = %s"
        params = (str(invoiceId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def findAll(self) -> List[Payment]:
        query = "SELECT * FROM payments"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def _map_row_to_entity(self, row) -> Payment:
        return Payment(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            invoice_id=uuid.UUID(str(row[3])),
            amount=float(row[4]),
            payment_method=PaymentMethod(row[5]),
            transaction_reference=row[6],
            payment_date=row[7]
        )
